import os
import discord
from firebase_admin import initialize_app
from bot264.discord_wrapper import DiscordWrapper
from bot264.env import Env
from bot264.killer import GracefulKiller
from bot264.database import Database, ServerDb, create_db
from bot264.commands import UserCommand, LockQueueCommand, UnLockQueueCommand
from bot264.common.user_response import UserResponse
from bot264.common.utils import iterate_commands, create_simple_message

if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv
    load_dotenv()

# Setting Up Env
Env.token = os.getenv('TOKEN')
Env.database_file_location = 'bucket/queueup.db'
Env.database_folder_location = 'bucket'

intents = discord.Intents.default()
intents.members = True
client: discord.Client = discord.Client(intents=intents)
killer: GracefulKiller = GracefulKiller(client)
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

def run_discord(server):
    initialize_app()

    @client.event
    async def on_ready():
        create_db()
        Database.init()
        killer.on_init()
        killer.start_flask(server)

    @client.event
    async def on_raw_reaction_add(payload: discord.raw_models.RawReactionActionEvent):
        db = ServerDb(payload.guild_id)
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
        db = ServerDb(message.guild.id)

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
        db = ServerDb(payload.guild_id)
        if payload.channel_id in db.queues:
            db.remove_student(payload.message_id)


    @client.event
    async def on_voice_state_update(member: discord.Member, before, after):
        db = ServerDb(member.guild.id)
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
    
    client.run(Env.token)
