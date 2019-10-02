from .base import db
from .base import ma

from marshmallow import fields

class TrackIdentifier(db.Model):
    __tablename__ = 'track_identifier'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    track_index_in_playlist = db.Column(db.Integer, nullable=False)
    track_added_at = db.Column(db.DateTime, nullable=False)
    playlist = db.relationship('Playlist', back_populates='tracks')
    track = db.relationship('Track', back_populates='playlists')

class TrackIdentifierSchema(ma.Schema):
    playlist_id = fields.Integer()
    track_id = fields.Integer()
    spotify_id = fields.String()
    track_index_in_playlist = fields.Integer()
    track_added_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%Z')

track_identifier_schema = TrackIdentifierSchema()
track_identifiers_schema = TrackIdentifierSchema(many=True)

#track_identifier = db.Table('track_identifier',
#    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
#    db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
#    # TODO: move this whole file to a full blown association table class as in https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
#    # so that we can add the data below to the association
#    #db.Column('position', db.Integer, nullable=False)
#    #db.Column('added_at', db.DateTime)
#)
