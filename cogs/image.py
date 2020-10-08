import discord
import json
from discord.ext import commands

from typing import Union
from discord.ext.commands import BucketType

class Image(commands.Cog):
    """Image releated commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Invert your or another users profile picture")
    async def invert(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/invert?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Blur your or another users profile picture")
    async def blur(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/blur?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(
        aliases=["b&w", "blackandwhite"],
        description="Convert to Black And White your or another users profile picture",
    )
    async def bw(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/b&w?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Pixelate your or another users profile picture")
    async def pixelate(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/pixelate?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(
        description="See a gay version of your or another users profile picture"
    )
    async def gay(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/gay?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Generates a minecraft style achievement image")
    async def achievement(self, ctx, text: commands.Greedy[str], icon: int=None):
        image = await (
            await self.bot.alex_api.achievement(text=text, icon=icon)
        ).read()  # BytesIO
        await ctx.send(
            f"Rendered by {ctx.author}",
            file=discord.File(image, filename="achievement.png"),
        )

    @commands.command(description='Generates a "Worse than hitler" image')
    async def hitler(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/hitler", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(
                title=f"{member.name} is Worse Than Hitler", color=0x2F3136
            )
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(description="Tweets a text")
    async def tweet(self, ctx, member: discord.Member = None, *, text):
        member = member or ctx.message.author
        username = member.name

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
            "name": username,
            "text": text,
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/tweet", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(
                title=f"{member.name} Posted a new tweet", color=0x2F3136
            )
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(description="Generates a wanted poster")
    async def wanted(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/wanted", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(title=f"{member.name} Wanted", color=0x2F3136)
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(
        aliases=["upscaled"], description="Upscales a users profile picture"
    )
    @commands.cooldown(1, 60, type=BucketType.user)
    async def upscale(self, ctx, scale_type, *, member: discord.Member = None):
        member = member or ctx.author
        if scale_type.lower() == "anime":
            url = "https://api.deepai.org/api/waifu2x"
        elif scale_type.lower() == "normal":
            url = "https://api.deepai.org/api/torch-srgan"
        else:
            await ctx.send("Invalid Format")

        message = await ctx.send("May take up to 15 seconds, Wait till then")
        async with self.bot.session.post(
            url,
            data={
                "image": str(member.avatar_url),
            },
            headers={"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"},
        ) as resp:
            fj = json.loads(await resp.text())
            url = fj["output_url"]

        await message.delete()
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=f"{member.name}'s Profile Picture Upscaled")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Image(bot))
