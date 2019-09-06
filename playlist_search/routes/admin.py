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

    get_user_playlists(user_spotify_id, spotify, test_mode=False)

    playlists = Playlist.query.all()

    result = playlists_schema.dump(playlists)

    return_val = {'result': playlists}
    return jsonify(result)

def get_user_playlists(user_id, spotify, fields=None, test_mode=False):
    PLAYLISTS_API_LIMIT = 50 # set limit to maximum

#    playlists = []
    track_id_map = {}
    album_id_map = {}

    user_playlists = spotify.user_playlists(user_id, limit=PLAYLISTS_API_LIMIT)
#    playlists.extend(user_playlists['items'])
    for playlist in user_playlists['items']:
        playlist_spotify_id = playlist['id']
        store_playlist_and_subobjects_to_db(user_id, playlist_spotify_id, spotify, track_id_map, album_id_map)

    i = PLAYLISTS_API_LIMIT
    while user_playlists.get('next') is not None and test_mode == False:
        print('i  = {}'.format(i ))
        user_playlists = spotify.user_playlists(user_id, limit=PLAYLISTS_API_LIMIT, offset=i)

        for playlist in user_playlists['items']:
            playlist_spotify_id = playlist['id']
            store_playlist_and_subobjects_to_db(user_id, playlist_spotify_id, spotify, track_id_map, album_id_map)
#        playlists.extend(user_playlists['items'])
        i += PLAYLISTS_API_LIMIT

#    return {'items': playlists}

def store_playlist_and_subobjects_to_db(user_spotify_id, playlist_spotify_id, spotify, track_id_map, album_id_map):
    playlist = Playlist(spotify_id=playlist_spotify_id)
    add_tracks_to_playlist(user_spotify_id, playlist, spotify, track_id_map, album_id_map)
    db.session.add(playlist)
    db.session.commit()

    # TODO: This is too late to be adding tracks to the track_id_map... What if a track is in a playlist twice?
    # Even if this doesn't happen, surely there could be one album listed twice in a single playlist, and we'll
    # have to do similar thing for albums... How can we get the id before the db.commit?? hmmm.
    for track in playlist.tracks:
        track_id_map[track.spotify_id] = track.id

def add_tracks_to_playlist(user_id, playlist, spotify, track_id_map, album_id_map):
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

        track_db_id = track_id_map.get(api_track_spotify_id)
        if track_db_id is not None:
            track = Track.query.get(track_db_id)
        else:
            track = Track(spotify_id=api_track_spotify_id)

        api_album = api_track.get('track', {}).get('album')

        if api_album is not None:
            api_album_spotify_id = api_album.get('id')
            album = Album(spotify_id=api_album_spotify_id)
            track.album = album

        playlist.tracks.append(track)

def get_user_playlist_tracks(user_id, playlist_id, fields, spotify):
    PLAYLIST_TRACKS_API_LIMIT=100
    tracks = []
    api_tracks = spotify.user_playlist_tracks(user_id, playlist_id, fields=fields, limit=PLAYLIST_TRACKS_API_LIMIT)
    tracks.extend(api_tracks['items'])

    i = PLAYLIST_TRACKS_API_LIMIT
    while api_tracks.get('next') is not None:
        print('track_i = {}'.format(i))
        api_tracks = spotify.user_playlist_tracks(user_id, playlist_id, fields=fields, limit=PLAYLIST_TRACKS_API_LIMIT, offset=i)
        tracks.extend(api_tracks['items'])
        i += PLAYLIST_TRACKS_API_LIMIT

    return {'items': tracks}
