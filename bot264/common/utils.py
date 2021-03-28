import discord
from discord.channel import CategoryChannel


def list_categories(channels):
    categories = []
    for item in channels:
        if type(item) is CategoryChannel and str(item) != 'Personal':
            categories.append(item)
    return categories


def create_simple_message(name, value, embed=None):
    if type(embed) != discord.Embed:
        embed = discord.Embed()
    return embed.add_field(name=name, value=value, inline=False)


def iterate_commands(content, commands, starts_with=True):
    for v, t in commands:
        if (starts_with and content.startswith(v)) or \
                (not starts_with and content == v):
            return t
    return None
