import json
import discord
from discord.ext import commands


class Games(commands.Cog):
    """Game Releated commands (most games have their own separate cog)
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["tod"], description="Truth Or Dare")
    async def truthordare(self, ctx, questype: str = "random"):
        levels = ["Disgusting", "Stupid", "Normal", "Soft", "Sexy", "Hot"]

        async with self.bot.session.get(
            "https://raw.githubusercontent.com/sylhare/Truth-or-Dare/master/src/output.json"
        ) as r:
            fj = json.loads(await r.text())

        if questype == "random":
            number = ctx.bot.secureRandom.randint(0, 553)
            picked = fj[number]
            level = levels[int(picked["level"])]
            summary = picked["summary"]
            questiontype = picked["type"]
        else:
            return
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=summary)
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Type", value=questiontype)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
