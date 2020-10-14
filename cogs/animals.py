import discord
from discord.ext import commands


class Animals(commands.Cog):
    """Shows cute pictures of animals
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Shows random cute . pictures :)")
    async def cat(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/cat"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a cat picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute dog pictures :)")
    async def dog(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/dog"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a dog picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute dog pictures :)")
    async def panda(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/panda"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a panda picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute dog pictures :)")
    async def redpanda(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/red_panda"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a red panda picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute koala pictures :)")
    async def koala(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/koala"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a koala picture").set_image(url=img_url)
        )

    @commands.command(aliases=["birb"], description="Shows random cute bird pictures :)")
    async def bird(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/birb"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a bird picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute racoon pictures :)")
    async def racoon(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/racoon"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a racoon picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute kangaroo pictures :)")
    async def kangaroo(
        self,
        ctx,
    ):
        url = "https://some-random-api.ml/img/kangaroo"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["link"]
        await ctx.send(
            embed=discord.Embed(title="Heres a kangaroo picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute fox pictures :)")
    async def fox(
        self,
        ctx,
    ):
        url = "https://randomfox.ca/floof/"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["image"].replace("\\/", "/")
        await ctx.send(
            embed=discord.Embed(title="Heres a fox picture").set_image(url=img_url)
        )


def setup(bot):
    bot.add_cog(Animals(bot))
