"""Main file."""
import asyncio
import datetime
import io
import os
import secrets
import time

import aiogoogletrans as translator
import aiohttp
import async_cleverbot
import async_cse
import asyncpg
import discord
import discordbio as dbio
import mystbin
import vacefron
from discord.ext import commands, tasks
from dotenv import load_dotenv
from playsound import playsound
from rich import traceback as rich_traceback
from rich.console import Console

from utils.bot import WMBot
from utils.classes import BlackListed

initial_extensions = [
    "cogs." + file[:-3] for file in os.listdir("cogs/") if file.endswith(".py")
]


async def get_prefix(_bot, message):
    """Use this to fetch the current servers prefix from the db.

    Parameters
    ----------
        _bot (commands.Bot): The bot to get the prefix of
        message (discord.Message): the message to get some metadata

    Returns
    -------
        typing.Union[str, List[str]]: prefix


    """
    if isinstance(message.channel, discord.DMChannel):
        return ["", ",", "wm,"]
    if message.author == bot.owner:
        return "wm,"
    prefix_for_this_guild = await _bot.db.fetchrow(
        """
            SELECT prefix
            FROM guilds
            WHERE id=$1
            """,
        message.guild.id,
    )
    if prefix_for_this_guild is None:
        await _bot.db.execute(
            """
                INSERT INTO guilds (id, prefix)
                VALUES ($1, $2)
                """,
            message.guild.id,
            ",",
        )
        prefix_for_this_guild = {"prefix": ","}
    prefix_return = str(prefix_for_this_guild["prefix"])
    return commands.when_mentioned_or(prefix_return)(_bot, message)


intents = discord.Intents(
    members=True,
    presences=True,
    guilds=True,
    emojis=True,
    invites=True,
    messages=True,
    reactions=True,
    voice_states=True,
)
loop = asyncio.get_event_loop()
session = aiohttp.ClientSession(loop=loop)

bot = WMBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    session=session,
    loop=loop,
)

load_dotenv("config/Bot/token.env")
load_dotenv("config/Apis/tokens.env")
load_dotenv("config/Database/db.env")

bot.cleverbot = async_cleverbot.Cleverbot(
    os.environ["cleverbot"], session=session, context=async_cleverbot.DictContext()
)
bot.secureRandom = secrets.SystemRandom()
bot.google_api = async_cse.Search(os.environ["google_search"], session=session)
bot.translate_api = translator.Translator()
bot.vacefron = vacefron.Client(session=session)
bot.mystbin_client = mystbin.Client(session=session)
bot.console = Console()
bot.dbioclient = client = dbio.DBioClient()
bot.api_keys = {"OMDB": os.environ["omdb"], "tenor": os.environ["tenor"]}
bot.snipes = {}
bot.command_uses = {}
bot.session = session
rich_traceback.install(console=bot.console)


@bot.before_invoke
async def before_invoke(ctx):
    """
    Starts typing in the channel to let the user know that the bot recieved the command and is working on it.

    Parameters
    ----------
        ctx : commands.Context
            Represents the context in which a command is being invoked under.
    """
    await ctx.channel.trigger_typing()


@bot.event
async def on_command_completion(
    ctx,
):
    """[summary]

    Parameters
        ----------
        ctx : [type]
            [description]
    """
    if ctx.command.parent is None:
        command_name = ctx.command.name
    else:
        command_name = f"{ctx.command.parent.name} {ctx.command.name}"
    usage = await bot.db.fetchrow(
        """
            SELECT usage
            FROM usages
            WHERE name=$1
            """,
        command_name,
    )
    if usage is None:
        await bot.db.execute(
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
        await bot.db.execute(
            """
                UPDATE usages
                SET usage = $2
                WHERE name = $1;
                """,
            command_name,
            usage,
        )


@bot.event
async def on_command(
    ctx,
):
    """Saves the details about the user of the command

    Parameters
        ----------
            ctx (commands.Context): Represents the context in which
            a command is being invoked under.
    """
    user_id = ctx.author.id
    usage = await bot.db.fetchrow(
        """
            SELECT usage
            FROM users
            WHERE user_id=$1
            """,
        user_id,
    )
    if usage is None:
        await bot.db.execute(
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
        await bot.db.execute(
            """
                UPDATE users
                SET usage = $2
                WHERE user_id = $1;
                """,
            user_id,
            usage,
        )


@bot.check
async def bot_check(
    ctx,
):
    """Checks if the user is blocked

    Parameters
    ----------
        ctx (commands.Context): the context in which
        the command was executed in

    Raises
    -------
        BlackListed: error to be catched in the error handler

    Returns
    -------
        bool: if the user can use the command
    """
    blocked = await bot.db.fetchrow(
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
    """Connects to the db and sets it as a variable"""
    bot.db = await asyncpg.create_pool(
        host=os.environ["host"],
        database=os.environ["database"],
        user=os.environ["user"],
        password=os.environ["password"],
        ssl=os.environ["ssl"],
    )
    playsound("assets/connected_to_database.mp3", block=False)


async def on_ready():
    """Fires when the bot goes online"""
    await bot.wait_until_ready()
    playsound("assets/connected_to_discord.mp3", block=False)
    start = time.time()
    print("Bot is online")
    owner = bot.get_user(723234115746398219)
    bot.load_extension("jishaku")
    bot.load_extension("hotreload")
    end = time.time()
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except commands.ExtensionFailed as exc:
            bot.console.print_exception()
            await owner.send(f"```py\n{exc}```")
    await owner.send(f"All cogs loaded in `{end-start}`ms")
    bot.started_at = datetime.datetime.utcnow()
    playsound("assets/bot_online.mp3", block=False)


bot.loop.run_until_complete(create_db_pool())
bot.loop.create_task(on_ready())


if __name__ == "__main__":
    # bot.ipc.start()  # start the IPC Server
    # new bot:
    bot.run(os.environ["token1"])
    # old bot:
    # bot.run(os.environ["token2"])