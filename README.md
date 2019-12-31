# playlist_search

playlist_search is a Python Flask app that helps users find which Spotify playlists a track is in.

# Running

### Preparation

1. Install Redis locally
2. `git clone git@github.com:alexpogue/playlist_search.git`
3. `cd playlist_search`
4. Set up config.py as follows

    ```
    SQLALCHEMY_DATABASE_URI="sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    SPOTIFY_CLIENT_ID="<spotify client id>"
    SPOTIFY_CLIENT_SECRET="<spotify client secret>"

    CELERY_BROKER_URL="redis://127.0.0.1:6379"
    CELERY_RESULT_BACKEND="redis://127.0.0.1:6379"
    ```

    Note: change `SQLALCHEMY_DATABASE_URI` if you want to post to another database.

5. `pipenv shell`
6. `pipenv update`

### Running

1. Open two terminals
1. `cd playlist_search` in both
2. `pipenv shell` in both
3. Run in one of the terminals: `celery -A celery_worker.celery worker --loglevel=info`
4. To run the app, in the other terminal, either:
    - For Flask dev server: `python main.py`
    - For gunicorn: `gunicorn --bind 0.0.0.0:5000 wsgi`

### Installing Wordpress plugin

1. `cd wordpress_plugin`
2. `zip -r playlist-search-plugin.zip playlist-search-plugin`
3. Navigate to the Wordpress plugins page and install it from the zip file.

### Setting up as system services (for RHEL 7)

#### playlist_search as a system service

1. Copy `etc/systemd/system/playlist_search.service` in the repo to `/etc/systemd/system/playlist_search.service`
2. In the above file, under `[Service]`, change the WorkingDirectory to the location the repo is cloned to.
3. `chmod 644 /etc/systemd/system/playlist_search.service`
3. To start, run `systemctl start playlist_search`
4. To enable on boot:
    1. `systemctl enable playlist_search`
    2. Ensure `systemctl status playlist_search` outputs "enabled" as in the following output:
        ```
                                                                     vvvvvvv
        Loaded: loaded (/etc/systemd/system/playlist_search.service; enabled; vendor preset: disabled)
        ```

#### celery as a system service

2. Copy `etc/default/celeryd` in the repo to `/etc/default/celeryd`
2. In the above file, change `cd` portion of `CELERY_BIN` to the location the repo is cloned to.
3. `chmod 755 /etc/default/celeryd`
4. To start, run `service celeryd start`
4. To enable on boot:
    1. `chkconfig --add celeryd`
    1. Ensure `chkconfig --list celeryd` outputs the following:
        ```
        celeryd        	0:off	1:off	2:on	3:on	4:on	5:on	6:off
        ```
    2. If above command returned more things listed `off`, try running `chkconfig celeryd on` and try again
