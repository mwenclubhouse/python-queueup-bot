#!/usr/bin/python3
from bot264.database import Database, ServerDb
from bot264.env import Env

Env.database_file_location = '../queueup.db'
Env.database_folder_location = '../test_queue_directory'

server_id = 0
bot_channel_id = 0
waiting_room = 0
uta_role_id = None
gta_role_id = None
professor_role_id = None
queue_channel_id = 0
history_channel_id = 0
# Rooms is {voice channel id: text channel id}
rooms = {0: 0}

ta_roles = dict()
for i in [uta_role_id, gta_role_id, professor_role_id]:
    if i is not None:
        ta_roles[i] = ''

Database.update_server(server_id, {
    'queues': {
        queue_channel_id: history_channel_id
    },
    'ta_roles': ta_roles,
    'bot': bot_channel_id,
    'waiting': waiting_room,
    'rooms': {k: v for k, v in rooms.items() if not (None in [k, v])}
})
