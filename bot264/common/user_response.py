import discord

from bot264.discord_wrapper import DiscordWrapper


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
                                ta_voice_channel: discord.member.VoiceState, is_admin=False):
        if emoji == "❌":
            await message.delete()
        elif is_admin:
            if ta_voice_channel is not None:
                if emoji == "👀":
                    # Add user into voice channel
                    self.set_options("helping")
                    await clear_emojis(message)
                    await self.send_message(message)
                elif emoji == "⌛":
                    # Kick out anyone in their voice channel rn btw.
                    self.set_options()
                    await clear_emojis(message)
                    await self.send_message(message)
                elif emoji == "✅":
                    # Kick out anyone in their voice channel rn btw.
                    await DiscordWrapper.add_history(message)
                    await message.delete()
                else:
                    return False
            else:
                if emoji == "🔄":
                    pass
                else:
                    return False
        else:
            return False
        return True

    def set_options(self, state=None):
        waiting_emoji = ["👀", "❌"]
        helping_emoji = ["✅", "⌛", "❌"]
        history_emoji = ["🔄", "❌"]
        if not self.done:
            if state == "helping":
                self.emoji = helping_emoji
            elif state == "history":
                self.emoji = history_emoji
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
