import discord
import random
import json
from pprint import pformat

def get_all_customs(obj, syntax_highlighting: bool = False) -> dict:
    dicted = {}
    for i in dir(obj):
        if not str(i).startswith('__') and not str(getattr(obj, i)).startswith('<'):
            dicted[i] = str(getattr(obj, i))
    dicted = pformat(dicted, indent=4)
    f = "```python\n" if syntax_highlighting else ""
    return f + dicted



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
        discord.Colour.dark_theme()
    ]
    return random.choice(colors)