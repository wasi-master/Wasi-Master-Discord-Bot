import json
import discord
from discord.ext import commands
import random, asyncio

class Games(commands.Cog):
    """Game Releated commands (most games have their own separate cog)
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["gtn"])
    @commands.has_permissions(manage_messages=True)
    async def guessthenumber(self, ctx, number_range: str):
        if len(number_range.split("-")) == 1:
            start_range = 1
            end_range = int(number_range.strip())
        elif len(number_range.split("-")) == 2:
            start_range, end_range = [int(i.strip()) for i in number_range.split("-")]
        else:
            await ctx.send("Invalid range")
            return
        if not end_range > start_range:
            await ctx.send("End is smaller than start")
            return
        # start_range, end_range = abs(start_range), abs(end_range)
        num = random.randint(start_range, end_range)
        await ctx.send(f"Okay, I picked a number between {start_range} and {end_range}, now try to guess what it is")
        await ctx.author.send(f"The number is ||{num}||\n\nDon\'t click on the spoiler if you want to participate")
        allowed_words = ["end", "stop", "hint", "h", "reduce", "r", "change", "c"]
        tries = 0
        last_hint = 0
        while True:
            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and not m.author.bot, timeout=60)
                if msg.content.isdigit():
                    guess = int(msg.content)
                    if guess > end_range:
                        await msg.delete()
                        await msg.author.send(f"You sent {guess} which is higher than the highest nunber possible ({end_range})")
                    elif guess < start_range:
                        await msg.delete()
                        await msg.author.send(f"You sent {guess} which is lower than the smallest nunber possible ({start_range})")
                    if guess == num:
                        await ctx.send(f"{msg.author.mention}, You nailed it, the number was {num}\n\n Tries: {tries}")
                        await ctx.send(":partying_face::partying_face::partying_face::partying_face::partying_face:")
                        return
                    else:
                        tries += 1
                else:
                    if msg.content in allowed_words:
                        # if (not msg.author.permissions_in(ctx.channel).manage_guild) and (not msg.content in ("hint", "h"))
                            # await ctx.send(f"{msg.author.mention}, lYou can\'t do that")
                        if msg.content in ("stop", "end"):
                            if msg.author.permissions_in(ctx.channel).manage_guild:
                                await ctx.send("Okay stopped the guessing game :(")
                            else:
                                await ctx.send(f"{msg.author.mention}, You don't have the permissions required to stop the guessing game")
                        elif msg.content in ("hint", "h"):
                            if not last_hint == 0:
                                last_hint = tries
                            if not (tries - last_hint) < 5:
                                hint_num = random.randint(1, 2)
                                if hint_num == 1:
                                    if not len(str(start_range)) == len(str(end_range)):
                                        await ctx.send(f"The number has {len(str(num))} digits")
                                elif hint_num == 2:
                                    digits = len(str(num))
                                    digit = random.randint(0, digits)
                                    picked_digit = str(num)[digit]
                                    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
                                    nums = random.sample(nums, 9)
                                    nums.append(digit)
                                    nums = [str(i) for i in set(nums)]
                                    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                                    await ctx.send(f"The {ordinal(digit+1)} digit of the picked number is in `{', '.join(nums)}`")
                                else:
                                    await ctx.send(f"{msg.author.mention}, Can't get a hint yet, try guessing some more")
                        
                    else:
                        await msg.delete()
                        await msg.author.send("You can't send that message there because a guess the number is going on there")
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Guess The Number Timed out", description=f"No one sent a message in thr last 60 seconds so I assume everyone left the game\n\nThe number was {num}"))

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
