from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_commands(self, data):
        return self.bot.commands[0]


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(IpcRoutes(bot))