import discord
from bot264.common.utils import create_simple_message
from bot264.discord_wrapper import DiscordWrapper
from bot264.database.utils import get_server_db_connection, get_sqlite_data

class Permissions:

    def __init__(self, server_id):
        [_, connection] = get_server_db_connection(server_id)
        command = f"SELECT * FROM rooms;"
        data = get_sqlite_data(connection, command)
        self.server_id = server_id
        self.rooms = {}
        if data:
            for room in data:
                self.rooms[room[0]] = room[1]

    async def remove_permissions_from_all_rooms(self, student):
        client: discord.Client = DiscordWrapper.client
        for _, v in self.rooms.items():
            target_channel: discord.TextChannel = client.get_channel(v)
            if target_channel is not None:
                try:
                    await target_channel.set_permissions(student, overwrite=None)
                except discord.Forbidden as e:
                    print(e)

    async def set_access_to_text_channel(self, student, ta_voice_channel, state):
        client: discord.Client = DiscordWrapper.client
        ta_channel_id = ta_voice_channel.channel.id
        if ta_channel_id in self.rooms:
            target_channel: discord.TextChannel = client.get_channel(self.rooms[ta_channel_id])
            try:
                await target_channel.purge()
                if state:
                    await target_channel.set_permissions(student, read_messages=state, send_messages=state)
                    message_to_student = """
                    You can have a 1 on 1 conversation here with your TA. 
                    Hopefully, this session is helpful.
                    """
                    discord_message = create_simple_message("Hey There {}".format(student.display_name),
                                                            message_to_student)
                    await target_channel.send(embed=discord_message)
                else:
                    await self.remove_permissions_from_all_rooms(student)
            except discord.Forbidden as e:
                print(e)

