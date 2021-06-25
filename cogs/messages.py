import datetime
import json

import discord
import humanize
from discord.ext import commands
from discord.ext.commands import BucketType


class Messages(commands.Cog):
    """Message releated commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["fm"], description="Shows the first message in a channel"
    )
    async def firstmessage(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        attachments = ""
        num = 0

        async for i in channel.history(oldest_first=True):
            if i.is_system:
                fmo = i
                break

        embed = discord.Embed(title=f"First message in {channel.name}", color=0x2F3136)
        embed.add_field(name="Message Author", value=fmo.author)
        try:
            embed.add_field(name="Message Content", value=fmo.content)
        except AttributeError:
            embed.add_field(name="Message Content", value="Failed to get the content")
        if len(fmo.attachments) > 0:
            for i in fmo.attachments:
                num += 1
                attachments += f"[{i.filename}](i.url)\n"
            embed.add_field(name="Attatchments", value=attachments)
        embed.add_field(
            name="Message sent at",
            value=f'{fmo.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}   \
            ({humanize.precisedelta(datetime.datetime.utcnow() - fmo.created_at)})',
        )
        if not fmo.edited_at is None:
            embed.add_field(
                name="Edited",
                value=f'{fmo.edited_at.strftime("%a, %d %B %Y, %H:%M:%S")}   \
                ({humanize.precisedelta(datetime.datetime.utcnow() - fmo.edited_at)})',
            )
        embed.add_field(name="Url", value=fmo.jump_url)
        embed.set_footer(
            text="Times are in UTC\nIt doesn’t show a system message such as a member join/leave or server boost "
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["rj"], description="Shows raw json of a message")
    async def rawjson(self, ctx, message_id: int):
        res = await self.bot.http.get_message(ctx.channel.id, message_id)
        await ctx.send(f"```json\n{json.dumps(res, indent=4)}```")

    @commands.command(aliases=["raw"], description="See a raw version of a message")
    async def rawmessage(self, ctx, message_id: int):
        message = await ctx.channel.fetch_message(message_id)
        res = discord.utils.escape_markdown(message.content)
        await ctx.send(res)

    @commands.command(description="See your/other user's messages in a channel")
    async def messages(self, ctx, limit=500):
        msg1 = await ctx.send(f"Loading {limit} messages <a:typing:597589448607399949>")
        if limit > 5000:
            limit = 5000
        try:
            channel = ctx.channel_mentions[0]
        except IndexError:
            channel = ctx.channel
        try:
            member = ctx.message.mentions[0]
            a = member.mention
        except IndexError:
            member = ctx.author
            a = "You"
        async with ctx.typing():
            messages = await channel.history(limit=limit).flatten()
            count = len([x for x in messages if x.author.id == member.id])
            perc = (100 * int(count)) / int(limit)
            emb = discord.Embed(
                description=f"{a} sent **{count} ({perc}%)** messages in {channel.mention} in the last **{limit}** messages."
            )
            await ctx.send(embed=emb)
        await msg1.delete()

    @commands.command(description="See a list of top active users in a channel")
    @commands.max_concurrency(1, BucketType.channel, wait=True)
    async def top(self, ctx, limit=500, *, channel: discord.TextChannel = None):
        msg1 = await ctx.send("Loading messages <a:typing:597589448607399949>")

        async with ctx.typing():
            if not channel:
                channel = ctx.channel
            if limit > 1000:
                limit = 1000
            res = {}
            ch = await channel.history(limit=limit).flatten()
            for a in ch:
                res[a.author] = {
                    "messages": len([b for b in ch if b.author.id == a.author.id])
                }
            lb = sorted(res, key=lambda x: res[x].get("messages", 0), reverse=True)
            oof = ""
            counter = 0
            for a in lb:
                counter += 1
                if counter > 10:
                    pass
                else:
                    oof += f"{str(a):<20} :: {res[a]['messages']}\n"
            prolog = f"""```prolog
    {'User':<20} :: Messages

    {oof}
    ```
    """
            emb = discord.Embed(
                description=f"Top {channel.mention} users (last {limit} messages): {prolog}",
                colour=discord.Color.blurple(),
            )
            await ctx.send(embed=emb)
            await msg1.delete()


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Messages(bot))
