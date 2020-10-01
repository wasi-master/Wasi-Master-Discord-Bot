import randomcolor
import json
import discord
from discord.ext import commands


class Colors(commands.Cog):
    """Color releated commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["col", "color"], description="Sends info about a color")
    async def colour(self, ctx, color: str):

        async with ctx.typing():
            generated_color = color
            hexcol = generated_color.replace("#", "")
            async with self.bot.session.get(
                f"http://www.thecolorapi.com/id?hex={hexcol}"
            ) as response:
                data = json.loads(await response.text())

            color_name = data.get("name").get("value")
            link = f"http://singlecolorimage.com/get/{hexcol}/1x1"
            thumb = f"http://singlecolorimage.com/get/{hexcol}/100x100"
            rgb = data.get("rgb").get("value")
            hexcol = data.get("hex").get("value")
            hsl = data["hsl"]["value"]
            hsv = data["hsv"]["value"]
            cmyk = data["cmyk"]["value"]
            xyz = data["XYZ"]["value"]
            intcol = int(hexcol.replace("#", ""), 16)

        embed = discord.Embed(
            timestamp=ctx.message.created_at, color=int(hexcol.replace("#", ""), 16)
        )
        embed.set_author(name=color_name)
        embed.set_image(url=link)
        embed.set_thumbnail(url=thumb)
        embed.set_footer(text=f"Made for {ctx.author}")
        embed.add_field(name="Hex", value=hexcol)
        embed.add_field(name="RGB", value=rgb)
        embed.add_field(name="INT", value=intcol)
        embed.add_field(name="HSL", value=hsl)
        embed.add_field(name="HSV", value=hsv)
        embed.add_field(name="CMYK", value=cmyk)
        embed.add_field(name="XYZ", value=xyz)
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["randcolor", "randomcol", "randcol", "randomcolor", "rc"],
        description="Generates a random color",
    )
    async def randomcolour(
        self,
        ctx,
    ):

        async with ctx.typing():
            rand_color = randomcolor.RandomColor()
            generated_color = rand_color.generate()[0]
            hexcol = generated_color.replace("#", "")
            async with self.bot.session.get(
                f"http://www.thecolorapi.com/id?hex={hexcol}"
            ) as response:
                data = json.loads(await response.text())
            color_name = data.get("name").get("value")
            link = f"http://singlecolorimage.com/get/{hexcol}/1x1"
            thumb = f"http://singlecolorimage.com/get/{hexcol}/100x100"
            rgb = data.get("rgb").get("value")
            hexcol = data.get("hex").get("value")
            intcol = int(hexcol.replace("#", ""), 16)
        embed = discord.Embed(timestamp=ctx.message.created_at, color=intcol)
        embed.set_author(name=color_name)
        embed.set_image(url=link)
        embed.set_thumbnail(url=thumb)
        embed.set_footer(text=f"Made for {ctx.author}")
        embed.add_field(name="Hex", value=hexcol)
        embed.add_field(name="RGB", value=rgb)
        embed.add_field(name="INT", value=intcol)
        embed.set_footer(
            text="You can use the color command to get more details about the color"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Colors(bot))
