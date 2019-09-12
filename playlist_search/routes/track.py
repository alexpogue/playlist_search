import json

from flask import Blueprint, request, abort, jsonify
from ..models.track import Track
from ..models.base import db

from ..models.track import track_schema, tracks_schema
from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint

from .util import get_by_id, lookup_track, lookup_playlists, get_track_in_playlist_details

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

track_blueprint = Blueprint('tracks', __name__)

@track_blueprint.route('/')
def get_track_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    api_track = lookup_track(requested_spotify_id, fields=['id', 'artists', 'album', 'name'])

    track_from_db = Track.query.filter_by(spotify_id=requested_spotify_id).first()

    if track_from_db is not None:
        playlists_from_db = track_from_db.playlists
        playlist_spotify_ids_from_db = [ playlist.spotify_id for playlist in playlists_from_db ]

        api_playlists = lookup_playlists(playlist_spotify_ids_from_db)

        for api_playlist in api_playlists['playlists']:
            track_in_playlist_details = get_track_in_playlist_details(api_track['id'], api_playlist['id'])
            api_playlist['track_rank'] = track_in_playlist_details['track_rank']
            api_playlist['added_at'] = track_in_playlist_details['added_at']

        api_track['playlists'] = api_playlists['playlists']

    return api_track

@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    track = get_by_id(Track, track_id, track_schema)
    print('track  = {}'.format(track ))
    return lookup_track(track['spotify_id'])
