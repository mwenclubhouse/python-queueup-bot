import os

import discord

from bot264.discord_wrapper import DiscordWrapper, init_discord_wrapper, process_rooms, create_db, Db
from .commands import UserCommand, LockQueueCommand, UnLockQueueCommand
from .common.user_response import UserResponse
from .common.utils import iterate_commands, create_simple_message

if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv

    load_dotenv()

intents = discord.Intents.default()
intents.members = True
client: discord.Client = discord.Client(intents=intents)
init_discord_wrapper()
process_rooms()
create_db()
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
    student_member: discord.Member = message.author
    is_admin = DiscordWrapper.is_admin(student_member)

    if DiscordWrapper.queue_channel == message.channel.id:
        if student_member != client.user and not is_admin:
            if not Db.is_student_in_queue(student_member.id):
                response.set_options("waiting")
                Db.add_student(student_member.id, message.id)
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
    elif DiscordWrapper.bot_channel == message.channel.id:
        if is_admin:
            await handle_bot_commands(message, response)
            if response.done:
                await response.send_message(message)
        else:
            response.set_options("failure")
            await response.send_message(message)


@client.event
async def on_message_delete(message):
    student_id = message.author.id
    student = Db.get_student(student_id)
    if student is not None and message.id == student[1]:
        Db.remove_student(student_id)


@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    if after.channel is not None and after.channel.id == DiscordWrapper.waiting_room:
        if not Db.is_student_in_queue(member.id):
            dm_channel = await member.create_dm()
            message = create_simple_message("Error", "Make sure to type your request inside THE QUEUE!!")
            message.color = 15158332
            await dm_channel.send(embed=message)
            await member.move_to(None, reason="Need a Request Help First")


def run_discord():
    client.run(os.getenv('TOKEN'))
