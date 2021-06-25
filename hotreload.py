"""A cog used for reloading other cogs after they're edited
"""
import os
import pathlib

from discord.ext import commands, tasks

# put your extension names in this list
# if you don't want them to be reloaded
IGNORE_EXTENSIONS = ["jishaku", "hotreload"]


def path_from_extension(extension: str) -> pathlib.Path:
    """Returns a path from a given extension

    Parameters
    ----------
    extension : str
        the extension for the path to be gotten form

    Returns
    -------
    pathlib.Path
        the path
    """
    return pathlib.Path(extension.replace(".", os.sep) + ".py")


class HotReload(commands.Cog):
    """
    Cog for reloading extensions as soon as the file is edited
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_modified_time = {}
        self.hot_reload_loop.start()

    def cog_unload(self):
        """Occurs when the cog is unloaded"""
        self.hot_reload_loop.stop()

    @tasks.loop(seconds=3)
    async def hot_reload_loop(self):
        """Loops every 3 seconds and checks if any extension has been updated."
        loads the extension if it was updated
        """
        for extension in list(self.bot.extensions.keys()):
            if extension in IGNORE_EXTENSIONS:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                continue
            except commands.ExtensionError:
                print(f"Couldn't reload extension: {extension}")
            else:
                print(f"Reloaded extension: {extension}")
            finally:
                self.last_modified_time[extension] = time

    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self):
        """saves the last modified time of an extension"""
        self.last_modified_time = {}
        # Mapping = {extension: timestamp}
        for extension in self.bot.extensions.keys():
            if extension in IGNORE_EXTENSIONS:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            self.last_modified_time[extension] = time


def setup(bot):
    """Adds the cog to the bot"""

    """runs when the bot was loaded

    Parameters
    ----------
    bot : commands.Bot
        the bot
    """
    cog = HotReload(bot)
    bot.add_cog(cog)
