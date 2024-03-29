from .base import db
from .base import ma

from marshmallow import fields

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(22), index=True, nullable=False)
    playlists = db.relationship("TrackIdentifier", back_populates='track', cascade="all, delete, delete-orphan")

class TrackSchema(ma.Schema):
    id = fields.Integer()
    spotify_id = fields.String()
    playlists = fields.Nested('PlaylistSchema', many=True, exclude=('tracks',))

track_schema = TrackSchema()
tracks_schema = TrackSchema(many=True)
