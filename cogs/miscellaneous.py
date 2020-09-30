import discord
from discord.ext import commands
import datetime
import asyncio
import re

from typing import Optional

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["speak", "echo", "s"], description="Sends a message")
    async def say(
        self,
        ctx,
        channel: Optional[discord.TextChannel] = None,
        *,
        text: commands.clean_content,
    ):
        if channel:
            channel = channel
            text = f"{text}\n\n    - sent by {ctx.author} from {ctx.channel.mention}"
        else:
            channel = ctx.channel
        m = await channel.send(text)

        def check(message):
            return message == ctx.message

        try:
            await self.bot.wait_for("message_delete", timeout=30, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            await m.edit(
                content=f"{text}\n\n    - sent by {ctx.author} but he deleted his message"
            )

    @commands.command(aliases=["webping", "pingweb", "wp", "pw"])
    async def websiteping(self, ctx, url: str):

        if not url.startswith("http://") or url.startswith("https://"):
            url = "https://" + url
        if re.match(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            url,
        ):
            start = datetime.datetime.utcnow()
            async with self.bot.session.get(url) as r:
                status = r.status

            end = datetime.datetime.utcnow()
            elapsed = end - start
            embed = discord.Embed(
                description=f"Website took **{round((elapsed.total_seconds() * 1000), 2)}ms** to complete"
            )
            embed.set_footer(text=f"Status Code: {status}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Invalid URL: {url}")

    @commands.command(
        aliases=["t"],
        description="Test your timing! As soon as the message shows, click on the reaction after some amount of seconds",
    )
    async def timing(self, ctx, time=10):
        if time > 60:
            time = 60
        if time < 1:
            time = 1
        embed = discord.Embed(
            title=f"Try to react to this message with :white_check_mark: exactly after {time} seconds"
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("\u2705")

        def check(r, u):
            return (
                u.id == ctx.author.id
                and r.message.channel.id == ctx.channel.id
                and str(r.emoji) == "\u2705"
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", check=check, timeout=time + (time / 2)
            )
            embed = discord.Embed(
                title=f"You reacted to this message with :white_check_mark: after {round((datetime.datetime.utcnow() - message.created_at).total_seconds(), 2)} seconds"
            )
            embed.set_footer(
                text=f"Exact time is {(datetime.datetime.utcnow() - message.created_at).total_seconds()}"
            )
            await message.edit(embed=embed)
        except asyncio.TimeoutError:
            await message.edit(
                embed=discord.Embed(
                    title=f"{ctx.author}, you didnt react with a :white_check_mark:"
                )
            )
            return


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
