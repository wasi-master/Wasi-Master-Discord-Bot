import asyncio
import functools
import json
import random
import typing
from pprint import pformat

import discord
from discord.ext import commands


def get_all_customs(obj, syntax_highlighting: bool = False) -> dict:
    dicted = {}
    for i in dir(obj):
        if not str(i).startswith("__") and not str(getattr(obj, i)).startswith("<"):
            attr = getattr(obj, i)
            if isinstance(attr, int):
                dicted[i] = int(attr)
            elif attr is None:
                dicted[i] = None
            elif isinstance(attr, bool):
                dicted[i] = attr
            else:
                dicted[i] = str(attr)
    dicted = pformat(dicted, indent=4, width=50)
    return (
        ("```python\n" if syntax_highlighting else "")
        + dicted
        + ("```" if syntax_highlighting else "")
    )


discord.Message.role_mentions


def convert_sec_to_min(seconds):
    """returns 1:30 if 90 is passed


    Parameters
    ----------
        seconds (int): the seconds to convert the data from

    Returns
    -------
        str: the 1:30
    """
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def get_p(percent: int):
    """Generates a progressbar


    Parameters
    ----------
        percent (int): Percentage

    Returns
    -------
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


def get_random_color():
    colors = [
        discord.Colour.default(),
        discord.Colour.teal(),
        discord.Colour.dark_teal(),
        discord.Colour.green(),
        discord.Colour.dark_green(),
        discord.Colour.blue(),
        discord.Colour.dark_blue(),
        discord.Colour.purple(),
        discord.Colour.dark_purple(),
        discord.Colour.magenta(),
        discord.Colour.dark_magenta(),
        discord.Colour.gold(),
        discord.Colour.dark_gold(),
        discord.Colour.orange(),
        discord.Colour.dark_orange(),
        discord.Colour.red(),
        discord.Colour.dark_red(),
        discord.Colour.light_gray(),
        discord.Colour.lighter_gray(),
        discord.Colour.dark_gray(),
        discord.Colour.darker_gray(),
        discord.Colour.blurple(),
        discord.Colour.greyple(),
        discord.Colour.dark_theme(),
    ]
    return random.choice(colors)


def executor_function(sync_function: typing.Callable):
    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        """
        Asynchronous function that wraps a sync function with an executor.
        """

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper


def split_by_slice(inp: str, length: int) -> list:
    size = length  # renaming the variable
    result = []  # declaring a list

    for index, item in enumerate(inp):  # looping through the string
        if size == length:  # checking if we already reached the limit
            size = 0  # we reset the limit
            result.append(
                inp[index : index + length]
            )  # we cut the string based on the limit
        size += 1  # we increase the size

    return result  # we return the result


async def get_agreement(ctx, text, destination=None, target=None, timeout=20):
    destination = destination or ctx.channel
    target = target or ctx.author

    def check(msg):
        return msg.author.id == target.id and msg.channel.id == destination.id

    await destination.send(text + " type `yes` or `no`")
    try:
        name = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        if isinstance(destination, commands.Context):
            await ctx.reply("You didnt respond in 30 seconds :(")
            return False
        await destination.send("You didnt respond in 30 seconds :(")
        return False
    else:
        if name.content == "yes":
            return True
        elif name.content == "no":
            await name.reply("OKay")
            return False
        else:
            await ctx.send(
                "I was hoping for `yes` or `no` but you said something else :("
            )
            return False
