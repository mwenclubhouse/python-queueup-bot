#!/usr/bin/python3
import os
os.environ['PRODUCTION'] = "1"
os.environ['DATABASE'] = '../queueup.db'
os.environ['DATABASE_DIRECTORY'] = '../test_queue_directory'
from bot264.discord_wrapper import create_server_db, Db, get_db_connection, create_db

server_id = 0
bot_channel_id = 0
waiting_room = 0
uta_role_id = None
gta_role_id = None
professor_role_id = 0
queue_channel_id = 0
history_channel_id = 0

# Rooms is {voice channel id: text channel id}
rooms = {None: None}

Db.database_file_location = os.getenv('DATABASE')
Db.database_folder_location = os.getenv('DATABASE_DIRECTORY')
create_db()
connection = get_db_connection(Db.database_file_location)
cursor = connection.cursor()
command = f"""
INSERT OR REPLACE INTO servers (server_id, bot_channel_id, waiting_room_id) VALUES({server_id}, {bot_channel_id}, {waiting_room}); 
"""
cursor.execute(command)

if uta_role_id is not None:
    command = f"""
    INSERT OR REPLACE INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({uta_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

if gta_role_id is not None:
    command = f"""
    INSERT OR REPLACE INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({gta_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

if professor_role_id is not None:
    command = f"""
    INSERT OR REPLACE INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({professor_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

command = f"""
INSERT OR REPLACE INTO queues (queue_channel_id, history_channel_id, server_id) VALUES({queue_channel_id}, {history_channel_id}, {server_id}); 
"""
cursor.execute(command)
cursor.close()
connection.commit()
connection.close()

connection = create_server_db(server_id, force_create=True, return_connection=True)
cursor = connection.cursor()
for k, v in rooms.items():
    if k is not None:
        command = f"""
        INSERT OR REPLACE INTO rooms (room_voice_channel_id, room_text_channel_id) VALUES ({k}, {v});
        """
        cursor.execute(command)
cursor.close()
connection.commit()
connection.close()
