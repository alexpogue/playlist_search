import playlist_search
import os

app = playlist_search.create_app()

if __name__ == '__main__':
    # Google AppEngine sets PORT env var to say which port it wants us to run on
    PORT = os.environ.get('PORT')
    if PORT is not None:
        app.run(port=PORT)
    else:
        app.run()
