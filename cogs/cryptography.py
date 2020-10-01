import discord
from discord.ext import commands
import base64 as base64module


class Cryptography(commands.Cog):
    """Encoding and Decoding text releated commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["b64"], description="Encode or decode text to base64")
    async def base64(self, ctx, task, *, text: commands.clean_content):
        if task.strip().lower() == "encode" or task.strip().lower() == "e":
            data = text
            encodedBytes = base64module.b64encode(data.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            await ctx.send(encodedStr)
        elif task.strip().lower() == "decode" or task.strip().lower() == "d":
            data = text
            message_bytes = base64module.b64decode(data)
            message = message_bytes.decode("ascii")
            await ctx.send(message)
        else:
            await ctx.send("Must have either encode or decode / e or d")

    @commands.command(aliases=["bin"], description="Converts text to binary")
    async def binary(self, ctx, number: int):
        await ctx.send(
            embed=discord.Embed(
                title=ctx.author.name,
                description=f"```py\n{bin(number).replace('0b', '')}```",
            )
        )

    @commands.command(aliases=["unbin"], description="Converts binary to text")
    async def unbinary(self, ctx, number: int):
        await ctx.send(
            embed=discord.Embed(
                title=ctx.author.name, description=f"```py\n{int(str(number), 2)}```"
            )
        )


def setup(bot):
    bot.add_cog(Cryptography(bot))
