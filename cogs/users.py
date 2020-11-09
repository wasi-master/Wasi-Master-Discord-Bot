import discord
from discord.ext import commands
import requests, asyncio, json, urllib, datetime, humanize

from io import BytesIO

def get_status(status: str):
    if str(status) == "online":
        return "<:status_online:596576749790429200>"
    elif str(status) == "dnd":
        return "<:status_dnd:596576774364856321>"
    elif str(status) == "streaming":
        return "<:status_streaming:596576747294818305>"
    elif str(status) == "idle":
        return "<:status_idle:596576773488115722>"
    elif str(status) == "offline":
        return "<:status_offline:596576752013279242>"
    else:
        return status


def get_flag(flag: str):
    if flag == "hypesquad_brilliance":
        return "<:hypesquadbrilliance:724328585363456070> \
        | HypeSquad Brilliance"
    elif flag == "hypesquad_bravery":
        return "<:hypesquadbravery:724328585040625667> | HypeSquad Bravery"
    elif flag == "hypesquad_balance":
        return "<:hypesquadbalance:724328585166454845> | HypeSquad Balance"
    elif flag == "hypesquad":
        return "<:hypesquad:724328585237626931> | HypeSquad Events"
    elif flag == "early_supporter":
        return "<:earlysupporter:724588086646014034> | Early Supporter"
    elif flag == "bug_hunter":
        return "<:bughunt:724588087052861531> | Bug Huntet"
    elif flag == "bug_hunter_level_2":
        return "<:bughunt2:726775007908462653> | Bug Hunter Level 2"
    elif flag == "verified_bot_developer":
        return ("<:verifiedbotdeveloper:740854331154235444> |"
                "Early Verified Bot Developer")
    elif flag == "verified_bot":
        return "<:verifiedbot:740855315985072189> | Verified Bot"
    elif flag == "partner":
        return "<:partner:724588086461202442> | Discord Partner"
    elif flag == "staff":
        return "Discord Staff"
    else:
        return flag.title().replace("_", "")


def get_p(percent: int):
    total = 22
    rn = round(percent * 0.22)
    body = "☐" * total
    li = list(body)

    for i, elem in enumerate(li[:rn]):
        li[i] = "■"

    ku = "".join(li)
    return f"{ku}"


def convert_sec_to_min(seconds):
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


