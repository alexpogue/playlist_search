import json

from flask import Blueprint, request, abort, jsonify
from ..models.track import Track
from ..models.base import db

from ..models.track import track_schema, tracks_schema
from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint

from .util import get_by_id, lookup_track, lookup_playlists

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

track_blueprint = Blueprint('tracks', __name__)

@track_blueprint.route('/')
def get_track_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    track = lookup_track(requested_spotify_id, fields=['album', 'artists', 'name'])

    track_from_db = Track.query.filter_by(spotify_id=requested_spotify_id).first()

    if track_from_db is not None:
        playlists_from_db = track_from_db.playlists
        playlist_spotify_ids_from_db = [ playlist.spotify_id for playlist in playlists_from_db ]

        api_playlists = lookup_playlists(playlist_spotify_ids_from_db)
        track['playlists'] = api_playlists['playlists']

        album_from_db = track_from_db.album
        #api_album = lookup_album(album_from_db.spotify_id)

        #print('album = {}'.format(album))

    return track

@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    track = get_by_id(Track, track_id, track_schema)
    print('track  = {}'.format(track ))
    return lookup_track(track['spotify_id'])
