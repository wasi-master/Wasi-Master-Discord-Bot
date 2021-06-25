import json
import random
from datetime import datetime

import discord
from discord.ext import commands


class Reddit(commands.Cog):
    """Needs to be worked upon"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="subreddit", aliases=["sr"])
    async def _subreddit(self, ctx, subreddit, post_filter=None):
        """Gets a randon post from a subreddit

        you can pass a optional post_filter that is either hot or top.
        so a command with hot as the post_filter would look like
        `subreddit r/memes hot`

        """
        if not "r/" in subreddit:
            if not subreddit.count("/") > 0:
                subreddit = "r/" + subreddit
            else:
                await ctx.send("Invalid subreddit")
                return
        base = "https://www.reddit.com/"
        if post_filter is None:
            url = f"{base}{subreddit}.json"
        elif post_filter == "hot":
            url = f"{base}{subreddit}/hot.json"
        elif post_filter == "top":
            url = f"{base}{subreddit}/top.json"
        else:
            await ctx.send("Invalid post filter")
            return
        async with self.bot.session.get(url, allow_redirects=True) as cs:
            js = await cs.json()
        if js.get("reason"):
            return await ctx.send(js["reason"])
        data = js["data"]["children"]
        if ctx.guild and not ctx.channel.is_nsfw():
            data = [i for i in data if not i["data"]["over_18"]]
        post = random.choice(data)["data"]
        # dv = round(post['ups']*(1-post['upvote_ratio']))
        embed = discord.Embed(
            title=post["title"],
            description=post["selftext"],
            timestamp=datetime.utcfromtimestamp(post["created"]),
            url=base + post["permalink"],
            color=0xFF5700,
        )
        if url := post.get("url_overridden_by_dest"):
            embed.set_image(url=url)
        embed.set_author(
            name=f'Uploaded by u/{post["author"]}',
            url=f"https://www.reddit.com/u/{post['author']}",
        )
        await ctx.send(base + post["permalink"], embed=embed)


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Reddit(bot))
