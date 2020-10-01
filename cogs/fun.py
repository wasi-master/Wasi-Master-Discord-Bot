import discord
import random
import asyncio
import unicodedata
import html
from discord.ext import commands
import async_cleverbot as ac
import json


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        groot = " ".join([random.choice(groots) + (random.choice(punct)*random.randint(0, 5))])
        print(groot)

    @commands.command(
        aliases=["q", "triv", " trivia"], description="Sends a quiz for you to answer"
    )
    async def quiz(
        self,
        ctx
    ):
        answered = False

        def check(message=discord.Message):
            if not message.author.bot:
                return (
                    message.author == ctx.message.author
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
                await ctx.message.channel.send(
                    f"{ctx.author.mention}, You didn\’t answer in time"
                )
        else:
            if not answered:
                if str(message.content).strip().lower() == correct_answer:
                    await ctx.message.channel.send("Correct you big brain")
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
        member = member or ctx.message.author
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name="Gay Telling Machine")
        embed.set_footer(text=f"Requested by {ctx.author}")
        if ctx.message.author.id == 538332632535007244:
            gay = 0
        else:
            gay = ctx.bot.secureRandom.randint(0, 100)
        embed.add_field(name="How Gay?", value=f"{member.name} is {gay}% gay")
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["mem"],
        description="See a meme",
    )
    async def meme(self, ctx):
        async with self.bot.session.get("https://meme-api.herokuapp.com/gimme") as r:
            fj = json.loads(await r.text())
        embed = discord.Embed(title=fj["title"], url=fj["postLink"], color=0xFF5700)
        embed.set_image(url=fj["url"])
        await ctx.send(embed=embed)

    @commands.command(
        name="chatbot", aliases=["cb"], description=" Talk with a chat bot"
    )
    async def cleverbot_(self, ctx, *, query: str):
        """Ask Cleverbot a question!"""
        try:
            async with ctx.typing():
                r = await ctx.bot.cleverbot.ask(
                    query, ctx.author.id
                )  # the ID is for context
        except ac.InvalidKey:
            return await ctx.send(
                "An error has occurred. The API key provided was not valid."
            )
        except ac.APIDown:
            return await ctx.send("I have to sleep sometimes. Please ask me later!")
        else:
            await ctx.send("{}, {}".format(ctx.author.mention, r.text))

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
    async def emojiparty(
        self,
        ctx,
    ):
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
                await message.edit(content="You were too late :(")
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
    async def whatsthispokemon(
        self,
        ctx,
    ):

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
                    await ctx.send(f"Wrong, you have {max_tries - counter} tries left")
                    if counter >= 1:
                        await ctx.send(f"Wrong, you can try `hint` to get a hint")
                    elif counter == max_tries:
                        embed = discord.Embed(
                            title="You lost",
                            description="The pokemon was {fj['pokemon']['name']}",
                        )
                        embed.set_image(url=fj["answer_image"])
                        await ctx.send(embed=embed)
                        return
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, you didn't reply within time")
                return


def setup(bot):
    bot.add_cog(Fun(bot))