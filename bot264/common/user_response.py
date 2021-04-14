import discord
from bot264.discord_wrapper import DiscordWrapper, Db


async def clear_emojis(message):
    for reaction in message.reactions:
        await reaction.clear()


class UserResponse:

    def __init__(self, done=False):
        self.response = []
        self.done = done
        self.emoji = []
        self.delete_message = False

        # (Channel, Author, Access)
        self.permissions = []
        self.loading = False

    @property
    def response_tail(self):
        if len(self.response) == 0:
            return None
        return self.response[-1]

    async def run_emoji_command(self, emoji, message: discord.message.Message,
                                ta_member: discord.Member, is_admin=False):
        ta_voice_state: discord.member.VoiceState = ta_member.voice
        if emoji == "❌":
            await DiscordWrapper.disconnect_user(message.author, ta_voice_state)
            await message.delete()
        elif is_admin:
            is_successful = False
            if ta_voice_state is not None:
                if emoji == "✋":
                    # Add user into voice channel
                    is_successful = await DiscordWrapper.move_user_to_office_hours(message.author, ta_voice_state)
                    if is_successful:
                        self.set_options("helping")
                        await clear_emojis(message)
                        await self.send_message(message)
                        Db.set_start_time(message.author.id, ta_member.id)
                elif emoji == "⌛":
                    # Kick out anyone in their voice channel rn btw.
                    if Db.is_ta_helping_student(message.author.id, ta_member.id):
                        is_successful = True
                        await DiscordWrapper.move_user_to_waiting_room(message.author, ta_voice_state)
                        self.set_options()
                        await clear_emojis(message)
                        await self.send_message(message)
                        Db.set_wait_time(message.author.id)
                elif emoji == "✅":
                    # Kick out anyone in their voice channel rn btw.
                    if Db.is_ta_helping_student(message.author.id, ta_member.id):
                        is_successful = True
                        await DiscordWrapper.disconnect_user(message.author, ta_voice_state)
                        await DiscordWrapper.add_history(message)
                        await message.delete()
                return is_successful
            else:
                if emoji == "🔄":
                    pass
                else:
                    return False
        else:
            return False
        return True

    def set_options(self, state=None):
        waiting_emoji = ["✋"]
        done_emoji = ["✅"]
        helping_emoji = ["✅", "⌛"]
        history_emoji = ["🔄"]
        failure_emoji = ["❌"]
        if not self.done:
            if state == "helping":
                self.emoji = helping_emoji
            elif state == "history":
                self.emoji = history_emoji
            elif state == 'done':
                self.emoji = done_emoji
            elif state == 'failure':
                self.emoji = failure_emoji
            else:
                self.emoji = waiting_emoji

    def add_response(self, item, done=False):
        if not self.done:
            self.done = self.done or done
            if item is not None and item != self.response_tail:
                self.response.append(item)

    async def send_loading(self, message):
        if self.loading:
            response = discord.Embed().add_field(name="Loading", value="Loading Content")
            await message.channel.send(embed=response)

    async def send_message(self, message, channel=None):
        channel = message.channel if channel is None else channel
        for author, channel, access in self.permissions:
            await channel.set_permissions(author, read_messages=access, send_messages=access)
        if message is not None:
            for i in self.emoji:
                await message.add_reaction(i)
        for i in self.response:
            if type(i) is str:
                await channel.send(i)
            else:
                await channel.send(embed=i)
