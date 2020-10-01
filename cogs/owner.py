import ast
import asyncio
import discord
import prettify_exceptions
import traceback

from  discord.ext import commands
from  discord.ext  import  menus

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
    async def format_page (self,  menu, entry):
        joined = ' \n '.join ( str(i)  for  i  in  entry)
        return f'** { entry } ** \n { joined } \n Page  { menu.current_page  +  1 } / { self.get_max_pages () } ' 


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await ctx.send("It\'s for the bot owner only and ur not my owner :grin:")
 




    @commands.command(name="eval", aliases=["e"])
    async def _eval(self, ctx, *, cmd):
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
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            "_bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "_ctx": ctx,
            "_guild": ctx.guild,
            "_author": ctx.author,
            "_channel": ctx.channel,
            "_client": self.bot,
            "__import__": __import__,
        }
        await ctx.message.add_reaction("\U0001f7e1")

        if not ctx.guild is None:
            me = ctx.guild.me
        else:
            me = self.bot.user

        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)
        except Exception as exc:
            await ctx.message.remove_reaction("\U0001f7e1", me)
            await ctx.message.add_reaction("\U0001f534")
            tb = "".join(
                prettify_exceptions.DefaultFormatter().format_exception(
                    type(exc), exc, exc.__traceback__
                )
            )
            pages = menus.MenuPages(source = Source(tb.split("\n"), key = lambda m: m, per_page = 12 ),  clear_reactions_after = True )
            await pages.start(ctx)
            return

        if isinstance(result, str):
            parsed_result = result.replace(
                self.bot.http.token, "[token ommitted]"
            )
        elif isinstance(result, (int, float, bool, list, dict)):
            parsed_result = str(result)
        elif isinstance(result, discord.File):
            await ctx.send(file=result)
        elif isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        elif isinstance(result, None):
            parsed_result = "None"
        else:
            parsed_result = repr(result)

        await ctx.send(parsed_result)
        await ctx.message.remove_reaction("\U0001f7e1", me)
        await ctx.message.add_reaction("\U0001f7e2")
"""
    @_eval.error
    async def eval_error(self, ctx, exc):
        tb = "".join(
                prettify_exceptions.DefaultFormatter().format_exception(
                    type(exc), exc, exc.__traceback__
                )
            )
            pages = menus.MenuPages(source = Source(list(tb),  key = lambda  t :  t, per_page = 12 ),  clear_reactions_after = True )
            await pages.start(ctx)
"""
def setup(bot):
    bot.add_cog(Owner(bot))
