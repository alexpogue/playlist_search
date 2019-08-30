import json

from flask import Blueprint, request, abort, jsonify
from ..models.track import Track
from ..models.base import db

from ..models.track import track_schema, tracks_schema

from flask_marshmallow import pprint

from .util import get_by_id

track_blueprint = Blueprint('tracks', __name__)

@track_blueprint.route('/')
def get_tracks():
    track = Track.query.first()
    requested_spotify_id = request.args.get('spotify_id')
    if requested_spotify_id is not None:
        track = Track.query.filter_by(spotify_id=requested_spotify_id).first()
    result, errors = track_schema.dump(track)
    return jsonify(result)

@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track(track_id):
    return get_by_id(Track, track_id, track_schema)
