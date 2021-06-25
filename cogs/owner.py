import ast
import asyncio
import collections
import io
import textwrap
import traceback
import typing

import discord
import prettify_exceptions
from discord.ext import commands, menus

import utils
from utils.converters import CodeblockConverter
from utils.functions import split_by_slice


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Source(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        joined = entry
        return f"** { entry.key } ** \n { joined } \n Page  { menu.current_page  +  1 } / { self.get_max_pages () } "


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


def progressbar(percent: int, empty: str = "☐", filled: str = "■"):
    """Generates a progressbar


    Parameters
    ----------
        percent (int): Percentage

    Returns
    -------
        empty (str): a progressbar
    """
    total_percentage = 15
    percent = percent * 0.15
    right_now = round(percent / 4)
    body = empty * total_percentage
    percentage_list = list(body)

    for i, _ in enumerate(percentage_list[:right_now]):
        percentage_list[i] = filled

    result = "".join(percentage_list)
    return f"{result}"


class Owner(commands.Cog):
    """Commands only available to be used by the bot owner"""

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.group(invoke_without_command=False, aliases=["msg"], name="bot_message")
    async def _bot_message(self, ctx):
        pass

    @_bot_message.command(name="delete", aliases=["d"])
    @commands.is_owner()
    async def message_delete(self, ctx, msg: discord.Message):
        try:
            await msg.delete()
        except Exception as e:
            await ctx.send(e)

    @_bot_message.command(name="edit", aliases=["e"])
    @commands.is_owner()
    async def message_edit(self, ctx, msg: discord.Message, content: str):
        try:
            await msg.edit(content=content, embed=msg.embeds[0])
        except Exception as e:
            await ctx.send(e)

    @_bot_message.command(name="delete_embed", aliases=["de"])
    @commands.is_owner()
    async def message_delete_embed(self, ctx, msg: discord.Message):
        try:
            await msg.edit(content="‌" + msg.content, embed=None)
        except Exception as e:
            await ctx.send(e)

    @commands.command(description="The bot leaves the server (bot owner only)")
    async def leaveserver(self, ctx):
        if ctx.author.id == 723234115746398219:
            await ctx.send("Bye Bye")
            ctx.guild.leave()
        else:
            await ctx.send("You are not the owner :grin:")

    @commands.command(
        aliases=["shutup"], description="Stops the bot, only for the bot owner"
    )
    async def shutdown(self, ctx):
        if ctx.author.id == 723234115746398219:
            exit()
        else:
            await ctx.send("You are not the bot owner :grin::grin::grin:")

    commands.command(
        aliases=["rs"], description="Stops the bot, only for the bot owner"
    )

    async def restart(self, ctx):
        if ctx.author.id == 723234115746398219:
            await self.bot.close()
        else:
            await ctx.send("You are not the bot owner :grin::grin::grin:")

    @commands.command()
    async def sendmessagetoallguilds(self, ctx):
        if not ctx.author.id == 723234115746398219:
            return
        wm_bot_2 = self.bot.get_user(847706412306268181)
        embed = discord.Embed(
            title="Hi everyone,",
            description="I am this bot's owner. and I am sad to say that this bot is no longer maintained\n",
            color=0xFF0000,
        )
        embed.set_author(
            name="Wasi Master",
            url="https://discord.com/users/723234115746398219",
            icon_url="https://cdn.discordapp.com/attachments/847709022965465098/849539344166551552/Wasi_Master8082.png",
        )
        embed.set_thumbnail(
            url="https://findicons.com/files/icons/1007/crystal_like/256/attention.png"
        )
        embed.add_field(
            name="**Why**",
            value="Because I lost my old account (due to 2FA) that I made this bot with, so\n"
            "I will no longer be able to work on *this* bot.\n",
            inline=False,
        )
        embed.add_field(
            name="**But do not fear**\n",
            value="I am working on the 2nd version of this bot. which is called WM Bot 2.0\n"
            "The second version is not ready yet. I am still working on _it so it is in beta_, "
            'You can still invite it [from here](https://discordapp.com/oauth2/authorize?client_id=847706412306268181&scope=bot&permissions=109640 "Invite link of the new bot") if you want to have this bot in your server\n'
            "And help me fix the issues and stuff. The new bot runs on the same code as the old one but has some optimisations\n\n",
            inline=False,
        )
        embed.add_field(
            name="**So kick this bot from the server if you want and __*add the new bot*__**\n",
            value="new bot invite link: https://discordapp.com/oauth2/authorize?client_id=847706412306268181&scope=bot&permissions=109640",
            inline=False,
        )
        embed.set_footer(
            text="If you are seeing this and you are not a moderator, please inform the moderator/admin of the server",
            icon_url="https://icons-for-free.com/iconfiles/png/512/info-131964752893297302.png",
        )
        all_guilds = self.bot.guilds
        for i, guild in enumerate(self.bot.guilds[20:], 1):
            print("Seeing {} ({}/{})".format(guild.name, i, len(all_guilds)))
            if wm_bot_2 in guild.members:
                print(
                    "Did not send message to {} becasue 2.0 is there".format(guild.name)
                )
                continue
            print("Sending message to {}".format(guild.name))

            for channel in guild.channels:
                try:
                    await channel.send(embed=embed)
                    print(
                        "Sent embed to {} channel of guild {}".format(
                            channel.name, guild.name
                        )
                    )
                    break
                except Exception as e:
                    print(
                        "Could not send embed to the channel {} of the guild {}".format(
                            channel.name, guild.name
                        )
                    )
                    pass
                else:
                    print(
                        "Sent embed to {} channel of guild {}".format(
                            channel.name, guild.name
                        )
                    )

    @commands.command(
        aliases=["bfutb", "bfb", "blockfrombot"],
        description="Blocks a user from using the bot (Owner only)",
    )
    async def blockfromusingthebot(self, ctx, task: str, user: discord.User = None):
        # TODO: Add Subcommands
        if ctx.author.id == 723234115746398219:
            if task.lower() == "add" and user:
                id_ = user.id
                await self.bot.db.execute(
                    """
                            INSERT INTO blocks (user_id)
                            VALUES ($1);
                            """,
                    id_,
                )
            elif task.lower() == "remove" and user:
                id_ = user.id
                await self.bot.db.execute(
                    """
                            DELETE FROM blocks WHERE user_id=$1;
                            """,
                    id_,
                )
            elif task.lower() == "list":
                list_of_users = await self.bot.db.fetch(
                    """
                SELECT *
                FROM blocks
                """
                )
                blocked_users = []
                for i in list_of_users:
                    user_id = list(i.values())[0]
                    user = self.bot.get_user(user_id)
                    blocked_users.append(str(user))
                nl = "\n"
                await ctx.send(
                    embed=discord.Embed(
                        title="Blocked Users",
                        description=f"```{nl.join(blocked_users)}```",
                    )
                )
            else:
                return await ctx.send(
                    "Oh wasi, you forgot again didn't you?\n you need either add remove or list"
                )
            msg = await ctx.send("Ok Done")
            try:
                await ctx.message.delete()
            except:
                pass
            await asyncio.sleep(2)
            await msg.delete()
        else:
            await ctx.send("It's for the bot owner only and ur not my owner :grin:")

    @commands.command(aliases=["curl"])
    async def get(self, ctx, url: str):
        async with self.bot.session.get(url) as r:
            resp = await r.text()
        embed = discord.Embed(title="Response")
        if len(resp) < 1023:
            embed.add_field(
                name="Raw Data",
                value="```json\n" + resp + "\n```",
                inline=False,
            )
            message = await ctx.send(embed=embed)
        else:
            message = await ctx.send(
                embed=embed,
                file=discord.File(
                    io.StringIO(resp),
                    filename="response.json",
                ),
            )

    @commands.command(name="eval", aliases=["e"])
    async def eval_command(self, ctx, *, cmd: CodeblockConverter):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        if not ctx.author.id == 723234115746398219:
            return await ctx.send(
                "**Eval**uating **Python** code is only for the bot owner since we cannot gurantee that you will not use it for something bad"
            )
        fn_name = "_eval_expr"
        # add a layer of indentation
        cmd = textwrap.indent(cmd.content, "    ")

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            "bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
            "message": ctx.message,
            "client": ctx.bot,
            "__import__": __import__,
            "utils": utils,
        }
        await ctx.message.add_reaction("\U0001f7e1")

        try:
            exec(compile(parsed, filename="<eval>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)
        except BaseException as error:
            await ctx.message.remove_reaction("\U0001f7e1", ctx.me)
            await ctx.message.add_reaction("\U0001f534")
            tb = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            embed = discord.Embed(
                title="Error", description="Code Evaluation raised a error:"
            )
            if len(tb) < 1023:
                embed.add_field(
                    name="Traceback",
                    value="```python\n" + tb + "\n```",
                    inline=False,
                )
                message = await ctx.send(embed=embed)
            else:
                message = await ctx.send(
                    embed=embed,
                    file=discord.File(
                        io.StringIO(tb),
                        filename="traceback.py",
                    ),
                )
            return
        else:
            await ctx.message.add_reaction("\U0001f7e2")
            await ctx.message.remove_reaction("\U0001f7e1", ctx.me)
            parsed_result = None
            if isinstance(result, str):
                parsed_result = result.replace(self.bot.http.token, "**[TOKEN]**")
            elif isinstance(result, (int, float, bool, list, dict)):
                parsed_result = str(result)
            elif isinstance(result, discord.File):
                await ctx.send(file=result)
            elif isinstance(result, discord.Embed):
                await ctx.send(embed=result)
            elif result is None:
                parsed_result = "None"
            else:
                parsed_result = repr(result)
            if parsed_result:
                await ctx.send(parsed_result)
        # jsk = self.bot.get_command("jishaku python")
        # await jsk(ctx, argument=cmd)

    @eval_command.error
    async def on_eval_error(self, ctx, error):
        await ctx.message.remove_reaction("\U0001f7e1", ctx.me)
        await ctx.message.add_reaction("\U0001f534")
        tb = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        embed = discord.Embed(
            title="Error", description="Code Evaluation raised a error:"
        )
        if len(tb) < 1023:
            embed.add_field(
                name="Traceback",
                value="```python\n" + tb + "\n```",
                inline=False,
            )
            message = await ctx.send(embed=embed)
        else:
            message = await ctx.send(
                embed=embed,
                file=discord.File(
                    io.StringIO(tb),
                    filename="traceback.py",
                ),
            )
        return


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Owner(bot))
