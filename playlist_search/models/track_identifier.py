from .base import db
from .base import ma

track_identifier = db.Table('track_identifier',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
)
