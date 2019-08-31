from flask import abort, jsonify
from flask import current_app as app

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def init_spotipy():
    spotify_client_id = app.config['SPOTIFY_CLIENT_ID']
    spotify_client_secret = app.config['SPOTIFY_CLIENT_SECRET']

    client_credentials_manager = SpotifyClientCredentials(spotify_client_id, spotify_client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_by_id(model_cls, lookup_id, schema):
    model_obj = model_cls.query.get(lookup_id)
    if model_obj is None:
        abort(404)
    result = schema.dump(model_obj)

    #table_name = model_cls.__table__.name
    #keyed_result = {table_name: result}
    return result

def lookup_track(track_spotify_id, fields=None):
    spotify = init_spotipy()
    track = spotify.track(track_spotify_id)
    if fields is not None:
        track = filter_track_by_fields(track, fields)
    return track

def lookup_tracks(track_spotify_ids, fields=None):
    spotify = init_spotipy()
    tracks = []
    MAX_REQUEST_IDS = 50
    i = 0
    while i < len(track_spotify_ids):
        segmented_ids = track_spotify_ids[i:i+MAX_REQUEST_IDS]
        cur_tracks = spotify.tracks(segmented_ids)
        tracks.extend(cur_tracks['tracks'])
        i += MAX_REQUEST_IDS

    if fields is not None:
        tracks = filter_tracks_by_fields(tracks, fields)

    return {'tracks': tracks}

def lookup_playlists(playlist_spotify_ids, fields=None):
    spotify = init_spotipy()
    playlists = []
    for playlist_spotify_id in playlist_spotify_ids:
        api_playlist = spotify.playlist(playlist_spotify_id)
        playlists.append(api_playlist)

    return {'playlists': playlists}

def filter_tracks_by_fields(tracks, fields):
    if fields is None:
        return tracks
    return [ filter_track_by_fields(track, fields) for track in tracks ]

def filter_track_by_fields(track, fields):
    if fields is None:
        return track
    return { field: track[field] for field in fields }

