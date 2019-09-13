import json

from flask import Blueprint, request, abort, jsonify

from flask import current_app as app

from ..models.playlist import Playlist, playlist_schema, playlists_schema
from ..models.track import Track
from ..models.album import Album
from ..models.base import db

from .util import get_by_id, init_spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/reset_db', methods=['GET'])
def reset_db():
    spotify = init_spotipy()

    user_spotify_id = 'particledetector'

    # completely reset
    db.drop_all()
    db.create_all()

    api_playlists = get_user_playlists(user_spotify_id, spotify, test_mode=False)
    for api_playlist in api_playlists:
        playlist_spotify_id = api_playlist['id']
        store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify)

    playlists = Playlist.query.all()

    result = playlists_schema.dump(playlists)

    return_val = {'result': playlists}
    return jsonify(result)

def get_user_playlists(user_id, spotify, test_mode=False):
    PLAYLISTS_API_LIMIT = 50 # set limit to maximum

    i = 0
    user_playlists = {'next':'blah'} # just something to fulfill the first condition
    while user_playlists.get('next') is not None:
        user_playlists = spotify.user_playlists(user_id, limit=PLAYLISTS_API_LIMIT, offset=i)

        for playlist in user_playlists['items']:
            yield playlist

        i += PLAYLISTS_API_LIMIT

def store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify):
    playlist = Playlist(spotify_id=playlist_spotify_id)
    add_tracks_to_playlist(user_spotify_id, playlist, spotify)
    db.session.commit()

def add_tracks_to_playlist(user_id, playlist, spotify):
    fields = 'items(track(id,album.id,artists)),next'
    api_tracks = get_user_playlist_tracks(user_id, playlist.spotify_id, fields, spotify)

    for api_track in api_tracks['items']:
        # need to do this instead of using .get('track', {}).get('id') because
        # sometimes the actual value of track is None in the API and the
        # `.get('track', {})` doesn't use the default value in that case
        api_track_track = api_track.get('track')
        if api_track_track is None:
            continue

        api_track_spotify_id = api_track_track.get('id')

        track = Track.query.filter_by(spotify_id=api_track_spotify_id).one_or_none()
        if track is None:
            track = Track(spotify_id=api_track_spotify_id)

        api_album = api_track.get('track', {}).get('album')

        if api_album is not None:
            api_album_spotify_id = api_album.get('id')
            album = Album(spotify_id=api_album_spotify_id)
            track.album = album

        track.playlists.append(playlist)
        db.session.add(track)
        # flush here so that when we query within this loop, we get the tracks
        # that haven't been committed. E.g. a song in a playlist twice
        db.session.flush()

def get_user_playlist_tracks(user_id, playlist_id, fields, spotify):
    PLAYLIST_TRACKS_API_LIMIT=100
    tracks = []

    i = 0
    api_tracks = {'next': 'blah'} # just something to fulfill the first condition
    while api_tracks.get('next') is not None:
        print('track_i = {}'.format(i))
        api_tracks = spotify.user_playlist_tracks(user_id, playlist_id, fields=fields, limit=PLAYLIST_TRACKS_API_LIMIT, offset=i)
        tracks.extend(api_tracks['items'])
        i += PLAYLIST_TRACKS_API_LIMIT

    return {'items': tracks}
