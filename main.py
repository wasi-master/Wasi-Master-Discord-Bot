"""
Main file
"""
import asyncio
import datetime
import os
import secrets

import aiogoogletrans as translator
import aiohttp
import alexflipnote
import async_cleverbot as ac
import async_cse as ag
import asyncpg
import dbl
import discord
import humanize
import youtube_dl as ytdl
from discord.ext import commands, tasks




ytdl.utils.but_reports_message = lambda: ""

initial_extensions = ["cogs." + file[:-3] for file in os.listdir("cogs/") if file.endswith(".py")]


class BlackListed(commands.CheckFailure):
    """Don't respond if the user is blocked from using the bot
    """



async def get_prefix(bot, message) -> str:
    """Used to fetch the current servers prefix from the db

    Args:
        bot (commands.Bot): The bot to get the prefix of
        message (discord.Message): the message to get some metadata

    Returns:
        str: prefix
    """
    if isinstance(message.channel, discord.DMChannel):
        return ["", ","]
    prefix_for_this_guild = await bot.db.fetchrow(
        """
            SELECT prefix
            FROM guilds
            WHERE id=$1
            """,
        message.guild.id,
    )
    if prefix_for_this_guild is None:
        await bot.db.execute(
            """
                INSERT INTO guilds (id, prefix)
                VALUES ($1, $2)
                """,
            message.guild.id,
            ",",
        )
        prefix_for_this_guild = {"prefix": ","}
    prefix_return = str(prefix_for_this_guild["prefix"])
    return commands.when_mentioned_or(prefix_return)(client, message)


def convert_sec_to_min(seconds):
    """returns 1:30 if 90 is passed

    Args:
        seconds (int): the seconds to convert the data from

    Returns:
        str: the 1:30
    """
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def get_p(percent: int):
    """Generates a progressbar

    Args:
        percent (int): Percentage

    Returns:
        str: a progressbar
    """
    total_percentage = 15
    percent = percent * 0.15
    right_now = round(percent / 4)
    body = "☐" * total_percentage
    percentage_list = list(body)

    for i, _ in enumerate(percentage_list[:right_now]):
        percentage_list[i] = "■"

    result = "".join(percentage_list)
    return f"{result}"


intents = discord.Intents(
    members=True,
    presences=True,
    guilds=True,
    emojis=True,
    invites=True,
    messages=True,
    reactions=True,
)

client = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False),
    intents=intents,
)
dblpy = dbl.DBLClient(
    client,
   ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
   "eyJpZCI6IjcwNzg4MzE0MTU0ODczNjUxMiIsIm"
   "JvdCI6dHJ1ZSwiaWF0IjoxNTk2NzM0ODg2fQ."
   "E0VY8HAgvb8V2WcL9x2qBf5hcKBp-WV0BhLLa"
   "GSfAPs"),
)
client.cleverbot = ac.Cleverbot("G[zm^mG5oOVS[J.Y?^YV", context=ac.DictContext())
client.secureRandom = secrets.SystemRandom()
client.alex_api = alexflipnote.Client()
client.google_api = ag.Search("AIzaSyCHpVwmhfCBX6sDTqMNYVfCZaOdsXp9BFk")
client.translate_api = translator.Translator()

client.emoji_list = []
client.emoji_list_str = []


if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)


@client.event
async def on_command_completion(
    ctx,
):
    """saves the details of the command

    Args:
        ctx (commands.Context): the context the command was executed upon
    """
    if ctx.command.parent is None:
        command_name = ctx.command.name
    else:
        command_name = f"{ctx.command.parent.name} {ctx.command.name}"
    usage = await client.db.fetchrow(
        """
            SELECT usage
            FROM usages
            WHERE name=$1
            """,
        command_name,
    )
    if usage is None:
        await client.db.execute(
            """
                INSERT INTO usages (usage, name)
                VALUES ($1, $2)
                """,
            1,
            command_name,
        )
    else:
        usage = usage["usage"]
        usage += 1
        await client.db.execute(
            """
                UPDATE usages
                SET usage = $2
                WHERE name = $1;
                """,
            command_name,
            usage,
        )


@client.event
async def on_command(
    ctx,
):
    """Saves the details about the user of the command

    Args:
        ctx (commands.Context): the context the command was executed upon
    """
    user_id = ctx.author.id
    usage = await client.db.fetchrow(
        """
            SELECT usage
            FROM users
            WHERE user_id=$1
            """,
        user_id,
    )
    if usage is None:
        await client.db.execute(
            """
                INSERT INTO users (usage, user_id)
                VALUES ($1, $2)
                """,
            1,
            user_id,
        )
    else:
        usage = usage["usage"]
        usage += 1
        await client.db.execute(
            """
                UPDATE users
                SET usage = $2
                WHERE user_id = $1;
                """,
            user_id,
            usage,
        )


