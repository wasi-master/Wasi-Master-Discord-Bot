import asyncio
import datetime
import json
import re
import urllib

import async_cse
import discord
import requests
import wikipedia as wikimodule
import youtube_dl
import youtube_dl as ytdl
from discord.ext import commands
from discord.ext.commands import BucketType
from pytube import YouTube
from youtubesearchpython.__future__ import VideosSearch

from utils.classes import NoAPIKey
from utils.paginator import Paginator
import humanize
import functools


def convert_sec_to_min(seconds):
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def get_streams(yt: YouTube, *args, **kwargs):
    return enumerate(
        sorted(
            yt.streams.filter(*args, **kwargs),
            key=lambda s: s.filesize_approx,
            reverse=True,
        ),
        1,
    )


class Search(commands.Cog):
    """For searching for things in the world wide web"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wiki", "searchwiki"], description="Searches Wikipedia")
    async def wikipedia(self, ctx, *, search_term):
        async with ctx.typing():
            result = wikimodule.summary(search_term)
            paginator = commands.Paginator(prefix="", suffix="", max_size=750)
            embeds = []
            for line in result.split("\n"):
                paginator.add_line(line)
            for page in paginator.pages:
                embeds.add_field(discord.Embed(title=search_term, description=page))
            menu = Paginator(embeds)
            await menu.start(ctx)

    @commands.command(aliases=["search", "g"], description="Searches Google")
    @commands.cooldown(1, 5, BucketType.user)
    async def google(self, ctx, *, search_term: commands.clean_content):
        try:
            results = await ctx.bot.google_api.search(
                search_term,
                safesearch=not ctx.channel.is_nsfw() if ctx.guild else False,
            )
        except async_cse.search.NoResults:
            return await ctx.send(
                "No search results found. "
                + (
                    "Perhaps, the results were nsfw, go to a nsfw channel and use this command again and see"
                    if (not ctx.channel.is_nsfw() if ctx.guild else False)
                    else ""
                )
            )
        embeds = []
        for result in results:
            embed = discord.Embed(
                title=result.title,
                description=result.description,
                url=result.url,
                color=0x2F3136,
            )
            embed.set_thumbnail(url=result.image_url)
            embeds.append(embed)
        menu = Paginator(embeds)
        await menu.start(ctx)

    @commands.command(
        aliases=["imagesearch", "is", "i"],
        description="Searched Google Images and returns the first image",
    )
    @commands.cooldown(1, 5, BucketType.user)
    async def image(self, ctx, *, search_term: commands.clean_content):
        try:
            results = await ctx.bot.google_api.search(
                search_term,
                safesearch=not ctx.channel.is_nsfw() if ctx.guild else False,
                image_search=True,
            )
        except async_cse.search.NoResults:
            return await ctx.send(
                "No images found. "
                + (
                    "Perhaps, the results were nsfw, go to a nsfw channel and use this command again and see"
                    if (not ctx.channel.is_nsfw() if ctx.guild else False)
                    else ""
                )
            )
        embeds = []
        for result in results:
            embed = discord.Embed(
                title=result.title,
                url=result.url,
                color=0x2F3136,
            )
            embed.set_image(url=result.image_url)
            embeds.append(embed)
        menu = Paginator(embeds)
        await menu.start(ctx)

    # @commands.group(aliases=["dl"], invoke_without_command=False)
    # @commands.cooldown(1, 15, BucketType.user)
    # async def download(self, ctx):
    #     pass

    # @download.command(name="mpeg4", aliases=["mp4"])
    # @commands.cooldown(1, 15, BucketType.user)
    # async def download_mpeg4(self, ctx, url):
    #     yt = YouTube(url)
    #     embed = discord.Embed()
    #     desc = "__Found these formats, which one do you want to download? type the number__\n\n"
    #     get_streams_func = functools.partial(get_streams, yt, file_extension="mp4")
    #     streams = await self.bot.loop.run_in_executor(None, get_streams_func)
    #     streamed_items = [i[1] for i in streams]
    #     for num, stream in enumerate(streamed_items, 1):
    #         if stream.type == "audio":
    #             continue
    #         desc += f"**{num}.**\nFile Extension: `.{stream.mime_type.replace('video/', '')}`\nResolution{stream.resolution}@{stream.fps}\nFile Size: {humanize.naturalsize(stream.filesize, False, True)}\n"
    #     embed.description = desc
    #     await ctx.send(embed=embed)
    #     try:
    #         msg = await self.bot.wait_for(
    #             "message",
    #             check=lambda msg: msg.author == ctx.author
    #             and msg.channel == ctx.channel,
    #             timeout=60,
    #         )
    #     except asyncio.TimeoutError:
    #         return await ctx.reply("Welp, You didn't respond")
    #     else:
    #         if not msg.content.isnumeric():
    #             return
    #         try:
    #             stream = streamed_items[int(msg.content) - 1]
    #             filesize = stream.filesize
    #             await ctx.send(
    #                 embed=discord.Embed(
    #                     title="Download Video",
    #                     description=f"[Click Here]({stream.url}) to download the video. \n Note: the video is `{humanize.naturalsize(stream.filesize, False, True)}`",
    #                 )
    #             )
    #         except IndexError:
    #             return await msg.reply("That number wasn't in the list smh")

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, text):
        """Searches youtube"""
        async with ctx.typing():
            search = VideosSearch(text, limit=10)
            results = (await search.next())["result"]
            if len(results) == 0:
                await ctx.message.reply("No Results")
            embedlist = []
            for video in results:
                if not video["type"] == "video":
                    continue
                embed = discord.Embed(title=video["title"], description=video["link"])
                embed.set_image(url=video["thumbnails"][0]["url"])
                embed.set_author(
                    name=video["channel"]["name"],
                    url=video["channel"]["link"],
                    icon_url=video["channel"]["thumbnails"][0]["url"],
                )
                embed.add_field(
                    name="Published", value=video["publishedTime"], inline=False
                )
                embed.add_field(name="Duration", value=video["duration"], inline=False)
                embed.add_field(
                    name="Views",
                    value=f'{video["viewCount"]["short"]}({video["viewCount"]["text"]})',
                    inline=False,
                )
                embedlist.append(embed)
            pag = Paginator(embedlist)
            await pag.start(ctx)

    @commands.command(aliases=["tenor"], description="Search for a gif")
    async def gif(self, ctx, *, query: str):
        apikey = self.bot.api_keys.get("tenor")
        if not apikey:
            raise NoAPIKey
        lmt = 1
        search_term = query

        async with ctx.typing():
            async with self.bot.session.get(
                "https://api.tenor.com/v1/search?q=%s&key=%s&contentfilter=high&limit=%s"
                % (search_term, apikey, lmt)
            ) as r:
                gifs = json.loads(await r.text())
                gif: str = gifs["results"][0]["media"][0]["gif"]["url"]

        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url=gif)
        embed.add_field(
            name="Link (click to see or long press to copy)",
            value=f"[click here]({gif})",
        )
        embed.set_footer(text=f"Asked by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(
        aliases=[
            "yti",
            "ytinfo",
            "youtubei",
            "videoinfo",
            "youtubevideoinfo",
            "ytvi",
            "vi",
        ],
        description=" See Details about a youtube video",
    )
    async def youtubeinfo(self, ctx, video_url: str):
        ops = {}
        msg = await ctx.send("Loading <a:typing:597589448607399949>")
        with ytdl.YoutubeDL(ops) as ydl:
            infos = ydl.extract_info(video_url, download=False)
        await msg.delete()
        description = infos["description"]
        if len(description) > 400:
            description = description[0:400] + "..."
        embed = discord.Embed(
            title=infos["title"], description=description, color=16711680
        )
        embed.set_author(name=infos["uploader"], url=infos["uploader_url"])
        embed.set_image(url=infos["thumbnails"][-1]["url"])
        embed.add_field(name="View Count", value=f"{infos['view_count']:,}")
        time = datetime.datetime.strptime(infos["upload_date"], "%Y%m%d")
        embed.add_field(name="Uploaded On", value=time.strftime("%d %B, %Y"))
        embed.add_field(name="Duration", value=convert_sec_to_min(infos["duration"]))
        if infos["age_limit"]:
            embed.add_field(
                name="Age Restriction",
                value=f"You must be {infos['age_limit']} or older in order to see this video",
            )
        if infos["categories"]:
            embed.add_field(name="Category", value="\n".join(infos["categories"]))
        if infos["tags"]:
            tags = "".join([f"`{i}`, " for i in infos["tags"]][:-3])
            embed.add_field(name="Tags/Keywords", value=tags)
        if infos["average_rating"]:
            embed.add_field(
                name="Likes", value=str(round(infos["average_rating"] * 20, 2)) + "%"
            )
        embed.add_field(
            name="Video Info",
            value=f"Video Quality: {infos['width']}x{infos['height']}@{infos['fps']}p\nVideo Codec: {infos['vcodec']}\nVideo File Extension: `.{infos['ext']}`",
        )
        embed.add_field(
            name="Audio Info",
            value=f"Audio Bitrate: {infos['abr']}Kbps\nAudio Codec: {infos['acodec']}",
        )
        await ctx.send(embed=embed)


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Search(bot))
