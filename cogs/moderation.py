import discord
import asyncio
from discord.ext import commands
from collections import Counter
from typing import Union


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Kicks a user ")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.mention}")

    @commands.command(
        aliases=["setnick", "setnickname", "nickname", "changenickname", "chnick"],
        description="Sets a users nickname",
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nick):
        await member.edit(nick=nick)
        await ctx.send(f"Nickname was changed for {member.mention} ")

    @commands.command(description="Bans a user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}")

    @commands.command(
        description="Unbans a previously banned user with their name and discriminator "
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: Union[int, str]):
        if isinstance(member, str):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (
                    member_name,
                    member_discriminator,
                ):
                    await ctx.guild.unban(user)
                    success = True
            if success:
                await ctx.send(f"Unbanned {user.mention}")
            else:
                await ctx.send("User not found")
        else:
            await ctx.guild.ban(discord.Object(id=member))

    @commands.command(
        name="clear",
        aliases=["remove", "delete", "erase", "c"],
        description=" clears a certain amount of messages",
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, member: discord.Member = None):
        def check(message):
            return message.author == member

        await ctx.message.delete()
        if not member:

            def reaction_check(r, u):
                return (
                    r.message.channel.id == ctx.channel.id
                    and reaction.message.id == ctx.message.id
                    and reaction.message.author.permissions.manage_messages
                )

            deleted = await ctx.channel.purge(limit=amount)
            a = "message" if len(deleted) else "messages"
            spammers = Counter(m.author.display_name for m in deleted)
            message = deleted = sum(spammers.values())
            messages = [
                f'{deleted} message{" was" if deleted == 1 else "s were"} removed.'
            ]
            if deleted:
                messages.append("")
                spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
                messages.extend(
                    f"- {count} by **{author}**" for author, count in spammers
                )
            msg = await ctx.send("\n".join(messages))
            await msg.add_reaction("\U0001f6ab")
            await msg.add_reaction("\U0001f512")
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=reaction_check, timeout=10
                )
                if reaction.emoji == "\U0001f6ab":
                    await msg.delete()
                else:
                    try:
                        await msg.clear_reactions()
                        return
                    except:
                        await msg.remove_reaction("\U0001f512", ctx.guild.me)
                        await msg.remove_reaction("\U0001f6ab", ctx.guild.me)
                        return
            except asyncio.TimeoutError:
                await msg.delete()
                return
        else:
            deleted = await ctx.channel.purge(
                limit=amount,
                check=check,
                reason=f"Deleted {member} (ID: {member.id})'s messages by {ctx.author} (ID: {ctx.author.id})",
            )
            a = "message" if len(deleted) else "messages"
            await ctx.message.delete()
            await ctx.send(
                f"Deleted `{len(deleted)}` messages by {member}", delete_after=3
            )

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the amount of messages to delete")

    @commands.command()
    async def mute(self, ctx, user: discord.Member, reason="No Reason Specified"):
        role = discord.utils.get(
            ctx.guild.roles, name="Muted"
        )  
        if not role:  
            try:  
                muted = await ctx.guild.create_role(
                    name="Muted", reason="To use for muting"
                )
                for channel in ctx.guild.channels:  
                    await channel.set_permissions(
                        muted,
                        send_messages=False,
                        read_message_history=False,
                        read_messages=False,
                    )
            except discord.Forbidden:
                return await ctx.send(
                    "I have no permissions to make a muted role"
                )  
            await user.add_roles(muted)  
            await ctx.send(f"{user.mention} has been muted for {reason}")
        else:
            await user.add_roles(role)  
            await ctx.send(f"{user.mention} has been muted for {reason}")

    @commands.command(aliases=["sd"], description="Custom Slow Mode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, slowmode: int):
        if slowmode > 21600:
            await ctx.send("Slow Mode too long")
        else:
            await ctx.channel.edit(slowmode_delay=slowmode)
            await ctx.send(
                f"Slow Mode set to {slowmode} seconds for {ctx.channel.mention}"
            )

    @commands.command(
        description="Changes role for a user (removes if he has the role, adds the role if he doesn't)"
    )
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        if role in member.roles:  
            await member.remove_roles(role)
            embed = discord.Embed(colour=16711680, timestamp=ctx.message.created_at)
            embed.set_author(name=f"Role Changed for {member}")
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Removed Role", value=f"@{role}")
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(colour=65280, timestamp=ctx.message.created_at)
            embed.set_author(name=f"Role Changed for {member}")
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Added Role", value=f"@{role}")
            await ctx.send(embed=embed)

    @commands.command(
        description="See your or other peoples permissions",
        aliases=["permissions"],
        usage="perms `[@mention]`\n\nperms\nperms @Wasi Master",
    )
    @commands.has_permissions(manage_roles=True)
    async def perms(
        self, ctx, member: discord.Member = None, channel: discord.TextChannel = None
    ):
        channel = channel or ctx.channel
        member = member or ctx.author
        perms = []
        permstr = ""
        for i in member.permissions_in(channel):
            perms.append(i)
        perms = dict(perms)
        for i in perms:
            if perms[i]:
                permstr += (
                    f"<:greenTick:596576670815879169> {i.replace('_', ' ').title()}\n"
                )
            else:
                continue
                
        embed = discord.Embed(
            title=f"{member}'s Permissions", description=permstr, color=0x2F3136
        )
        await ctx.send(embed=embed)


@commands.command(
    aliases=["nk"],
    description="Nuke a channel\nCreates a new channel with all the same properties (permissions, name, topic etc.) ",
)
@commands.has_permissions(manage_channels=True)
async def nuke(self, ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await ctx.send(
        "Are you sure you want to nuke this channel?\n type `yes` to confirm or `no` to decline"
    )

    def check(m):  
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    try:
        name = await self.bot.wait_for("message", check=check, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send(f"You didnt respond in 30 seconds :(\n{ctx.author.mention}!")
        return
    else:
        if name.content == "yes":
            message = await ctx.send(f"Okay, Nuking {channel.name}...")
            position = channel.position
            await channel.delete()
            newchannel = await channel.clone(reason=f"Nuked by {ctx.author}")
            await message.delete()
            newchannel.edit(position=position)
            await ctx.send("Channel Nuked")
        elif name.content == "no":
            return await ctx.send("Okay then")
        else:
            return await ctx.send(
                "I was hoping for `yes` or `no` but you said something else :("
            )

    @commands.command(
        aliases=["cln"],
        description="Clone a channel\nCreates a new channel with all the same properties (permissions, name, topic etc.) ",
    )
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await ctx.send(
            "Are you sure you want to clone this channel?\n type `yes` to confirm or `no` to decline"
        )

        def check(m):  
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            name = await self.bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send(f"You didnt respond in 30 seconds :(\n{ctx.author.mention}!")
            return
        else:
            if name.content == "yes":
                message = await ctx.send(f"Okay, cloning {channel.name}...")
                await channel.clone(reason=f"Cloned by {ctx.author}")
                await message.delete()
                await ctx.send("Channel Cloned")
            elif name.content == "no":
                return await ctx.send("Okay then")
            else:
                return await ctx.send(
                    "I was hoping for `yes` or `no` but you said something else :("
                )

    @commands.command(aliases=["lck", "lk"], description="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, *, role: discord.Role = None):
        role = (
            role or ctx.guild.default_role
        )  
        channel = ctx.channel
        try:
            await channel.set_permissions(
                role, send_messages=False, read_message_history=True, read_messages=True
            )
            await ctx.send("Channel Locked")
        except discord.Forbidden:
            return await ctx.send("I have no permissions to lock")

    @commands.command(aliases=["unlck", "ulk"], description=" Unlocks a channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, *, role: discord.Role = None):
        role = (
            role or ctx.guild.default_role
        )  
        channel = ctx.channel
        try:
            await channel.set_permissions(
                role, send_messages=True, read_message_history=True, read_messages=True
            )
            await ctx.send("Channel Unlocked")
        except discord.Forbidden:
            return await ctx.send("I have no permissions to lock")

    @commands.command(description="Unmutes a muted user")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        try:
            await user.remove_roles(
                discord.utils.get(ctx.guild.roles, name="Muted")
            )  
            await ctx.send(f"{user.mention} has been unmuted")
        except discord.Forbidden:
            await ctx.send("No Permissions")

    @commands.command(description="Blocks a user from chatting in current channel.")
    @commands.has_permissions(manage_channels=True)
    async def block(self, ctx, user: discord.Member):
        try:
            await ctx.set_permissions(
                user, send_messages=False
            )  
        except discord.Forbidden:
            await ctx.send("No permissions")

    @commands.command(description="Unblocks a user from current channel")
    @commands.has_permissions(manage_channels=True)
    async def unblock(self, ctx, user: discord.Member):
        try:
            await ctx.set_permissions(
                user, send_messages=True
            )  
        except discord.Forbidden:
            await ctx.send("No permissions")


def setup(bot):
    bot.add_cog(Moderation(bot))
