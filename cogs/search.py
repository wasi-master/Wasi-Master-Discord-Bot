import discord
import youtube_dl as ytdl
import datetime
import json, urllib, requests, asyncio
from discord.ext import commands
import wikipedia as wikimodule
import re

from discord.ext.commands import BucketType

def convert_sec_to_min(seconds):
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


class Search(commands.Cog):
    """For searching for things in the worls wide web
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wiki", "searchwiki"], description="Searches Wikipedia")
    async def wikipedia(self, ctx, *, search_term):
        async with ctx.typing():
            result = wikimodule.summary(search_term)
            if len(result) < 1997:
                await ctx.send(result)
            else:
                await ctx.send(result[0:2000])

    @commands.command(aliases=["search", "g"], description="Searches Google")
    @commands.cooldown(1, 5, BucketType.user)
    async def google(self, ctx, *, search_term: commands.clean_content):
        num = 0
        results = await ctx.bot.google_api.search(
            search_term, safesearch=not ctx.channel.is_nsfw()
        )
        result = results[num]
        embed = discord.Embed(
            title=result.title,
            description=result.description,
            url=result.url,
            color=0x2F3136,
        )
        embed.set_thumbnail(url=result.image_url)
        embed.set_footer(text=f"Page {num + 1}/{len(results)}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("\u25c0\ufe0f")
        await message.add_reaction("\u23f9\ufe0f")
        await message.add_reaction("\u25b6\ufe0f")
        while True:

            def check(reaction, user):
                return (
                    user.id == ctx.author.id
                    and reaction.message.channel.id == ctx.channel.id
                )

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=120
                )
            except asyncio.TimeoutError:
                embed.set_footer(icon_url=str(ctx.author.avatar_url), text="Timed out")
                await message.edit(embed=embed)
                try:
                    return await message.clear_reactions()
                except:
                    await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                    await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                    await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                    break
                    return
            else:
                if reaction.emoji == "\u25c0\ufe0f":
                    try:
                        message.remove_reaction("\u25c0\ufe0f", ctx.author)
                    except discord.Forbidden:
                        pass
                    num -= 1
                    try:
                        result = results[num]
                    except IndexError:
                        pass
                    embed = discord.Embed(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        color=0x2F3136,
                    )
                    embed.set_thumbnail(url=result.image_url)
                    embed.set_footer(text=f"Page {num + 1}/{len(results)}")
                    await message.edit(embed=embed)
                elif reaction.emoji == "\u25b6\ufe0f":
                    try:
                        await message.remove_reaction("\u25b6\ufe0f", ctx.author)
                    except discord.Forbidden:
                        pass
                    num += 1
                    try:
                        result = results[num]
                    except IndexError:
                        pass
                    embed = discord.Embed(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        color=0x2F3136,
                    )
                    embed.set_thumbnail(url=result.image_url)
                    embed.set_footer(text=f"Page {num + 1}/{len(results)}")
                    await message.edit(embed=embed)
                elif reaction.emoji == "\u23f9\ufe0f":
                    embed = discord.Embed(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        color=0x2F3136,
                    )
                    embed.set_thumbnail(url=result.image_url)
                    #  embed.set_footer(text=f"Page {num+1}/{len(results)}")
                    await message.edit(embed=embed)
                    try:
                        return await message.clear_reactions()
                    except:
                        await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                        break
                        return
                else:
                    pass

    @commands.command(
        aliases=["imagesearch", "is", "i"],
        description="Searched Google Images and returns the first image",
    )
    @commands.cooldown(1, 5, BucketType.user)
    async def image(self, ctx, *, search_term: commands.clean_content):
        num = 0
        results = await ctx.bot.google_api.search(
            search_term, safesearch=not ctx.channel.is_nsfw(), image_search=True
        )
        result = results[num]
        embed = discord.Embed(title=result.title, url=result.url, color=0x2F3136)
        embed.set_image(url=result.image_url)
        embed.set_footer(text=f"Page {num + 1}/{len(results)}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("\u25c0\ufe0f")
        await message.add_reaction("\u23f9\ufe0f")
        await message.add_reaction("\u25b6\ufe0f")
        while True:

            def check(reaction, user):
                return (
                    user.id == ctx.author.id
                    and reaction.message.channel.id == ctx.channel.id
                )

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=120
                )
            except asyncio.TimeoutError:
                embed.set_footer(icon_url=str(ctx.author.avatar_url), text="Timed out")
                await message.edit(embed=embed)
                try:
                    return await message.clear_reactions()
                except:
                    await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                    await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                    await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                    break
                    return
            else:
                if reaction.emoji == "\u25c0\ufe0f":
                    try:
                        await message.remove_reaction("\u25c0\ufe0f", ctx.author)
                    except discord.Forbidden:
                        pass
                    num -= 1
                    try:
                        result = results[num]
                    except IndexError:
                        pass
                    embed = discord.Embed(
                        title=result.title, url=result.url, color=0x2F3136
                    )
                    embed.set_image(url=result.image_url)
                    embed.set_footer(text=f"Page {num + 1}/{len(results)}")
                    await message.edit(embed=embed)
                elif reaction.emoji == "\u25b6\ufe0f":
                    try:
                        message.remove_reaction("\u25b6\ufe0f", ctx.author)
                    except discord.Forbidden:
                        pass
                    num += 1
                    try:
                        result = results[num]
                    except IndexError:
                        pass
                    embed = discord.Embed(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        color=0x2F3136,
                    )
                    embed.set_image(url=result.image_url)
                    embed.set_footer(text=f"Page {num + 1}/{len(results)}")
                    await message.edit(embed=embed)
                elif reaction.emoji == "\u23f9\ufe0f":
                    embed = discord.Embed(
                        title=result.title, url=result.url, color=0x2F3136
                    )
                    embed.set_image(url=result.image_url)
                    #  embed.set_footer(text=f"Page {num+1}/{len(results)}")
                    await message.edit(embed=embed)
                    try:
                        return await message.clear_reactions()
                    except:
                        await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                        break
                        return
                else:
                    pass

    @commands.command(aliases=["yt"], description="Search youtube for stuff")
    @commands.cooldown(2, 15, BucketType.user)
    async def youtube(self, ctx, *, search_term: str):
        search_terms = search_term
        max_results = 1

        def parse_html(response):
            results = []
            start = (
                response.index('window["ytInitialData"]')
                + len('window["ytInitialData"]')
                + 3
            )
            end = response.index("};", start) + 1
            json_str = response[start:end]
            data = json.loads(json_str)

            videos = data["contents"]["twoColumnSearchResultsRenderer"][
                "primaryContents"
            ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

            for video in videos:
                res = {}
                if "videoRenderer" in video.keys():
                    video_data = video["videoRenderer"]
                    res["id"] = video_data["videoId"]
                    res["thumbnails"] = [
                        thumb["url"] for thumb in video_data["thumbnail"]["thumbnails"]
                    ]
                    res["title"] = video_data["title"]["runs"][0]["text"]
                    # res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
                    res["channel"] = video_data["longBylineText"]["runs"][0]["text"]
                    res["duration"] = video_data.get("lengthText", {}).get(
                        "simpleText", 0
                    )
                    res["views"] = video_data.get("viewCountText", {}).get(
                        "simpleText", 0
                    )
                    res["url_suffix"] = video_data["navigationEndpoint"][
                        "commandMetadata"
                    ]["webCommandMetadata"]["url"]
                    results.append(res)
            return results

        def search():
            encoded_search = urllib.parse.quote(search_terms)
            BASE_URL = "https://youtube.com"
            url = f"{BASE_URL}/results?search_query={encoded_search}"
            response = requests.get(url).text
            while 'window["ytInitialData"]' not in response:
                response = requests.get(url).text
            results = parse_html(response)
            if max_results is not None and len(results) > max_results:
                return results[:max_results]
            return results

        videos = search()
        text = f'**__{videos[0]["title"]}__**\n```bash\n"Channel" :  {videos[0]["channel"]}\n"Duration":  {videos[0]["duration"]}\n"Views"   :  {videos[0]["views"]}```'
        url = f"https://www.youtube.com{videos[0]['url_suffix']}"
        await ctx.send(content=text + "\n" + url)

    @commands.command(aliases=["tenor"], description="Search for a gif")
    async def gif(self, ctx, *, query: str):
        apikey = "8ZQV38KW9TWP"
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
        embed.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command(
        name="pypi",
        description="Searches pypi for python packages",
        aliases=["pypl", "pip"],
    )
    async def pythonpackagingindex(self, ctx, package_name: str):

        url = f"https://pypi.org/pypi/{package_name}/json"
        async with self.bot.session.get(url) as response:
            if (
                "We looked everywhere but couldn't find this page"
                in await response.text()
            ):
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        fj = fj["info"]
        if not len(fj["summary"]) == 0:
            embed = discord.Embed(
                title=fj["name"],
                description=fj["summary"].replace("![", "[").replace("]", ""),
                color=0x2F3136,
            )
        else:
            embed = discord.Embed(title=fj["name"], color=0x2F3136)
        if len(fj["author_email"]) == 0:
            email = "None"
        else:
            email = fj["author_email"]
        embed.add_field(name="Author", value=f"Name: {fj['author']}\nEmail: {email}")
        embed.add_field(name="Version", value=fj["version"])
        # embed.add_field(name="Summary", value=fj["summary"])
        hp = "Github Repo" if re.match(r"https:\/\/(www\.)?github\.com\/.{0,39}\/.{0,100}", fj["home_page"]) else "Home Page"
        embed.add_field(
            name="Links",
            value=f"[{hp}]({fj['home_page']})\n[Project Link]({fj['project_url']})\n[Release Link]({fj['release_url']})",
        )
        if fj["license"] is None or len(fj["license"]) < 3:
            license = "Not Specified"
        else:
            license = fj["license"].replace("{", "").replace("}", "").replace("'", "")
        embed.add_field(name="License", value=f"‌{license}")
        if not fj["requires_dist"] is None:
            if len(fj["requires_dist"]) > 15:
                embed.add_field(name="Dependencies", value=len(fj["requires_dist"]))
            elif not len(fj["requires_dist"]) == 0:
                embed.add_field(
                    name=f"Dependencies ({len(fj['requires_dist'])})",
                    value="\n".join([i.split(" ")[0] for i in fj["requires_dist"]]),
                )
        if not fj["requires_python"] is None:
            if len(fj["requires_python"]) > 2:
                embed.add_field(
                    name="<:python:596577462335307777> Python Version Required",
                    value=fj["requires_python"],
                )
        await ctx.send(embed=embed)


    @commands.command(
        name="npm",
        description="Searches npm for JavaScript packages",
    )
    async def nodepackagemanager(self, ctx, package_name: str):

        url = f"https://registry.npmjs.org/{package_name}"
        async with self.bot.session.get(url) as response:
            if (
                '{"error":"Not found"}'
                in await response.text()
            ):
                return await ctx.send("Project not found")
            else:
                fj = json.loads(await response.text())
        if not len(fj["description"]) == 0:
            embed = discord.Embed(
                title=fj["_id"],
                description=fj["description"].replace("![", "[").replace("]", ""),
                color=0x2F3136,
            )
        else:
            embed = discord.Embed(title=fj["_id"], color=0x2F3136)
        author = fj["author"]
        embed.add_field(name="Author", value=f"Name: ({author.get('name')})[{author.get('url')}]\nEmail: {author.get('email')}", inline=False)
        latest_ver = sorted(fj["versions"])[-1]
        embed.add_field(name="Version", value=latest_ver)
        main = ""
        for maintainer in fj["maintainers"]:
            author = maintainer
            main += f"    Name: ({author.get('name')})[{author.get('url']}]\nEmail: {author.get('email')}\n"
        embed.add_field(name="Maintainers",  value=main, inline=False)
        links = []
        if fj.get("homepage"):
            links.append(f'(Home Page)[{fj["homepage"]}]')
        if fj.get("bugs"):
            links.append(f'(Bug Tracker)[{fj["bugs"]}')
        if (github!:= re.find(r"https:\/\/(www\.)?github\.com\/.{0,39}\/.{0,100}", fj["repository"]["url"])):
            links.append(f'(Github Repo)[{github}]')
        links.append(f"(Package Link)[{'https://www.npmjs.com/package/'+fj['_id']}]")
        embed.add_field(name="Links", value="\n".join(links))
        if fj.get("license")
            embed.add_field(name="License", value=fj["license"])
        dependencies = list(fj["versions"][latest_ver]["dependencies"])
        if dependencies:
            if len(dependencies) > 15:
                embed.add_field(name="Dependencies", value=len(dependencies), inline=False)
            elif len(dependencies) > 7:
                embed.add_field(name="Dependencies", value=", ".join(dependencies))
            else:
                embed.add_field(name="Dependencies", value="\n".join(dependencies))
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
    bot.add_cog(Search(bot))