async def bot_check(
    ctx,
):
    """Checks if the user is blocked

    Args:
        ctx (commands.Context): the context in which the command was executed in

    Raises:
        BlackListed: error to be catched in the error handler

    Returns:
        bool: if the user can use the command
    """
    blocked = await client.db.fetchrow(
        """
            SELECT *
            FROM blocks
            WHERE user_id=$1
            """,
        ctx.author.id,
    )
    if blocked is None:
        return True
    raise BlackListed


async def create_db_pool():
    """Connects to the db and sets it as a variable
    """
    client.db = await asyncpg.create_pool(
     host="ec2-52-23-86-208.compute-1.amazonaws.com",
     database="d5squd8cvojua1",
     user="poladbevzydxyx",
     password="5252b3d45b9dd322c3b67430609656173492b3c97cdfd5ce5d9b8371942bb6b8",
    )


client.loop.run_until_complete(create_db_pool())



async def fake_on_ready():
    """Fires when the bot goes online
    """
    await client.wait_until_ready()
    print("Bot is online")
    client.session = aiohttp.ClientSession()
    owner = client.get_user(538332632535007244)
    try:
        await owner.send("Bot Online")
    except AttributeError:
        pass
    client.started_at = datetime.datetime.utcnow()
    update_server_count.start()
    client.load_extension("jishaku")


client.loop.create_task(fake_on_ready())


@tasks.loop(seconds=86400)
async def update_server_count():
    """updates the bot's status
    """
    memberlist = []
    serverlist = []
    for guild in client.guilds:
        serverlist.append(guild)
        for member in guild.members:
            memberlist.append(member)
    await dblpy.post_guild_count()
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(memberlist)} people in {len(serverlist)} servers 😁😁😁",
        )
    )


@client.event
async def on_guild_join(guild):
    """Sends a message to the owner when bot is added to a guild

    Args:
        guild (discord.Guild): the guild bot was added to
    """
    owner = client.get_user(538332632535007244)
    guild_owner = client.get_user(guild.owner_id)
    features = ""
    for i in guild.features:
        features += "\n" + i.title().replace("_", " ")
    embed = discord.Embed(
        title=f"Bot Added To {guild.name}",
        description=f"Name: {guild.name}\n \
        Created At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')} \
        ({humanize.precisedelta(datetime.datetime.utcnow() - guild.created_at)})\
        \nID: {guild.id}\nOwner: {guild_owner}\n \
        Icon Url: [click here]({guild.icon_url})\n \
        Region: {str(guild.region)}\n \
        Verification Level: {str(guild.verification_level)}\n \
        Members: {len(guild.members)}\n \
        Boost Level: {guild.premium_tier}\n \
        Boosts: {guild.premium_subscription_count}\n \
        Boosters: {len(guild.premium_subscribers)}\n \
        Total Channels: {len(guild.channels)}\n \
        Text Channels: {len(guild.text_channels)}\n \
        Voice Channels: {len(guild.voice_channels)}\n \
        Categories: {len(guild.categories)}\n \
        Roles: {len(guild.roles)}\n \
        Emojis: {len(guild.emojis)}/{guild.emoji_limit}\n \
        Upload Limit: {round(guild.filesize_limit / 1048576)} Megabytes (MB)\n \
        **Features:** {features}",
    )
    embed.set_thumbnail(url=guild.icon_url)
    await owner.send(embed=embed)
    await client.db.execute(
        """
                INSERT INTO guilds (id, prefix)
                VALUES ($1, $2)
                """,
        guild.id,
        ",",
    )


