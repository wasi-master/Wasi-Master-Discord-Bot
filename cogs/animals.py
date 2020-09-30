import discord
from discord.ext import commands


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Shows random cute . pictures :)")
    async def cat(
        self,
        ctx,
    ):
        url = "https://api.thecatapi.com/v1/images/search"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj[0]["url"]
        await ctx.send(
            embed=discord.Embed(title="Heres a cat picture").set_image(url=img_url)
        )

    @commands.command(description="Shows random cute dog pictures :)")
    async def dog(
        self,
        ctx,
    ):
        url = "https://dog.ceo/api/breeds/image/random"

        async with self.bot.session.get(url) as cs:
            fj = await cs.json()
        img_url = fj["message"].replace("\\/", "/")
        await ctx.send(
            embed=discord.Embed(title="Heres a dog picture").set_image(url=img_url)
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
