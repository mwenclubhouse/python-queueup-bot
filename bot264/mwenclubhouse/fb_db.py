import os
import time
from typing import List

from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.watch import DocumentChange

from bot264.discord_wrapper import get_db_connection, Db, get_server_db_connection


def get_db():
    reference = os.getenv('REFERENCE', None)
    if reference is None:
        return None
    return firestore.Client().collection(u'servers').document(reference).collection('queueup-bot')


def get_server_db():
    return firestore.Client().collection(u'discord').document(u'queueup-bot').collection('servers')


class FbDb:
    db: firestore.CollectionReference = None
    servers: firestore.CollectionReference = None
    snapshot: firestore.Watch = None

    @staticmethod
    def init():
        FbDb.db = get_db()
        FbDb.servers = get_server_db()

    @staticmethod
    def on_set(server_id, attributes):
        connection = get_db_connection(Db.database_file_location)
        if connection:
            cursor = connection.cursor()
            command = f"""DELETE FROM teaching_roles WHERE server_id={server_id};"""
            cursor.execute(command)
            command = f"""DELETE FROM queues WHERE server_id={server_id};"""
            cursor.execute(command)

            if 'queues' in attributes:
                for k, v in attributes['queues'].items():
                    v = "NULL" if v is None else v
                    command = f"""REPLACE INTO queues (queue_channel_id, history_channel_id, server_id) 
                    VALUES({k}, {v}, {server_id})"""
                    cursor.execute(command)

            if 'ta_roles' in attributes:
                for k, _ in attributes['ta_roles'].items():
                    command = f"""
                    REPLACE INTO teaching_roles (teaching_role_id, assigned_level, server_id) 
                    VALUES({k}, 0, {server_id}); 
                    """
                    cursor.execute(command)

            bot_channel_id = attributes['bot'] if 'bot' in attributes else "NULL"
            waiting_room = attributes['waiting'] if 'waiting' in attributes else "NULL"
            command = f"""
            REPLACE INTO servers (server_id, bot_channel_id, waiting_room_id) 
            VALUES({server_id}, {bot_channel_id}, {waiting_room}); 
            """
            cursor.execute(command)
            cursor.close()
            connection.commit()
            connection.close()

        connection = get_server_db_connection(server_id, force_create=True)
        if connection:
            cursor = connection.cursor()
            command = """DELETE FROM rooms WHERE room_voice_channel_id NOT NULL;"""
            cursor.execute(command)
            if 'rooms' in attributes:
                for k, v in attributes['rooms'].items():
                    v = "NULL" if v is None else v
                    command = f"""
                    REPLACE INTO rooms (room_voice_channel_id, room_text_channel_id) VALUES({k}, {v});
                    """
                    cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    @staticmethod
    def get_server(server_id):
        response = FbDb.servers.document(server_id).get()
        if response:
            return response.to_dict()
        return None

    @staticmethod
    def on_snapshot(document_snapshot, changes: List[DocumentChange], read_time):
        for c in changes:
            if c.type.name == 'ADDED':
                to_dict = c.document.to_dict()
                server_id = to_dict['server']
                FbDb.on_set(server_id, FbDb.get_server(server_id))
                FbDb.db.document(c.document.id).delete()

    @staticmethod
    def listen():
        if not FbDb.db:
            return
        FbDb.snapshot = FbDb.db.on_snapshot(FbDb.on_snapshot)

    @staticmethod
    def kill():
        if FbDb.snapshot:
            # FbDb.snapshot.close()
            FbDb.snapshot = None
