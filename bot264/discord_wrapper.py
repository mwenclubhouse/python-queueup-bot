import json
import os
import sqlite3
import time

import discord

from bot264.common import create_simple_message


class Permissions:

    def __init__(self, server_id):
        connection = get_server_db_connection(server_id)
        command = f"SELECT * FROM rooms;"
        data = get_sqlite_data(connection, command)
        self.rooms = {}
        if data:
            for room in data:
                self.rooms[room[0]] = room[1]

    async def remove_permissions_from_all_rooms(self, student):
        client: discord.Client = DiscordWrapper.client
        for _, v in self.rooms.items():
            target_channel: discord.TextChannel = client.get_channel(v)
            if target_channel is not None:
                await target_channel.set_permissions(student, overwrite=None)

    async def set_access_to_text_channel(self, student, ta_voice_channel, state):
        client: discord.Client = DiscordWrapper.client
        ta_channel_id = ta_voice_channel.channel.id
        if ta_channel_id in self.rooms:
            target_channel: discord.TextChannel = client.get_channel(self.rooms[ta_channel_id])
            await target_channel.purge()
            if state:
                await target_channel.set_permissions(student, read_messages=state, send_messages=state)
                message_to_student = """
                You can have a 1 on 1 conversation here with your TA. 
                Hopefully, this session is helpful.
                """
                discord_message = create_simple_message("Hey There {}".format(student.display_name), message_to_student)
                await target_channel.send(embed=discord_message)
            else:
                await self.remove_permissions_from_all_rooms(student)


def get_db_connection(file_location):
    if file_location is not None:
        return sqlite3.connect(file_location)
    return None


def get_server_db_connection(server_id):
    if Db.database_folder_location is None:
        return None
    return get_db_connection(f'{Db.database_folder_location}/{server_id}.db')


def create_directory(directory_name):
    if directory_name is not None:
        try:
            os.makedirs(directory_name)
        except OSError as e:
            return


def create_db():
    Db.database_file_location = os.getenv('DATABASE', None)
    Db.database_folder_location = os.getenv('DATABASE_DIRECTORY', None)
    create_directory(create_directory(Db.database_folder_location))

    connection = get_db_connection(Db.database_file_location)
    if connection:
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
        connection.close()


def create_server_db(server_id):
    connection = get_server_db_connection(server_id)
    if connection:
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
        connection.close()


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


