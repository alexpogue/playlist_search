import json

from flask import Blueprint, request, abort, jsonify
from ..models.track import Track
from ..models.base import db

from ..models.track import track_schema, tracks_schema
from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint

from .util import get_by_id, lookup_track, lookup_playlists, get_track_in_playlist_details, lookup_playlist

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

track_blueprint = Blueprint('tracks', __name__)

@track_blueprint.route('/')
def get_track_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    api_track = lookup_track(requested_spotify_id, fields=['id', 'artists', 'album', 'name'])

    track_from_db = Track.query.filter_by(spotify_id=requested_spotify_id).first()
    print('track_from_db  = {}'.format(track_from_db ))

    if track_from_db is not None:
        print('track_from_db is not None')
        track_identifiers_from_db = track_from_db.playlists

        # this array is filled in below
        api_track['playlists'] = []

        for track_identifier in track_identifiers_from_db:
            playlist_spotify_id = track_identifier.playlist.spotify_id
            api_playlist = lookup_playlist(playlist_spotify_id, ['name', 'external_urls'])

            api_playlist['track_rank'] = track_identifier.track_index_in_playlist + 1
            api_playlist['added_at'] = track_identifier.track_added_at

            api_track['playlists'].append(api_playlist)

    return api_track

@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    track = get_by_id(Track, track_id, track_schema)
    print('track  = {}'.format(track ))
    return lookup_track(track['spotify_id'])
