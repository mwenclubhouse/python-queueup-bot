import json
from flask import Flask, Request, request 
from flask_cors import CORS
from firebase_admin.auth import verify_id_token
from bot264.database.discord import DiscordDb
import discord

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
    servers = []
    server_ids = await Database.get_servers(user)
    for server_id in server_ids:
        server = await Database.get_server(server_id)
        server["id"] = server_id
        servers.append(server)
    return {
        "servers": servers
    }

@app.get("/servers/<server_id>")
async def get_server_properties(server_id):
    user = await check_firebase_auth(request)
    if not user:
        return 'not authenticated', 400
    access = await Database.can_access(user, server_id)
    if (access & 1 == 0):
        return 'not allowed to access server', 400
    response = {
        "queueup": await Database.get_server(server_id),
        "discord": {
            "channels": {},
            "roles": [],
            "name": "",
            "owner": {
                "name": "",
                "id": -1
            }
        }
    }

    def add_category(category_id):
        if category_id not in response["discord"]["channels"]:
            response["discord"]["channels"][category_id] = {
                "text": [],
                "vc": [],
                "name": DiscordDb.get_channel(category_id).name
            }

    server = DiscordDb.get_server(server_id)
    for text_channel in server.channels:
        if type(text_channel) == discord.channel.TextChannel:
            category = text_channel.category_id
            add_category(category)
            response["discord"]["channels"][category]["text"].append({
                "id": text_channel.id,
                "position": text_channel.position,
                "name": text_channel.name
            })
            
    for vc_channel in server.voice_channels:
        if type(vc_channel) == discord.channel.VoiceChannel:
            category = vc_channel.category_id
            add_category(category)
            response["discord"]["channels"][category]["vc"].append({
                "id": vc_channel.id,
                "position": vc_channel.position,
                "name": vc_channel.name
            })

    for role in server.roles:
        response["discord"]["roles"].append({
            "id": role.id,
            "name": role.name
        })
    response["discord"]["name"] = server.name
    response["discord"]["owner"]["name"] = server.owner.name
    response["discord"]["owner"]["id"] = server.owner_id
    return response

@app.post("/servers/<server_id>")
async def update_server_properties(server_id):
    user = await check_firebase_auth(request)
    if not user:
        return 'not authenticated', 400
    access = await Database.can_access(user, server_id)
    if (access & 1) == 0:
        return 'not allowed to access server', 400
    response = json.loads(request.data)
    Database.update_server(server_id, response)
    return await get_server_properties(server_id)

def flask_app():
    return app