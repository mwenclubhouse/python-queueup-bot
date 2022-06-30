import asyncio
import os
import signal
import sys
from threading import Thread

class GracefulKiller:
    kill_now = False
    flask_app = None
    thread = None

    def __init__(self, client=None, fbdb_method=None):
        self.client = client
        self.fbdb_method = fbdb_method
    
    def on_init(self):
        if os.name != 'nt' and self.client:
            self.client.loop.add_signal_handler(signal.SIGINT, self.exit_gracefully)
            self.client.loop.add_signal_handler(signal.SIGTERM, self.exit_gracefully)
    
    def start_flask(self, flask_app):
        self.flask_app = flask_app
        def start_app():
            self.flask_app.serve_forever()
        self.thread = Thread(target=start_app)
        self.thread.start()

    def exit_gracefully(self):
        self.kill_now = True
        if self.fbdb_method:
            self.fbdb_method()
        if self.client:
            asyncio.ensure_future(self.client.close())
        if self.flask_app and self.thread:
            print("shutting down flask app")
            self.flask_app.shutdown()
            self.thread.join()
        sys.exit()