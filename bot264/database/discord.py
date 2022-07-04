import discord
from bot264.discord_wrapper import DiscordWrapper


class DiscordDb:

    @staticmethod
    def get_channel(channel_id):
        client: discord.Client = DiscordWrapper.client
        return client.get_channel(channel_id)

    @staticmethod
    def get_roles(user_id):
        client: discord.Client = DiscordWrapper.client
        member: discord.Member = client.get_user(user_id)
        print(member)
