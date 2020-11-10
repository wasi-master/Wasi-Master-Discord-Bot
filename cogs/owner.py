import ast
import asyncio
import collections
import discord
import prettify_exceptions
import traceback

from discord.ext import commands
from discord.ext import menus


Codeblock = collections.namedtuple('Codeblock', 'language content')

def codeblock_converter(argument):
    """
    A converter that strips codeblock markdown if it exists.
    Returns a namedtuple of (language, content).
    :attr:`Codeblock.language` is an empty string if no language was given with this codeblock.
    It is ``None`` if the input was not a complete codeblock.
    """
    if not argument.startswith('`'):
        return Codeblock(None, argument)

    # keep a small buffer of the last chars we've seen
    last = collections.deque(maxlen=3)
    backticks = 0
    in_language = False
    in_code = False
    language = []
    code = []

    for char in argument:
        if char == '`' and not in_code and not in_language:
            backticks += 1  # to help keep track of closing backticks
        if last and last[-1] == '`' and char != '`' or in_code and ''.join(last) != '`' * backticks:
            in_code = True
            code.append(char)
        if char == '\n':  # \n delimits language and code
            in_language = False
            in_code = True
        # we're not seeing a newline yet but we also passed the opening ```
        elif ''.join(last) == '`' * 3 and char != '`':
            in_language = True
            language.append(char)
        elif in_language:  # we're in the language after the first non-backtick character
            if char != '\n':
                language.append(char)

        last.append(char)

    if not code and not language:
        code[:] = last

    return Codeblock(''.join(language), ''.join(code[len(language):-backticks]))

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


