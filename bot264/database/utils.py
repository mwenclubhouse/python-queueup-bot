from ctypes import Union
from discord import Forbidden
import os
import sqlite3
from typing import Any, List
from firebase_admin.firestore import firestore

from bot264.env import Env

def get_db_connection(file_location, force_create=False):
    is_setup, connection = False, None
    if file_location is not None:
        is_setup = os.path.isfile(file_location)
        if force_create or is_setup:
            connection = sqlite3.connect(file_location)
    return [is_setup, connection]


def get_server_db_connection(server_id, force_create=False):
    if Env.database_folder_location is None:
        return None
    return get_db_connection(
        f'{Env.database_folder_location}/{server_id}.db',
        force_create=force_create
    )


def get_db():
    try:
        return firestore.Client().collection(u'users')
    except:
        return None


def get_server_db():
    try:
        return firestore.Client().collection(u'discord').document(u'queueup-bot').collection('servers')
    except:
        return None

def create_directory(directory_name):
    if directory_name is not None:
        try:
            os.makedirs(directory_name)
        except OSError as e:
            return

def create_db(force_create=False, return_connection=False):
    create_directory(Env.database_folder_location)

    [is_setup, connection] = get_db_connection(Env.database_file_location, force_create=force_create)

    if connection and not is_setup:
        cursor = connection.cursor()
        command = """CREATE TABLE IF NOT EXISTS servers (
                            server_id integer PRIMARY KEY, 
                            bot_channel_id integer NOT NULL, 
                            waiting_room_id integer NOT NULL
        );"""
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS teaching_roles (
                            teaching_role_id INTEGER PRIMARY KEY, 
                            assigned_level INTEGER NOT NULL,
                            server_id INTEGER NOT NULL
        );"""
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS queues (
                            queue_channel_id INTEGER PRIMARY KEY, 
                            history_channel_id integer NULL,
                            server_id INTEGER NOT NULL
        );"""
        cursor.execute(command)
        cursor.close()

    if connection and not return_connection:
        connection.close()
        connection = None

    return connection


def create_server_db(server_id, force_create=False, return_connection=False):
    [is_setup, connection] = get_server_db_connection(server_id, force_create=force_create)

    if connection and not is_setup:
        command = """CREATE TABLE IF NOT EXISTS queues (
                            author_id integer PRIMARY KEY, 
                            message_id integer NOT NULL,
                            ta_id integer,
                            wait_time integer,
                            start_time integer,
                            queue_channel_id integer
        );"""
        cursor = connection.cursor()
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS history (
                            id integer PRIMARY KEY, 
                            student_id integer, 
                            ta_id integer,
                            student_name TEXT,
                            ta_name TEXT,
                            start_time integer, 
                            end_time integer,
                            total_time integer,
                            wait_time integer
                            );
                            """
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS students (
                            student_id integer PRIMARY KEY, 
                            student_name TEXT,
                            num_requests integer,
                            total_time integer, 
                            recorded_date integer 
                            );
                            """
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS member_names (
            student_id integer PRIMARY KEY,
            student_name TEXT
        );"""
        cursor.execute(command)
        command = """CREATE TABLE IF NOT EXISTS rooms (
                            room_voice_channel_id integer PRIMARY KEY, 
                            room_text_channel_id integer
        );"""
        cursor.execute(command)
        cursor.close()

    if return_connection:
        return connection
    if connection:
        connection.close()
    return None


def get_sqlite_data(connection, select_command, close_connection=True):
    data = None
    if connection:
        cursor = connection.cursor()
        cursor.execute(select_command)
        data = cursor.fetchall()
        cursor.close()
        if close_connection:
            connection.close()
    return data
