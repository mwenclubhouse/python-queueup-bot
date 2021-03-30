import os
from typing import List
import discord

from bot264.common import create_simple_message


def get_int_env(name):
    env_str = os.getenv(name, 0)
    return 0 if env_str in [None, ''] else int(env_str)


def init_discord_wrapper():
    # Text Channel Settings
    DiscordWrapper.queue_channel = get_int_env('QUEUE_CHANNEL_ID')
    DiscordWrapper.history_channel = get_int_env('HISTORY_CHANNEL_ID')

    # Voice Channel Settings
    DiscordWrapper.waiting_room = get_int_env("WAITING_ROOM")

    # Role IDS
    DiscordWrapper.uta_role_id = get_int_env('UTA_ROLE_ID')
    DiscordWrapper.gta_role_id = get_int_env('GTA_ROLE_ID')
    DiscordWrapper.prof_role_id = get_int_env('PROFESSOR_ROLE_ID')


class DiscordWrapper:
    client = None
    queue_channel = None
    history_channel = None

    waiting_room = None

    uta_role_id = None
    gta_role_id = None
    prof_role_id = None

    @staticmethod
    def get_waiting_room() -> discord.channel.VoiceChannel or None:
        if DiscordWrapper.waiting_room != 0:
            return DiscordWrapper.client.get_channel(DiscordWrapper.waiting_room)
        return None

    @staticmethod
    async def move_user_to_office_hours(user_id: discord.member.Member, ta_voice_state):
        if ta_voice_state is None:
            return False
        dest_voice_channel: discord.channel.VoiceChannel = ta_voice_state.channel
        waiting_room: discord.channel.VoiceChannel = DiscordWrapper.get_waiting_room()
        if None in [waiting_room, user_id.voice]:
            return False
        await user_id.move_to(dest_voice_channel)
        return True

    @staticmethod
    async def move_user_to_waiting_room(user_id):
        waiting_room: discord.channel.VoiceChannel = DiscordWrapper.get_waiting_room()
        if None in [waiting_room, user_id.voice]:
            return False
        await user_id.move_to(waiting_room)
        return True

    @staticmethod
    async def disconnect_user(user_id):
        if user_id.voice is not None:
            await user_id.move_to(None)

    @staticmethod
    def is_emoji_channels(channel_id):
        return channel_id in [DiscordWrapper.queue_channel, DiscordWrapper.history_channel]

    @staticmethod
    def is_admin(roles: List[discord.role.Role]):
        for i in roles:
            if i.id in [DiscordWrapper.uta_role_id, DiscordWrapper.gta_role_id, DiscordWrapper.prof_role_id]:
                return True
        return False

    @staticmethod
    async def add_history(message: discord.message.Message):
        embed_message = create_simple_message(message.author.name, message.content)
        if DiscordWrapper.history_channel is not None:
            history_channel: discord.TextChannel = DiscordWrapper.client.get_channel(DiscordWrapper.history_channel)
            message = await history_channel.send(embed=embed_message)
            for i in ["🔄", "❌"]:
                await message.add_reaction(i)
