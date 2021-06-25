from discord.ext import commands


class BlackListed(commands.CheckFailure):
    """Don't respond if the user is blocked from using the bot"""


class NoAPIKey(commands.CheckFailure):
    """The bot owner didn't setup a api key yet"""
