import asyncio
import traceback

import discord
from discord.ext import commands
from isort import io
from rich import traceback as rich_traceback
from rich.console import Console

from utils.classes import BlackListed

console = Console()
rich_traceback.install(console=console)


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Error Handler

        Parameters
        ----------
            ctx (commands.Context): [The context the command was executed in]
            error (commands.CommandInvokeError): [the error it raised]

        Raises
        -------
            error: the error that occured

        Returns
        -------
            NoneType: Nothing
        """
        if hasattr(ctx.command, "on_error"):
            return
        error = getattr(error, "original", error)
        if isinstance(
            error, (BlackListed, commands.CommandNotFound)
        ) or "Cannot send messages to this user" in str(error):
            return
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                f"You don't have the permission to use {ctx.command} command"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            signature = ctx.prefix + ctx.invoked_with + " " + ctx.command.signature
            missing_arg_original = error.param.name
            missing_arg = missing_arg_original
            if "_" in missing_arg:
                missing_arg = missing_arg.replace("_", " ")
            missing_arg = missing_arg.title()
            signature = signature.replace(missing_arg_original, missing_arg)
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += (
                " " * signature.index(missing_arg)
                + " " * round(len(missing_arg) / 2)
                + "^\n"
            )
            error_message += (
                f"SyntaxError: the required argument {missing_arg} is missing```"
            )
            await ctx.send(
                embed=discord.Embed(title="Missing Argument", description=error_message)
            )
        elif isinstance(error, commands.TooManyArguments):
            signature = ctx.message.content
            missing_arg = ctx.message.content.split()[-1]
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += (
                " " * signature.index(missing_arg)
                + " " * round(len(missing_arg) / 2)
                + "^\n"
            )
            error_message += f"SyntaxError: the argument {missing_arg} is not required but was passed```"
            await ctx.send(
                embed=discord.Embed(
                    title="Too Many Arguments", description=error_message
                )
            )
        elif "not found" in str(error):
            await ctx.send(
                embed=discord.Embed(title="Not Found", description=str(error))
            )
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I am missing permissions")
        elif isinstance(error, commands.BadArgument):
            signature = ctx.prefix + ctx.invoked_with + " " + ctx.command.signature
            missing_arg_original = error.param.name
            missing_arg = missing_arg_original
            if "_" in missing_arg:
                missing_arg = missing_arg.replace("_", " ")
            missing_arg = missing_arg.title()
            signature = signature.replace(missing_arg_original, missing_arg)
            error_message = "```ml\n"
            error_message += signature + "\n"
            error_message += (
                " " * signature.index(missing_arg)
                + " " * round(len(missing_arg) / 2)
                + "^\n"
            )
            error_message += (
                f"SyntaxError: the required argument {missing_arg} is missing```"
            )
            await ctx.send(
                embed=discord.Embed(title="Missing Argument", description=error_message)
            )
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Slow Down!",
                description=(
                    f"The command `{ctx.command}` is on cooldown, "
                    f"please try again after **{round(error.retry_after, 2)}** seconds."
                    "\nPatience, patience."
                ),
                colour=16711680,
            )
            await ctx.send(embed=embed)
        else:
            if ctx.author == ctx.owner:
                botembed = discord.Embed(
                    description=(
                        f"Hey wasi, umm your command didn't work properly. Go and fix it pls"
                    )
                )
                tb = "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
                if len(tb) < 1023:
                    botembed.add_field(
                        name="Traceback",
                        value="```python\n" + tb + "\n```",
                        inline=False,
                    )
                    message = await ctx.send(embed=botembed)
                else:
                    message = await ctx.send(
                        embed=botembed,
                        file=discord.File(
                            io.StringIO(
                                "".join(
                                    traceback.format_exception(
                                        type(error), error, error.__traceback__
                                    )
                                )
                            ),
                            filename="traceback.py",
                        ),
                    )
            else:
                botembed = discord.Embed(
                    title="Error",
                    description="Ask owner to fix by pressing :white_check_mark:",
                    color=discord.Color.red(),
                )
                message = await ctx.send(embed=botembed)
            await message.add_reaction("\u2705")

            def check(
                reaction, user
            ):  # r = discord.Reaction, u = discord.Member or discord.User.
                return (
                    user.id == ctx.author.id
                    and reaction.message.channel.id == ctx.channel.id
                )

            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=20
                )
            except asyncio.TimeoutError:
                try:
                    botembed.set_footer(
                        icon_url=ctx.author.avatar_url,
                        text="You were too late to answer",
                    )
                    await message.edit(embed=botembed)
                    return await message.clear_reactions()
                except discord.Forbidden:
                    botembed.set_footer(
                        icon_url=ctx.author.avatar_url,
                        text="You were too late to answer",
                    )
                    await message.edit(embed=botembed)
                    me = ctx.guild.me if ctx.guild else self.bot.user
                    return await message.remove_reaction("\u2705", me)
            else:
                if reaction.emoji == "\u2705":
                    botembed.set_footer(
                        icon_url=ctx.author.avatar_url,
                        text="Reported to The Support Server",
                    )
                    await message.edit(embed=botembed)
                    guild = self.bot.get_guild(576016234152198155)
                    channel = guild.get_channel(739673341388128266)
                    embed = discord.Embed(color=0x2F3136)
                    embed.set_author(name="Error")
                    embed.add_field(name="User", value=ctx.author)
                    embed.add_field(
                        name="Guild", value=ctx.guild.name if ctx.guild else "DM"
                    )
                    embed.add_field(name="Message", value=ctx.message.content)
                    embed.add_field(name="Error", value=f"```{str(error)}```")
                    try:
                        embed.add_field(
                            name="Traceback",
                            value="```python\n"
                            + "".join(
                                traceback.format_exception(
                                    type(error), error, error.__traceback__
                                )
                            )
                            + "\n```",
                            inline=False,
                        )
                        console.print_exception(show_locals=True)
                    except:
                        pass
                    embed.add_field(
                        name="Message Links",
                        value=(
                            f"[User Message]({ctx.message.jump_url})\n[Bot Message]({message.jump_url})"
                        ),
                    )
                    await ctx.owner.send(embed=embed)
                    return
            raise error


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Errors(bot))
