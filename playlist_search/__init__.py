from flask import Flask

from .util import generate_config_file_from_heroku_env
import os

if 'RUNNING_ON_HEROKU' in os.environ and os.environ['RUNNING_ON_HEROKU'] == 'True':
    generate_config_file_from_heroku_env()

def create_app():
    from . import models, routes
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    models.init_app(app)
    routes.init_app(app)
    return app
