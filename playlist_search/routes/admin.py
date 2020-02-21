import json
import datetime

from flask import Blueprint, request, abort, jsonify, url_for

from flask import current_app as app

from ..models.playlist import Playlist, playlist_schema, playlists_schema
from ..models.track import Track
from ..models.track_identifier import TrackIdentifier, track_identifier_schema
from ..models.base import db

from .. import celery

from .util import get_by_id, init_spotipy, lookup_playlist

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/count_playlists', methods=['GET'])
def count_playlists():
    return str(Playlist.query.count())

@admin_blueprint.route('/drop_db', methods=['GET'])
def drop_db():
    db.drop_all()
    return "dropped"

@celery.task(bind=True)
def reset_db_task(self):
    spotify = init_spotipy()

    user_spotify_ids = ['particledetector', 'thesoundsofspotify']

    db.create_all()

    user_playlist_counts = [get_user_playlist_count(u, spotify) for u in user_spotify_ids]
    print('user_playlist_counts  = {}'.format(user_playlist_counts ))
    total_playlist_count = sum(user_playlist_counts)
    print('total_playlist_count  = {}'.format(total_playlist_count ))

    # add playlists in db to total so that progress bar only shows complete after we delete old playlists too
    count_playlists_in_db = Playlist.query.count()

    cur_playlist = 0
    
    for user_spotify_id in user_spotify_ids:
        app.logger.info('user_spotify_id = {}'.format(user_spotify_id))
        
        api_playlists = get_user_playlists(user_spotify_id, spotify, test_mode=False)
        for api_playlist in api_playlists:
            api_playlist_snapshot_id = api_playlist.snapshot_id
            playlist_spotify_id = api_playlist.id
            app.logger.info('playlist_spotify_id  = {}'.format(playlist_spotify_id ))

            db_playlist = Playlist.query.filter_by(spotify_id=playlist_spotify_id).first()
            if db_playlist is not None:
                if db_playlist.snapshot_id == api_playlist.snapshot_id:
                    app.logger.info('found playlist already in database and up to date - skipping: {}'.format(playlist_spotify_id))
                else:
                    app.logger.info('found playlist already in playlist, but not up to date - updating: {}'.format(playlist_spotify_id))
                    db.session.delete(db_playlist)
                    store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify)
            else:
                app.logger.info('did not find playlist in database, creating a new one: {}'.format(playlist_spotify_id))
                store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify)

            cur_playlist += 1
            self.update_state(state='PROGRESS',
                          meta={'current': cur_playlist, 'total': total_playlist_count,
                                'status': 'syncing_playlists_{}'.format(user_spotify_id)})


#   for every playlist in playlist database:
#       look up playlist by id in spotify
#       if playlist is None:
#           delete playlist from database

    return {'current': total_playlist_count, 'total': total_playlist_count, 'status': 'completed'}


@admin_blueprint.route('/reset_db', methods=['POST'])
def reset_db():
    task = reset_db_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('admin.status', task_id=task.id)}
    #reset_db_no_celery()

@admin_blueprint.route('/status/<task_id>')
def status(task_id):
    task = reset_db_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

def get_user_playlist_count(user_id, spotify):
    user_playlist_data = spotify.playlists(user_id, limit=50)
    return user_playlist_data.total

def get_user_playlists(user_id, spotify, test_mode=False):
    PLAYLISTS_API_LIMIT = 50 # set limit to maximum

    i = 0
    while True:
        user_playlists = spotify.playlists(user_id, limit=PLAYLISTS_API_LIMIT, offset=i)
        app.logger.info("total user_playlists = {}".format(user_playlists.total))

        for playlist in user_playlists.items:
            yield playlist

        i += PLAYLISTS_API_LIMIT

        if user_playlists.next is None:
            break

def store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify):
    playlist_snapshot_id  = lookup_playlist(playlist_spotify_id, fields=['snapshot_id'])['snapshot_id']

    playlist = Playlist(spotify_id=playlist_spotify_id, snapshot_id=playlist_snapshot_id)

    add_tracks_to_playlist(user_spotify_id, playlist, spotify)
    db.session.commit()

def add_tracks_to_playlist(user_id, playlist, spotify):
    fields = 'items(track(id),added_at),next'
    api_tracks = get_user_playlist_tracks(user_id, playlist.spotify_id, fields, spotify)

    for index, api_track in enumerate(api_tracks['items']):
        # need to do this instead of using .get('track', {}).get('id') because
        # sometimes the actual value of track is None in the API and the
        # `.get('track', {})` doesn't use the default value in that case
        api_track_track = api_track.get('track')
        if api_track_track is None:
            continue

        api_track_spotify_id = api_track_track.get('id')

        track = Track.query.filter_by(spotify_id=api_track_spotify_id).first()
        if track is None:
            track = Track(spotify_id=api_track_spotify_id)

        added_at_string = api_track.get('added_at')
        added_at_datetime = None
        if added_at_string is not None:
            added_at_datetime = datetime.datetime.strptime(added_at_string, '%Y-%m-%dT%H:%M:%SZ')

        ti = TrackIdentifier()
        ti.playlist = playlist
        ti.track_index_in_playlist = index

        if added_at_datetime is not None:
            ti.track_added_at = added_at_datetime

        track.playlists.append(ti)
        db.session.add(track)

        # flush here so that when we query within this loop, we get the tracks
        # that haven't been committed. E.g. a song in a playlist twice
        db.session.commit()


def get_user_playlist_tracks(user_id, playlist_id, fields, spotify):
    PLAYLIST_TRACKS_API_LIMIT=100
    tracks = []

    app.logger.info('processing playlist {}'.format(playlist_id))

    offset = 0
    while True:
        api_tracks = spotify.playlist_tracks(playlist_id, fields=fields, limit=PLAYLIST_TRACKS_API_LIMIT, offset=offset)
        tracks.extend(api_tracks['items'])
        offset += PLAYLIST_TRACKS_API_LIMIT
        if api_tracks['next'] is None:
            break

    return {'items': tracks}



