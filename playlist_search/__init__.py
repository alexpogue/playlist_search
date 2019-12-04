from flask import Flask

import logging
from logging.handlers import SysLogHandler

from celery import Celery
import config

from .util import generate_config_file_from_heroku_env
import os
import sys
import config

celery = Celery(__name__, backend=config.CELERY_RESULT_BACKEND, broker=config.CELERY_BROKER_URL)

if 'RUNNING_ON_HEROKU' in os.environ and os.environ['RUNNING_ON_HEROKU'] == 'True':
    generate_config_file_from_heroku_env()

def create_app():
    from . import models, routes
    app = Flask(__name__)
    app.config.from_object(config)

    syslog_handler = None
    if sys.platform == 'darwin':
        syslog_handler = SysLogHandler(address='/var/run/syslog')
    elif sys.platform == 'linux':
        syslog_handler = SysLogHandler(address='/dev/log')

    if syslog_handler is not None:
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    app.logger.addHandler(stdout_handler)

    app.logger.setLevel(logging.INFO)

    app.logger.info('db uri = {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

    celery.conf.update(app.config)

    models.init_app(app)
    routes.init_app(app)
    return app
