import asyncio
import discord
import humanize
import datetime
from tabulate import tabulate
import random
import time as timemodule
from discord.ext import menus

from discord.ext import commands
from collections import Counter
from discord.ext.commands import BucketType

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

async def _basic_cleanup_strategy(self, ctx, search):
    count = 0
    async for msg in ctx.history(limit=search, before=ctx.message):
        if msg.author == ctx.me:
            await msg.delete()
            count += 1
    return {"Bot": count}


async def _complex_cleanup_strategy(self, ctx, search):
    prefix_for_this_guild = await self.bot.db.fetchrow(
        """
            SELECT prefix
            FROM guilds
            WHERE id=$1
            """,
        ctx.message.guild.id,
    )
    prefix = str(prefix_for_this_guild["prefix"])

    def check(m):
        return m.author == ctx.me or m.content.startswith(prefix)

    deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
    return Counter(m.author.display_name for m in deleted)

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

class PaginationMaster(menus.MenuPages):
    def __init__(self, source):
        super().__init__(source=source, check_embeds=True)

    async def finalize(self, timed_out):
        try:
            if timed_out:
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except discord.HTTPException:
            pass

    @menus.button('\N{INFORMATION SOURCE}\ufe0f', position=menus.Last(3))
    async def show_help(self, payload):
        """shows this message"""
        embed = discord.Embed(title='Paginator help', description='Hello! Welcome to the help page.')
        messages = []
        for (emoji, button) in self.buttons.items():
            messages.append(f'{emoji}: {button.action.__doc__}')

        embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)
        embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

    @menus.button('\N{INPUT SYMBOL FOR NUMBERS}', position=menus.Last(1.5))
    async def numbered_page(self, payload):
        """lets you type a page number to go to"""
        channel = self.message.channel
        author_id = payload.user_id
        to_delete = []
        to_delete.append(await channel.send('What page do you want to go to?'))

        def message_check(m):
            return m.author.id == author_id and \
                   channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            await self.show_checked_page(page - 1)

        try:
            await channel.delete_messages(to_delete)
        except Exception:
            pass
class BotHelpPageSource(menus.ListPageSource):
    def __init__(self, help_command, commands):
        # entries = [(cog, len(sub)) for cog, sub in commands.items()]
        # entries.sort(key=lambda t: (t[0].qualified_name, t[1]), reverse=True)
        super().__init__(entries=sorted(commands.keys(), key=lambda c: c.qualified_name), per_page=6)
        self.commands = commands
        self.help_command = help_command
        self.prefix = help_command.clean_prefix

    def format_commands(self, cog, commands):
        # A field can only have 1024 characters so we need to paginate a bit
        # just in case it doesn't fit perfectly
        # However, we have 6 per page so I'll try cutting it off at around 800 instead
        # Since there's a 6000 character limit overall in the embed
        if cog.description:
            short_doc = cog.description.split('\n', 1)[0] + '\n'
        else:
            short_doc = 'No help found...\n'

        current_count = len(short_doc)
        ending_note = '+%d not shown'
        ending_length = len(ending_note)

        page = []
        for command in commands:
            value = f'`{command.name}`'
            count = len(value) + 1 # The space
            if count + current_count < 800:
                current_count += count
                page.append(value)
            else:
                # If we're maxed out then see if we can add the ending note
                if current_count + ending_length + 1 > 800:
                    # If we are, pop out the last element to make room
                    page.pop()

                # Done paginating so just exit
                break

        if len(page) == len(commands):
            # We're not hiding anything so just return it as-is
            return short_doc + ' '.join(page)

        hidden = len(commands) - len(page)
        return short_doc + ' '.join(page) + '\n' + (ending_note % hidden)


    async def format_page(self, menu, cogs):
        prefix = menu.ctx.prefix
        description = f'Use "{prefix}help command" for more info on a command.\n' \
                      f'Use "{prefix}help category" for more info on a category.\n' \
                       'For more help, join the official bot support server: https://discord.gg/5jn3bQX'

        embed = discord.Embed(title='Categories', description=description, colour=get_random_color())

        for cog in cogs:
            commands = self.commands.get(cog)
            if commands:
                value = self.format_commands(cog, commands)
                embed.add_field(name=cog.qualified_name, value=value, inline=True)

        maximum = self.get_max_pages()
        embed.set_footer(text=f'Page {menu.current_page + 1}/{maximum}')
        return embed