def convert_sec_to_min(seconds):
    """returns 1:30 if 90 is passed

    Args:
        seconds (int): the seconds to convert the data from

    Returns:
        str: the 1:30
    """
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def progressbar(percent: int, empty: str = "☐", filled: str = "■"):
    """Generates a progressbar

    Args:
        percent (int): Percentage

    Returns:
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
    @commands.group(invoke_without_command=False, aliases=["msg"])
    async def bot_message(ctx):
        pass
    
    @bot_message.command(name="delete", aliases=["d"])
    @commands.is_owner()
    async def message_delete(ctx, msg: discord.Message):
        try:
            await msg.delete()
        except Exception as e:
            await ctx.send(e)
    @bot_message.command(name="edit", aliases=["e"])
    @commands.is_owner()
    async def message_edit(ctx, msg: discord.Message, content: str):
        try:
            await msg.edit(content=content, embed=msg.embeds[0])
        except Exception as e:
            await ctx.send(e)
    
    @bot_message.command(name="delete_embed", aliases=["de"])
    @commands.is_owner()
    async def message_delete_embed(ctx, msg: discord.Message):
        try:
            await msg.edit(content="‌"+msg.content, embed=None)
        except Exception as e:
            await ctx.send(e)


    @commands.command(description="The bot leaves the server (bot owner only)")
    async def leaveserver(
        self,
        ctx,
    ):
        if ctx.message.author.id == 538332632535007244:
            await ctx.send("Bye Bye")
            ctx.message.guild.leave()
        else:
            await ctx.send("You are not the owner :grin:")

    @commands.command(
        aliases=["shutup"], description="Stops the bot, only for the bot owner"
    )
    async def shutdown(
        self,
        ctx,
    ):
        if ctx.message.author.id == 538332632535007244:
            exit()
        else:
            await ctx.send("You are not the bot owner :grin::grin::grin:")

    commands.command(
        aliases=["rs"], description="Stops the bot, only for the bot owner"
    )

    async def restart(
        self,
        ctx,
    ):
        if ctx.message.author.id == 538332632535007244:
            await self.bot.close()
        else:
            await ctx.send("You are not the bot owner :grin::grin::grin:")

    @commands.command(
        aliases=["bfutb", "bfb", "blockfrombot"],
        description="Blocks a user from using the bot (Owner only)",
    )
    async def blockfromusingthebot(self, ctx, task: str, user: discord.User = None):
        if ctx.author.id == 538332632535007244:
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

    @commands.command(name="eval", aliases=["e"])
    async def eval_command(self, ctx, *, cmd: codeblock_converter):
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
        if not ctx.author.id == 538332632535007244:
            return await ctx.send(
                "**Eval**uating **Python** code is only for the bot owner since we cannot gurantee that you will not use it for something bad"
            )
        # fn_name = "_eval_expr"
        # cmd = cmd.rstrip("```").lstrip("```").lstrip("py")
        # cmd = cmd.replace(";", "\n").replace("; ", " \n")
        # # add a layer of indentation
        # cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # # wrap in async def body
        # body = f"async def {fn_name}():\n{cmd}"

        # parsed = ast.parse(body)
        # body = parsed.body[0].body

        # insert_returns(body)

        # env = {
        #     "bot": ctx.bot,
        #     "discord": discord,
        #     "commands": commands,
        #     "ctx": ctx,
        #     "guild": ctx.guild,
        #     "author": ctx.author,
        #     "channel": ctx.channel,
        #     "message": ctx.message,
        #     "client": ctx.bot,
        #     "__import__": __import__,
        #     "progressbar": progressbar,
        #     "split_by_slice": split_by_slice,
        #     "convert_sec_to_min": convert_sec_to_min,
        # }
        # await ctx.message.add_reaction("\U0001f7e1")

        # if not ctx.guild is None:
        #     me = ctx.guild.me
        # else:
        #     me = self.bot.user
        # try:
        #     exec(compile(parsed, filename="<eval>", mode="exec"), env)
        #     result = await eval(f"{fn_name}()", env)
        # except BaseException as exc:
        #     await ctx.message.remove_reaction("\U0001f7e1", me)
        #     await ctx.message.add_reaction("\U0001f534")
        #     tb = "".join(traceback.format_exc())
        #     tb = tb.replace(
        #         "/app/.heroku/python/lib/python3.9/site-packages",
        #         "C:/Users/Wasi/AppData/Roaming/Python/Python38/site-packages",
        #     ).replace(
        #         "/app/", "C:/Users/Wasi/Documents/Github/Wasi-Master-Discord-Bot/"
        #     ).replace('File "C:/Users/Wasi/Documents/Github/Wasi-Master-Discord-Bot/cogs/owner.py", line 240, in eval_command\nresult = await eval(f"{fn_name}()", env)\nFile "<eval>",', 'In')
        #     if len(tb) < 1000:
        #         embed = discord.Embed(title="Traceback", description=tb)
        #         await ctx.send(embed=embed)
        #         return
        #     results = split_by_slice(tb, 2000)
        #     num = 0
        #     embed = discord.Embed(title="Traceback", description=results[num])
        #     embed.set_footer(text=f"Page {num + 1}/{len(results)}")
        #     message = await ctx.send(embed=embed)
        #     await message.add_reaction("\u25c0\ufe0f")
        #     await message.add_reaction("\u23f9\ufe0f")
        #     await message.add_reaction("\u25b6\ufe0f")
        #     while True:

        #         def check(reaction, user):
        #             return (
        #                 user.id == ctx.author.id
        #                 and reaction.message.channel.id == ctx.channel.id
        #             )

        #         try:
        #             reaction, user = await self.bot.wait_for(
        #                 "reaction_add", check=check, timeout=120
        #             )
        #         except asyncio.TimeoutError:
        #             embed.set_footer(
        #                 icon_url=str(ctx.author.avatar_url), text="Timed out"
        #             )
        #             await message.edit(embed=embed)
        #             try:
        #                 return await message.clear_reactions()
        #             except:
        #                 await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
        #                 await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
        #                 await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
        #                 break
        #                 return
        #         else:
        #             if reaction.emoji == "\u25c0\ufe0f":
        #                 try:
        #                     message.remove_reaction("\u25c0\ufe0f", ctx.author)
        #                 except discord.Forbidden:
        #                     pass
        #                 num -= 1
        #                 try:
        #                     result = results[num]
        #                 except IndexError:
        #                     pass
        #                 embed = discord.Embed(
        #                     title="Traceback", description=results[num]
        #                 )
        #                 embed.set_footer(text=f"Page {num + 1}/{len(results)}")
        #                 await message.edit(embed=embed)
        #             elif reaction.emoji == "\u25b6\ufe0f":
        #                 try:
        #                     await message.remove_reaction("\u25b6\ufe0f", ctx.author)
        #                 except discord.Forbidden:
        #                     pass
        #                 num += 1
        #                 try:
        #                     result = results[num]
        #                 except IndexError:
        #                     pass
        #                 embed = discord.Embed(
        #                     title="Traceback", description=results[num]
        #                 )
        #                 embed.set_footer(text=f"Page {num + 1}/{len(results)}")
        #                 await message.edit(embed=embed)
        #             elif reaction.emoji == "\u23f9\ufe0f":
        #                 embed = discord.Embed(
        #                     title="Traceback", description=results[num]
        #                 )
        #                 await message.edit(embed=embed)
        #                 try:
        #                     return await message.clear_reactions()
        #                 except:
        #                     await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
        #                     await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
        #                     await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
        #                     break
        #                     return
        #             else:
        #                 pass

        #     return
        # else:
        #     parsed_result = None
        #     if isinstance(result, str):
        #         parsed_result = result.replace(self.bot.http.token, "**[TOKEN]**")
        #     elif isinstance(result, (int, float, bool, list, dict)):
        #         parsed_result = str(result)
        #     elif isinstance(result, discord.File):
        #         await ctx.send(file=result)
        #     elif isinstance(result, discord.Embed):
        #         await ctx.send(embed=result)
        #     elif result is None:
        #         parsed_result = "None"
        #     else:
        #         parsed_result = repr(result)
        #     if parsed_result:
        #         await ctx.send(parsed_result)
        #     await ctx.message.remove_reaction("\U0001f7e1", me)
        #     await ctx.message.add_reaction("\U0001f7e2")
        jsk = self.bot.get_command("jishaku python")
        await jsk(ctx, argument=cmd)

def setup(bot):
    bot.add_cog(Owner(bot))
