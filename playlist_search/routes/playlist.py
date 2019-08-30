import json

from flask import Blueprint, request, abort, jsonify
from ..models.playlist import Playlist
from ..models.base import db

from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint
from .util import get_by_id

playlist_blueprint = Blueprint('playlists', __name__)

@playlist_blueprint.route('/')
def get_playlists():
    playlist = Playlist.query.first()
    result, errors = playlist_schema.dump(playlist)
    #result_without_errors = result[0]
    #keyed_result = {"playlists": result_without_errors}
    #keyed_result = {"playlists": result}

    return jsonify(result)
    
@playlist_blueprint.route('/<int:playlist_id>', methods=['GET'])
def get_goal(playlist_id):
    return get_by_id(Playlist, playlist_id, playlist_schema)
