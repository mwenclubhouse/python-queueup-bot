import asyncio
import os
import signal
import sys

import discord

from bot264.discord_wrapper import DiscordWrapper, Db, create_db
from bot264.mwenclubhouse import FbDb
from .commands import UserCommand, LockQueueCommand, UnLockQueueCommand
from .common.user_response import UserResponse
from .common.utils import iterate_commands, create_simple_message

if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv

    load_dotenv()

intents = discord.Intents.default()
intents.members = True
client: discord.Client = discord.Client(intents=intents)
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


class GracefulKiller:
    kill_now = False

    def __init__(self):
        client.loop.add_signal_handler(signal.SIGINT, self.exit_gracefully)
        client.loop.add_signal_handler(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self):
        self.kill_now = True
        FbDb.kill()
        asyncio.ensure_future(client.close())
        sys.exit()


@client.event
async def on_ready():
    create_db()
    FbDb.init()
    FbDb.listen()
    GracefulKiller()


@client.event
async def on_raw_reaction_add(payload: discord.raw_models.RawReactionActionEvent):
    db = Db(payload.guild_id)
    if payload.user_id == client.user.id:
        return

    if not db.is_emoji_channels(payload.channel_id):
        return

    message: discord.message.Message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    author = message.author
    is_admin = db.is_admin(payload.member)
    run_command = False
    if is_admin or payload.user_id == author.id:
        response = UserResponse()
        run_command = await response.run_emoji_command(db,
                                                       payload.emoji.name, message, payload.member, is_admin=is_admin)

    if not run_command:
        await message.remove_reaction(payload.emoji, payload.member)


@client.event
async def on_message(message: discord.message.Message):
    if message.guild is None:
        return
    db = Db(message.guild.id)

    response: UserResponse = UserResponse()
    student_member: discord.Member = message.author
    is_admin = db.is_admin(student_member)
    db.add_name_by_id(student_member)

    if message.channel.id in db.queues:
        if student_member != client.user and not is_admin:
            if not db.is_student_in_queue(student_member.id):
                response.set_options("waiting")
                db.add_student(student_member.id, message.id)
                await response.send_message(message)
                title = f"Hello {student_member.display_name}"
                context = f"Please enter Waiting Room Voice Channel"
                color = 3066993
            else:
                title = f"I'm sorry {student_member.display_name}"
                context = f"You are only allowed 1 ticket at a time."
                color = 15158332
                await message.delete()
            new_message = create_simple_message(title, context)
            new_message.color = color
            dm_channel = await student_member.create_dm()
            await dm_channel.send(embed=new_message)
    elif db.bot_channel == message.channel.id:
        if is_admin:
            await handle_bot_commands(message, response)
            if response.done:
                await response.send_message(message)
        else:
            response.set_options("failure")
            await response.send_message(message)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    db = Db(payload.guild_id)
    if payload.channel_id in db.queues:
        db.remove_student(payload.message_id)


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    db = Db(member.guild.id)
    is_admin = db.is_admin(member)
    if is_admin:
        return
    if after.channel is None:
        await db.permission.remove_permissions_from_all_rooms(member)
    elif after.channel.id == db.waiting_room:
        if not db.is_student_in_queue(member.id):
            dm_channel = await member.create_dm()
            message = create_simple_message("Error", "Make sure to type your request inside THE QUEUE!!")
            message.color = 15158332
            await dm_channel.send(embed=message)
            await member.move_to(None, reason="Need a Request Help First")


def run_discord():
    client.run(os.getenv('TOKEN'))
