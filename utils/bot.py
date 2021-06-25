import discord
from discord.ext import commands, ipc


class WMBot(commands.Bot):
    """A subclass of commands.Bot"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ipc = ipc.Server(self, secret_key="WMBot")  # create our IPC Server

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or WMBotContext)

    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

    @property
    def owner(self):
        _owner = self.get_user(723234115746398219)
        return _owner


class WMBotContext(commands.Context):
    """A subclass of commands.Context"""

    @property
    def owner(self):
        _owner = self.bot.get_user(723234115746398219)
        return _owner

    async def send(self, *args, **kwargs):
        message = await self.reply(*args, **kwargs)
        self.bot.command_uses[self.message] = message
        return message
