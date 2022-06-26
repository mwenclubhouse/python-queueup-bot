#!/usr/bin/env python3
from threading import Thread
from flask import Flask
from bot264 import run_discord
from werkzeug.serving import make_server

app = Flask(__name__)
server = make_server('0.0.0.0', 8000, app)

@app.get("/")
def welcome():
    return {"ping": "pong"}

run_discord(server)

