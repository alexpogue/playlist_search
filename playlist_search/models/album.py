from .base import db
from .base import ma

from .album_identifier import album_identifier

from marshmallow import fields

class Album(db.Model):
    __tablename__ = 'album'
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(22), nullable=False)
    playlists = db.relationship(
        "Playlist",
        secondary=album_identifier,
        back_populates="albums"
    )

class AlbumSchema(ma.Schema):
    id = fields.Integer()
    spotify_id = fields.String()
    playlists = fields.Nested('PlaylistSchema', many=True, exclude=('albums',))

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)
