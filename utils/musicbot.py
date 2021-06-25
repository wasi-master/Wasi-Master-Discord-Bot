from discord.ext import commands


class MusicBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        for guild in self.guilds:
            if not guild.me.name == "MusicMaster":
                await guild.me.edit(nick="MusicMaster")

    async def close(self):
        for guild in self.guilds:
            if not guild.me.name == "MusicMaster":
                await guild.me.edit(nick="MusicMaster")
