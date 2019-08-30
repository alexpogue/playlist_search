from .base import db
from .base import ma

from .track_identifier import track_identifier

from marshmallow import fields

class Playlist(db.Model):
    __tablename__ = 'playlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    tracks = db.relationship(
        "Track",
        secondary=track_identifier,
        back_populates="playlists"
    )

    def __repr__(self):
        return "<Playlist: '{}', tracks: {}>".format(self.name, self.tracks)

class PlaylistSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    tracks = fields.Nested('TrackSchema', many=True, exclude=('playlists',))

playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True)
