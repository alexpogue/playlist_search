import os
import configparser

DB_URL_KEY_HEROKU = 'DATABASE_URL'
DB_URL_KEY_CONFIG = 'SQLALCHEMY_DATABASE_URI'

TRACK_MODIFICATIONS_CONFIG = 'SQLALCHEMY_TRACK_MODIFICATIONS'
TRACK_MODIFICATIONS_DEFAULT = False

CONFIG_FILE_NAME = 'config.py'

def generate_config_file_from_heroku_env():
    if 'RUNNING_ON_HEROKU' not in os.environ or os.environ['RUNNING_ON_HEROKU'] != 'True':
        print('Tried to generate config file, but not running on Heroku. Abort.')
        return

    config = {}
    config[TRACK_MODIFICATIONS_CONFIG] = TRACK_MODIFICATIONS_DEFAULT
    if DB_URL_KEY_HEROKU not in os.environ:
        print('Could not find {} in environment variables. Abort.'.format(DB_URL_KEY_HEROKU))
        return

    db_url = os.environ[DB_URL_KEY_HEROKU]
    config[DB_URL_KEY_CONFIG] = db_url
    with open(CONFIG_FILE_NAME, 'w') as configfile:
        for key, val in config.items():
            if isinstance(val, str):
                line = '{} = "{}"'.format(key,val)
            else:
                line = '{} = {}'.format(key, val)

            configfile.write('{}\n'.format(line))