class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group, commands, *, prefix):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    async def format_page(self, menu, commands):
        embed = discord.Embed(title=self.title, description=self.description, colour=get_random_color())

        for command in commands:
            signature = f'{command.qualified_name} {command.signature}'
            embed.add_field(name=signature, value=command.short_doc or 'No help given...', inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed

class HelpMenu(PaginationMaster):
    def __init__(self, source):
        super().__init__(source)

    @menus.button('\N{WHITE QUESTION MARK ORNAMENT}', position=menus.Last(5))
    async def show_bot_help(self, payload):
        """shows how to use the bot"""

        embed = discord.Embed(title='Using the bot', colour=get_random_color())
        embed.title = 'Using the bot'
        embed.description = 'Hello! Welcome to the help page.'

        entries = (
            ('<argument>', 'This means the argument is __**required**__.'),
            ('[argument]', 'This means the argument is __**optional**__.'),
            ('[A|B]', 'This means that it can be __**either A or B**__.'),
            ('[argument...]', 'This means you can have multiple arguments.\n' \
                              'Now that you know the basics, it should be noted that...\n' \
                              '__**You do not type in the brackets!**__')
        )

        embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

        for name, value in entries:
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
        await self.message.edit(embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Shows help about the bot, a command, or a category',
            'aliases': ["h"]
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True)

        all_commands = {}
        for command in entries:
            if command.cog is None:
                continue
            try:
                all_commands[command.cog].append(command)
            except KeyError:
                all_commands[command.cog] = [command]


        menu = HelpMenu(BotHelpPageSource(self, all_commands))
        await menu.start(self.context)

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix=self.clean_prefix))
        await menu.start(self.context)

    async def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command._buckets._cooldown:
            embed_like.add_field(name="Cooldown", value=f"{command._buckets._cooldown.per} seconds per {command._buckets._cooldown.rate} commands per {str(command._buckets._cooldown.type).split('.')[1]}")
        command_usage = await .db.fetchrow("""
                    SELECT *
                    FROM usages
                    WHERE command_name = $1;
                    """,
                    command.name,
        )
        embed.add_field(name="Popularity", value=f"Used {command_usage['usage']} times")
        if not command.help is None:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.description or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=get_random_color())
        await self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.clean_prefix)
        await self.common_command_formatting(source, group)
        menu = HelpMenu(source)
        await menu.start(self.context)
