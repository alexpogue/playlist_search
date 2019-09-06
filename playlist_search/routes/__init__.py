from .playlist import playlist_blueprint
from .track import track_blueprint
from .album import album_blueprint
from .root_api import root_api_blueprint

from .admin import admin_blueprint

def init_app(app):
    app.register_blueprint(playlist_blueprint, url_prefix='/playlist')
    app.register_blueprint(track_blueprint, url_prefix='/track')
    app.register_blueprint(album_blueprint, url_prefix='/album')
    app.register_blueprint(root_api_blueprint, url_prefix='/', template_folder='../templates', static_folder='../static')

    app.register_blueprint(admin_blueprint, url_prefix='/admin')
