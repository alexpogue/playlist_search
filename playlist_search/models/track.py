from .base import db
from .base import ma

from marshmallow import fields

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(22), index=True, nullable=False)
    playlists = db.relationship("TrackIdentifier", back_populates='track', cascade="all, delete, delete-orphan")
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    album = db.relationship("Album", back_populates="tracks", single_parent=True, cascade="all, delete, delete-orphan")

class TrackSchema(ma.Schema):
    id = fields.Integer()
    spotify_id = fields.String()
    playlists = fields.Nested('PlaylistSchema', many=True, exclude=('tracks',))
    album = fields.Nested('AlbumSchema', exclude=('tracks',))

track_schema = TrackSchema()
tracks_schema = TrackSchema(many=True)
