from .base import db
from .base import ma

from .playlist import Playlist
from .track import Track
from .album import Album
from .track_identifier import TrackIdentifier

from flask_migrate import Migrate

def init_app(app):
    ma.init_app(app)
    db.init_app(app)

    migrate = Migrate(app, db)


    with app.app_context():
        db.create_all()
