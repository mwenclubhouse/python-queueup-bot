import json
import os

import discord

from bot264.discord_wrapper import DiscordWrapper, init_discord_wrapper
from .commands import UserCommand
from .common.user_response import UserResponse
from .common.utils import iterate_commands

if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv

    load_dotenv()

intents = discord.Intents.default()
intents.members = True
client: discord.Client = discord.Client(intents=intents)
init_discord_wrapper()
DiscordWrapper.client = client


def create_direct_command(content):
    return iterate_commands(content, [])


def create_scheduler_command(content):
    return iterate_commands(content, [])


async def run(obj, message, response):
    if obj is not None:
        inst: UserCommand = obj(message.author, message.content, response)
        await response.send_loading(message)
        await inst.run()


async def handle_direct_message(message, response: UserResponse):
    if not response.done:
        content = message.content.lower()
        await run(create_direct_command(content), message, response)


async def handle_scheduler_message(message, response: UserResponse):
    if not response.done:
        obj = create_scheduler_command(message.content)
        await run(obj, message, response)


@client.event
async def on_ready():
    pass


@client.event
async def on_raw_reaction_add(payload: discord.raw_models.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    if not DiscordWrapper.is_emoji_channels(payload.channel_id):
        return

    message: discord.message.Message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    author: discord.User = message.author

    is_admin = DiscordWrapper.is_admin(payload.member.roles)
    run_command = False
    if is_admin or payload.user_id == author.id:
        response = UserResponse()
        run_command = await response.run_emoji_command(
            payload.emoji.name, message, payload.member.voice, is_admin=is_admin)

    if not run_command:
        await message.remove_reaction(payload.emoji, payload.member)


@client.event
async def on_message(message: discord.message.Message):
    response: UserResponse = UserResponse()
    if message.author == client.user:
        return
    if DiscordWrapper.queue_channel == message.channel.id:
        response.set_options("waiting")
        await response.send_message(message)
        return
    list_type = [handle_direct_message, handle_scheduler_message]
    for i in list_type:
        await i(message, response)
        if response.done:
            await response.send_message(message)
            return


@client.event
async def on_member_join(member):
    print(member)


@client.event
async def on_member_remove(member):
    print(member)


def run_discord():
    client.run(os.getenv('TOKEN'))
