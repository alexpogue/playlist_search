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

