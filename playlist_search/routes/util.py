import json
from flask import abort, jsonify
from flask import current_app as app

from tekore import Spotify
from tekore._auth.util import request_client_token
from tekore._sender import RetryingSender

def init_spotipy():
    spotify_client_id = app.config['SPOTIFY_CLIENT_ID']
    spotify_client_secret = app.config['SPOTIFY_CLIENT_SECRET']

    app_token = request_client_token(spotify_client_id, spotify_client_secret)

    # use RetryingSender to retry when we are rate limited by spotify API
    sender = RetryingSender(retries=100)
    return Spotify(app_token, sender=sender)

def get_by_id(model_cls, lookup_id, schema):
    model_obj = model_cls.query.get(lookup_id)
    if model_obj is None:
        abort(404)
    result = schema.dump(model_obj)

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

    str_fields = None
    if fields is not None:
        str_fields = ','.join(fields)

    playlists = []
    for playlist_spotify_id in playlist_spotify_ids:
        api_playlist = spotify.playlist(playlist_spotify_id, fields=str_fields)
        playlists.append(api_playlist)

    return {'playlists': playlists}

def lookup_playlist(playlist_spotify_id, fields=None):
    spotify = init_spotipy()

    str_fields = None
    if fields is not None:
        str_fields = ','.join(fields)

    # Commented out because of issue with `fields` param on this function,
    # see https://github.com/felix-hilden/tekore/issues/142 for details
    api_playlist = spotify.playlist(playlist_spotify_id, fields=str_fields)
    return api_playlist

def get_track_in_playlist_details(track_spotify_id, playlist_spotify_id):
    api_tracks = lookup_tracks_from_playlist(playlist_spotify_id, ['items.track.id', 'items.added_at'])

    rank = -1
    added_at = 'not found'
    for index, track in enumerate(api_tracks):
        track_track = track.get('track')
        if track_track is not None and track_track['id'] == track_spotify_id:
            rank = index + 1
            added_at = track['added_at']
            break

    return {'track_rank': rank, 'added_at': added_at}

def lookup_tracks_from_playlist(playlist_spotify_id, fields=None):
    if fields is not None:
        fields.append('next') # needed for paging
    spotipy = init_spotipy()

    str_fields = None
    if fields is not None:
        str_fields = ','.join(fields)

    TRACKS_API_LIMIT = 100 # set limit to maximum

    # TODO: I think there is some error here that makes it continue yielding into infinity for playlist 1MgizgTkP3tKN0qCwQRZTN searching for track 6WykLJ5yFXXcqhahrlonLY
    #       ... Maybe this function yields to infinity on all playlists, but we find a matching track in a playlist first so we break early from get_track_in_playlist_details.

    # TODO: clean up the duplicated code - use similar strategy as admin.get_user_playlist_tracks
    api_tracks = spotipy.playlist_items(playlist_spotify_id, fields=str_fields, limit=TRACKS_API_LIMIT)
    for api_track in api_tracks['items']:
        yield api_track

    i = TRACKS_API_LIMIT
    while api_tracks.get('next') is not None:
        api_tracks = spotipy.playlist_items(playlist_spotify_id, fields=str_fields, limit=TRACKS_API_LIMIT, offset=i)
        for api_track in api_tracks['items']:
            yield api_track

def filter_tracks_by_fields(tracks, fields):
    if fields is None:
        return tracks
    return [ filter_track_by_fields(track, fields) for track in tracks ]

def filter_track_by_fields(track, fields):
    if fields is None:
        return track
    return { field: getattr(track, field) for field in fields }
