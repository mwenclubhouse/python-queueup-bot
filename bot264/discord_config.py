import os

import discord

from bot264.discord_wrapper import DiscordWrapper, init_discord_wrapper
from .commands import UserCommand
from .commands.lock_queue_command import LockQueueCommand, UnLockQueueCommand, StateQueueCommand
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


def create_bot_command(content):
    return iterate_commands(content, [
        ('$lock', LockQueueCommand), ('$unlock', UnLockQueueCommand)
    ])


async def run(obj, message, response):
    if obj is not None:
        inst: UserCommand = obj(message, response)
        await response.send_loading(message)
        await inst.run()


async def handle_direct_message(message, response: UserResponse):
    if not response.done:
        content = message.content.lower()
        await run(create_direct_command(content), message, response)


async def handle_bot_commands(message, response: UserResponse):
    if not response.done:
        obj = create_bot_command(message.content)
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
    author = message.author

    is_admin = DiscordWrapper.is_admin(payload.member)
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
    is_admin = DiscordWrapper.is_admin(message.author)

    if DiscordWrapper.queue_channel == message.channel.id:
        if message.author != client.user and not is_admin:
            response.set_options("waiting")
            await response.send_message(message)
    elif DiscordWrapper.bot_channel == message.channel.id:
        if is_admin:
            await handle_bot_commands(message, response)
            if response.done:
                await response.send_message(message)
        else:
            response.set_options("failure")
            await response.send_message(message)


def run_discord():
    client.run(os.getenv('TOKEN'))
