import discord
from discord.ext import commands
import humanize, datetime, difflib


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["halp", "h"],
        description="Sends help :)",
        usage="help `[command]`",
    )
    async def helpcommand(self, ctx, command: str = None):
        all_commands = ""
        if command is None:
            if ctx.guild is None:
                color = 0x2F3136
            else:
                color = ctx.guild.me.color
            cogs = list(iter(self.bot.cogs))
            cogs.sort()
            text = ""
            for cog_name in cogs:
                cog = self.bot.get_cog(cog_name)
                cog_commands = cog.get_commands()
                text += f"**{cog_name}: **"
                if len(cog_commands) > 3:
                    text += "\n"
                text_alt += ", ".join([f'`{command}`' for command in cog_commands])
                text += f"\n{text_alt}"
            embed = discord.Embed(title="Help", description=text)
            embed.add_field(
                name="Help for the Help Command",
                value=f"```diff\n+ Type {ctx.prefix}help <command> for more help on a command!\n+ Type {ctx.prefix}help <cog> for help on a Cog```",
            )
            await ctx.send(embed=embed)
        else:
            all_commands_list = []
            all_commands_name_list = []
            command_for_use = None
            for i in self.bot.commands:
                all_commands_name_list.append(i.name)
                if (
                    i.name == command.strip().lower()
                    or command.strip().lower() in i.aliases
                ):
                    command_for_use = i
            if not command_for_use is None:
                aliases = ""
                for i in command_for_use.aliases:
                    aliases += f"`{i}`, "
                embed = discord.Embed(
                    color=0x2F3136,
                    description=f"```diff\n- [] = optional argument\n- <> = required argument\n- Do NOT type these when using commands!\n+ Type {ctx.prefix}help for a list of commands!```",
                )

                embed.set_author(name=str(command_for_use.name))

                embed.add_field(name="Name", value=command_for_use.name)
                embed.add_field(
                    name="Description", value=command_for_use.description, inline=False
                )
                if not len(aliases) == 0:
                    embed.add_field(name="Aliases", value=aliases[:-2])
                else:
                    pass
                if not command_for_use.usage is None:
                    embed.add_field(
                        name="Usage", value=ctx.prefix + command_for_use.usage
                    )
                else:
                    embed.add_field(
                        name="Usage",
                        value=ctx.prefix
                        + command_for_use.name
                        + " "
                        + " ".join(
                            [
                                f"`{i}`"
                                for i in self.bot.get_command(
                                    command_for_use.name
                                ).signature.split(" ")
                            ]
                        ),
                    )
                if command_for_use._buckets._cooldown is None:
                    embed.add_field(name="Cooldown", value="None")
                else:
                    embed.add_field(
                        name="Cooldown",
                        value=f"{command_for_use._buckets._cooldown.per} seconds ({humanize.naturaldelta(datetime.timedelta(seconds=int(command_for_use._buckets._cooldown.per)))}) per {command_for_use._buckets._cooldown.rate} commands per {str(command_for_use._buckets._cooldown.type).split('.')[1].title()}",
                    )
                await ctx.send(embed=embed)
            else:
                try:
                    embed = discord.Embed(
                        title=f'Command "{str(command)}" was not found',
                        description=f"Did you mean `{difflib.get_close_matches(command.strip().lower(), all_commands_name_list, n=1, cutoff=0.2)[0]}`",
                    )
                except IndexError:
                    embed = discord.Embed(title="Not Found", color=0x2F3136)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
