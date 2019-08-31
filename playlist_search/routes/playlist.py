import json

from flask import Blueprint, request, abort, jsonify
from ..models.playlist import Playlist
from ..models.base import db

from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint
from .util import get_by_id, lookup_tracks

playlist_blueprint = Blueprint('playlists', __name__)

@playlist_blueprint.route('/')
def get_playlists():
    playlist = Playlist.query.first()
    result, errors = playlist_schema.dump(playlist)

    return jsonify(result)
    
@playlist_blueprint.route('/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = get_by_id(Playlist, playlist_id, playlist_schema)
    spotify_track_ids = [ t['spotify_id'] for t in playlist['tracks'] ]

    api_tracks = lookup_tracks(spotify_track_ids, fields=['name', 'id'])

    track_list = api_tracks['tracks']

    for track in track_list:
        track['spotify_id'] = track.pop('id')

    playlist_response = {'id': playlist_id, 'tracks': track_list}
    return playlist_response
