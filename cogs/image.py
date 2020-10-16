import discord
import json


from  discord.ext import commands
from  typing import Union, Optional
from  discord.ext.commands import BucketType
from  bytesio import bytesIO

class Image(commands.Cog):
    """Image releated commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["dbf"])
    async def distractedbf(self, ctx, girlfriend: Union[discord.Member, str], boyfriend: Union[discord.Member, str], another_girl: Union[discord.Member, str]):
        """Makes a **distracted boyfriend** meme from the given arguments
        parameters passed can be a user or a name 
        
        the meme basically is a boyfriend being distracted by another girl while his girlfriend is watching him 
        can be used when someone is disregarding something and going for another thing
        """
        if isinstance(girlfriend, discord.Member):
            girlfriend_img = girlfriend.avatar_url
        if isinstance(boyfriend, discord.Member):
            boyfriend_img = boyfriend.avatar_url
        if isinstance(another_girl, discord.Member):
            another_img = another_girl.avatar_url
        
        result = await self.bot.vacefron.distracted_bf(boyfriend_img, girlfriend_img,  another_img)
        await ctx.send(
            f"{boyfriend} is distracted at {another_girl} while {girlfriend} is watching\n\nRendered by {ctx.author}",
            file=discord.File(
                await result.read(bytesio=True),
                filename="Distracted Boyfriend.png")
                )


    @commands.command(aliases=["cmm"])
    async def changemymind(self, ctx, *, text):
        """Makes a change my mind meme from the text
        """
        result = await self.bot.vacefron.change_my_mind(text)
        await ctx.send(
            f"Invoked by {ctx.author}",
            file=discord.File(
                await result.read(bytesio=True),
                filename="Change My Mind.png")
                )


    @commands.command(aliases=["em"])
    async def emergency_meeting(self, ctx, *, text):
        result = await self.bot.vacefron.emergency_meeting(text)
        await ctx.send(
            f"Invoked by {ctx.author}",
            file=discord.File(
                await result.read(bytesio=True),
                filename="Emergency Meeting.png")
                )
    
    
    @commands.command(aliases=["eject", "ejection"])
    async def ejected(self, ctx, person: Union[discord.User, str], color="random", imposter: str = None):
        """Makes a image of ejecting the mentioned user or the name passed
        person can be a user (id, name, name#discriminatir, @mention) or a string
        you can provide a color for the crewmate, defaults to random
        possible colors are the ones available in among us
        example would be `eject @Wasi Master red` to make a ejection image containing Wasi Master and the crewmate color being red
        another example would ne `eject "Donald Trump" red` to make a image with the name being Donald Trump
        """
        if imposter is None:
            imposter = "true"
        else:
            if imposter.lower() == "false" or imposter.lower() == "f":
                imposter = "false"
            else:
                imposter = "true"
        color = color.lower().replace("green", "darkgreen").replace("dark green", "darkgreen")
        if isinstance(person, discord.User):
            person = person.display_name
        if not color in ["black", "blue", "brown", "cyan", "darkgreen", "lime", "orange", "pink", "purple", "red", "white", "yellow"]:
            await ctx.send("Invalid color")
            return
        url = f"https://vacefron.nl/api/ejected?name={person}&impostor={imposter}&crewmate={color}"
        async with self.bot.session.get(url) as j:
            r = await j.read()
        await ctx.send(
            f"{ctx.author} asked for this",
            file=discord.File(
                BytesIO(r),
                filename="Ejected.png")
                )

    @commands.command(aliases=["waste"])
    async def wasted(self, ctx, wasted: discord.User):
        text = wasted.name + " Wasted"
        url=f"https://some-random-api.ml/canvas/wasted?avatar={wasted.avatar_url}"
        async with self.bot.session.get(url) as result:
            file = await result.read()
        
        await ctx.send(
            text,
            file=discord.File(
                file,
                filename="Comment.png")
                )

    @commands.command(aliases=["trigger"])
    async def triggered(self, ctx, to_trigger: discord.User):
        text = to_trigger.name + " is **Triggered**"
        url=f"https://some-random-api.ml/canvas/triggered?avatar={to_trigger.avatar_url}"
        async with self.bot.session.get(url) as result:
            file = await result.read()
        
        await ctx.send(
            text,
            file=discord.File(
                file,
                filename="Comment.png")
                )
    
    @commands.command(aliases=["ytcmnt", "cmnt"])
    async def comment(self, ctx, commenter: Union[discord.User, str], comment):
        if isinstance(commenter, discord.User):
            avatar = commenter.avatar_url
            name = commenter.display_name
        else:
            commenter = str(commenter)
            avatar = "https://www.shit.jpg"

        url = ("https://some-random-api.ml/canvas/youtube-comment"
              f"?avatar={avatar}&username={name}&comment={comment}")
        async with self.bot.session.get(url) as result:
            file = await result.read()
        
        await ctx.send(
            f"{ctx.author} asked for this",
            file=discord.File(
                file,
                filename="Comment.png")
                )

    @commands.command(aliases=["ft"])
    async def firsttime(self, ctx, *, user: Union[discord.User, str] = None):
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await self.bot.vacefron.first_time(avatar)
        await ctx.send(
            f"{ctx.author} made this",
            file=discord.File(
                await r.read(bytesio=True),
                filename="First Time.png")
                )

    @commands.command(aliases=["milkyou", "canmilkyou", "milkable", "icmy"])
    async def icanmilkyou(
        self, ctx, 
        milker: Union[discord.User, str],
        to_milk: Union[discord.User, str]
    ):
        if isinstance(milker, discord.User):
            milker = str(milker.avatar_url)
        if isinstance(to_milk, discord.User):
            to_milk = str(to_milk.avatar_url)
        r = await self.bot.vacefron.i_can_milk_you(milker, to_milk)
        await ctx.send(
            f"{ctx.author} asked for this", 
            file=discord.File(
                await r.read(bytesio=True),
                filename="I can milk you.png")
                )
    
    @commands.command(aliases=["ias"])
    async def iamspeed(self, ctx, whoisspeed: Union[discord.User, str]):
        if isinstance(whoisspeed, discord.User):
            whoisspeed = str(whoisspeed.avatar_url)
        r = await self.bot.vacefron.iam_speed(whoisspeed)
        await ctx.send(
            f"Command Invoked by {ctx.author}",
            file=discord.File(
                await r.read(bytesio=True),
                filename="I am speed.png")
                )
    
    
    @commands.command(aliases=["wd"])
    async def wide(self, ctx, *, user: Union[discord.User, str] = None):
        if user is None:
            user = ctx.author
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await self.bot.vacefron.wide(avatar)
        await ctx.send(
            f"{ctx.author} made this wide",
            file=discord.File(
                await r.read(bytesio=True),
                filename="Wide.png")
                )


    @commands.command(aliases=["stonk"])
    async def stonks(self, ctx, *, user: Union[discord.User, str] = None):
        if isinstance(user, discord.User):
            avatar = str(user.avatar_url)
        else:
            if ctx.message.attachments:
                avatar = ctx.message.attachments[0].url
            if isinstance(user, str):
                avatar = user
        r = await self.bot.vacefron.stonks(avatar)
        await ctx.send(
            f"{ctx.author} made me do this",
            file=discord.File(
                await r.read(bytesio=True),
                filename="Stonks.png")
                )

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

        try:
            embed = discord.Embed(title=f"{member.name} Wanted", color=0x2F3136)
            embed.set_image(url=formatted_json["url"])
            await ctx.send(embed=embed)
        except:
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