class Db:
    database_file_location = None
    database_folder_location = None

    def __init__(self, server_id):
        self.server_id = server_id
        self.permission = Permissions(server_id)

        connection = get_db_connection(Db.database_file_location)
        command = f"SELECT queue_channel_id FROM queues WHERE server_id={self.server_id};"
        data = get_sqlite_data(connection, command, close_connection=False)
        self.queue_channel = None
        if data and len(data) > 0:
            self.queue_channel = data[0][0]

        command = f"SELECT waiting_room_id FROM servers WHERE server_id={self.server_id};"
        data = get_sqlite_data(connection, command, close_connection=False)
        self.waiting_room = None
        if data and len(data) > 0:
            self.waiting_room = data[0][0]

        command = f"SELECT history_channel_id FROM queues where server_id={self.server_id};"
        data = get_sqlite_data(connection, command, close_connection=False)
        self.history_channel = None
        if data and len(data) > 0:
            self.history_channel = data[0][0]

        command = f"SELECT bot_channel_id FROM servers WHERE server_id={self.server_id};"
        data = get_sqlite_data(connection, command, close_connection=True)
        self.bot_channel = None
        if data and len(data) > 0:
            self.bot_channel = data[0][0]

    def get_queue_channel(self) -> discord.channel.TextChannel or None:
        if self.queue_channel != 0:
            return DiscordWrapper.client.get_channel(self.queue_channel)
        return None

    def get_waiting_room(self) -> discord.channel.VoiceChannel or None:
        if self.waiting_room != 0:
            return DiscordWrapper.client.get_channel(self.waiting_room)
        return None

    async def move_user_to_office_hours(self, user_id: discord.member.Member, ta_voice_state):
        if ta_voice_state is None:
            return False
        dest_voice_channel: discord.channel.VoiceChannel = ta_voice_state.channel
        waiting_room: discord.channel.VoiceChannel = self.get_waiting_room()
        if None in [waiting_room, user_id.voice]:
            return False
        await user_id.move_to(dest_voice_channel)
        await self.permission.set_access_to_text_channel(user_id, ta_voice_state, True)
        return True

    async def move_user_to_waiting_room(self, user_id, ta_voice_state):
        await self.permission.set_access_to_text_channel(user_id, ta_voice_state, False)
        waiting_room: discord.channel.VoiceChannel = self.get_waiting_room()
        if None in [waiting_room, user_id.voice]:
            return False
        await user_id.move_to(waiting_room)
        return True

    async def disconnect_user(self, user_id, ta_voice_state):
        await self.permission.set_access_to_text_channel(user_id, ta_voice_state, False)
        if user_id.voice is not None:
            await user_id.move_to(None)

    def is_emoji_channels(self, channel_id):
        connection = get_db_connection(Db.database_file_location)
        command = "SELECT queue_channel_id, history_channel_id FROM queues;"
        data = get_sqlite_data(connection, command)
        return channel_id in data[0] if data is not None and len(data) > 0 else False

    @staticmethod
    def is_admin_role(role: discord.role.Role):
        connection = get_db_connection(Db.database_file_location)
        command = f"SELECT teaching_role_id FROM teaching_roles WHERE teaching_role_id={role.id};"
        data = get_sqlite_data(connection, command)
        return data is not None and len(data) > 0

    def is_admin(self, member):
        if type(member) != discord.member.Member:
            return False
        for i in member.roles:
            if Db.is_admin_role(i):
                return True
        return False

    async def add_history(self, message: discord.message.Message):
        embed_message = create_simple_message(message.author.display_name, message.content)
        if self.history_channel is not None:
            history_channel: discord.TextChannel = DiscordWrapper.client.get_channel(self.history_channel)
            message = await history_channel.send(embed=embed_message)
            for i in ["🔄", "❌"]:
                await message.add_reaction(i)

    def add_name_by_id(self, member: discord.Member):
        connection = get_server_db_connection(self.server_id)
        if connection:
            display_name = member.display_name
            member_id = member.id
            command = f"""
            REPLACE INTO member_names (student_id, student_name) 
            VALUES ({member_id}, "{display_name}");"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def get_name_by_id(self, student_id, default_value=None):
        connection = get_server_db_connection(self.server_id)
        command = f"SELECT * FROM member_names WHERE student_id={student_id}"
        data = get_sqlite_data(connection, command)
        return data[0][1] if len(data) > 0 else default_value

    def is_ta_helping_student(self, student_id, ta_id):
        student = self.get_queue_by_student_id(student_id)
        if student is not None:
            return student[2] == ta_id
        return False

    def get_queue_by_student_id(self, student_id):
        connection = get_server_db_connection(self.server_id)
        command = "SELECT * FROM queues WHERE author_id={};".format(student_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def get_queue_by_message_id(self, message_id):
        connection = get_server_db_connection(self.server_id)
        command = "SELECT * FROM queues WHERE message_id={};".format(message_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def get_student(self, student_id):
        connection = get_server_db_connection(self.server_id)
        command = "SELECT * FROM students WHERE student_id={};".format(student_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def is_student_in_queue(self, student_id):
        student = self.get_queue_by_student_id(student_id)
        return student is not None

    def add_student(self, student_id, message_id):
        connection = get_server_db_connection(self.server_id)
        if connection:
            command = f"""INSERT INTO queues (author_id, message_id, wait_time)
                      VALUES ({student_id}, {message_id}, {int(time.time())});"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def set_start_time(self, student_id, ta_id):
        connection = get_server_db_connection(self.server_id)
        if connection:
            command = f"""UPDATE queues SET start_time={int(time.time())}, ta_id={ta_id}
                        WHERE author_id={student_id};"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def set_wait_time(self, student_id):
        connection = get_server_db_connection(self.server_id)
        if connection:
            command = f"""UPDATE queues SET wait_time={int(time.time())} 
                        WHERE author_id={student_id};"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def remove_student(self, message_id):
        connection = get_server_db_connection(self.server_id)
        if connection:
            student = self.get_queue_by_message_id(message_id)
            command = "DELETE FROM queues WHERE message_id={};".format(message_id)
            cursor = connection.cursor()
            cursor.execute(command)

            if student is not None and len(student) >= 5 and \
                    (student[4] not in [None, 0]) and (student[2] not in [None, 0]):
                client: discord.Client = DiscordWrapper.client
                student_user: discord.User = client.get_user(student[0])
                ta_user: discord.User = client.get_user(student[2])
                end_time = int(time.time())
                total_time = end_time - student[4]
                wait_time = student[4] - student[3]
                command = f"""INSERT INTO 
                history (student_id, ta_id, student_name, ta_name, start_time, end_time, total_time, wait_time)
                VALUES ({student[0]}, {student[2]}, "{student_user.display_name}", "{ta_user.display_name}", 
                {student[4]}, {end_time}, {total_time}, {wait_time});
                """
                cursor.execute(command)

                student_usage = self.get_student(student[0])
                if student_usage is None:
                    command = f"""INSERT INTO students (student_id, student_name, num_requests, total_time) 
                                VALUES ({student[0]}, "{student_user.display_name}", 1, {total_time});"""
                else:
                    command = f"""UPDATE students SET num_requests={student_usage[2] + 1}, 
                                total_time={student_usage[3] + total_time}
                                WHERE student_id={student[0]};"""
                cursor.execute(command)

            connection.commit()
            cursor.close()
            connection.close()


class DiscordWrapper:
    client = None
