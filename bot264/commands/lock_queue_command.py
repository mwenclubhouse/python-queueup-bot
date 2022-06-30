from .command import UserCommand
from bot264.database import ServerDb


async def set_queue(message, state):
    db = ServerDb(message.guild.id)
    queues = db.get_queues()
    for q in queues:
        for i in message.author.roles:
            if not db.is_admin_role(i):
                await q.set_permissions(send_messages=state, target=i)


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
