from .base import db
from .base import ma

album_identifier = db.Table('album_identifier',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'))
)
