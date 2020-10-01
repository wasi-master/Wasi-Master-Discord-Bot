import discord
import random

from discord.ext import commands
from collections import Counter
from typing import Optional


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


class Random(commands.Cog):
    """commands that have to do something with the word random (made, done, or happening without method or conscious decision.)
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description="Chooses between multiple choices N times.", aliases=["cbo"]
    )
    async def choosebestof(
        self, ctx, times: Optional[int], *choices: commands.clean_content
    ):
        if len(choices) < 2:
            return await ctx.send("Not enough choices to pick from.")

        if times is None:
            times = (len(choices) ** 2) + 1

        times = min(10001, max(1, times))
        results = Counter(random.choice(choices) for i in range(times))
        builder = []
        if len(results) > 10:
            builder.append("Only showing top 10 results...")
        for index, (elem, count) in enumerate(results.most_common(10), start=1):
            builder.append(
                f"{index}. {elem} ({plural(count):time}, {count / times:.2%})"
            )

        await ctx.send("\n".join(builder))

    @commands.command(
        name="8ball",
        aliases=["eightball", "eight ball", "question", "answer", "8b"],
        description="Sends a yes/no type answer to a question",
    )
    async def _8ball(self, ctx, *, question: commands.clean_content):
        answers = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes – definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes Signs point to yes",
            "Reply hazy",
            "try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Dont count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]
        await ctx.send(
            f"`Question:` {question}\n`Answer:` {ctx.bot.secureRandom.choice(answers)}"
        )

    @commands.command(
        aliases=["pick", "choice", "ch"], description="makes desicions for you :)"
    )
    async def choose(self, ctx, *, choices):
        mesg = choices
        mesglist = mesg.split(",")
        mesglist = [i.strip() for i in mesg]
        num = 0
        choices = ""
        embed = discord.Embed(timestamp=ctx.message.created_at)
        embed.set_author(name="Choice Machine")
        embed.set_footer(text=f"Asked by {ctx.author}")
        for i in mesglist:
            num += 1
            choices += f"`{i}`, "
        embed.add_field(name="Choice {num}", value=f"{choices[:-2]}")
        embed.add_field(name="‌", value="‌")
        embed.add_field(
            name="**Chosen**", value=f"{ctx.bot.secureRandom.choice(mesglist)}"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Random(bot))
