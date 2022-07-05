#!/usr/bin/env python3
from bot264 import run_discord, flask_app
from werkzeug.serving import make_server

app = flask_app()
server = make_server('0.0.0.0', 8000, app)

run_discord(server)

