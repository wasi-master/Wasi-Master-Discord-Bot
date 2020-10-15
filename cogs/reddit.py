import discord
from discord.ext import commands
from datetime import datetime
import random

class Reddit(commands.Cog):
    """Needs to be worked upon
    """
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
        data = js["data"]["children"]
        post = random.choice(data)["data"]
        embed = discord.Embed(
            title=post["title"],
            description=f":thumbsup: Upvotes: {post['ups']}\n:thumbsdown: Downvotes: {post['downs']}",
            timetsamp=datetime.utcfromtimestamp(post["created"])
        )
        try:
            embed.set_image(
                post["preview"]
                ["images"][0]
                ["source"]["url"]
                )
        except:
            pass
def setup(bot):
    bot.add_cog(Reddit(bot))
