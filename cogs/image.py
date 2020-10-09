import discord
import json
import vacefron

from discord.ext import commands
from typing import Union, Optional
from discord.ext.commands import BucketType, Greedy

class Image(commands.Cog):
    """Image releated commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["dbf"])
    async def distractedbf(self, ctx, girlfriend_name: Union[discord.Member, str], boyfriend_name: Union[discord.Member, str], another_girl: Union[discord.Member, str]):
        """Makes a **distracted boyfriend** meme from the given arguments
        parameters passed can be a user or a name 
        
        the meme basically is a boyfriend being distracted by another girl while his girlfriend is watching him 
        can be used when someone is disregarding something and going for another thing
        """
        if isinstance(girlfriend_name, discord.Member):
            gf_name = girlfriend_name.display_name
        if isinstance(boyfriend_name, discord.Member):
            gf_name = boyfriend_name.display_name
        if isinstance(another_girl, discord.Member):
            gf_name = another_girl.display_name
        
        result = await vacefron.distracted_bf(boyfriend_name, girlfriend_name,  another_girl)
        await ctx.send(f"{boyfriend_name} is distractes at {another_girl} while {girlfriend_name} is watching\n\nRendered by {ctx.author}", file=discord.File(await result.read()))


    @commands.command()
    async def changemymind(self, ctx, text):
        """Makes a change my mind meme from the text
        """
        result = await vacefron.change_my_mind(text)
        await ctx.send(f"Invoked by {ctx.author}", file=await result.read())


    @commands.command(aliases=["em"])
    async def emergency_meeting(self, ctx, text):
        result = await vacefron.emergency_meeting(text)
        await ctx.send(f"Invoked by {ctx.author}", file=await result.read())
    
    
    @commands.command(aliases=["eject", "ejection"])
    async def ejected(self, ctx, person: Union[Greedy[discord.User], str], color="random"):
        color = color.lower()
        if isinstance(person, discord.User):
            person = person.display_name
        r = await vacefron.ejected(person, color)
        await ctx.send(f"{ctx.author} asked for this", file=discord.File(await r.read()))
    
    @commands.command(aliases=["ft"])
    async def firsttime(self, ctx, *, user: Union[discord.User, str] = None):
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await vacefron.first_time(avatar)
        await ctx.send(f"{ctx.author} made this", file=discord.File(await r.read()))

    @commands.command(aliases=["milkyou", "canmilkyou", "milkable", "icmy"])
    async def icanmilkyou(
        self, ctx, 
        milker: Union[Greedy[discord.User], str],
        to_milk: Union[Greedy[discord.User], str]
    ):
        if isinstance(milker, discord.User):
            milker = str(milker.avatar_url)
        if isinstance(to_milk, discord.User):
            to_milk = str(to_milk.avatar_url)
        r = await vacefron.i_can_milk_you(milker, to_milk)
        await ctx.send(f"{ctx.author} asked for this", file=disocrd.File(await r.read()))
    
    @commands.command(aliases=["ias"])
    async def iamspeed(ctx, whoisspeed: Union[Greedy[discord.User], str]):
        if isinstance(whoisspeed, discord.User):
            whoisspeed = str(whoisspeed.avatar_url)
        r = await vacefron.iam_speed(whoisspeed)
        await ctx.send(f"Command Invoked by {ctx.author}", file=discord.File(r.read()))
    
    
    @commands.command(aliases=["wd"])
    async def wide(self, ctx, *, user: Union[discord.User, str] = None):
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await vacefron.wide(avatar)
        await ctx.send(f"{ctx.author} made this wide", file=discord.File(await r.read()))


    @commands.command(aliases=["stonk"])
    async def stonks(self, ctx, *, user: Union[discord.User, str] = None):
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await vacefron.stonks(avatar)
        await ctx.send(f"{ctx.author} made this", file=discord.File(await r.read()))

    @commands.command(description="Invert your or another users profile picture")
    async def invert(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/invert?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Blur your or another users profile picture")
    async def blur(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/blur?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(
        aliases=["b&w", "blackandwhite"],
        description="Convert to Black And White your or another users profile picture",
    )
    async def bw(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/b&w?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Pixelate your or another users profile picture")
    async def pixelate(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/pixelate?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(
        description="See a gay version of your or another users profile picture"
    )
    async def gay(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author
        url = f"https://api.alexflipnote.dev/filter/gay?image={member.avatar_url}"
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=url)
        e.set_footer(text=f"Asked by {ctx.message.author}")
        await ctx.send(embed=e)

    @commands.command(description="Generates a minecraft style achievement image")
    async def achievement(self, ctx, icon: Optional[int]=None, text: str = None):
        if text == None:
            text = "Dumb, didn't provide a text to go here"
        image = await (
            await self.bot.alex_api.achievement(text=text, icon=icon)
        ).read()  # BytesIO
        await ctx.send(
            f"Rendered by {ctx.author}",
            file=discord.File(image, filename="achievement.png"),
        )

    @commands.command(description='Generates a "Worse than hitler" image')
    async def hitler(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/hitler", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(
                title=f"{member.name} is Worse Than Hitler", color=0x2F3136
            )
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(description="Tweets a text")
    async def tweet(self, ctx, member: discord.Member = None, *, text):
        member = member or ctx.message.author
        username = member.name

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
            "name": username,
            "text": text,
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/tweet", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(
                title=f"{member.name} Posted a new tweet", color=0x2F3136
            )
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(description="Generates a wanted poster")
    async def wanted(self, ctx, member: discord.Member = None):
        member = member or ctx.message.author

        headers = {
            "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
            "url": str(member.avatar_url),
        }
        async with ctx.typing():
            async with self.bot.session.post(
                "https://dagpi.tk/api/wanted", headers=headers
            ) as response:
                loaded_response = await response.text()
            formatted_json = json.loads(loaded_response)

        if formatted_json["success"]:
            embed = discord.Embed(title=f"{member.name} Wanted", color=0x2F3136)
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error")

    @commands.command(
        aliases=["upscaled"], description="Upscales a users profile picture"
    )
    @commands.cooldown(1, 60, type=BucketType.user)
    async def upscale(self, ctx, scale_type, *, member: discord.Member = None):
        member = member or ctx.author
        if scale_type.lower() == "anime":
            url = "https://api.deepai.org/api/waifu2x"
        elif scale_type.lower() == "normal":
            url = "https://api.deepai.org/api/torch-srgan"
        else:
            await ctx.send("Invalid Format")

        message = await ctx.send("May take up to 15 seconds, Wait till then")
        async with self.bot.session.post(
            url,
            data={
                "image": str(member.avatar_url),
            },
            headers={"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"},
        ) as resp:
            fj = json.loads(await resp.text())
            url = fj["output_url"]

        await message.delete()
        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=f"{member.name}'s Profile Picture Upscaled")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Image(bot))
