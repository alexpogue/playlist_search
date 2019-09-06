import json

from flask import Blueprint, request, abort, jsonify
from ..models.album import Album
from ..models.base import db

from ..models.album import album_schema, album_schema

from flask_marshmallow import pprint

from .util import get_by_id, lookup_album, lookup_tracks, lookup_playlists

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

album_blueprint = Blueprint('album', __name__)

@album_blueprint.route('/')
def get_album_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    album = lookup_album(requested_spotify_id, fields=None) # TODO fill in fields

    album_from_db = Album.query.filter_by(spotify_id=requested_spotify_id).first()

    if album_from_db is not None:
        tracks_from_db = album_from_db.tracks

        db_tracks_dict = { track.spotify_id:track for track in tracks_from_db }

        tracks_spotify_ids_from_db = [ track.spotify_id for track in tracks_from_db ]
        api_tracks = lookup_tracks(tracks_spotify_ids_from_db, ['name', 'id'])['tracks']

        # fill in api_tracks with the playlists lists
        for api_track in api_tracks:
            spotify_id = api_track['id']
            track_from_db = db_tracks_dict[spotify_id]
            playlists_from_db = track_from_db.playlists
            playlist_spotify_ids_from_db = [ playlist.spotify_id for playlist in playlists_from_db ]

            api_playlists = lookup_playlists(playlist_spotify_ids_from_db, ['name'])

            api_track['playlists'] = api_playlists['playlists']
            print('api_track = {}'.format(json.dumps(api_track, indent=4)))


        api_album = lookup_album(album_from_db.spotify_id)
        api_album['tracks'] = api_tracks

        print('album = {}'.format(json.dumps(album, indent=4)))

    return album

@album_blueprint.route('/<int:album_id>', methods=['GET'])
def get_album_by_id(album_id):
    album = get_by_id(Album, album_id, album_schema)
    print('album  = {}'.format(album ))
    return lookup_album(album['spotify_id'])