class Bot(commands.Cog):
    """All the bot rleated commands
    """
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand(bot)
        bot.help_command.cog = self

    @commands.command(description="Used to test if bot is online")
    async def hello(
        self,
        ctx,
    ):
        await ctx.send("Hi im online :)")

    @commands.command(aliases=["p"], description="Shows the bot's speed")
    async def ping(
        self,
        ctx,
    ):
        start = timemodule.perf_counter()
        embed = discord.Embed(
            description="**Websocket Latency** = Time it takes to recive data from the discord API\n**Response Time** = Time it took mske this embed\n**Bot Latency** = Time needed to send/edit messages"
        )
        embed.set_author(name="Ping")
        embed.set_footer(text=f"Asked by {ctx.author}")
        embed.add_field(
            name="Websocket Latency", value=f"{round(self.bot.latency * 1000)}ms"
        )
        message = await ctx.send(embed=embed)
        end = timemodule.perf_counter()
        message_ping = (end - start) * 1000
        embed.set_author(name="Ping")
        embed.set_footer(text=f"Asked by {ctx.author}")
        embed.add_field(
            name="Response Time",
            value=f"{round((message.created_at - ctx.message.created_at).total_seconds() / 1000, 4)}ms",
        )
        embed.add_field(name="Bot Latency", value=f"{round(message_ping)}ms")
        await message.edit(embed=embed)

    @commands.command(description="Get a invite link to the bots support server")
    async def support(
        self,
        ctx,
    ):
        await ctx.send("https://discord.gg/5jn3bQX")


    @commands.command(aliases=["info"])
    async def botinfo(self, ctx):
        """Lists some general stats about the bot."""
        bot_member = self.bot.user if not ctx.guild else ctx.guild.me
        color = bot_member.color if isinstance(bot_member,discord.Member) else 0x2F3136
        message = await ctx.send(embed=discord.Embed(title="Gathering info...", color=color))
        
        # Get guild count
        guild_count = "{:,}".format(len(self.bot.guilds))
        
        # Try to do this more efficiently, and faster
        total_members = [x.id for x in self.bot.get_all_members()]
        unique_members = set(total_members)
        if len(total_members) == len(unique_members):
            member_count = "{:,}".format(len(total_members))
        else:
            member_count = "{:,} ({:,} unique)".format(len(total_members), len(unique_members))
            
        # Get commands/cogs count
        cog_amnt  = 0
        empty_cog = 0
        for cog in self.bot.cogs:
            visible = []
            for c in self.bot.get_cog(cog).get_commands():
                if c.hidden:
                    continue
                visible.append(c)
            if not len(visible):
                empty_cog +=1
                # Skip empty cogs
                continue
            cog_amnt += 1
        
        cog_count = "{:,} cog".format(cog_amnt)
        # Easy way to append "s" if needed:
        if not len(self.bot.cogs) == 1:
            cog_count += "s"
        if empty_cog:
            cog_count += " [{:,} without commands]".format(empty_cog)

        visible = []
        for command in self.bot.commands:
            if command.hidden:
                continue
            visible.append(command)
            
        command_count = "{:,}".format(len(visible))
        
        # Get localized created time

        # Get the current prefix
        prefix = await self.bot.command_prefix(self.bot, ctx.message)
        prefix = ", ".join([x for x in prefix if not x == "<@!{}> ".format(self.bot.user.id)])

        # Get the owners
        
        
        owners = "Wasi Master#4245"
        # Get bot's avatar url
        avatar = bot_member.avatar_url
        if not len(avatar):
            avatar = bot_member.default_avatar_url
        
        # Build the embed
        fields = [
            {"name":"Members","value":member_count,"inline":True},
            {"name":"Servers","value":guild_count,"inline":True},
            {"name":"Commands","value":command_count + " (in {})".format(cog_count),"inline":True},
            {"name":"Owners","value":owners,"inline":True},
            {"name":"Prefixes","value":prefix,"inline":True},
            {"name":"Shard Count","value":self.bot.shard_count,"inline":True}
        ]
        if isinstance(bot_member,discord.Member):
            # Get status
            status_text = get_status(str(bot_member.status))
            fields.append({"name":"Status","value":status_text,"inline":True})

            if bot_member.activity and bot_member.activity.name:
                play_list = [ "Playing", "Streaming", "Listening to", "Watching" ]
                try:
                    play_string = play_list[bot_member.activity.type]
                except:
                    play_string = "Playing"
                fields.append({"name":play_string,"value":str(bot_member.activity.name),"inline":True})
                if bot_member.activity.type == 1:
                    # Add the URL too
                    fields.append({"name":"Stream URL","value":"[Watch Now]({})".format(bot_member.activity.url),"inline":True})
        embed = discord.Embed(
            title=ctx.guild.me.display_name + " Info",
            color=color,
            description="Current Bot Information",
            thumbnail=avatar
        )
        for field in fields:
            embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        # Update the embed
        await message.edit(embed=embed)
    @commands.command(
        aliases=["sug", "suggestion", "rep", "report"],
        description="Suggest a thing to be added to the bot",
    )
    @commands.cooldown(1, 3600, BucketType.user)
    async def suggest(self, ctx, *, suggestion: commands.clean_content):
        guild = self.bot.get_guild(576016234152198155)
        channel = guild.get_channel(740071107041689631)
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name="Suggestion Added")
        embed.add_field(name="User", value=ctx.message.author)
        embed.add_field(name="Guild", value=ctx.guild.name)
        embed.add_field(name="Suggestion", value=f"```{str(suggestion)}```")
        message = await channel.send(embed=embed)
        await ctx.send("Suggestion sent")
        await message.add_reaction("\u2b06\ufe0f")
        await message.add_reaction("\u2b07\ufe0f")

    @commands.command(
        aliases=["chpfp", "cp"], description="Change the bots profile picture on random"
    )
    @commands.cooldown(2, 900, BucketType.default)
    async def changepfp(
        self,
        ctx,
    ):
        pfps = [
            "profile_pics/pink.png",
            "profile_pics/red.png",
            "profile_pics/blue.png",
            "profile_pics/green.png",
            "profile_pics/cyan.png",
        ]
        pfp = random.choice(pfps)
        with open(pfp, "rb") as f:
            avatar = f.read()
            await self.bot.user.edit(avatar=avatar)
            file = discord.File(pfp, filename="avatar.png")
            await ctx.send("Changed Profile picture to:", file=file)
            server = self.bot.get_guild(576016234152198155)
            channel = server.get_channel(741371556277518427)
            embed = discord.Embed(
                title=f"Avatar was changed by {ctx.author}", color=0x2F3136
            )
            await channel.send(embed=embed)
        f.close()

    @commands.command(
        aliases=["usr", "user"], description="Shows usage statistics about users"
    )
    @commands.cooldown(1, 10, BucketType.user)
    async def users(
        self,
        ctx,
    ):
        command_usage = await self.bot.db.fetch(
            """
                    SELECT *
                    FROM users;
                    """
        )
        dict_command_usage = {}
        for i in command_usage:
            user = self.bot.get_user(i["user_id"])
            dict_command_usage[str(user)] = i["usage"]
        dict_c_u = list(
            reversed(sorted(dict_command_usage.items(), key=lambda item: item[1]))
        )
        tabular = tabulate(
            dict_c_u[:10], headers=["User", "Commands Used"], tablefmt="fancy_grid"
        )
        await ctx.send(
            embed=discord.Embed(title="Top 10 Users", description=f"```{tabular}```")
        )

    @commands.command(
        aliases=["usg", "usages"], description="Shows usage statistics about commands"
    )
    @commands.cooldown(1, 10, BucketType.user)
    async def usage(
        self,
        ctx,
    ):
        command_usage = await self.bot.db.fetch(
            """
                    SELECT *
                    FROM usages;
                    """
        )
        dict_command_usage = {}
        for i in command_usage:
            dict_command_usage[i["name"]] = i["usage"]
        dict_c_u = list(
            reversed(sorted(dict_command_usage.items(), key=lambda item: item[1]))
        )
        tabular = tabulate(
            dict_c_u[:15], headers=["Name", "Usage"], tablefmt="fancy_grid"
        )
        await ctx.send(
            embed=discord.Embed(title="Top 15 Commands", description=f"```{tabular}```")
        )

    @commands.command(aliases=["upt"], description="Shows how long the bot was up for")
    async def uptime(
        self,
        ctx,
    ):
        delta = datetime.datetime.utcnow() - ctx.bot.started_at
        precisedelta = humanize.precisedelta(delta, minimum_unit="seconds")
        naturalday = humanize.naturalday(ctx.bot.started_at)
        if naturalday == "today":
            naturalday = ""
        else:
            naturalday = f"Bot is online since {naturalday}"
        embed = discord.Embed(
            description=f"Bot is online for {precisedelta}\n{naturalday}"
        )
        embed.set_author(name="Bot Uptime")
        embed.set_footer(
            text=f"Note: This also means thr bot hasn’t been updated for {precisedelta} because the bot is restarted to update"
        )
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["clnup"],
        description="Cleans the bot's messages and the person that executed that command's messages if bot has permissions to do that",
    )
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.
        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        You must have Manage Messages permission to use this.
        """

        strategy = _basic_cleanup_strategy
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = _complex_cleanup_strategy

        spammers = await strategy(self, ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)

    @commands.command(
        aliases=["botinvite", "inv"], description="Sends the invite link for the bot"
    )
    async def invite(
        self,
        ctx,
    ):
        await ctx.send(
            embed=discord.Embed(
                title="Invite",
                description="[Invite](https://discordapp.com/oauth2/authorize?client_id=707883141548736512&scope=bot&permissions=109640)",
                color=0x2F3136,
            )
        )

    @commands.command(description="Shows information about the bots server")
    async def servers(
        self,
        ctx,
    ):
        serverlist = []
        memberlist = []
        for guild in self.bot.guilds:
            serverlist.append(guild)
            for member in guild.members:
                memberlist.append(member)
        servers = len(serverlist)
        members = len(memberlist)
        average = round(int(members) / int(servers))
        await ctx.send(
            f"I'm in {servers:3,} servers and there are {members:3,} members ({len(self.bot.users):3,} Unique) total in all servers combined and {average:3,} on average in each server"
        )


def setup(bot):
    bot.add_cog(Bot(bot))
