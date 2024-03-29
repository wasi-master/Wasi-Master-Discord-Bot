import asyncio
import datetime
import html
import json
import random
import unicodedata
from typing import Union
from urllib.parse import quote

import async_cleverbot as ac
import discord
from discord.ext import commands


class Fun(commands.Cog):
    """Fun commands :)"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["co"])
    async def cookie(self, ctx):
        m = await ctx.send(embed=discord.Embed(title="🍪 Cookie is coming..."))
        await asyncio.sleep(3)
        await m.edit(embed=discord.Embed(title="🍪 Cookie is coming in **3**"))
        await asyncio.sleep(1)
        await m.edit(embed=discord.Embed(title="🍪 Cookie is coming in **2**"))
        await asyncio.sleep(1)
        await m.edit(embed=discord.Embed(title="🍪 Cookie is coming in **1**"))
        await asyncio.sleep(1)
        await m.edit(embed=discord.Embed(title="🍪 Grab the Cookie"))
        await m.add_reaction("🍪")
        try:
            r, u = await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: str(r.emoji) == "🍪"
                and r.message == m
                and r.message.channel == ctx.channel
                and not u.bot,
                timeout=10,
            )
        except asyncio.TimeoutError:
            await ctx.send("No one got the cookie :(")
        else:
            await m.edit(
                embed=discord.Embed(
                    title=f"**{u}** got the cookie in **{round((datetime.datetime.utcnow()-m.edited_at).total_seconds(), 3)}** seconds"
                )
            )

    @commands.command(
        aliases=["giveyouup", "gyu", "nggyu", "giveup", "never_gonna_give_you_up"]
    )
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def nevergonnagiveyouup(self, ctx, whotogiveup: Union[discord.Member, str]):
        if isinstance(whotogiveup, discord.Member):
            person = whotogiveup.display_name
        else:
            person = whotogiveup
        if "\n" in person:
            person = person.split("\n")[0]
        if person.count(" ") > 2:
            return await ctx.send("Why so large name? not gonna do that")
        gwp = """Never gonna give {0} up
