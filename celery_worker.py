#!/usr/bin/env python
import os
from playlist_search import celery, create_app

app = create_app()
app.app_context().push()
