import discord
from bot264.discord_wrapper import DiscordWrapper


class DiscordDb:

    @staticmethod
    def get_channel(channel_id):
        client: discord.Client = DiscordWrapper.client
        return client.get_channel(channel_id)

    @staticmethod
    def get_user_roles(user_id, server_id):
        server_id, user_id = int(server_id), int(user_id)
        client: discord.Client = DiscordWrapper.client
        server: discord.Guild = client.get_guild(server_id)
        member: discord.Member = server.get_member(user_id) 
        return member.roles
    
    @staticmethod
    def get_server(server_id):
        server_id = int(server_id)
        client: discord.Client = DiscordWrapper.client
        server: discord.Guild = client.get_guild(server_id)
        return server
    