Never gonna let {0} down
Never gonna run around and desert {0} 
Never gonna make {0} cry
Never gonna say goodbye
Never gonna tell a lie and hurt {0}
Never gonna give {0} up
Never gonna let {0} down
Never gonna run around and desert {0}. 
Never gonna make {0} cry
Never gonna say goodbye
Never gonna tell a lie and hurt {0}.
Never gonna give {0} up
Never gonna let {0} down
Never gonna run around and desert {0} 
Never gonna make {0} cry
Never gonna say goodbye
Never gonna tell a lie and hurt {0}""".format(
            person
        )
        gwp = discord.utils.escape_markdown(gwp)
        await ctx.send(gwp, allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        snipes = self.bot.snipes
        if snipes.get(channel.id):
            message = snipes[channel.id]
            e = discord.Embed(
                title="Said:",
                description=message.content,
                timestamp=message.created_at,
                color=discord.Colour.green(),
            )
            if message.author.display_name == message.author.name:
                name = str(message.author)
            else:
                name = f"{message.author} ({message.author.display_name})"
            e.set_author(icon_url=message.author.avatar_url, name=name)
            e.set_thumbnail(url=message.author.avatar_url)
            await ctx.send(embed=e)
        else:
            await ctx.send("No messages to snipe")

    @commands.command()
    async def imagine(self, ctx, *, thing):
        await ctx.send(f"I can't even imagine {thing} bro")

    @commands.command()
    async def cakeday(self, ctx):
        await ctx.send("")

    @commands.command()
    async def advice(self, ctx):
        async with self.bot.session.get("https://api.adviceslip.com/advice") as r:
            resp = json.loads(await r.text())
            await ctx.send(
                embed=discord.Embed(
                    title="Advice", description=resp["slip"]["advice"], color=0x2F3136
                )
            )

    @commands.command()
    async def topic(self, ctx):
        async with self.bot.session.get("https://dinosaur.ml/random/topic/") as r:
            resp = await r.json()
            await ctx.send(
                discord.Embed(title="Topic", description=resp["topic"], color=0x2F3136)
            )

    @commands.command(aliases=["bsm", "bsmap", "map"])
    @commands.cooldown(1, 2, commands.BucketType.default)
    async def brawlstarsmap(self, ctx, *, provided_map: str):
        embed = discord.Embed()
        maplist = provided_map.split(" ")
        map = ""
        for i in maplist:
            preps = ["on", "the", "of"]
            if not i.strip().lower() in preps:
                map += " " + i.lower().capitalize()
            else:
                map += " " + i.lower()
        map = map.strip().replace(" ", "-")
        url = f"https://www.starlist.pro/assets/map/{map}.png"
        # session = aiohttp.ClientSession()
        async with self.bot.session.get(url) as response:
            text = await response.text()
            if "Not Found" in text:
                embed.add_field(
                    name="Map not found",
                    value=f"The map `{map.replace('-', ' ')}` is not found",
                )
            else:
                embed.set_image(url=url)
        embed.title = map.replace("-", " ")
        await ctx.send(embed=embed)

    @commands.command()
    async def groot(self, ctx):
        """Who... who are you?"""
        groots = [
            "I am Groot",
            "**I AM GROOT**",
            "I... am... *Groot*",
            "I am Grooooot",
            "i am groot",
        ]
        punct = [
            "!",
            ".",
            "?",
        ]
        # Build our groots
        groot_max = 1
        groot = " ".join(
            [random.choice(groots) + (random.choice(punct) * random.randint(0, 5))]
        )
        await ctx.send(groot)

    @commands.command(
        aliases=["q", "triv", " trivia"], description="Sends a quiz for you to answer"
    )
    async def quiz(self, ctx):
        answered = False

        def check(message=discord.Message):
            if not message.author.bot:
                return (
                    message.author == ctx.author
                    and message.channel.id == ctx.channel.id
                )

        ordinal = lambda n: "%d%s" % (
            n,
            "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
        )
        ordlist = [ordinal(n) for n in range(1, 5)]
        async with ctx.typing():
            async with self.bot.session.get(
                "https://opentdb.com/api.php?amount=1&type=multiple"
            ) as response:
                data = json.loads(await response.text())

            question = (
                data.get("results")[0]
                .get("question")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é")
            )
            difficulty = data.get("results")[0].get("difficulty")
            category = (
                data.get("results")[0]
                .get("category")
                .replace("Entertainment: ", "")
                .replace("Science: ", "")
            )
            embed = discord.Embed(
                title=question,
                description=f"Category: {category.title()}\nDifficulty: {difficulty.title()}",
                color=0x2F3136,
            )
            embed.set_footer(text=f"Trivia/Quiz for {ctx.author}")
            correct_answer = "not found"
            randomint = ctx.bot.secureRandom.randint(1, 4)
            if randomint == 1:
                correct_answer = "a"
                embed.add_field(
                    name="A",
                    value=html.parser.unescape(
                        data.get("results")[0].get("correct_answer")
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="B",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[0]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="C",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[1]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="D",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[2]
                    ),
                    inline=False,
                )
            if randomint == 2:
                correct_answer = "b"
                embed.add_field(
                    name="A",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[0]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="B",
                    value=html.parser.unescape(
                        data.get("results")[0].get("correct_answer")
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="C",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[1]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="D",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[2]
                    ),
                    inline=False,
                )
            if randomint == 3:
                correct_answer = "c"
                embed.add_field(
                    name="A",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[0]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="B",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[1]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="C",
                    value=html.parser.unescape(
                        data.get("results")[0].get("correct_answer")
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="D",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[2]
                    ),
                    inline=False,
                )
            if randomint == 4:
                correct_answer = "d"
                embed.add_field(
                    name="A",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[0]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="B",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[1]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="C",
                    value=html.parser.unescape(
                        data.get("results")[0].get("incorrect_answers")[2]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="D",
                    value=html.parser.unescape(
                        data.get("results")[0].get("correct_answer")
                    ),
                    inline=False,
                )
        await ctx.send(embed=embed)
        try:
            message = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            if not answered:
                await ctx.channel.send(
                    f"{ctx.author.mention}, You didn\’t answer in time"
                )
        else:
            if not answered:
                if str(message.content).strip().lower() == correct_answer:
                    await ctx.channel.send("Correct you big brain")
                else:
                    await ctx.send(
                        f"Poo Poo Brain xD, Correct answer was {correct_answer.upper()} ({ordlist[randomint - 1]} option)"
                    )
                answered = True

    @commands.command(
        aliases=["hg", "howlesbian", "hl"],
        description="Check how gay a person is (random)",
    )
    async def howgay(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Gay Telling Machine")
        embed.set_footer(text=f"Requested by {ctx.author}")
        if ctx.author.id == 723234115746398219:
            gay = 0
        else:
            gay = ctx.bot.secureRandom.randint(0, 100)
        embed.add_field(name="How Gay?", value=f"{member.name} is {gay}% gay")
        await ctx.send(embed=embed)

    @commands.command(aliases=["mem"], description="See a meme")
    async def meme(self, ctx):
        async with self.bot.session.get("https://meme-api.herokuapp.com/gimme") as r:
            fj = json.loads(await r.text())
        embed = discord.Embed(title=fj["title"], url=fj["postLink"], color=0xFF5700)
        embed.set_image(url=fj["url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx):
        await ctx.send("Type `rock` or `paper` or `scissors`")

        def check(message):
            return (
                message.author == ctx.author
                and message.channel == ctx.channel
                and message.content in ["rock", "paper", "scissors"]
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await ctx.reply(
                "Didn't respond with neither `rock`, `paper` or `scissors`"
            )
        else:
            user_action = msg.content.lower()
            computer_action = random.choice(["rock", "paper", "scissors"])
            if user_action == computer_action:
                await msg.reply(
                    f"I picked {computer_action}, Both players selected `{user_action}`. It's a tie!"
                )
            elif user_action == "rock":
                if computer_action == "scissors":
                    await msg.reply(
                        f"I picked {computer_action}, Rock smashes scissors! You win!"
                    )
                else:
                    await msg.reply(
                        f"I picked {computer_action}, Paper covers rock! You lose."
                    )
            elif user_action == "paper":
                if computer_action == "rock":
                    await msg.reply(
                        f"I picked {computer_action}, Paper covers rock! You win!"
                    )
                else:
                    await msg.reply(
                        f"I picked {computer_action}, Scissors cuts paper! You lose."
                    )
            elif user_action == "scissors":
                if computer_action == "paper":
                    await msg.reply(
                        f"I picked {computer_action}, Scissors cuts paper! You win!"
                    )
                else:
                    await msg.reply(
                        f"I picked {computer_action}, Rock smashes scissors! You lose."
                    )

    @commands.command(
        name="chatbot", aliases=["cb"], description=" Talk with a chat bot"
    )
    async def chatbot(self, ctx):
        """Talk to AI Chatbot"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        e = discord.Embed(
            title="Session has started",
            description=f"Say anything you like and chatbot will respond, may take up to 5 seconds for it to respond, say `cancel` to cancel",
        )
        e.set_footer(text="Timeout in 60 secs")
        await ctx.send(embed=e)
        while True:
            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.reply("What about the chatbot, you didn't respond")
                return
            if "cancel " in msg.content:
                await msg.reply("Okay, stopped")
                break

            response = await self.bot.cleverbot.ask(msg.content, msg.author.id)
            e = discord.Embed(title="AI Responded", description=response.text)
            e.set_footer(text="Timeout in 60 secs")
            await msg.reply(embed=e)

    @commands.command(
        name="penis", aliases=["pp"], description="See someone's penis size (random)"
    )
    async def pp(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        ppsize = random.randint(0, 30)
        if ppsize > 0 and ppsize < 5:
            comment = "Hehe, pp smol"
        elif ppsize > 6 and ppsize < 9:
            comment = "okay"
        elif ppsize > 10 and ppsize < 12:
            comment = "normal pp"
        elif ppsize > 13 and ppsize < 18:
            comment = "huge pp"
        elif ppsize > 19 and ppsize < 25:
            comment = "extremely big pp"
        else:
            comment = "tremendous pp "
        embed = discord.Embed(
            title=f"{member.name}'s pp size",
            description="8" + "=" * ppsize + "D",
            color=0x2F3136,
        )
        embed.set_footer(text=comment)
        await ctx.send(embed=embed)

    @commands.command(
        description="Bot will send the name of every emoji reacted to the bot's message"
    )
    async def emojiparty(self, ctx):
        message = await ctx.send("React to this message with any emoji")
        _list = []

        def check(r, u):
            return r.message.channel.id == ctx.channel.id and r.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=15
                )
            except asyncio.TimeoutError:
                await message.edit(
                    content=message.content + "\n\nOkay I stopped now :)"
                )
                return
            else:
                if not isinstance(reaction.emoji, discord.Emoji):
                    try:
                        _list.append(
                            f"{reaction.emoji} - {unicodedata.name(reaction.emoji).title()}"
                        )
                        await message.edit(content="\n".join(_list))
                    except:
                        try:
                            await message.remove_reaction(reaction.emoji, ctx.author)
                        except discord.Forbidden:
                            pass
                else:
                    _list.append(f"{reaction.emoji} - {reaction.emoji.name}")
                    await message.edit(content="\n".join(_list))

    @commands.command(aliases=["wtp"], description="You have to guess the pokemon")
    async def whatsthispokemon(self, ctx):

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB"
        }

        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        async with self.bot.session.get(
            "https://dagpi.tk/api/wtp", headers=headers
        ) as cs:
            fj = await cs.json()
        embed = discord.Embed(title="What's this pokemon?")
        embed.set_image(url=fj["question_image"])
        await ctx.send(embed=embed)
        counter = 0
        max_tries = 3
        guessed = 0
        while True:
            try:
                message = await self.bot.wait_for("message", check=check, timeout=20)
                if message.content.lower() == fj["pokemon"]["name"].lower():
                    embed = discord.Embed(
                        title="You got it right",
                        description=f"The pokemon was {fj['pokemon']['name']}",
                    )
                    embed.set_image(url=fj["answer_image"])
                    await ctx.send(embed=embed)
                    return
                elif message.content.lower() == "hint":
                    guessed += 1
                    counter += 1
                    if counter == 1:
                        await ctx.send("You can't get a hint without guessing")
                    elif counter > 1:
                        name = list(fj["pokemon"]["name"])
                        for index, i in enumerate(name):
                            if random.randint(0, 100) >= 40:
                                name[index] = "_"
                        name = "".join(name)
                        await ctx.send(f"The pokemon name is {name}")
                else:
                    await ctx.send(
                        f"Wrong.send( you have {max_tries - counter} tries left"
                    )
                    if counter >= 1:
                        await ctx.send(f"Wrong.send( you can try `hint` to get a hint")
                    elif counter == max_tries:
                        embed = discord.Embed(
                            title="You lost",
                            description="The pokemon was {fj['pokemon']['name']}",
                        )
                        embed.set_image(url=fj["answer_image"])
                        await ctx.send(embed=embed)
                        return
            except asyncio.TimeoutError:
                await ctx.send(
                    f"{ctx.author.mention}.send( you didn't reply within time"
                )
                return


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Fun(bot))