@client.event
async def on_guild_remove(guild):
    """Sends a message to the owner when bot is removed from a guild

    Args:
        guild (discord.Guild): the guild bot was removed from
    """
    owner = client.get_user(538332632535007244)
    guild_owner = client.get_user(guild.owner_id)
    features = ""
    for i in guild.features:
        features += "\n" + i.title().replace("_", " ")
    embed = discord.Embed(
        title=f"Bot Removed From {guild.name}",
        description=f"Name: {guild.name}\n \
            Created At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')} \
            ({humanize.precisedelta(datetime.datetime.utcnow() - guild.created_at)})\
            \nID: {guild.id}\nOwner: {guild_owner}\n \
            Icon Url: [click here]({guild.icon_url})\n \
            Region: {str(guild.region)}\n \
            Verification Level: {str(guild.verification_level)}\n \
            Members: {len(guild.members)}\n \
            Boost Level: {guild.premium_tier}\n \
            Boosts: {guild.premium_subscription_count}\n \
            Boosters: {len(guild.premium_subscribers)}\n \
            Total Channels: {len(guild.channels)}\n \
            Text Channels: {len(guild.text_channels)}\n \
            Voice Channels: {len(guild.voice_channels)}\n \
            Categories: {len(guild.categories)}\n \
            Roles: {len(guild.roles)}\n \
            Emojis: {len(guild.emojis)}/{guild.emoji_limit}\n \
            Upload Limit: {round(guild.filesize_limit / 1048576)} Megabytes (MB)\n \
            **Features:** {features}",
    )
    embed.set_thumbnail(url=guild.icon_url)
    await owner.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    """Error Handler

    Args:
        ctx (commands.Context): [The context the command was executed in]
        error (commands.CommandInvokeError): [the error it raised]

    Raises:
        error: the error that occured

    Returns:
        NoneType: Nothing
    """
    if hasattr(ctx.command, "on_error"):
        return
    error = getattr(error, "original", error)
    if isinstance(error, (BlackListed, commands.CommandNotFound)) or \
        "Cannot send messages to this user" in str(error):
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"You don't have the permission to use {ctx.command} command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"The {str(error.param).split(':')[0].strip()} argument is missing"
        )
    elif "not found" in str(error):
        await ctx.send(embed=discord.Embed(title="Not Found", description=str(error)))
    elif isinstance(error, discord.Forbidden):
        await ctx.send("I am missing permissions")
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Slow Down!",
            description=(f"The command `{ctx.command}` is on cooldown, "
            f"please try again after **{round(error.retry_after, 2)}** seconds."
            "\nPatience, patience."),
            colour=16711680,
        )
        await ctx.send(embed=embed)
    else:
        botembed = discord.Embed(
            description=(f"Welp, The command was unsuccessful for this reason:\n```{error}```\n"
            "React with :white_check_mark: to report the error to the support server\n"
            "If you can't understand why this happens, ask Wasi Master#4245"
            " or join the bot support server (you can get the invite with the support command)")
        )
        message = await ctx.send(embed=botembed)
        await message.add_reaction("\u2705")

        def check(reaction, user):  # r = discord.Reaction, u = discord.Member or discord.User.
            return user.id == ctx.author.id and reaction.message.channel.id == ctx.channel.id

        try:
            reaction, _ = await client.wait_for(
                "reaction_add", check=check, timeout=20
            )
        except asyncio.TimeoutError:
            try:
                botembed.set_footer(
                    icon_url=ctx.author.avatar_url,
                    text="You were too late to amswer",
                )
                await message.edit(embed=botembed)
                return await message.clear_reactions()
            except discord.Forbidden:
                botembed.set_footer(
                    icon_url=ctx.author.avatar_url,
                    text="You were too late to answer",
                )
                await message.edit(embed=botembed)
                return await message.remove_reaction("\u2705", ctx.guild.me)
        else:
            if reaction.emoji == "\u2705":
                botembed.set_footer(
                    icon_url=ctx.author.avatar_url,
                    text="Reported to The Support Server",
                )
                await message.edit(embed=botembed)
                guild = client.get_guild(576016234152198155)
                channel = guild.get_channel(739673341388128266)
                embed = discord.Embed(color=0x2F3136)
                embed.set_author(name="Error")
                embed.add_field(name="User", value=ctx.message.author)
                embed.add_field(name="Guild", value=ctx.guild.name)
                embed.add_field(name="Message", value=ctx.message.content)
                embed.add_field(name="Error", value=f"```{str(error)}```")
                embed.add_field(
                    name="Message Links",
                    value=(f"[User Message]({ctx.message.jump_url})\n"
                           f"[Bot Message]({message.jump_url})"),
                )
                await channel.send(embed=embed)
                return
        raise error



@client.event
async def on_member_update(old, new):
    """Stores status

    Args:
        old (discord.Member): [the old member object before updating ]
        new (discord.Member): [the new member object after updatig]
    """
    if not (
        new.status != old.status
        and str(old.status) != "offline"
        and str(new.status) == "offline"
        and len(new.guild.members) < 500
    ):
        return
    time = datetime.datetime.utcnow()

    status = await client.db.fetchrow(
        """
            SELECT *
            FROM status
            WHERE user_id=$1
            """,
        new.id,
    )

    if status is None:
        await client.db.execute(
            """
                    INSERT INTO status (last_seen, user_id)
                    VALUES ($1, $2)
                    """,
            time,
            new.id,
        )
    else:
        await client.db.execute(
            """
                UPDATE status
                SET last_seen = $2
                WHERE user_id = $1;
                """,
            new.id,
            time,
        )



# @commands.command(
#     aliases=["ss"],
#     description="Takes a sceenshot of a website"
# )
# @commands.cooldown(1, 30, BucketType.default)
# async def screenshot(ctx, website:str):
#     async with ctx.typing():

#         async with client.session.get(
#             "https://magmafuck.herokuapp.com/api/v1",
#             headers={"website": website}
#         ) as response:
#             data = await response.json()
#             embed = discord.Embed(title=data["website"], url=website)
#            r = json.loads(requests.get(
#                f"https://nsfw-categorize.it/api.php?url={data['snapshot']}"
#                ).text)
#            if int(round(r["porn_probability"])) > 5 and not ctx.channel.is_nsfw():
#                return await ctx.send("NSFW Filter Active")
#             else:
#                 embed.set_image(url=data["snapshot"])
#         await ctx.send(embed=embed)
#         session.close()

client.run(os.environ["token"], bot=True, reconnect=True)
