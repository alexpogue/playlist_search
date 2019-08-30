from .base import db
from .base import ma

from .track_identifier import track_identifier

from marshmallow import fields

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(22), nullable=False)
    playlists = db.relationship(
        "Playlist",
        secondary=track_identifier,
        back_populates="tracks"
    )

class TrackSchema(ma.Schema):
    id = fields.Integer()
    spotify_id = fields.String()
    playlists = fields.Nested('PlaylistSchema', many=True, exclude=('tracks',))

track_schema = TrackSchema()
tracks_schema = TrackSchema(many=True)
