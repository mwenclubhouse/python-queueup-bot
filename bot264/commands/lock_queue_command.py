import discord

from .command import UserCommand
from ..discord_wrapper import DiscordWrapper


async def set_queue(message, state):
    queue_channel: discord.channel.TextChannel = DiscordWrapper.get_queue_channel()
    for i in message.author.roles:
        if not DiscordWrapper.is_admin_role(i):
            await queue_channel.set_permissions(send_messages=state, target=i)


class LockQueueCommand(UserCommand):

    async def run(self):
        self.response.set_options("done")
        await set_queue(self.message, False)
        self.response.done = True


class UnLockQueueCommand(UserCommand):

    async def run(self):
        self.response.set_options("done")
        await set_queue(self.message, True)
        self.response.done = True
