import json

import discord
from discord.ext import commands


class Animals(commands.Cog):
    """Shows cute pictures of animals"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cat(self, ctx):
        """Shows random cute cat pictures"""
        url = "https://some-random-api.ml/animal/cat"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a cat picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command()
    async def dog(self, ctx):
        """Shows cute dog pictures"""
        url = "https://some-random-api.ml/animal/dog"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a dog picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute dog pictures")
    async def panda(self, ctx):
        """Shows cute panda pictures"""
        url = "https://some-random-api.ml/animal/panda"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a panda picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute dog pictures")
    async def redpanda(self, ctx):
        """Shows cute red panda pictures"""
        url = "https://some-random-api.ml/animal/red_panda"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a red panda picture").set_image(
                    url=img_url
                )
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a red panda picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute koala pictures")
    async def koala(self, ctx):
        """Shows cute koala pictures"""
        url = "https://some-random-api.ml/animal/koala"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a koala picture").set_image(
                    url=img_url
                )
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a koala picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(aliases=["birb"], description="Shows random cute bird pictures")
    async def bird(self, ctx):
        """Shows cute bird pictures"""
        url = "https://some-random-api.ml/animal/birb"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        await ctx.send(
            embed=discord.Embed(title="Heres a bird picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute racoon pictures")
    async def racoon(self, ctx):
        """Shows racoon pictures"""
        url = "https://some-random-api.ml/animal/racoon"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a racoon picture").set_image(
                    url=img_url
                )
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a racoon picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute kangaroo pictures")
    async def kangaroo(self, ctx):
        url = "https://some-random-api.ml/animal/kangaroo"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"]
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a kangaroo picture").set_image(
                    url=img_url
                )
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a kangaroo picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command(description="Shows random cute fox pictures")
    async def fox(self, ctx):
        url = "https://randomfox.ca/floof/"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"].replace("\\/", "/")
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a fox picture").set_image(url=img_url)
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a fox picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )

    @commands.command()
    async def car(self, ctx):
        url = "https://dinosaur.ml/random/images/car/"

        async with self.bot.session.get(url) as cs:
            fj = json.loads(await cs.text())
        img_url = fj["link"].replace("\\/", "/")
        if not fj.get("fact"):
            return await ctx.send(
                embed=discord.Embed(title="Heres a car picture").set_image(url=img_url)
            )
        await ctx.send(
            embed=discord.Embed(title="Heres a car picture")
            .set_image(url=img_url)
            .set_footer(text="Fun Fact: " + fj["fact"])
        )


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Animals(bot))
