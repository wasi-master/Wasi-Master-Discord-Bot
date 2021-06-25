import discord
from discord.ext import commands


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_subcommands=True, aliases=["tg"])
    async def tag(self, ctx, tag_name):
        await ctx.send("")

    @tag.command(name="create", aliases=["add"])
    async def tag_create(self, ctx, tag_name, tag_content):
        await ctx.send("")

    @tag.command(name="delete", aliases=["remove"])
    async def tag_delete(self, ctx, tag_name):
        await ctx.send("")


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Tags(bot))
