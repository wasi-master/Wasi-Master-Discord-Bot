import discord
import re
import datetime
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
import humanize
from typing import Union
from discord.ext.commands.cooldowns import BucketType

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ci", "chi"], description=" See info about a channel")
    async def channelinfo(
        self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel] = None
    ):
        channel = channel or ctx.channel
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=f"Channel Information for {channel.name}")
        embed.add_field(
            name="Created at",
            value=f'{channel.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - channel.created_at)} old)',
        )
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(
            name="Position", value=f"{channel.position}/{len(ctx.guild.text_channels)}"
        )
        embed.add_field(name="Category", value=channel.category.name)
        if not channel.topic is None:
            embed.add_field(name="Topic", value=channel.topic)
        if not channel.slowmode_delay is None:
            embed.add_field(
                name="Slowmode",
                value=f"{channel.slowmode_delay} seconds ({humanize.naturaldelta(datetime.timedelta(seconds=int(channel.slowmode_delay)))})",
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=["ri", "rlinf"], description=" See info about a role")
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            return await ctx.send(
                "Please specify (mention or write the name) of a role"
            )
        embed = discord.Embed(colour=role.colour.value)
        embed.set_author(name=f"Role Information for {role.name}")
        embed.add_field(
            name="Created at",
            value=f"{role.created_at.strftime('%a, %d %B %Y, %H:%M:%S')}  ({humanize.precisedelta(datetime.datetime.utcnow() - role.created_at)}",
        )
        embed.add_field(name="ID", value=role.id)
        embed.add_field(
            name="Position",
            value=f"{len(ctx.guild.roles) - role.position}/{len(ctx.guild.roles)}",
        )
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(
            name="Role Color",
            value=f"INT: {role.color.value}\nHEX: {'#%02x%02x%02x' % role.color.to_rgb()}\nRGB: rgb{role.color.to_rgb()}",
        )
        if role.hoist:
            embed.add_field(name="Displayed Separately?", value="Yes")
        else:
            embed.add_field(name="Displayed Separately?", value="No")
        if role.mentionable:
            embed.add_field(name="Mentionable", value="Yes")
        else:
            embed.add_field(name="Mentionable", value="No")
        await ctx.send(embed=embed)

    @commands.command(
        description="Shows info about a emoji", aliases=["ei", "emoteinfo"]
    )
    async def emojiinfo(self, ctx, emoji: discord.Emoji):
        embed = discord.Embed(title=emoji.name, description="\\" + str(emoji))
        embed.set_thumbnail(url=emoji.url)
        embed.set_image(url=emoji.url)
        embed.add_field(name="ID", value=emoji.id)
        if not emoji.user is None:
            embed.add_field(name="Added by", value=emoji.user)
        embed.add_field(name="Server", value=emoji.guild)
        embed.add_field(
            name="Created at",
            value=f'{emoji.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - emoji.created_at)})',
        )
        embed.add_field(name="URL", value=f"[Click Here]({emoji.url})")
        await ctx.send(embed=embed)

    @commands.command(
        description="Shows info about a file extension", aliases=["fe", "fi"]
    )
    @commands.cooldown(1, 10, BucketType.user)
    async def fileinfo(self, ctx, file_extension: str):
        msg = await ctx.send("Searching <a:typing:597589448607399949>")
        data = requests.get(f"https://fileinfo.com/extension/{file_extension}").text
        await msg.edit(content="Loading <a:typing:597589448607399949>")
        soup = BeautifulSoup(data, "lxml")

        filename = soup.find_all("h2")[0].text.replace("File Type", "")

        developer = soup.find_all("table")[0].find_all("td")[1].text

        fileType = soup.find_all("a")[10].text

        fileFormat = soup.find_all("a")[11].text

        whatIsIt = soup.find_all("p")[0].text

        moreInfo = soup.find_all("p")[1].text

        embed = discord.Embed(title=filename, description=whatIsIt)
        if not developer == "N/A" and len(developer) != 0:
            embed.add_field(name="Developed by", value=developer)
        if not fileType == "N/A" and len(fileType) != 0:
            embed.add_field(name="File Type", value=fileType)
        if not fileFormat == "N/A" and len(fileFormat) != 0:
            embed.add_field(name="File Format", value=fileFormat)
        if not moreInfo == "N/A" and len(moreInfo) != 0:
            embed.add_field(name="More Info", value=moreInfo)
        await ctx.send(embed=embed)
        await msg.delete()


def setup(bot):
    bot.add_cog(Information(bot))
