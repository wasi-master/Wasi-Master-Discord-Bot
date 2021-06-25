import datetime

import discord
import humanize
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Sends a message to the owner when bot is added to a guild


        Parameters
        ----------
                guild (discord.Guild): the guild bot was added to
        """
        owner = self.bot.get_user(723234115746398219)
        guild_owner = self.bot.get_user(guild.owner_id)
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
        await self.bot.owner.send(embed=embed)
        await self.bot.db.execute(
            """
                    INSERT INTO guilds (id, prefix)
                    VALUES ($1, $2)
                    """,
            guild.id,
            ",",
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Sends a message to the owner when bot is removed from a guild


        Parameters
        ----------
                guild (discord.Guild): the guild bot was removed from
        """
        owner = self.bot.get_user(723234115746398219)
        guild_owner = self.bot.get_user(guild.owner_id)
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
        await self.bot.owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message in self.bot.command_uses:
            await self.bot.command_uses[message].delete()
        self.bot.snipes[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before in self.bot.command_uses:
            await self.bot.command_uses[before].delete()
        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None or not message.mentions:
            return
        afk_people = []
        for user in message.mentions:
            is_afk = await self.bot.db.fetchrow(
                """
                    SELECT *
                    FROM afk
                    WHERE user_id=$1;
                    """,
                user.id,
            )
            afk_people.append(is_afk)
        if not afk_people:
            return
        else:
            for record in afk_people:
                if not record is None:
                    await message.channel.send(
                        f"Hey {message.author.mention}, the person you mentioned: {self.bot.get_user(record['user_id'])} is currently afk for {humanize.naturaldelta(datetime.datetime.utcnow() - record['last_seen'])}\n\nreason: {record['reason']}"
                    )
        if not message.guild.me in message.mentions:
            return
        if not (await self.bot.get_context(message)).valid:
            return
        prefix = await self.bot.command_prefix(self.bot, message)
        prefix = "\n".join(
            [x for x in prefix if not x == "<@!{}> ".format(self.bot.user.id)]
        )
        await message.channel.send(
            f"Hello, I see that you mentioned me, my prefixes here are \n\n{prefix}"
        )

    @commands.Cog.listener()
    async def on_member_update(self, old, new):
        """Stores status


        Parameters
        ----------
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

        status = await self.bot.db.fetchrow(
            """
                SELECT *
                FROM status
                WHERE user_id=$1
                """,
            new.id,
        )

        if status is None:
            await self.bot.db.execute(
                """
                        INSERT INTO status (last_seen, user_id)
                        VALUES ($1, $2)
                        """,
                time,
                new.id,
            )
        else:
            await self.bot.db.execute(
                """
                    UPDATE status
                    SET last_seen = $2
                    WHERE user_id = $1;
                    """,
                new.id,
                time,
            )


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Events(bot))
