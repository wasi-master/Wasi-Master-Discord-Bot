import asyncio
import datetime
import difflib
import json
import re
import typing
from typing import Union

import discord
import humanize
import requests
from discord.ext import commands

from utils.converters import TimeConverter


class Time(commands.Cog):
    """Commands releated to time"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Reminds you something")
    async def remind(self, ctx, time: TimeConverter, *, text: str):
        seconds = time
        natural_time = humanize.naturaldelta(datetime.timedelta(seconds=int(seconds)))
        user = ctx.author
        texttosend = text
        timetowait = natural_time
        await ctx.send(f"Gonna remind you `{texttosend}` in {timetowait}")
        await asyncio.sleep(seconds)
        await self.user.send(texttosend)

    @commands.command(
        aliases=["tzs", "timezoneset", "settimezone", "stz", "ts"],
        description=" Set your time zone to be used in the timr command",
    )
    async def timeset(self, ctx, *, timezone: str):
        location = timezone
        continents = ["asia", "europe", "oceania", "australia", "africa"]
        if location.lower() in continents:
            return await ctx.send("I need a area not a continent")

        async with self.bot.session.get(
            f"http://worldtimeapi.org/api/timezone/{location}"
        ) as r:
            fj = json.loads(await r.text())

        try:
            fj["error"]
            error = True
        except:
            error = False
        if not error:
            savedtimezone = await self.bot.db.fetchrow(
                """
            SELECT * FROM timezones
            WHERE user_id = $1
                """,
                ctx.author.id,
            )
            if not savedtimezone is None:
                savedtimezone = await self.bot.db.execute(
                    """
                UPDATE timezones
                SET timezone = $2
                WHERE user_id = $1
                    """,
                    ctx.author.id,
                    timezone,
                )
            else:
                await self.bot.db.execute(
                    """
                    INSERT INTO timezones (timezone, user_id)
                    VALUES ($1, $2)
                    """,
                    timezone,
                    ctx.author.id,
                )
            embed = discord.Embed(
                title="Success",
                description=f"Timezone set to {location}",
                color=5028631,
            )
            await ctx.send(embed=embed)
        else:
            if fj["error"] == "unknown location":
                locations = json.loads(
                    requests.get("http://worldtimeapi.org/api/timezone").text
                )
                suggestions = difflib.get_close_matches(
                    location, locations, n=5, cutoff=0.3
                )
                suggestionstring = ""
                embed = discord.Embed(
                    title="Unknown Location",
                    description="The location couldn't be found",
                    color=14885931,
                )
                for i in suggestions:
                    suggestionstring += f"`{i}`\n"
                #  embed.set_author(name="Location Not Found")
                embed.add_field(name="Did you mean?", value=suggestionstring)
                await ctx.send(embed=embed)

    @commands.command(aliases=["tm"], description="See time")
    async def time(self, ctx, location_or_user: Union[discord.Member, str] = None):
        embed = discord.Embed(color=0x2F3136)
        location = location_or_user
        if location is None:
            location = await self.bot.db.fetchrow(
                """
            SELECT * FROM timezones
            WHERE user_id = $1""",
                ctx.author.id,
            )
            if not location is None:
                location = location["timezone"]
            if location is None:
                embed = discord.Embed(
                    title="Timezone Not set",
                    description='Set your time with the timeset command (shortest alias "ts")',
                    color=14885931,
                )
                await ctx.send(embed=embed)
                return
        elif isinstance(location, discord.Member):
            location = await self.bot.db.fetchrow(
                """
            SELECT * FROM timezones
            WHERE user_id = $1""",
                location.id,
            )
            if not location is None:
                location = location["timezone"]
            else:
                embed = discord.Embed(
                    title=f"{location_or_user.name} has not yet set his tinezone",
                    description='Set timezone with the timeset command (shortest alias "ts")',
                    color=14885931,
                )
                await ctx.send(embed=embed)
                return

        async with self.bot.session.get(
            f"http://worldtimeapi.org/api/timezone/{location}"
        ) as r:
            fj = json.loads(await r.text())

        try:
            fj["error"]
            error = True
        except KeyError:
            error = False
        if error:
            # await ctx.send(f"```json\n{fj}```")
            if fj["error"] == "unknown location":
                locations = json.loads(
                    requests.get("http://worldtimeapi.org/api/timezone").text
                )
                suggestions = difflib.get_close_matches(
                    location, locations, n=5, cutoff=0.3
                )
                suggestionstring = ""
                for i in suggestions:
                    suggestionstring += f"`{i}`\n"
                embed = discord.Embed(description=f"{location} is not available")
                embed.set_author(name="Location Not Found")
                embed.add_field(name="Did you mean?", value=suggestionstring)
                await ctx.send(embed=embed)
        else:
            currenttime = datetime.datetime.strptime(
                fj["datetime"][:-13], "%Y-%m-%dT%H:%M:%S"
            )
            gmt = fj["utc_offset"]
            embed.set_author(name="Time")
            embed.add_field(
                name=location, value=currenttime.strftime("%a, %d %B %Y, %H:%M:%S")
            )
            embed.add_field(name="UTC Offset", value=gmt)
            await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Time(bot))
