from multiprocessing.dummy import Array
import time
from discord import Forbidden
import discord
from typing import Any
from firebase_admin.firestore import firestore
from bot264.common.utils import create_simple_message
from bot264.discord_wrapper import DiscordWrapper
from .utils import get_db, get_server_db_connection, create_db, get_sqlite_data, create_server_db
from bot264.common.permissions import Permissions


class Database:
    db: firestore.CollectionReference = None

    @staticmethod
    def init():
        Database.db = get_db()
    
    @staticmethod
    async def can_access(user):
        print(user)
        return -1
    
    @staticmethod
    async def get_servers(user) -> Array:
        if not (Database.db):
            return []
        user_id = user['user_id']
        if not (user_id):
            return []
        user_data = Database.db.document(user_id).get().to_dict()
        if not ('queueup' in user_data and 'servers' in user_data['queueup']):
            return []
        return user_data['queueup']['servers'] or []
    
    @staticmethod
    async def get_server(server_id) -> Any:
        [_, connection] = get_server_db_connection(server_id)
        connection = create_db(force_create=True, return_connection=True)
        if not connection:
            return None
        command = f"""SELECT * FROM teaching_roles WHERE server_id={server_id}"""
        data = get_sqlite_data(connection, command)
        print(data)
        

    @staticmethod
    def update_server(server_id, attributes):
        connection = create_db(force_create=True, return_connection=True)
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
            
            if 'bot' in attributes:
                bot_channel_id = attributes['bot']
                command = f"""
                REPLACE INTO servers (server_id, bot_channel_id) VALUES({server_id}, {bot_channel_id});
                """
                cursor.execute(command)

            if 'waiting' in attributes:
                waiting_room = attributes['waiting'] 
                command = f"""
                REPLACE INTO servers (server_id,  waiting_room_id) 
                VALUES({server_id}, {waiting_room}); 
                """
                cursor.execute(command)
            cursor.close()
            connection.commit()
            connection.close()

        connection = create_server_db(server_id, force_create=True, return_connection=True)
        if connection:
            cursor = connection.cursor()
            command = """DELETE FROM rooms WHERE room_voice_channel_id NOT NULL;"""
            cursor.execute(command)

            # The room_text_channel_id is depreciated 
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


class ServerDb:

    def __init__(self, server_id):
        self.server_id = server_id
        self.permission = Permissions(server_id)

        connection = create_db(force_create=True, return_connection=True)
        command = f"SELECT queue_channel_id FROM queues WHERE server_id={self.server_id};"
        data = get_sqlite_data(connection, command, close_connection=False)
        self.queues = []
        if data and len(data) > 0:
            self.queues = [i[0] for i in data]

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

    def get_queues(self):
        queues = []
        client = DiscordWrapper.client
        for i in self.queues:
            queues.append(client.get_channel(i))
        return queues

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
        return True

    async def move_user_to_waiting_room(self, user_id, ta_voice_state):
        waiting_room: discord.channel.VoiceChannel = self.get_waiting_room()
        if None in [waiting_room, user_id.voice]:
            return False
        await user_id.move_to(waiting_room)
        return True

    async def disconnect_user(self, user_id, ta_voice_state):
        if user_id.voice is not None:
            await user_id.move_to(None)

    def is_emoji_channels(self, channel_id):
        return channel_id == self.history_channel or channel_id in self.queues

    @staticmethod
    def is_admin_role(role: discord.role.Role):
        connection = create_db(return_connection=True)
        command = f"SELECT teaching_role_id FROM teaching_roles WHERE teaching_role_id={role.id};"
        data = get_sqlite_data(connection, command)
        return data is not None and len(data) > 0

    def is_admin(self, member):
        if type(member) != discord.member.Member:
            return False
        for i in member.roles:
            if ServerDb.is_admin_role(i):
                return True
        return False

    def add_name_by_id(self, member: discord.Member):
        [_, connection] = get_server_db_connection(self.server_id)
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
        [_, connection] = get_server_db_connection(self.server_id)
        command = f"SELECT * FROM member_names WHERE student_id={student_id}"
        data = get_sqlite_data(connection, command)
        return data[0][1] if len(data) > 0 else default_value

    def is_ta_helping_student(self, student_id, ta_id):
        student = self.get_queue_by_student_id(student_id)
        if student is not None:
            return student[2] == ta_id
        return False

    def get_queue_by_student_id(self, student_id):
        [_, connection] = get_server_db_connection(self.server_id)
        command = "SELECT * FROM queues WHERE author_id={};".format(student_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def get_queue_by_message_id(self, message_id):
        [_, connection] = get_server_db_connection(self.server_id)
        command = "SELECT * FROM queues WHERE message_id={};".format(message_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def get_student(self, student_id):
        [_, connection] = get_server_db_connection(self.server_id)
        command = "SELECT * FROM students WHERE student_id={};".format(student_id)
        data = get_sqlite_data(connection, command)
        return data[0] if len(data) > 0 else None

    def is_student_in_queue(self, student_id):
        student = self.get_queue_by_student_id(student_id)
        return student is not None

    def add_student(self, student_id, message_id):
        [_, connection] = get_server_db_connection(self.server_id)
        if connection:
            command = f"""INSERT INTO queues (author_id, message_id, wait_time)
                      VALUES ({student_id}, {message_id}, {int(time.time())});"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def set_start_time(self, student_id, ta_id):
        [_, connection] = get_server_db_connection(self.server_id)
        if connection:
            command = f"""UPDATE queues SET start_time={int(time.time())}, ta_id={ta_id}
                        WHERE author_id={student_id};"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def set_wait_time(self, student_id):
        [_, connection] = get_server_db_connection(self.server_id)
        if connection:
            command = f"""UPDATE queues SET wait_time={int(time.time())} 
                        WHERE author_id={student_id};"""
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
            cursor.close()
            connection.close()

    def remove_student(self, message_id):
        [_, connection] = get_server_db_connection(self.server_id)
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
