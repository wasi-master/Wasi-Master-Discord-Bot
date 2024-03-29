import asyncio
import datetime
import json
import os
import random
import shutil
from zipfile import ZipFile

import discord
import humanize
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands import BucketType

from utils.paginator import Paginator
import base64


def get_p(percent: int):
    total = 15
    percent = percent * 0.15
    rn = round(percent / 4)
    body = "☐" * total
    li = list(body)

    for i, elem in enumerate(li[:rn]):
        li[i] = "■"

    ku = "".join(li)
    return f"{ku}"


class Utility(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command(aliases=["copyguild", "servercopy", "guildcopy"])
    # @bot_has_permissions()
    async def copyserver(self, ctx, copy_to: int):
        if (guild := self.bot.get_guild(copy_to)):
            if not ctx.author in guild.members:
                return await ctx.send("You are not in that server")
            if not ctx.author.id == guild.owner_id:
                return await ctx.send("You are in that server but you do not own that server")
            if not ctx.author.id == ctx.guild.owner_id:
                return await ctx.send("You do own that server but do not own this server")
            m = await ctx.send("Work Starting")
            await asyncio.sleep(3)
            await m.edit(content="Deleting all channels of that server")
            for channel in guild.channels:
                await channel.delete(reason=f"Copying From {ctx.guild.name} (ID: {ctx.guild.id})")
            await m.edit(content="Creating all channels from this server to that server")
            missed = {}
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        if channel.categoryis None:
                            await guild.create_text_channel(name=channel.name, overwrites=overwrites)
                    except Exception, e:
                        missed[channel] = str(e)
                elif isinstance(channel, discord.VoiceChannel):
                    try:
                        # TODO: write code...
                    except Exception, e:
                        missed[chanel] = str(e)
                elif isinstance(channel, discord.CategoryChannel):
                    try:
                        # TODO: write code...
                    except Exception, e:
                        missed[channel] = str(e)
                else:
                    missed[channel] = "Can't copy this type of channel"
        else:
            await ctx.send("The bot is not in that server")
    """

    @commands.command(aliases=["redirect", "unshort", "us"])
    async def unshorten(self, ctx, url: str):
        async with self.bot.session.get(url, allow_redirects=True) as cs:
            if cs.url == url:
                await ctx.send("The url didn't redirect me to any website :(")
                return
            result_url = cs.url
        embed = discord.Embed(
            title=f"{url} redirected me to",
            description=result_url,
            color=discord.Colour.red(),
        )
        embed.set_footer(
            icon_url=ctx.author.avatar_url,
            text="Command executed by " + str(ctx.author),
        )
        await ctx.send(embed=embed)

    @commands.command(name="id", aliases=["snowflake", "snf"])
    async def snowflake(self, ctx, *, snowflake_id: str = None):
        """Show the date a snowflake ID was created"""

        snowflake_id = int(snowflake_id)
        timestamp = (
            (snowflake_id >> 22) + 1420070400000
        ) / 1000  # python uses seconds not milliseconds
        cdate = datetime.datetime.utcfromtimestamp(timestamp)
        msg = "ID created {}".format(cdate.strftime("%A, %B %d %Y at %H:%M:%S UTC"))
        return await ctx.send(msg)

    @commands.command(aliases=["snowflakeinfo", "snfi", "idi"])
    async def idinfo(self, ctx, *, snowflake_id: str = None):
        """Show all available data about a snowflake ID"""
        snowflake_id = int(snowflake_id)
        timestamp = (
            (snowflake_id >> 22) + 1420070400000
        ) / 1000  # python uses seconds not milliseconds
        iwid = (snowflake_id & 0x3E0000) >> 17
        ipid = (snowflake_id & 0x1F000) >> 12
        icount = snowflake_id & 0xFFF

        cdate = datetime.datetime.utcfromtimestamp(timestamp)
        fdate = cdate.strftime("%A, %B %d %Y at %H:%M:%S UTC")

        embed = discord.Embed(title=snowflake_id, description="Discord snowflake ID")
        embed.add_field(name="Date created", value=fdate)
        embed.add_field(
            name="Internal worker/process", value="{}/{}".format(iwid, ipid)
        )
        embed.add_field(name="Internal counter", value=icount)
        embed.add_field(name="As user ping", value="<@{}>".format(snowflake_id))
        embed.add_field(name="As channel ping", value="<#{}>".format(snowflake_id))
        embed.add_field(name="As role ping", value="<@&{}>".format(snowflake_id))
        embed.add_field(name="As custom emote", value="<:test:{}>".format(snowflake_id))
        embed.add_field(
            name="As animated emote", value="<a:test:{}>".format(snowflake_id)
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["pt"])
    async def parsetoken(self, ctx, token):
        user, time, _ = token.split(".")
        user_id = base64.b64decode(user).decode("utf-8")
        time = datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=int.from_bytes(base64.standard_b64decode(time + "b=="), "big")
            + 1293840000
            - 33349320000
        )
        user = await self.bot.fetch_user(user_id)
        embed = discord.Embed(title=(user), description=f"ID: `{user.id}`")
        embed.set_thumbnail(url=str(user.avatar_url))
        embed.add_field(name="Type", value="Bot Token" if user.bot else "Account Token")
        embed.add_field(
            name="Token Creation",
            value=f'{time.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - time)})',
            inline=False,
        )
        embed.add_field(
            name="Account Creation",
            value=f'{user.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - user.created_at)})',
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def embed(self, ctx, *, embed_json):
        embed_json = embed_json.lstrip("```json\n").strip("```").strip()
        try:
            embed_dict = json.loads(embed_json)
        except Exception as e:
            embed = discord.Embed(
                title="Invalid JSON",
                color=0xFF0000,
                description=f"```json\n{embed_json}```",
            )
            embed.set_footer(text=str(e))
            await ctx.send(embed=embed)
            return
        if (col := embed_dict.get("color", embed_dict.get("colour"))) :
            if isinstance(col, str):
                converter = commands.ColourConverter()
                embed_dict["color"] = (await converter.convert(ctx, col)).value
        try:
            emby = discord.Embed.from_dict(embed_dict)
        except Exception as e:
            return await ctx.send("Error occured: " + str(e))
        try:
            if ctx.author.permissions_in(ctx.channel).manage_messages:
                await ctx.send(embed=emby)
            else:
                await ctx.send(f"Sent by {ctx.author}", embed=emby)
        except Exception as e:
            if hasattr(e, "code"):
                if e.code == 50006:
                    return await ctx.send("Invalid embed")
                elif e.code == 50035:
                    return await ctx.send("Invalid Field: " + str(e))
                else:
                    return await ctx.send("Error occured: " + str(e))
            else:
                return await ctx.send(
                    "Error Occured.send( check if everything was right"
                )

    @commands.command(
        aliases=["link", "message", "ml"],
        description="Generates a link to a message (usefull in mobile)",
    )
    async def messagelink(
        self, ctx, message: int = None, channel: discord.TextChannel = None
    ):
        channel = channel or ctx.channel
        if message:
            message = await channel.fetch_message(message)
        else:
            message = ctx.message
        await ctx.send(message.jump_url)

    @commands.command(description="Sends you stuff")
    async def dm(self, ctx, *, message_to_dm: str):
        await ctx.author.send(message_to_dm)

    @commands.command(aliases=["members"], description="Get who are in a certain role")
    async def getusers(self, ctx, *, role: discord.Role):
        if not role.members:
            return await ctx.send("No Members")
        paginator = commands.Paginator(prefix="", suffix="")
        embeds = []
        for member in role.members:
            paginator.add_line(
                f"{member}{f'({member.display_name})' if member.nick else ''}"
            )
        for page in paginator.pages:
            embeds.append(
                discord.Embed(
                    description=page,
                    color=0x2F3136 if role.color == 0x000000 else role.color,
                )
            )
        menu = Paginator(embeds)
        menu.start(ctx)

    @commands.command()
    async def tos(self, ctx, *, term: str):
        """Searches discord terms of service"""
        await ctx.send(
            f"Go to <https://discord.com/terms>. Press Ctrl+F and write {term}"
        )

    @commands.command(
        description="Shows a `<name:id> for standard emojis and `<a:name:id>` for animated emojis`",
        usage="emoji `<name>`\n\nemoji hyper_pinged",
    )
    async def emojiid(self, ctx, *, emoji: discord.Emoji):
        await ctx.send(f"```{emoji}```")

    @commands.command(description="Rolls a dice and gives you a number")
    async def dice(self, ctx):
        msg = await ctx.send(":game_die: Rolling Dice <a:typing:597589448607399949>")

        dice_emoji = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]
        dice = random.randint(0, 5)
        await asyncio.sleep(2)
        await msg.edit(content=f"Your number is  {dice_emoji[dice]}")

    @commands.command(
        aliases=["ph", "catch"],
        description="Tells you which pokemon it is that has been spawned by a bot",
    )
    async def pokemonhack(self, ctx, channel: discord.TextChannel = None):
        #  msg1 = await ctx.send(f"Finding <a:typing:597589448607399949>")
        channel = channel or ctx.channel
        url = None
        img_url = None
        raw_result = None
        async for message in channel.history(
            limit=8, oldest_first=False, before=ctx.message
        ):
            if not message.author == ctx.guild.me:
                if message.embeds:
                    embed = message.embeds[0]
                    if not embed.image:
                        pass
                    else:
                        img_url = embed.image.url
                else:
                    pass
            else:
                pass
        if not img_url:
            return await ctx.send("Message containing a pokemon Not Found")
        url = (
            f"https://www.google.com/searchbyimage?hl=en-US&image_url={img_url}&start=0"
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        }
        msg1 = await ctx.send(f"Searching <a:typing:597589448607399949>")
        async with self.bot.session.get(
            url, headers=headers, allow_redirects=True
        ) as r:
            q = await r.read()
        await msg1.edit(content=f"Getting the result <a:typing:597589448607399949>")
        result = ""
        wrong = {
            "bonsai": "bonsly",
            "golet": "golette",
            "ポケモン ホルビー": "diggersby",
            "golett  go": " golett",
            "excalibur": "escavalier",
            "flower": "ralts",
            "tranquil": "tranquill",
            "shutterbug": "scatterbug",
            "fletching": "fletchling",
            "oricorio baile style": "oricorio",
            "sword and shield coal": "rolycoly",
            "psychic type cute physic pokemon": "skitty",
        }
        soup = BeautifulSoup(q.decode("utf-8"), "html.parser")
        for best_guess in soup.findAll("a", attrs={"class": "fKDtNb"}):
            #  await ctx.send(best_guess)
            if not best_guess.get_text().replace("pokemon", "").strip().isdigit():
                raw_result = best_guess.get_text()
                result = (
                    best_guess.get_text()
                    .lower()
                    .replace("pokemon go", "")
                    .replace("pokemon", "")
                    .replace("png", "")
                    .replace("evolution", "")
                    .replace("shiny", "")
                    .replace("pokedex", "")
                    .replace("pokémon", "")
                    .strip()
                )
                if result in wrong:
                    result = wrong[result]
                break
            else:
                continue
        emby = discord.Embed(description=f"**p!catch {result}**", color=0x2F3136)
        emby.set_author(name=result)
        emby.set_image(url=img_url)
        emby.set_footer(
            text=f"Long press the p!catch {result} on mobile to copy quickly\n\nCommand Invoked by {ctx.author}\nRaw Result: {raw_result}",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=emby)
        await msg1.delete()
        #  kek = result.split(' ')
        #  await ctx.send(result[0])

    @commands.command(
        aliases=["sae", "getallemojis", "gae"],
        description="Saves all emojis to a zip file and sends the zip file",
    )
    @commands.max_concurrency(1, BucketType.channel, wait=True)
    async def saveallemojis(self, ctx):
        guild = ctx.guild
        gn = guild.name
        if os.path.isdir(gn):
            shutil.rmtree(gn)
        os.makedirs(gn)
        emojis = guild.emojis
        time_required = 0.25 * len(emojis)
        embed = discord.Embed(
            title="Saving <a:typing:597589448607399949>",
            description=f"This should take {round(time_required, 2)} seconds if all things go right",
        )
        msg = await ctx.send(embed=embed)
        done = 0
        embed.add_field(
            name="Progress",
            value=f"{done} {get_p(done / (len(emojis) / 100))} {len(emojis)}",
        )
        for item in emojis:
            done += 1
            name = item.name
            ext = "." + str(item.url).split(".")[-1]
            await item.url.save(gn + "/" + name + ext)
            if done // 5 == 0:
                time_required = 0.25 * (len(emojis) - done)
                embed = discord.Embed(
                    title="Saving <a:typing:597589448607399949>",
                    description=f"This should take {round(time_required, 2)} more seconds if all things go right",
                )
                embed.add_field(
                    name="Progress",
                    value=f"{done} {get_p(done / (len(emojis) / 100))} {len(emojis)}",
                )
                await msg.edit(embed=embed)
        embed = discord.Embed(
            title="Zipping <a:typing:597589448607399949>",
            description=f"This should take a few more seconds if all things go right",
        )
        await msg.edit(embed=embed)

        def get_all_file_paths(directory):
            file_paths = []
            for root, directories, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
            return file_paths

        directory = "./" + gn
        file_paths = get_all_file_paths(directory)
        filename = gn + "_emojis" + ".zip"
        with ZipFile(filename, "w") as zip:
            for file in file_paths:
                zip.write(file)
        size = os.path.getsize(filename)
        size = humanize.naturalsize(size, gnu=True)
        size = size.replace("K", "kB").replace("M", "MB")
        await msg.delete()
        embed = discord.Embed(
            title="Completed",
            description=f"Task finished\n\nMade a zip file containing **{len(emojis)}** emojis in a **{size}** zip file",
            color=discord.Colour.green(),
        )
        embed.add_field(name="Original File size", value=size)
        embed.set_footer(
            text="Discord may show a different size since it stores some more metadata about the file in their database"
        )
        await ctx.send(embed=embed.send(file=discord.File(filename)))
        shutil.rmtree(gn)


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Utility(bot))