class Users(commands.Cog):
    """Details About Users
    """    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["nafk", "unafk", "rafk", "removeafk", "dafk", "disableafk"])
    async def notawayfromkeyboard(self, ctx):
        is_afk = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM afk
                WHERE user_id=$1
                """,
            ctx.author.id,
        )
        if not is_afk:
            await ctx.send("You are not afk")
        else:
            await self.bot.db.execute(
            """
            DELETE FROM afk WHERE user_id=$1
            """,
            ctx.author.id,
        )
            await ctx.send("Removed your afk")
    @commands.command(aliases=["afk"])
    async def awayfromkeyboard(self, ctx, *, reason: commands.clean_content =None):
        if reason:
            await ctx.send(f"{ctx.author.mention}, You are now afk for {reason} :)")
        else:
            await ctx.send(f"{ctx.author.mention}, You are now afk :)")
        is_afk = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM afk
                WHERE user_id=$1
                """,
            ctx.author.id,
        )
        time = datetime.datetime.utcnow()
        if is_afk is None:
            await self.bot.db.execute(
                """
                    INSERT INTO afk (last_seen, user_id, reason)
                    VALUES ($1, $2, $3)
                    """,
                time,
                ctx.author.id,
                reason,
            )
        else:
            await self.bot.db.execute(
            """
                UPDATE afk
                SET last_seen = $1,
                reason = $2
                WHERE user_id = $3;
                """,
            time,
            reason,
            ctx.author.id,
        )
    
    
    @commands.command(
        aliases=["pfp", "av", "profilepicture", "profile"],
        description="Sends your or another users avatar",
    )
    async def avatar(
        self,
        ctx,
        *,
        user: discord.User = None,
    ):
        user = user or ctx.author
        ext = 'gif' if user.is_avatar_animated() else 'png'
        await ctx.send(file=discord.File(BytesIO(await user.avatar_url.read()), f"{user}.{ext}")) 

    @commands.command(
        aliases=["ui", "whois", "wi", "whoami", "me"],
        description="Shows info about a user",
    )
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = member or ctx.message.author
        status = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM status
                WHERE user_id=$1
                """,
            member.id,
        )
        if not len(member.roles) == 1:
            roles = [role for role in reversed(member.roles)]
            roles = roles[:-1]
        flaglist = [flag for flag in member.public_flags.all()]
        flagstr = ""
        for i in flaglist:
            flagstr += f"{get_flag(i.name)} "
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        if member.id == 538332632535007244:
            embed.add_field(
                name="Fun Fact:",
                value="He is the owner and the only person that developed this bot",
            )
        embed.add_field(name="ID: ", value=member.id)
        if not member.name == member.display_name:
            embed.add_field(name="Nickname:", value=member.display_name)
        a = (
            sorted(ctx.guild.members, key=lambda member: member.joined_at).index(member)
            + 1
        )
        embed.add_field(
            name="Join Position", value=f"{a:3,}/{len(ctx.guild.members):3,}"
        )
        if not len(flaglist) == 0:
            embed.add_field(name="Badges", value=flagstr, inline=False)
        if not status is None and str(member.status) == "offline":
            embed.add_field(
                name="Last Seen",
                value=humanize.precisedelta(
                    datetime.datetime.utcnow() - status["last_seen"]
                )
                + " ago",
            )
        embed.add_field(
            name="Online Status",
            value=f"{get_status(member.desktop_status.name)} Desktop\n{get_status(member.web_status.name)} Web\n{get_status(member.mobile_status.name)} Mobile",
        )
        embed.add_field(
            name="Created at",
            value=f'{member.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - member.created_at)})',
            inline=False,
        )

        embed.add_field(
            name="Joined at:",
            value=f'{member.joined_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.datetime.utcnow() - member.joined_at)})',
            inline=False,
        )
        if not len(member.roles) == 1:
            embed.add_field(
                name=f"Roles ({len(roles)})",
                value=" | ".join([role.mention for role in roles]),
            )
        if not member.bot:
            member_type = ":blond_haired_man: Human"
        else:
            member_type = ":robot: Robot"
        embed.add_field(name="Type", value=member_type)

        await ctx.send(embed=embed)

    @commands.command(
        aliases=["spt"], description="See your or another users spotify info"
    )
    async def spotify(self, ctx, *, member: discord.Member = None):
        success = False
        member = member or ctx.message.author
        activity = ctx.message.guild.get_member(member.id)
        for activity in activity.activities:
            if isinstance(activity, discord.Spotify):
                success = True
                search_terms = activity.artist + " - " + activity.title
                max_results = 1
                """
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
                    ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"][
                        "contents"
                    ]

                    for video in videos:
                        res = {}
                        if "videoRenderer" in video.keys():
                            video_data = video["videoRenderer"]
                            res["id"] = video_data["videoId"]
                            res["thumbnails"] = [
                                thumb["url"]
                                for thumb in video_data["thumbnail"]["thumbnails"]
                            ]
                            res["title"] = video_data["title"]["runs"][0]["text"]
                            # res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
                            res["channel"] = video_data["longBylineText"]["runs"][0][
                                "text"
                            ]
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
                """
                #videos = search()
                embed = discord.Embed(color=activity.color)
                embed.set_thumbnail(
                    url="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
                )
                embed.set_image(url=activity.album_cover_url)
                embed.add_field(name="Song Name", value=activity.title)
                if len(activity.artists) == 0:
                    embed.add_field(name="Artist", value=activity.artist)
                else:
                    embed.add_field(name="Artists", value=activity.artist)
                try:
                    embed.add_field(name="Album", value=activity.album)
                except:
                    embed.add_field(name="Album", value="None")
                #await ctx.send(f"Hey umm, the duration I got is {activity.duration} and I tried to make it {str(activity.duration)[2:7]}")
                if len(str(activity.duration)[2:-7]) > 1:
                    embed.add_field(
                      name="Song Duration", value=str(activity.duration)[2:-7]
                   )
                embed.add_field(
                    name="Spotify Link",
                    value=f"[Click Here](https://open.spotify.com/track/{activity.track_id})",
                )
                """embed.add_field(
                    name="Youtube Link",
                    value=f"[Click Here](https://www.youtube.com{videos[0]['url_suffix']})",
                )"""
                try:
                    embed.add_field(
                        name="Time",
                        value=f"{convert_sec_to_min((datetime.datetime.utcnow() - activity.start).total_seconds())} {get_p((abs((datetime.datetime.utcnow() - activity.start).total_seconds())) / (abs(((activity.start - activity.end)).total_seconds()) / 100))} {str(activity.duration)[2:-7]}",
                    )
                except IndexError:
                    pass
                embed.set_footer(text="Track ID:" + activity.track_id)
                await ctx.send(embed=embed)
            else:
                success = False
        if not success:
            await ctx.send("Not listening to spotify :(")


def setup(bot):
    bot.add_cog(Users(bot))
