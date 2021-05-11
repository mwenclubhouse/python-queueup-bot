#!/usr/bin/python3
from bot264.discord_wrapper import create_server_db, Db, get_db_connection, get_server_db_connection, create_db

Db.database_file_location = ""
Db.database_folder_location = ""
server_id = 0
bot_channel_id = 0
waiting_room = 0

uta_role_id = None
gta_role_id = None
professor_role_id = None

queue_channel_id = 0
history_channel_id = 0
rooms = {None: None}

create_db()
create_server_db(server_id)
connection = get_db_connection(Db.database_file_location)
cursor = connection.cursor()
command = f"""
INSERT INTO servers (server_id, bot_channel_id, waiting_room_id) VALUES({server_id}, {bot_channel_id}, {waiting_room}); 
"""
cursor.execute(command)

if uta_role_id is not None:
    command = f"""
    INSERT INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({uta_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

if gta_role_id is not None:
    command = f"""
    INSERT INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({gta_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

if professor_role_id is not None:
    command = f"""
    INSERT INTO teaching_roles (teaching_role_id, assigned_level, server_id) VALUES({professor_role_id}, 0, {server_id}); 
    """
    cursor.execute(command)

command = f"""
INSERT INTO queues (queue_channel_id, history_channel_id, server_id) VALUES({queue_channel_id}, {history_channel_id}, {server_id}); 
"""
cursor.execute(command)
cursor.close()
connection.commit()

connection = get_server_db_connection(server_id)
cursor = connection.cursor()
for k, v in rooms.items():
    if k is not None:
        command = f"""
        INSERT INTO rooms (room_voice_channel_id, room_text_channel_id) VALUES ({k}, {v});
        """
        cursor.execute(command)
cursor.close()
connection.commit()
