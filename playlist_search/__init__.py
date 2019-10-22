from flask import Flask
from celery import Celery
import config

from .util import generate_config_file_from_heroku_env
import os
import config

celery = Celery(__name__, broker=config.CELERY_BROKER_URL)

if 'RUNNING_ON_HEROKU' in os.environ and os.environ['RUNNING_ON_HEROKU'] == 'True':
    generate_config_file_from_heroku_env()

def create_app():
    from . import models, routes
    app = Flask(__name__)
    app.config.from_object(config)
    print('db uri = {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

    celery.conf.update(app.config)

    models.init_app(app)
    routes.init_app(app)
    return app
