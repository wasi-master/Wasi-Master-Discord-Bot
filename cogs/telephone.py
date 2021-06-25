import asyncio
import random
import typing

import discord
from discord.ext import commands

from utils.converters import TelephoneConverter
from utils.functions import get_agreement


class Telephone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["call", "tp"], invoke_without_command=True)
    async def telephone(
        self, ctx, person: typing.Union[discord.Member, TelephoneConverter]
    ):
        phone_number = await self.bot.db.fetchrow(
            """
            SELECT phone_number FROM telephones WHERE user_id = $1
            """,
            ctx.author.id,
        )
        if phone_number is None:
            return await ctx.send(
                f"You don't have a phone number, create one with `{ctx.prefix}telephone rgister`"
            )
        if isinstance(person, TelephoneConverter):
            user_id = await self.bot.db.fetchrow(
                """
                SELECT user_id FROM telephones WHERE phone_number = $1
                """,
                person,
            )
            phone_number = person
            if user_id is None:
                return await ctx.send("No one has that telephone number.")
            user = self.bot.get_user(user_id)
        elif isinstance(person, discord.Member):
            phone_number = await self.bot.db.fetchrow(
                """
                SELECT phone_number FROM telephones WHERE user_id = $1
                """,
                person.id,
            )
            user = person
            if phone_number is None:
                return await ctx.send("The person has no telephone number")
        if not await get_agreement(
            ctx,
            f"{ctx.author} is calling you. do you accept it?",
            user.dm_channel,
            user,
            300,
        ):
            return await ctx.reply(f"{user.name} Declined the call")

        def check(msg):
            return msg.author in (ctx.author, user) and msg.channel in (
                ctx.channel,
                ctx.author.dm_channel,
                user.dm_channel,
            )

        await ctx.reply(
            f"You have started a call with {user.name}, write anything here and it'll be sent to the user. type `wm,cancel` to cancel"
        )
        await user.send(
            f"Call started with {ctx.author.name}, write anything here and it'll be sent to the user. type `wm,cancel` to cancel"
        )
        while True:
            try:
                message = await self.bot.wait_for("message", check=check, timeout=120)
                if message.author == ctx.author:
                    await user.send(f"**__{ctx.author.name}__**: {message.content}")
                if message.author == user:
                    await ctx.send(f"**__{user.name}__**: {message.content}")
                if message.content.startswith("wm,cancel"):
                    if message.author == ctx.author:
                        await ctx.send("You have cancelled the call")
                        await user.send(f"{ctx.author.name} has cancelled the call")
                        return
                    if message.author == user:
                        await user.send("You have cancelled the call")
                        await ctx.reply(f"{user.name} has cancelled the call")
                        return

            except asyncio.TimeoutError:
                await user.send("Timed out")
                await ctx.reply("Timed out")
                return

    @telephone.command(name="register", aliases=["new", "create", "n", "r", "c"])
    async def telephone_register(self, ctx):
        phone_number = await self.bot.db.fetchrow(
            """
            SELECT phone_number FROM telephones WHERE user_id = $1
            """,
            ctx.author.id,
        )
        if phone_number:
            if not await get_agreement(
                ctx,
                "You already have a telephone, do you want to create a new number?",
            ):
                return
        phone_number = int("".join(str(random.randint(0, 9)) for i in range(11)))
        await self.bot.db.execute(
            """
                INSERT INTO telephones (user_id, phone_number)
                VALUES ($1, $2)
                """,
            ctx.author.id,
            phone_number,
        )
        await ctx.send(
            embed=discord.Embed(
                title="Registration Succesfull",
                color=discord.Color.green(),
                description=f"Your phone number is {phone_number}",
            )
        )


def setup(bot):
    """Adds the cog to the bot"""
    bot.add_cog(Telephone(bot))
