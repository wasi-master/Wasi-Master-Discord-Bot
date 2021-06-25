import datetime
import difflib
import json
from collections import Counter

import discord
import humanize
from discord.ext import commands
from discord.ext.commands import BucketType

from utils.paginator import Paginator


class Server(commands.Cog):
    """Server releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["setprefix"],
        description="Sets a prefix for a server but doesn’t work always :(",
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix: str):
        await self.bot.db.execute(
            """
                    UPDATE guilds
                    SET prefix = $2
                    WHERE id = $1;
                    """,
            ctx.guild.id,
            prefix,
        )
        await ctx.send(f"prefix set to `{prefix}`")

    @commands.command(
        aliases=["guildinfo", "si", "gi"], description="See details of a server"
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild
        owner = self.bot.get_user(guild.owner_id)
        features = ""
        for i in guild.features:
            features += "\n" + i.title().replace("_", " ")
        embed = discord.Embed(
            title=f"Server Information for {guild.name}",
            description=f"Name: {guild.name}\nCreated At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')}  ({humanize.precisedelta(datetime.datetime.utcnow() - guild.created_at)})\nID: {guild.id}\nOwner: {owner}\nIcon Url: [click here]({guild.icon_url})\nRegion: {str(guild.region)}\nVerification Level: {str(guild.verification_level)}\nTotal Members: {len(guild.members)}\nBots: {len([member for member in ctx.guild.members if member.bot])}\nHumans: {len(ctx.guild.members) - len([member for member in ctx.guild.members if member.bot])}\n<:boost4:724328585137225789> Boost Level: {guild.premium_tier}\n<:boost1:724328584893956168> Boosts: {guild.premium_subscription_count}\n<:boost1:724328584893956168> Boosters: {len(guild.premium_subscribers)}\nTotal Channels: {len(guild.channels)}\n<:textchannel:724637677395116072> Text Channels: {len(guild.text_channels)}\n<:voicechannel:724637677130875001> Voice Channels: {len(guild.voice_channels)}\n<:category:724330131421659206> Categories: {len(guild.categories)}\nRoles: {len(guild.roles)}\n:slight_smile: Emojis: {len(guild.emojis)}/{guild.emoji_limit}\nUpload Limit: {round(guild.filesize_limit / 1048576)} Megabytes (MB)\n\n**Features:** {features}",
        )
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(description="See all the boosters of this server")
    async def boosters(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people_who_boosted = sorted(
            ctx.guild.premium_subscribers, key=lambda member: member.joined_at
        )
        for i in people_who_boosted:
            peoples.add_line(f"{i.name} (ID: {i.id})")
        for page in peoples.pages:
            embeds.append(
                discord.Embed(
                    title=f"{len(people_who_boosted)} Boosters", description=page
                )
            )
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        description="See all the members of this server first",
        aliases=["memlist", "allmembers", "am", "servermembers", "sm", "memberslist"],
    )
    async def memberlist(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people = sorted(
            ctx.guild.members, key=lambda member: member.top_role, reverse=True
        )
        for n, i in enumerate(people, 1):

            peoples.add_line(f"{n}. {i.name} (ID: {i.id} TOP_ROLE: {i.top_role.name})")
        for page in peoples.pages:
            embeds.append(
                discord.Embed(title=f"{len(people)} Members", description=page)
            )
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        description="See all the members of this server first",
        aliases=["fj", "whojoinedfirst", "wjf", "firstmembers", "fmem", "oldmembers"],
    )
    async def firstjoins(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people = sorted(ctx.guild.members, key=lambda member: member.joined_at)
        for n, i in enumerate(people, 1):
            peoples.add_line(f"{n}. {i.name} (ID: {i.id})")
        for page in peoples.pages:
            embeds.append(
                discord.Embed(title=f"{len(people)} Members", description=page)
            )
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(
        description="See all the members of this server first",
        aliases=["nj", "whojoinedlast", "wjl", "lastmembers", "lm", "newmembers"],
    )
    async def newjoins(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people = sorted(
            ctx.guild.members, key=lambda member: member.joined_at, reverse=True
        )
        for n, i in enumerate(people, 1):
            peoples.add_line(f"{n}. {i.name} (ID: {i.id})")
        for page in peoples.pages:
            embeds.append(
                discord.Embed(title=f"{len(people)} Members", description=page)
            )
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(description="See all the members of this server first")
    async def bots(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people = filter(lambda member: member.bot, ctx.guild.members)
        people = sorted(people, key=lambda member: member.joined_at)
        for n, i in enumerate(people, 1):
            peoples.add_line(f"{n}. {i.name} (ID: {i.id})")
        for page in peoples.pages:
            embeds.append(discord.Embed(title=f"{len(people)} Bots", description=page))
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(description="See all the members of this server first")
    async def humans(self, ctx):
        peoples = commands.Paginator(max_size=500)
        embeds = []
        people = filter(lambda member: not member.bot, ctx.guild.members)
        people = sorted(people, key=lambda member: member.joined_at)
        for n, i in enumerate(people, 1):
            peoples.add_line(f"{n}. {i.name} (ID: {i.id})")
        for page in peoples.pages:
            embeds.append(
                discord.Embed(title=f"{len(people)} Humans", description=page)
            )
        paginator = Paginator(embeds)
        await paginator.start(ctx)

    @commands.command(description="Adds a emoji from https://emoji.gg to your server")
    @commands.has_permissions(manage_emojis=True)
    async def emoji(self, ctx, task: str, emoji_name: str):
        # TODO: Add subcommands
        if len(ctx.bot.emoji_list) == 0:
            msg1 = await ctx.send(f"Loading emojis <a:typing:597589448607399949>")

            async with self.bot.session.get("https://emoji.gg/api") as resp:
                ctx.bot.emoji_list = json.loads(await resp.text())
                fj = ctx.bot.emoji_list
            await msg1.delete()
            ctx.bot.emoji_list_str = [i["title"].lower() for i in fj]

        emoji_from_api = None
        if task == "view" or task == "add":
            for i in ctx.bot.emoji_list:
                if i["title"].lower() == emoji_name.lower():
                    emoji_from_api = i
                    break
                else:
                    continue
            if emoji_from_api is None:
                embed = discord.Embed(
                    title="Emoji not found",
                    description=f"Did you mean any of these?\n{', '.join(difflib.get_close_matches(emoji_name.lower(), ctx.bot.emoji_list_str, n=5, cutoff=0.2))}",
                    color=0x2F3136,
                )
                return await ctx.send(embed=embed)
            else:
                if task == "view":
                    embed = discord.Embed(
                        title=emoji_name,
                        url=emoji_from_api["image"].replace(
                            "discordemoji.com", "emoji.gg"
                        ),
                        color=0x2F3136,
                    )
                    embed.add_field(name="Author", value=emoji_from_api["submitted_by"])
                    # await ctx.send(f"""```{emoji_from_api['image']].replace("discordemoji.com".send("emoji.gg")}```""")
                    embed.set_thumbnail(
                        url=emoji_from_api["image"].replace(
                            "discordemoji.com", "emoji.gg"
                        )
                    )
                    embed.set_image(
                        url=emoji_from_api["image"].replace(
                            "discordemoji.com", "emoji.gg"
                        )
                    )
                    embed.set_footer(
                        text="Because of a discord bug, we may bot be able to show the emoji as a big image, so here is the small version",
                        icon_url=emoji_from_api["image"],
                    )
                    await ctx.send(embed=embed)
                elif task == "add":
                    if not ctx.author.guild_permissions.manage_emojis:
                        return await ctx.send(
                            "You don't have the Manage Emojis permission to add a emoji to this server"
                        )

                    async with self.bot.session.get(emoji_from_api["image"]) as r:
                        try:
                            emoji = await ctx.guild.create_custom_emoji(
                                name=emoji_name, image=await r.read()
                            )
                            await ctx.send(f"Emoji {emoji} added succesfully :)")
                        except discord.Forbidden:
                            await ctx.send(
                                "Unable to add emoji, check my permissions and try again"
                            )
        else:
            return await ctx.send("Invalid Task.send( task should be add or view")

    @commands.command(
        aliases=["il", "it", "invitelogger"], description="Tracks Invites"
    )
    @commands.has_permissions(manage_guild=True)
    async def invitetracker(self, ctx, log_channel: discord.TextChannel):
        channel = log_channel.id
        await self.bot.db.execute(
            """
                    INSERT INTO channel (guild_id, channel_id)
                    VALUES ($1, $2)
                    """,
            ctx.guild.id,
            channel.id,
        )

    @commands.command(
        aliases=["flags"], description="Shows how many badges are in this guild"
    )
    @commands.cooldown(1, 60, BucketType.user)
    async def badges(self, ctx, server: discord.Guild = None):
        count = Counter()
        guild = server or ctx.guild
        for member in guild.members:
            for flag in member.public_flags.all():
                count[flag.name] += 1

        msg = ""
        count = dict(reversed(sorted(count.items(), key=lambda item: item[1])))
        for k, v in count.items():
            msg += f'{k.title().replace("_", " ")}: **{v}**\n\n'

        embed = discord.Embed()
        embed.set_author(name=f"Badge Count in {guild.name}", icon_url=guild.icon_url)
        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Server(bot))
