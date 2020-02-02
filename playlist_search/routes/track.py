import json
import io
import csv
import datetime

from flask import Blueprint, request, abort, jsonify, make_response, current_app as app
from ..models.track import Track
from ..models.base import db

from ..models.track import track_schema, tracks_schema
from ..models.playlist import playlist_schema, playlists_schema

from flask_marshmallow import pprint

from .util import get_by_id, lookup_track, lookup_playlists, get_track_in_playlist_details, lookup_playlist

track_blueprint = Blueprint('tracks', __name__)

@track_blueprint.route('/')
def get_track_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    track = combine_info_for_track(requested_spotify_id)

    return track


CSV_HEADINGS = ['platform', 'playlist_id', 'playlist_name', 'playlist_link', 'curator_id', 'curator_name', 'currently_in', 'added_at', 'current_position', 'days_in', 'followers']

@track_blueprint.route('/csv')
def get_track_csv_by_spotify_id():
    requested_spotify_id = request.args.get('spotify_id')

    track = combine_info_for_track(requested_spotify_id)

    track_in_csv = convert_track_to_csv(track)
    return track_in_csv

def combine_info_for_track(spotify_id):
    api_track = lookup_track(spotify_id, fields=['id', 'artists', 'album', 'name'])

    track_from_db = Track.query.filter_by(spotify_id=spotify_id).first()
    app.logger.info('track_from_db  = {}'.format(track_from_db ))

    if track_from_db is not None:
        track_identifiers_from_db = track_from_db.playlists

        # this array is filled in below
        api_track['playlists'] = []

        for track_identifier in track_identifiers_from_db:
            playlist_spotify_id = track_identifier.playlist.spotify_id
            api_playlist = lookup_playlist(playlist_spotify_id, ['name', 'id', 'external_urls', 'owner', 'followers'])

            api_playlist['track_rank'] = track_identifier.track_index_in_playlist + 1
            api_playlist['added_at'] = track_identifier.track_added_at

            api_track['playlists'].append(api_playlist)

    return api_track

def convert_track_to_csv(track):
    string_io = io.StringIO()
    csv_writer = csv.writer(string_io)
    csv_writer.writerow(CSV_HEADINGS)

    playlists = track.get('playlists', [])
    for playlist in playlists:
        csv_row = []
        # platform
        csv_row.append('spotify')

        playlist_id = playlist.get('id')
        csv_row.append(playlist_id)

        playlist_name = playlist.get('name')
        csv_row.append(playlist_name)

        playlist_link = playlist.get('external_urls', {}).get('spotify')
        csv_row.append(playlist_link)

        curator_id = playlist.get('owner', {}).get('id')
        csv_row.append(curator_id)

        curator_name = playlist.get('owner', {}).get('display_name')
        csv_row.append(curator_name)

        currently_in = 'TRUE'
        csv_row.append(currently_in)

        added_at = playlist.get('added_at').date()
        csv_row.append(added_at)

        current_position = playlist.get('track_rank')
        csv_row.append(current_position)

        now = datetime.datetime.now().date()
        delta = now - added_at
        days_in = delta.days
        csv_row.append(days_in)

        followers = playlist.get('followers', {}).get('total')
        csv_row.append(followers)

        csv_writer.writerow(csv_row)

    output = make_response(string_io.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    track = get_by_id(Track, track_id, track_schema)
    app.logger.info('track  = {}'.format(track ))
    return lookup_track(track['spotify_id'])
