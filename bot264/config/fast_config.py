from flask import Flask, Request, request 
from flask_cors import CORS
from firebase_admin.auth import verify_id_token

from bot264.database.fb_db import Database
app = Flask(__name__)
CORS(app, support_credentials=True)

async def check_firebase_auth(r: Request):
    authorization = request.headers.get('authorization')
    if authorization is None:
        return None
    if not (authorization.startswith("Bearer ")):
        return None
    token = authorization.split("Bearer ")[1]
    try:
        return verify_id_token(token) 
    except:
        return None

@app.get("/")
def welcome():
    check_firebase_auth(request)
    return {"ping": "pong"}

@app.get("/servers")
async def get_servers():
    user = await check_firebase_auth(request)
    if not user:
        return 'not authenticated', 400
    servers = await Database.get_servers(user)
    print(servers)
    for server in servers:
        pass
    return {
        "servers": [
            {
                "example": "example 1"
            }
        ]
    }

@app.get("/servers/<server_id>")
async def get_server_properties(server_id):
    print(server_id)
    user = await check_firebase_auth(request)
    if not user:
        return 'not authenticated', 400
    access = await Database.can_access(user)
    if access < 0:
        return 'not allowed to access server', 400
    return {
        "queueup": {
        },
        "discord": {
            "text_channels": [],
            "voice_channels": []
        }
    }

def flask_app():
    return app