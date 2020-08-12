import ast
import asyncio
import base64 as base64module
import codecs
from datetime import datetime
import difflib
import discord
import json
import os
import secrets
import time as timemodule
import random

import aiohttp
import async_cleverbot as ac
from bs4 import BeautifulSoup
import humanize
import psutil
import randomcolor
import requests
import wikipedia as wikimodule
import dbl

from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import has_permissions
from discord.ext.commands.cooldowns import BucketType
import urllib.parse


def get_prefix(client, message):
    try:
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        return prefixes[str(message.guild.id)]
    except (KeyError, AttributeError):
        return ","


def convert_sec_to_min(seconds):
    minutes, sec = divmod(seconds, 60)
    return "%02d:%02d" % (minutes, sec)


def get_p(prog, num=0):
    numlist = list(range(0, 101, 4))
    text = ""
    for i in numlist:
        num += 1
        if prog >= i and numlist[num] > prog:
            text += "⬤"
        else:
            text += "—"
    return f"`{text}`"


def get_flag(flag: str):
	if flag == "hypesquad_brilliance":
		return "<:hypesquadbrilliance:724328585363456070>"
	elif flag == "hypesquad_bravery":
		return "<:hypesquadbravery:724328585040625667>"
	elif flag == "hypesquad_balance":
		return "<s:hypesquadbalance:724328585166454845>"
	elif flag == "hypesquad":
		return "<:hypesquad:724328585237626931>"
	elif flag == "early_supporter":
		return "<:earlysupporter:724588086646014034>"
	elif flag == "bug_hunter":
		return "<:bughunt:724588087052861531>"
	elif flag == "bug_hunter_level_2":
		return "<:bughunt2:726775007908462653>"
	elif flag == "verified_bot_developer":
		return "<:verifiedbotdeveloper:740854331154235444>"
	elif flag == "verified_bot":
		return "<:verifiedbot:740855315985072189>"
	elif flag == "partner":
		return "<:partner:724588086461202442>"


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


client = commands.Bot(command_prefix=get_prefix)
dblpy = dbl.DBLClient(client, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjcwNzg4MzE0MTU0ODczNjUxMiIsImJvdCI6dHJ1ZSwiaWF0IjoxNTk2NzM0ODg2fQ.E0VY8HAgvb8V2WcL9x2qBf5hcKBp-WV0BhLLaGSfAPs")
cleverbot = ac.Cleverbot("G[zm^mG5oOVS[J.Y?^YV", context=ac.DictContext())
secureRandom = secrets.SystemRandom()
client.remove_command("help")

@tasks.loop(seconds=86400)
async def update_server_count():
    memberlist = []
    serverlist = []
    for guild in client.guilds:
        serverlist.append(guild)
        for member in guild.members:
            memberlist.append(member)
    await dblpy.post_guild_count()
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(memberlist)} people in {len(serverlist)} servers 😁😁😁",
        )
    )



@client.event
async def on_ready():
    print("Bot is online")
    owner = client.get_user(538332632535007244)
    await owner.send("Bot Online")
    update_server_count.start()
    client.load_extension("jishaku")


@client.event
async def on_guild_join(guild):
    owner = client.get_user(538332632535007244)
    guild_owner = client.get_user(guild.owner_id)
    features = ""
    for i in guild.features:
        features += "\n" + i.title().replace("_", " ")
    embed = discord.Embed(
        title=f"Bot Added To {guild.name}",
        description=f"Name: {guild.name}\nCreated At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')} ({humanize.precisedelta(datetime.utcnow() - guild.created_at)})\nID: {guild.id}\nOwner: {guild_owner}\nIcon Url: [click here]({guild.icon_url})\nRegion: {str(guild.region)}\nVerification Level: {str(guild.verification_level)}\nMembers: {len(guild.members)}\nBoost Level: {guild.premium_tier}\nBoosts: {guild.premium_subscription_count}\nBoosters: {len(guild.premium_subscribers)}\nTotal Channels: {len(guild.channels)}\nText Channels: {len(guild.text_channels)}\nVoice Channels: {len(guild.voice_channels)}\nCategories: {len(guild.categories)}\nRoles: {len(guild.roles)}\nEmojis: {len(guild.emojis)}/{guild.emoji_limit}\nUpload Limit: {round(guild.filesize_limit /1048576 )} Megabytes (MB)\n**Features:** {features}",
    )
    embed.set_thumbnail(url=guild.icon_url)
    await owner.send(embed=embed)
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = ","

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    owner = client.get_user(538332632535007244)
    guild_owner = client.get_user(guild.owner_id)
    features = ""
    for i in guild.features:
        features += "\n" + i.title().replace("_", " ")
    embed = discord.Embed(
        title=f"Bot Removed From {guild.name}",
        description=f"Name: {guild.name}\nCreated At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')}  ({humanize.precisedelta(datetime.now() - guild.created_at)})\nID: {guild.id}\nOwner: {guild_owner}\nIcon Url: [click here]({guild.icon_url})\nRegion: {str(guild.region)}\nVerification Level: {str(guild.verification_level)}\nMembers: {len(guild.members)}\nBoost Level: {guild.premium_tier}\nBoosts: {guild.premium_subscription_count}\nBoosters: {len(guild.premium_subscribers)}\nTotal Channels: {len(guild.channels)}\nText Channels: {len(guild.text_channels)}\nVoice Channels: {len(guild.voice_channels)}\nCategories: {len(guild.categories)}\nRoles: {len(guild.roles)}\nEmojis: {len(guild.emojis)}/{guild.emoji_limit}\nUpload Limit: {round(guild.filesize_limit /1048576 )} Megabytes (MB)\n**Features:** {features}",
    )
    embed.set_thumbnail(url=guild.icon_url)
    await owner.send(embed=embed)
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
    	return
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"You don't have the permission to use {ctx.command}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("I can't do that")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"The {error.param} argument is missing")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, discord.Forbidden):
    	await ctx.send("I am Missing permissions")
    elif "Cannot send messages to this user" in str(error):
        pass
    else:
        botembed = discord.Embed(
            description=f"Welp, The command was unsuccessful for this reason:\n```{error}```\nReact with :white_check_mark: to report the error to the support server\nIf you can't understand why this happens, ask Wasi Master#4245 or join the bot support server (you can get the invite with the support command)"
        )
        message = await ctx.send(embed=botembed)
        await message.add_reaction("\u2705")

        def check(r, u):  # r = discord.Reaction, u = discord.Member or discord.User.
            return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id

        try:
            reaction = await client.wait_for(
                "reaction_add", check=check, timeout=10
            )
        except asyncio.TimeoutError:
            try:
                return await message.clear_reactions()
            except commands.Forbidden:
                return await message.remove_reaction("\u2705", ctx.guild.me)
        else:
            if str(reaction.emoji) == "\u2705":
                botembed.set_footer(
                    icon_url=ctx.author.avatar_url,
                    text="Reported to The Support Server",
                )
                await message.edit(embed=botembed)
                guild = client.get_guild(576016234152198155)
                channel = guild.get_channel(739673341388128266)
                embed = discord.Embed()
                embed.set_author(name="Error")
                embed.add_field(name="User", value=ctx.message.author)
                embed.add_field(name="Guild", value=ctx.guild.name)
                embed.add_field(name="Message", value=ctx.message.content)
                embed.add_field(name="Error", value=f"```{str(error)}```")
                embed.add_field(
                    name="Message Links",
                    value=f"[User Message]({ctx.message.jump_url})\n[Bot Message]({message.jump_url})",
                )
                await channel.send(embed=embed)
        raise error


def pad(to_pad):
    return to_pad + "=" * ((4 - len(to_pad) % 4) % 4)


@client.command(description="Unmutes a muted user")
@has_permissions(manage_roles=True)
async def unmute(ctx, user: discord.Member):
    try:
        await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted")) # removes muted role
        await ctx.send(f"{user.mention} has been unmuted")
    except discord.Forbidden:
        await ctx.send("No Permissions")
@client.command(description="Blocks a user from chatting in current channel.")
@has_permissions(manage_channels=True)
async def block(ctx, user: discord.Member=None):
                            
    if not user: # checks if there is user
        return await ctx.send("You must specify a user")
    try:
        await ctx.set_permissions(user, send_messages=False) # sets permissions for current channel
    except discord.Forbidden:
        await ctx.send("No permissions")
@client.command(description="Unblocks a user from current channel")
@has_permissions(manage_channels=True)
async def unblock(ctx, user: discord.Member=None):
                            
    if not user: # checks if there is user
        return await ctx.send("You must specify a user")
    try:
        await ctx.set_permissions(user, send_messages=True) # gives back send messages permissions
    except discord.Forbidden:
        await ctx.send("No permissions")


@client.command()
async def weather(ctx, location: str):
	session = aiohttp.ClientSession()
	apiKey = "cbe36b072a1ef0a4aa566782989eb847"
	location = location.replace(" ", "")
	url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&APPID={apiKey}"
	async with session.get(url) as r:
		fj = json.loads(await r.text())
	if not fj["cod"] == "404":
		embed = discord.Embed(title=fj["name"], description=f'**{fj["weather"][0]["main"]}**\n{fj["weather"][0]["description"]}')
		embed.add_field(name="Temperature", value=f'Main: {round(fj["main"]["temp"]-273.15, 2)}°C\nFeels Like: {round(fj["main"]["feels_like"]-273.15, 2)}°C\nMinimum: {round(fj["main"]["temp_min"]-273.15, 2)}°C\nMaximum: {round(fj["main"]["temp_max"]-273.15, 2)}°C')
		embed.add_field(name="Wind", value=f'Speed: {fj["wind"]["speed"]}Kmh\nDirection: {fj["wind"]["deg"]}°')
		embed.add_field(name="Cloudyness", value=str(fj["clouds"]["all"]) + "%")
		#embed.add_field(name="Sun", value=f'Sunrise: {datetime.fromtimestamp(fj["sys"]["sunrise"]).strftime("%I:%M:%S")}\nSunset: {datetime.fromtimestamp(fj["sys"]["sunset"]).strftime("%I:%M:%S")}')
		await ctx.send(embed=embed)
	elif fj["cod"] == "404":
		await ctx.send("Location not found")
	else:
		await ctx.send("Error")
	await session.close()

@client.command(aliases=["chpfp","cp"], description="Change the bots profile picture on random" )
@commands.cooldown(2, 900, BucketType.default)
async def changepfp(ctx):
	pfps = ["pink.png", "red.png", "blue.png", "green.png", "cyan.png"]
	pfp = random.choice(pfps)
	with open(pfp, "rb") as f:
		avatar = f.read()
		await client.user.edit(avatar=avatar)
		file = discord.File(pfp, filename="avatar.png")
		await ctx.send("Changed Profile picture to:", file=file)
		server = client.get_guild(576016234152198155)
		channel = server.get_channel(741371556277518427)
		embed = discord.Embed(title=f"Avatar was changed by {ctx.author}")
		await channel.send(embed=embed)
	f.close()

@client.command(aliases=["lck", "lk"],description="Lock a channel")
@has_permissions(manage_channels=True)
async def lock(ctx, *, role: discord.Role=None):
    role = role or ctx.guild.default_role# retrieves muted role returns none if there isn't
    channel = ctx.channel
    try:
        await channel.set_permissions(role,send_messages=False,read_message_history=True,read_messages=True)
        await ctx.send("Channel Locked")
    except discord.Forbidden:
        return await ctx.send(
                "I have no permissions to lock"
            )


@client.command(aliases=["unlck", "ulk"], description=" Unlocks a channel")
@has_permissions(manage_channels=True)
async def unlock(ctx, *, role: discord.Role=None):
    role = role or ctx.guild.default_role# retrieves muted role returns none if there isn't
    channel = ctx.channel
    try:
        await channel.set_permissions(role, send_messages=True,read_message_history=True,read_messages=True)
        await ctx.send("Channel Unlocked")
    except discord.Forbidden:
        return await ctx.send(
                "I have no permissions to lock"
            )


@client.command(name="pypi", description="Searches pypi for python packages", aliases=["pypl"])
async def pypi(ctx, package_name:str):
	session = aiohttp.ClientSession()
	url = f"https://pypi.org/pypi/{package_name}/json"
	async with session.get(url) as response:
		if "We looked everywhere but couldn't find this page" in await response.text():
			return await ctx.send("Project not found")
		else:
			fj = json.loads(await response.text())
	fj = fj["info"]
	if not len(fj["summary"]) == 0: 
		embed = discord.Embed(title=fj["name"], description=fj["summary"].replace("![", "["))
	else:
		embed = discord.Embed(title=fj["name"])
	if len(fj["author_email"]) == 0:
		email = "None"
	else:
		email = fj["author_email"]
	embed.add_field(name="Author", value=f"Name: {fj['author']}\nEmail: {email}")
	embed.add_field(name="Version", value=fj["version"])
	#embed.add_field(name="Summary", value=fj["summary"])
	embed.add_field(name="Links", value=f"[Hoem Page]({fj['home_page']})\n[Project Link]({fj['project_url']})\n[Release Link]({fj['release_url']})")
	if len(fj["license"]) == 0:
		license = "Not Specified"
	else:
		license = fj["license"]
	embed.add_field(name="License", value={license})
	if not fj["requires_dist"] is None:
		if len(fj["requires_dist"]) > 5:
			embed.add_field(name="Dependencies", value=len(fj["requires_dist"]))
	elif not len(fj["requires_dist"]) == 0:
		embed.add_field(name=f"Dependencies ({len(fj['requires_dist'])})", value="\n".join([i.split(" ")[0] for i in fj["requires_dist"]]))
	if not len(fj["requires_python"]) == 0:
		embed.add_field(name="<:python:596577462335307777> Python Version Required", value=fj["requires_python"])
	await ctx.send(embed=embed)
	await session.close()


@client.command(name="penis", aliases=["pp"], description="See someone's penis size (random)")
async def pp(ctx, *, member: discord.Member=None):
	member = member or ctx.author
	ppsize = random.randint(0, 30)
	if ppsize < 6:
		comment = "Hehe, pp smol"
	elif ppsize < 9 and ppsize > 6:
		comment = "okay"
	elif ppsize > 9 and ppsize < 12:
		comment = "normal pp"
	elif ppsize > 12 and ppsize < 18:
		comment = "huge pp"
	elif ppsize > 18 and ppsize < 25:
		comment = "extremely big pp"
	else:
		comment = "tremendous pp "
	embed = discord.Embed(title=f"{member.name}'s pp size", description="8" + "="*ppsize + "D")
	embed.set_footer(text=comment)
	await ctx.send(embed=embed)

@client.command(name="gender", description="Get a gender by providing a name")
@commands.cooldown(1, 60, BucketType.user)
async def gender(ctx, *, name: str):
	session = aiohttp.ClientSession()
	url = f"https://gender-api.com/get?name={name.replace(' ', '%20')}&key=tKYMESVFrAEhpCpuwz"
	async with session.get(url) as r:
		fj = json.loads(await r.text())
	if fj['gender'] == "male":
		gender = "Male"
		color = 2929919
	elif fj["gender"] == "female":
		gender = "Female"
		color = 16723124
	else:
		gender = "Unknown"
		color = 6579300
	positive = str(fj['accuracy']) + "%"
	negative = str(100 - fj['accuracy']) + "%"
	if not gender == "Unknown":
		text = f"The name {fj['name_sanitized']} has a **{positive}** chance of being a  **{gender}** and a {negative} chance of not being a {gender}"
	else:
		text = f"The name {fj['name_sanitized']} is not in our database"
	embed = discord.Embed(title=fj["name_sanitized"], description=text, color=color)
	await ctx.send(embed=embed)


@client.command(description="See details about a movie")
async def movie(ctx, *, query):
	session = aiohttp.ClientSession()
	url = f"http://www.omdbapi.com/?i=tt3896198&apikey=4e62e2fc&t={query}"
	async with session.get(url) as response:
		fj = json.loads(await response.text())
	if fj["Response"] == "True":
		embed = discord.Embed(title=fj["Title"], description=fj["Plot"])
		embed.set_image(url=fj["Poster"])
		embed.add_field(name="Released On", value=fj["Released"])
		embed.add_field(name="Rated", value=fj["Rated"])
		mins = []
		embed.add_field(name="Duration", value=f"{fj['Runtime']}")
		embed.add_field(name="Genre", value=fj["Genre"])
		embed.add_field(name="Credits", value=f"**Director**: {fj['Director']}\n**Writer**: {fj['Writer']}\n**Casts**: {fj['Actors']}")
		embed.add_field(name="Language(s)", value=fj['Language'])
		embed.add_field(name="IMDB", value=f"Rating: {fj['imdbRating']}\nVotes: {fj['imdbVotes']}")
		embed.add_field(name="Production", value=f"[{fj['Production']}]({fj['Website']})")
		await ctx.send(embed=embed)
		await session.close()
	else:
		await ctx.send("Movie Not Found")


@client.command(aliases=["ri", "rlinf"], description=" See info about a role")
async def roleinfo(ctx, role: discord.Role = None):
    if role is None:
        return await ctx.send("Please specify (mention or write the name) of a role")
    embed = discord.Embed(colour=role.colour.value)
    embed.set_author(name=f"Role Information for {role.name}")
    embed.add_field(
        name="Created at", value=f"{role.created_at.strftime('%a, %d %B %Y, %H:%M:%S')}  ({humanize.precisedelta(datetime.utcnow() - role.created_at)}"
    )
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Position", value=f"{role.position}/{len(ctx.guild.roles)}")
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Role Color", value=f"INT: {role.color.value}\nHEX: {'#%02x%02x%02x' % role.color.to_rgb()}\nRGB: rgb{role.color.to_rgb}")
    if role.hoist:
        embed.add_field(name="Displayed Separatel?", value="Yes")
    else:
        embed.add_field(name="Displayed Separatel?", value="No")
    if role.mentionable:
        embed.add_field(name="Mentionable", value="Yes")
    else:
        embed.add_field(name="Mentionable", value="No")
    await ctx.send(embed=embed)


@client.command(aliases=["tm"], description="See time")
async def time(ctx, location: str=None):
	embed = discord.Embed()
	session = aiohttp.ClientSession()
	async with session.get(f"http://worldtimeapi.org/api/timezone/{location}") as r:
		fj = json.loads(await r.text())
	await session.close()
	try:
		fj["error"]
		error = True
	except:
		error = False
	if error:
		if fj["error"] == "unknown location":
			locations = json.loads(requests.get("http://worldtimeapi.org/api/timezone").text)
			suggestions = difflib.get_close_matches(location, locations, n=5, cutoff=0.3)
			suggestionstring = ""
			for i in suggestions:
				suggestionstring += f"`{i}`\n"
			embed.set_author(name="Location Not Found")
			embed.add_field(name="Did you mean?", value=suggestionstring)
			await ctx.send(embed=embed)
	else:
		currenttime = datetime.strptime(fj["datetime"][:-13], "%Y-%m-%dT%H:%M:%S")
		gmt = fj["utc_offset"]
		embed.set_author(name="Time")
		embed.add_field(name=location, value=currenttime.strftime("%a, %d %B %Y, %H:%M:%S"))
		embed.add_field(name="UTC Offset", value=gmt)
		await ctx.send(embed=embed)
		
@client.command(
    aliases=["ss"],
    description="Takes a sceenshot of a website"
)
@commands.cooldown(1, 30, BucketType.default)
async def screenshot(ctx, website:str):
    async with ctx.typing():
        session = aiohttp.ClientSession()
        async with session.get(
            "https://magmafuck.herokuapp.com/api/v1",
            headers={"website": website}
        ) as response:
            data = await response.json()
            embed = discord.Embed(title=data["website"], url=website)
            r = json.loads(requests.get(f"https://nsfw-categorize.it/api.php?url={data['snapshot']}").text)
            if int(round(r["porn_probability"])) > 5 and not ctx.channel.is_nsfw():
                return await ctx.send("NSFW Filter Active")
            else:
                embed.set_image(url=data["snapshot"])
        await ctx.send(embed=embed)
        session.close()


@client.command(aliases=["ci", "chi"], description=" See info about a channel")
async def channelinfo(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    embed = discord.Embed()
    embed.set_author(name=f"Channel Information for {channel.name}")
    embed.add_field(
        name="Created at", value=f'{channel.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.utcnow() - channel.created_at)})'
    )
    embed.add_field(name="ID", value=channel.id)
    embed.add_field(name="Position", value=f"{channel.position}/{len(ctx.guild.text_channels)}")
    embed.add_field(name="Category", value=channel.category.name)
    if not channel.topic is None:
        embed.add_field(name="Topic", value=channel.topic)
    if not channel.slowmode_delay is None:
        embed.add_field(name="Slowmode", value=f"{channel.slowmode_delay} seconds")
    await ctx.send(embed=embed)

@client.command(
    aliases=["nk"],
    description="Nuke a channel\nCreates a new channel with all the same properties (permissions, name, topic etc.) ",
)
@has_permissions(manage_channels=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await ctx.send(
        "Are you sure you want to nuke this channel?\n type `yes` to confirm or `no` to decline"
    )

    def check(m):  # m = discord.Message.
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    try:
        name = await client.wait_for("message", check=check, timeout=20)
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


@client.command(
    aliases=["cln"],
    description="Clone a channel\nCreates a new channel with all the same properties (permissions, name, topic etc.) ",
)
@has_permissions(manage_channels=True)
async def clone(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await ctx.send(
        "Are you sure you want to clone this channel?\n type `yes` to confirm or `no` to decline"
    )

    def check(m):  # m = discord.Message.
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    try:
        name = await client.wait_for("message", check=check, timeout=20)
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


@client.command(
    aliases=["sug", "suggestion"], description="Suggest a thing to be added to the bot"
)
@commands.cooldown(1, 3600, BucketType.user)
async def suggest(ctx, *, suggestion: commands.clean_content):
    guild = client.get_guild(576016234152198155)
    channel = guild.get_channel(740071107041689631)
    embed = discord.Embed()
    embed.set_author(name="Suggestion Added")
    embed.add_field(name="User", value=ctx.message.author)
    embed.add_field(name="Guild", value=ctx.guild.name)
    embed.add_field(name="Suggestion", value=f"```{str(suggestion)}```")
    message = await channel.send(embed=embed)
    await ctx.send("Suggestion sent")
    message.add_reaction("\u2b06\ufe0f")
    message.add_reaction("\u2b07\ufe0f")


@client.command(aliases=["upscaled"], description="Upscales a users profile picture")
@commands.cooldown(1, 3600, type=BucketType.user)
async def upscale(ctx, scaletype, *, member: discord.Member = None):
    member = member or ctx.author
    if scaletype.lower() == "anime":
        url = "https://api.deepai.org/api/waifu2x"
    elif scaletype.lower() == "normal":
        url = "https://api.deepai.org/api/torch-srgan"
    else:
        await ctx.send("Invalid Format")
    session = aiohttp.ClientSession()
    message = await ctx.send("May take up to 15 seconds, Wait till then")
    async with session.post(
        url,
        data={"image": str(member.avatar_url),},
        headers={"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"},
    ) as resp:
        fj = json.loads(await resp.text())
        url = fj["output_url"]
    await session.close()
    await message.delete()
    embed = discord.Embed()
    embed.set_author(name=f"{member.name}'s Profile Picture Upscaled")
    embed.set_image(url=url)
    await ctx.send(embed=embed)


@client.command(aliases=["randomfact", "rf", " f"], description="Get a random fact")
async def fact(ctx):
    session = aiohttp.ClientSession()
    async with session.get(
        "https://uselessfacts.jsph.pl/random.json?language=en"
    ) as resp:
        fj = json.loads(await resp.text())
    embed = discord.Embed(title="Random Fact", description=fj["text"])
    await ctx.send(embed=embed)
    await session.close()


@client.command(description="Sends a waifu")
async def waifu(ctx):
    session = aiohttp.ClientSession()
    gender = "male"
    async with ctx.typing():
        while gender == "male":
            async with session.get("https://mywaifulist.moe/random") as resp:
                response = await resp.text()
            soup = BeautifulSoup(response, "html.parser")
            image_url = ast.literal_eval(
                "{"
                + str(soup.find("script", type="application/ld+json"))
                .split("\n      ")[3]
                .split(",")[0]
                + "}"
            )["image"]
            name = ast.literal_eval(
                "{"
                + str(soup.find("script", type="application/ld+json"))
                .split("\n      ")[4]
                .split(",")[0]
                + "}"
            )["name"]
            gender = ast.literal_eval(
                "{"
                + str(soup.find("script", type="application/ld+json"))
                .split("\n      ")[5]
                .split(",")[0]
                + "}"
            )["gender"]
        embed = discord.Embed(title=name.replace("&quot;", '"'))
        embed.set_image(url=image_url)
    await session.close()
    message = await ctx.send(embed=embed)
    await message.add_reaction("\u2764\ufe0f")

    def check(r, u):  # r = discord.Reaction, u = discord.Member or discord.User.
        return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id

    try:
        reaction = await client.wait_for("reaction_add", check=check, timeout=10)
    except asyncio.TimeoutError:
        try:
            return await message.clear_reactions()
        except commands.MissingPermissions:
            return await message.remove_reaction("\u2764\ufe0f", ctx.guild.me)
    else:
        if str(reaction.emoji) == "\u2764\ufe0f":
            embed.set_footer(
                icon_url=ctx.author.avatar_url, text=f"Claimed by {ctx.author.name}"
            )
            await message.edit(embed=embed)
            return await ctx.send(
                f":couple_with_heart: {ctx.author.mention} is now married with **{name.replace('&quot;', '')}** :couple_with_heart:"
            )


@client.command(
    description="Shows a `<name:id> for standard emojis and `<a:name:id>` for animated emojis`",
    usage="emoji `<name>`\n\nemoji hyper_pinged",
)
async def emoji(ctx, *, name: str):
    await ctx.send(f"```{discord.utils.get(ctx.guild.emojis, name=name)}```")


@client.command(
    description="See your or other peoples permissions",
    aliases=["permissions"],
    usage="perms `[@mention]`\n\nperms\nperms @Wasi Master",
)
async def perms(
    ctx, member: discord.Member = None, channel: discord.TextChannel = None
):
    channel = channel or ctx.channel
    perms = []
    permstr = ""
    for i in member.permissions_in(channel):
        perms.append(i)
    perms = dict(perms)
    for i in perms:
        if perms[i]:
            permstr += (
                f"<:greenTick:596576670815879169> {i.replace('_', ' ' ).title()}\n"
            )
        else:
            continue
            # permstr += f"{i.replace('_', ' ' ).title()}  <:redTick:596576672149667840>\n"
    embed = discord.Embed(title=f"{member}'s Permissions", description=permstr)
    await ctx.send(embed=embed)


@client.command(aliases=["fm"], description="Shows the first message in a channel")
async def firstmessage(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    attachments = ""
    num = 0

    async for i in channel.history(oldest_first=True):
        if i.is_system:
            fmo = i
            break

    embed = discord.Embed(title=f"First message in {channel.name}")
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
        name="Message sent at", value=f'{fmo.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}   ({humanize.precisedelta(datetime.utcnow() - fmo.created_at)})'
    )
    if not fmo.edited_at is None:
        embed.add_field(
            name="Edited", value=f'{fmo.edited_at.strftime("%a, %d %B %Y, %H:%M:%S")}   ({humanize.precisedelta(datetime.utcnow() - fmo.edited_at)})'
        )
    embed.add_field(name="Url", value=fmo.jump_url)
    embed.set_footer(
        text="Times are in UTC\nIt doesn’t show a system message such as a member join/leave or server boost "
    )
    await ctx.send(embed=embed)


@client.command(aliases=["stop"], description="Stops the bot, only for the bot owner")
async def shutdown(ctx):
    if ctx.message.author.id == 538332632535007244:
        await client.close()
    else:
        await ctx.send("You are not the bot owner :grin::grin::grin:")


@client.command(aliases=["sd"],description="Custom Slow Mode")
@has_permissions(manage_channels=True)
async def slowmode(ctx, slowmode: int):
    if slowmode > 21600:
        await ctx.send("Slow Mode too long")
    else:
        await ctx.channel.edit(slowmode_delay=slowmode)
        await ctx.send(f"Slow Mode set to {slowmode} seconds for {ctx.channel.mention}")


@client.command(description="Lick a user")
async def lick(ctx, member: discord.Member = None):
    if not member:
        embed = discord.Embed(
            title="Error",
            description="Please Mention a User to lick If you do not mention a user, the command will not work!",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Command Error")
        return await ctx.send(embed=embed)

    if member == ctx.author:
        embed = discord.Embed(
            title="Lick", description=f"{ctx.author.mention} has licked themselves"
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Lick",
            description=f"{ctx.author.mention} has licked {member.mention}",
        )
        await ctx.send(embed=embed)


@client.command(description="Reverses a text")
async def reverse(ctx, *, string: str):
    result = ""
    for i in reversed(list(string)):
        result += i
    embed = discord.Embed(
        title="Reverse", description=f"**Original**:\n{string}\n**Reversed**:\n{result}"
    )
    await ctx.send(result, embed=embed)


@client.command(aliases=["tod"], description="Truth Or Dare")
async def truthordare(ctx, questype: str = "random"):
    levels = ["Disgusting", "Stupid", "Normal", "Soft", "Sexy", "Hot"]
    session = aiohttp.ClientSession()
    async with session.get(
        "https://raw.githubusercontent.com/sylhare/Truth-or-Dare/master/src/output.json"
    ) as r:
        fj = json.loads(await r.text())
    await session.close()
    if questype == "random":
        number = secureRandom.randint(0, 553)
        picked = fj[number]
        level = levels[int(picked["level"])]
        summary = picked["summary"]
        questiontype = picked["type"]
    else:
        return
    embed = discord.Embed()
    embed.set_author(name=summary)
    embed.add_field(name="Level", value=level)
    embed.add_field(name="Type", value=questiontype)
    await ctx.send(embed=embed)


@client.command(description="Generates a wanted poster")
async def wanted(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    session = aiohttp.ClientSession()
    headers = {
        "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
        "url": str(member.avatar_url),
    }
    async with ctx.typing():
        async with session.post(
            "https://dagpi.tk/api/wanted", headers=headers
        ) as response:
            loaded_response = await response.text()
        formatted_json = json.loads(loaded_response)
        await session.close()
    if formatted_json["succes"]:
        embed = discord.Embed(title=f"{member.name} Wanted")
        embed.set_image(url=formatted_json["url"])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Error")


@client.command(description='Generates a "Worse than hitler" image')
async def hitler(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    session = aiohttp.ClientSession()
    headers = {
        "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
        "url": str(member.avatar_url),
    }
    async with ctx.typing():
        async with session.post(
            "https://dagpi.tk/api/hitler", headers=headers
        ) as response:
            loaded_response = await response.text()
        formatted_json = json.loads(loaded_response)
        await session.close()
    if formatted_json["succes"]:
        embed = discord.Embed(title=f"{member.name} is Worse Than Hitler")
        embed.set_image(url=formatted_json["url"])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Error")


@client.command(description="Tweets a text")
async def tweet(ctx, member: discord.Member = None, *, text):
    member = member or ctx.message.author
    username = member.name
    session = aiohttp.ClientSession()
    headers = {
        "token": "VWTwUej1JzUQ1iAPjeZUNOavwlX3EIeOHtSfskjNDtIODoYugLxBNcHFEHMqiJtB",
        "url": str(member.avatar_url),
        "name": username,
        "text": text,
    }
    async with ctx.typing():
        async with session.post(
            "https://dagpi.tk/api/tweet", headers=headers
        ) as response:
            loaded_response = await response.text()
        formatted_json = json.loads(loaded_response)
        await session.close()
    if formatted_json["succes"]:
        embed = discord.Embed(title=f"{member.name} Posted a new tweet")
        embed.set_image(url=formatted_json["url"])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Error")


@client.command(description="Coronavirus Stats")
async def covid(ctx, area: str = "Global"):
    num = 0
    session = aiohttp.ClientSession()
    async with ctx.typing():
        async with session.get("https://api.covid19api.com/summary") as r:
            formatted_json = json.loads(await r.text())
    await session.close()
    if not area.lower() == "global":
        for i in formatted_json["Countries"]:
            num += 1
            if i["Slug"] == area.lower:
                formatted_json = i[num - 1]
                await ctx.send(formatted_json)
                break
            else:
                continue
    else:
        formatted_json = formatted_json["Global"]
    embed = discord.Embed(title=f"Covid 19 Stats ({area.title()})")
    embed.add_field(name="New Cases", value=f"{formatted_json['NewConfirmed']:,}")
    embed.add_field(name="Total Cases", value=f"{formatted_json['TotalConfirmed']:,}")
    embed.add_field(name="New Deaths", value=f"{formatted_json['NewDeaths']:,}")
    embed.add_field(name="Total Deaths", value=f"{formatted_json['TotalDeaths']:,}")
    embed.add_field(name="New Recovered", value=f"{formatted_json['NewRecovered']:,}")
    embed.add_field(
        name="Total Recovered", value=f"{formatted_json['TotalRecovered']:,}"
    )
    await ctx.send(embed=embed)


@client.command(name="chatbot", aliases=["cb"], description=" Talk with a chat bot")
async def cleverbot_(ctx, *, query: str):
    """Ask Cleverbot a question!"""
    try:
        async with ctx.typing():
            r = await cleverbot.ask(query, ctx.author.id)  # the ID is for context
    except ac.InvalidKey:
        return await ctx.send(
            "An error has occurred. The API key provided was not valid."
        )
    except ac.APIDown:
        return await ctx.send("I have to sleep sometimes. Please ask me later!")
    else:
        await ctx.send("{}, {}".format(ctx.author.mention, r.text))


@client.command(description="See all the boosters of this server")
async def boosters(ctx):
    peoples = []
    for i in ctx.message.guild.premium_subscribers:
        peoples.append(i.name)
    await ctx.send("\n".join(peoples))


@client.command(description="Invert your or another users profile picture")
async def invert(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    url = f"https://api.alexflipnote.dev/filter/invert?image={member.avatar_url}"
    e = discord.Embed()
    e.set_image(url=url)
    e.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=e)


@client.command(description="Blur your or another users profile picture")
async def blur(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    url = f"https://api.alexflipnote.dev/filter/blur?image={member.avatar_url}"
    e = discord.Embed()
    e.set_image(url=url)
    e.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=e)


@client.command(
    aliases=["b&w", "blackandwhite"],
    description="Convert to Black And White your or another users profile picture",
)
async def bw(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    url = f"https://api.alexflipnote.dev/filter/b&w?image={member.avatar_url}"
    e = discord.Embed()
    e.set_image(url=url)
    e.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=e)


@client.command(description="Pixelate your or another users profile picture")
async def pixelate(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    url = f"https://api.alexflipnote.dev/filter/pixelate?image={member.avatar_url}"
    e = discord.Embed()
    e.set_image(url=url)
    e.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=e)


@client.command(
    description="See a gay version of your or another users profile picture"
)
async def gay(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    url = f"https://api.alexflipnote.dev/filter/gay?image={member.avatar_url}"
    e = discord.Embed()
    e.set_image(url=url)
    e.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=e)


@client.command(aliases=["tenor"], description="Search for a gif")
async def gif(ctx, *, query: str):
    apikey = "8ZQV38KW9TWP"
    lmt = 1
    search_term = query
    session = aiohttp.ClientSession()
    async with ctx.typing():
        async with session.get(
            "https://api.tenor.com/v1/search?q=%s&key=%s&contentfilter=high&limit=%s"
            % (search_term, apikey, lmt)
        ) as r:
            gifs = json.loads(await r.text())
            gif: str = gifs["results"][0]["media"][0]["gif"]["url"]
    await session.close()
    embed = discord.Embed()
    embed.set_image(url=gif)
    embed.add_field(
        name="Link (click to see or long press to copy)", value=f"[click here]({gif})"
    )
    embed.set_footer(text=f"Asked by {ctx.message.author}")
    await ctx.send(embed=embed)


@client.command(aliases=["b64"], description="Encode or decode text to base64")
async def base64(ctx, task, *, text):
    if task.strip().lower() == "encode" or task.strip().lower == "e":
        data = text
        encodedBytes = base64module.b64encode(data.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")
        await ctx.send(encodedStr)
    elif task.strip().lower() == "decode" or task.strip().lower == "d":
        data = text
        message_bytes = base64module.b64decode(data)
        message = message_bytes.decode("ascii")
        await ctx.send(message)
    else:
        await ctx.send("Must have either encode or decode")


@client.command(description="Get a invite link to the bots support server")
async def support(ctx):
    await ctx.send("https://discord.gg/5jn3bQX")


@client.command(description="Reminds you something")
async def remind(ctx, time: int, *, text: str):
    user = ctx.message.author
    texttosend = text
    timetowait = time
    await ctx.send(f"Gonna remind you `{texttosend}` in `{timetowait}` seconds")
    await asyncio.sleep(timetowait)
    await user.send(texttosend)


@client.command(aliases=["makememe"], description="See or make a meme")
async def meme(ctx, *, text: str = None):
    Make = True
    if not text is None:
        base_url = "https://memegen.link/api/templates"
        text = (
            text.strip()
            .replace(" ", "-")
            .replace("?", "~q")
            .replace("#", "~h")
            .replace("%", "~p")
            .replace("/", "~s")
            .replace("''", '"')
        )
        textlist = text.split(":")[1].split("||")
        template = text.split(":")[0].strip().replace(" ", "").lower()
    else:
        textlist = []
    if len(textlist) == 2:
        url = f"{base_url}/{template}/{textlist[0]}/{textlist[1]}"
    elif len(textlist) == 1:
        url = f"{base_url}/{template}/{textlist[0]}"
    else:
        Make = False
        session = aiohttp.ClientSession()
        async with session.get("https://meme-api.herokuapp.com/gimme") as r:
            fj = json.loads(await r.text())
        embed = discord.Embed(title=fj["title"], url=fj["postLink"])
        embed.set_image(url=fj["url"])
        await ctx.send(embed=embed)
        await session.close()
    if Make:
        session = aiohttp.ClientSession()
        async with ctx.typing():
            async with session.get(url) as response:
                response_json = json.loads(await response.text())
        await session.close()
        try:
            masked_url = response_json["direct"]["masked"]
        except:
            await ctx.send("Error")
        embed = discord.Embed()
        embed.set_author(name=template.title())
        embed.set_image(url=masked_url)
        await ctx.send(embed=embed)


@client.command(aliases=["yt"], description="Search youtube for stuff")
async def youtube(ctx, *, args):
    search_terms = args
    max_results = 1

    def parse_html(response):
        results = []
        start = (
            response.index('window["ytInitialData"]')
            + len('window["ytInitialData"]')
            + 3
        )
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos:
            res = {}
            if "videoRenderer" in video.keys():
                video_data = video["videoRenderer"]
                res["id"] = video_data["videoId"]
                res["thumbnails"] = [
                    thumb["url"] for thumb in video_data["thumbnail"]["thumbnails"]
                ]
                res["title"] = video_data["title"]["runs"][0]["text"]
                # res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
                res["channel"] = video_data["longBylineText"]["runs"][0]["text"]
                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                res["url_suffix"] = video_data["navigationEndpoint"]["commandMetadata"][
                    "webCommandMetadata"
                ]["url"]
                results.append(res)
        return results

    def search():
        encoded_search = urllib.parse.quote(search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = requests.get(url).text
        while 'window["ytInitialData"]' not in response:
            response = requests.get(url).text
        results = parse_html(response)
        if max_results is not None and len(results) > max_results:
            return results[:max_results]
        return results

    videos = search()
    embed = discord.Embed(title=videos[0]["title"])
    embed.add_field(name="Channel", value=videos[0]["channel"])
    embed.add_field(name="Duration", value=videos[0]["duration"])
    embed.add_field(name="Views", value=videos[0]["views"])
    embed.add_field(
        name="Watch",
        value=f"[Click Here to open or long press to copy](https://www.youtube.com{videos[0]['url_suffix']})",
    )
    try:
        embed.set_image(
            url=f"https://img.youtube.com/vi/{videos[0]['id']}/hqdefault.jpg"
        )
    except:
        try:
            embed.set_image(url=videos[0]["thumbnails"][1])
        except:
            try:
                embed.set_image(url=videos[0]["thumbnails"][2])
            except:
                embed.set_image(url=videos[0]["thumbnails"][3])
    await ctx.send(embed=embed)


@client.command(
    aliases=["guildinfo", "si", "gi"], description="See details of a server"
)
async def serverinfo(ctx):
    guild = ctx.message.guild
    owner = client.get_user(guild.owner_id)
    features = ""
    for i in guild.features:
        features += "\n" + i.title().replace("_", " ")
    embed = discord.Embed(
        title=f"Server Information for {guild.name}",
        description=f"Name: {guild.name}\nCreated At: {guild.created_at.strftime('%a, %d %B %Y, %H:%M:%S')}  ({humanize.precisedelta(datetime.utcnow() - guild.created_at)})\nID: {guild.id}\nOwner: {owner}\nIcon Url: [click here]({guild.icon_url})\nRegion: {str(guild.region)}\nVerification Level: {str(guild.verification_level)}\nTotal Members: {len(guild.members)}\nBots: {len([member for member in ctx.guild.members if member.bot])}\nHumans: {len(ctx.guild.members) - len([member for member in ctx.guild.members if member.bot])}\n<:boost4:724328585137225789> Boost Level: {guild.premium_tier}\n<:boost1:724328584893956168> Boosts: {guild.premium_subscription_count}\n<:boost1:724328584893956168> Boosters: {len(guild.premium_subscribers)}\nTotal Channels: {len(guild.channels)}\n<:textchannel:724637677395116072> Text Channels: {len(guild.text_channels)}\n<:voicechannel:724637677130875001> Voice Channels: {len(guild.voice_channels)}\n<:category:724330131421659206> Categories: {len(guild.categories)}\nRoles: {len(guild.roles)}\n:slight_smile: Emojis: {len(guild.emojis)}/{guild.emoji_limit}\nUpload Limit: {round(guild.filesize_limit /1048576 )} Megabytes (MB)\n\n**Features:** {features}",
    )
    embed.set_thumbnail(url=guild.icon_url)
    await ctx.send(embed=embed)


@client.command(description="See info about the bot")
async def info(ctx):
    total = 0
    embed = discord.Embed(title="Statistics")
    embed.add_field(name="Code", value=f"Lines: {total:3,}")
    ram = psutil.virtual_memory()
    embed.add_field(
        name="CPU",
        value=f"Percentage:{get_p(psutil.cpu_percent())}\nFrequency {psutil.cpu_freq().current}Mhz\nCores: {psutil.cpu_count()}",
    )
    embed.add_field(
        name="RAM",
        value=f"Used: {round(ram.used/1048576)}MB\nAvailable: {round(ram.available/54316236)}MB\nTotal: {round(ram.total/54316236)}MB\nPercentage:{get_p(round((ram.used/ram.total)))*100}",
    )
    with codecs.open("bot.py", "r", "utf-8") as f:
        for l in enumerate(f):
            if (
                l.strip().startswith("#") or len(l.strip()) == 0
            ):  # skip commented lines.
                pass
            else:
                total += 1
    await ctx.send(embed=embed)


@client.command(aliases=["spt"], description="See your or another users spotify info")
async def spotify(ctx, *, member: discord.Member = None):
    member = member or ctx.message.author
    activity = ctx.message.guild.get_member(member.id)
    successfull = False
    for activity in activity.activities:
        if isinstance(activity, discord.Spotify):
            search_terms = activity.artist + " - " + activity.title
            max_results = 1

            def parse_html(response):
                results = []
                start = (
                    response.index('window["ytInitialData"]')
                    + len('window["ytInitialData"]')
                    + 3
                )
                end = response.index("};", start) + 1
                json_str = response[start:end]
                data = json.loads(json_str)

                videos = data["contents"]["twoColumnSearchResultsRenderer"][
                    "primaryContents"
                ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"][
                    "contents"
                ]

                for video in videos:
                    res = {}
                    if "videoRenderer" in video.keys():
                        video_data = video["videoRenderer"]
                        res["id"] = video_data["videoId"]
                        res["thumbnails"] = [
                            thumb["url"]
                            for thumb in video_data["thumbnail"]["thumbnails"]
                        ]
                        res["title"] = video_data["title"]["runs"][0]["text"]
                        # res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
                        res["channel"] = video_data["longBylineText"]["runs"][0]["text"]
                        res["duration"] = video_data.get("lengthText", {}).get(
                            "simpleText", 0
                        )
                        res["views"] = video_data.get("viewCountText", {}).get(
                            "simpleText", 0
                        )
                        res["url_suffix"] = video_data["navigationEndpoint"][
                            "commandMetadata"
                        ]["webCommandMetadata"]["url"]
                        results.append(res)
                return results

            def search():
                encoded_search = urllib.parse.quote(search_terms)
                BASE_URL = "https://youtube.com"
                url = f"{BASE_URL}/results?search_query={encoded_search}"
                response = requests.get(url).text
                while 'window["ytInitialData"]' not in response:
                    response = requests.get(url).text

                results = parse_html(response)
                if max_results is not None and len(results) > max_results:
                    return results[:max_results]
                return results
            videos = search()
            embed = discord.Embed(color=activity.color)
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
            )
            embed.set_image(url=activity.album_cover_url)
            embed.add_field(name="Song Name", value=activity.title)
            if len(activity.artists) == 0:
                embed.add_field(name="Artist", value=activity.artist)
            else:
                embed.add_field(name="Artists", value=activity.artist)
            try:
                embed.add_field(name="Album", value=activity.album)
            except:
                embed.add_field(name="Album", value="None")
            embed.add_field(name="Song Duration", value=str(activity.duration)[2:-7])
            embed.add_field(
                name="Spotify Link",
                value=f"[Click Here](https://open.spotify.com/track/{activity.track_id})",
            )
            embed.add_field(
                name="Youtube Link",
                value=f"[Click Here](https://www.youtube.com{videos[0]['url_suffix']})",
            )
            embed.add_field(
                name="Time",
                value=f"{convert_sec_to_min((datetime.utcnow() - activity.start).total_seconds())} {get_p((abs((datetime.utcnow() - activity.start).total_seconds()))/(abs(((activity.start - activity.end)).total_seconds())/100))} {str(activity.duration)[2:-7]}",
            )
            embed.set_footer(text="Track ID:" + activity.track_id)
            await ctx.send(embed=embed)
            successfull = True
        else:
            successfull = False
    if not successfull:
        await ctx.send("Not listening to spotify :(")


@client.command(description="The bot leaves the server (bot owner only)")
async def leaveserver(ctx):
    if ctx.message.author.id == 538332632535007244:
        await ctx.send("Bye Bye")
        ctx.message.guild.leave()
    else:
        await ctx.send("You are not the owner :grin:")


@client.command(description="Find details about a music")
async def music(ctx, *, args):
    url = "https://deezerdevs-deezer.p.rapidapi.com/search"
    querystring = {"q": args}
    session = aiohttp.ClientSession()
    headers = {
        "x-rapidapi-host": "deezerdevs-deezer.p.rapidapi.com",
        "x-rapidapi-key": "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d",
    }
    async with ctx.typing():
        async with session.get(url, headers=headers, params=querystring) as response:
            formatted_response = json.loads(await response.text())
    await session.close()
    data = formatted_response.get("data")[0]

    # song
    name = data.get("title")
    explict = data.get("explicit_lyrics")
    # artist
    artist = data.get("artist")
    artist_name = artist.get("name")
    artist_picture = artist.get("picture_xl")
    # album
    album = data.get("album")
    album_name = album.get("title")
    album_cover = album.get("cover_xl")

    embed = discord.Embed()
    embed.set_author(name=name, icon_url=artist_picture)
    embed.add_field(name="Explict", value=explict)
    embed.add_field(name="Song Name", value=name, inline=True)
    embed.add_field(name="Artist", value=artist_name, inline=True)
    embed.add_field(name="Album", value=album_name, inline=True)
    embed.set_image(url=album_cover)
    await ctx.send(embed=embed)


@client.command(description="Sends you stuff")
async def dm(ctx, *, args):
    await ctx.message.author.send(args)


@client.command(
    aliases=["randcolor", "randomcol", "randcol", "randomcolor", "rc"],
    description="Generates a random color",
)
async def randomcolour(ctx):
    session = aiohttp.ClientSession()
    async with ctx.typing():
        rand_color = randomcolor.RandomColor()
        generated_color = rand_color.generate()[0]
        hexcol = generated_color.replace("#", "")
        async with session.get(f"http://www.thecolorapi.com/id?hex={hex}") as response:
            data = json.loads(await response.text())
        color_name = data.get("name").get("value")
        link = f"http://singlecolorimage.com/get/{hexcol}/1x1"
        thumb = f"http://singlecolorimage.com/get/{hexcol}/100x100"
        rgb = data.get("rgb").get("value")
        hexcol = data.get("hex").get("value")
        intcol = int(hexcol.replace("#", ""), 16)
    embed = discord.Embed(timestamp=ctx.message.created_at, color=intcol)
    embed.set_author(name=color_name)
    embed.set_image(url=link)
    embed.set_thumbnail(url=thumb)
    embed.set_footer(text=f"Made for {ctx.author}")
    embed.add_field(name="Hex", value=hexcol)
    embed.add_field(name="RGB", value=rgb)
    embed.add_field(name="INT", value=intcol)
    embed.set_footer(
        text="You can use the color command to get more details about the color"
    )
    await ctx.send(embed=embed)


@client.command(aliases=["col", "color"], description="Sends info about a color")
async def colour(ctx, color: str):
    session = aiohttp.ClientSession()
    async with ctx.typing():
        generated_color = color
        hexcol = generated_color.replace("#", "")
        async with session.get(f"http://www.thecolorapi.com/id?hex={hexcol}") as response:
            data = json.loads(await response.text())
        await session.close()
        color_name = data.get("name").get("value")
        link = f"http://singlecolorimage.com/get/{hexcol}/1x1"
        thumb = f"http://singlecolorimage.com/get/{hexcol}/100x100"
        rgb = data.get("rgb").get("value")
        hexcol = data.get("hex").get("value")
        hsl = data["hsl"]["value"]
        hsv = data["hsv"]["value"]
        cmyk = data["cmyk"]["value"]
        xyz = data["XYZ"]["value"]
        intcol = int(hexcol.replace("#", ""), 16)

    embed = discord.Embed(
        timestamp=ctx.message.created_at, color=int(hexcol.replace("#", ""), 16)
    )
    embed.set_author(name=color_name)
    embed.set_image(url=link)
    embed.set_thumbnail(url=thumb)
    embed.set_footer(text=f"Made for {ctx.author}")
    embed.add_field(name="Hex", value=hexcol)
    embed.add_field(name="RGB", value=rgb)
    embed.add_field(name="INT", value=intcol)
    embed.add_field(name="HSL", value=hsl)
    embed.add_field(name="HSV", value=hsv)
    embed.add_field(name="CMYK", value=cmyk)
    embed.add_field(name="XYZ", value=xyz)
    await ctx.send(embed=embed)
    session.close()


@client.command(
    aliases=["setprefix"],
    description="Sets a prefix for a server but doesn’t work always :(",
)
@has_permissions(manage_guild=True)
async def prefix(ctx, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    await ctx.send(f"prefix set to `{prefix}`")
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@client.command(aliases=["speak", "echo", "s"], description="Sends a message")
async def say(ctx, *, args: commands.clean_content):
    mesg = args
    channel = ctx.message.channel
    try:
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
    except commands.MissingPermissions:
        pass
    await channel.send(mesg)


@client.command(
    description="Changes role for a user (removes if he has the role, adds the role if he doesn't)"
)
async def role(ctx, member: discord.Member,*,  role: discord.Role):
    try:
        member = member[0]
        role = role[0]
    except IndexError:
        await ctx.send("Invalid usage")
    
    if role in member.roles:  # checks all roles the member has
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


@client.command(
    aliases=["hg", "howlesbian", "hl"], description="Check how gay a person is (random)"
)
async def howgay(ctx, member: discord.Member = None):
    member = member or ctx.message.author
    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
    embed.set_author(name="Gay Telling Machine")
    embed.set_footer(text=f"Requested by {ctx.author}")
    if ctx.message.author.id == 538332632535007244:
        gay = 0
    else:
        gay = secureRandom.randint(0, 100)
    embed.add_field(name="How Gay?", value=f"{member.name} is {gay}% gay")
    await ctx.send(embed=embed)


@client.command(aliases=["search"], description="Generates a link to search google")
async def google(ctx, *, args):
    result = "http://www.google.com/search?q=" + args.replace(" ", "+") + "&safe=active"
    await ctx.send(result)


@client.command(
    aliases=["pick", "choice", "ch"], description="makes desicions for you :)"
)
async def choose(ctx, *, args):
    mesg = args
    mesglist = mesg.split(",")
    num = 0
    choices = ""
    embed = discord.Embed(timestamp=ctx.message.created_at)
    embed.set_author(name="Choice Machine")
    embed.set_footer(text=f"Asked by {ctx.author}")
    for i in mesglist:
        num += 1
        choices += f"`{i}`, "
    embed.add_field(name="Choice {num}", value=f"{choices[:-2]}")
    embed.add_field(name="‌", value="‌")
    embed.add_field(name="**Chosen**", value=f"{secureRandom.choice(mesglist)}")
    await ctx.send(embed=embed)


@client.command(aliases=["p"], description="Shows the bot's speed")
async def ping(ctx):
    start = timemodule.perf_counter()
    embed = discord.Embed(
        description="**Websocket Latency** = Time it takes to recive data from the discord API\n**Response Time** = Time it takes between seeing your message then sending a response\n**Bot Latency** = Time needed to send/edit messages"
    )
    embed.set_author(name="Ping")
    embed.set_footer(text=f"Asked by {ctx.author}")
    embed.add_field(name="Websocket Latency", value=f"{round(client.latency * 1000)}ms")
    message = await ctx.send(embed=embed)
    end = timemodule.perf_counter()
    message_ping = (end - start) * 1000
    embed.set_author(name="Ping")
    embed.set_footer(text=f"Asked by {ctx.author}")
    embed.add_field(
        name="Response Time",
        value=f"{round((message.created_at - ctx.message.created_at).total_seconds()/1000, 4)}ms",
    )
    embed.add_field(name="Bot Latency", value=f"{round(message_ping)}ms")
    await message.edit(embed=embed)


@client.command(aliases=["synonym"], description="Sends synomyms for a word")
async def synonyms(ctx, *, args):
    api_key = "dict.1.1.20200701T101603Z.fe245cbae2db542c.ecb6e35d1120ee008541b7c1f962a6d964df61dd"
    session = aiohttp.ClientSession()
    async with ctx.typing():
        embed = discord.Embed(timestamp=ctx.message.created_at)
        embed.set_author(name=f"Synonyms for {args}")
        async with session.get(
            f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={api_key}&lang=en-en&text={args.lower()}"
        ) as response:
            data = await response.json()
        await session.close()
        num = 0
        try:
            synonyms = data.get("def")[0].get("tr")
            for i in synonyms:
                num += 1
                embed.add_field(name=f"Synonym {num}", value=i.get("text"), inline=True)
        except:
            embed.add_field(name="No synonyms found", value="‌Command Aborted")
    await ctx.send(embed=embed)


@client.command(
    aliases=["urbandict", "urbandefine", "urbandefinition", "ud", "urbandictionary"],
    description="Searches The Urban Dictionary (nsfw only)",
)
async def urban(ctx, *, args):
    if not ctx.channel.is_nsfw():
        await ctx.send(
            "You can use this only in nsfw channels because the results may include nsfw content"
        )
    else:
        params = {"term": args}
        headers = {
            "x-rapidapi-host": "mashape-community-urban-dictionary.p.rapidapi.com",
            "x-rapidapi-key": "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d",
        }
        num = 0
        embed = discord.Embed(timestamp=ctx.message.created_at)
        embed.set_footer(text="From Urban Dictionary")
        session = aiohttp.ClientSession()
        async with ctx.typing():
            async with session.get(
                "https://mashape-community-urban-dictionary.p.rapidapi.com/define",
                params=params,
                headers=headers,
            ) as response:
                parsed_json = json.loads(await response.text())
            await session.close()
            try:
                data = parsed_json.get("list")
                for i in data:
                    num += 1
                    if not len(i.get("definition")) > 1024:
                        embed.add_field(
                            name=f"Definition {num}",
                            value=i.get("definition")
                            .replace("[", "**")
                            .replace("]", "**"),
                        )
                    else:
                        embed.add_field(name=i.get("definition")[0:1024], value="‌")
            except:
                embed.add_field(name="Error Occured", value="Command Aborted")
            await ctx.send(embed=embed)


@client.command(aliases=["members"], description="Get who are in a certain role")
async def getusers(ctx, *, role: discord.Role):
    embed = discord.Embed()
    embed.set_footer(text=f"Asked by {ctx.author}")
    async with ctx.typing():
        empty = True
        for member in ctx.message.guild.members:
            if role in member.roles:
                embed.add_field(name=member, value=member.mention)
                empty = False
    if empty:
        await ctx.send("Nobody has the role {}".format(role.mention))
    else:
        await ctx.send(embed=embed)


@client.command(aliases=["q", "triv", " trivia"], description="Sends a quiz for you to answer")
async def quiz(ctx):
    answered = False
    session = aiohttp.ClientSession()

    def check(message=discord.Message):
        if not message.author.bot:
            return (
                message.author == ctx.message.author
                and message.channel.id == ctx.channel.id
            )

    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    ordlist = [ordinal(n) for n in range(1,5)]
    async with ctx.typing():
        async with session.get(
            "https://opentdb.com/api.php?amount=1&type=multiple"
        ) as response:
            data = json.loads(await response.text())
        await session.close()
        question = (
            data.get("results")[0]
            .get("question")
            .replace("&#039;", "'")
            .replace("&quot;", '"')
            .replace("&amp;", " &")
            .replace("&eacute;", "é")
        )
        difficulty = data.get("results")[0].get("difficulty")
        category = (
            data.get("results")[0]
            .get("category")
            .replace("Entertainment: ", "")
            .replace("Science: ", "")
        )
        embed = discord.Embed(title=question, description=f"Category: {category.title()}\nDifficulty: {difficulty.title()}")
        embed.set_footer(text=f"Trivia/Quiz for {ctx.author}")
        correct_answer = "not found"
        randomint = secureRandom.randint(1, 4)
        if randomint == 1:
            correct_answer = "a"
            embed.add_field(
                name="A",
                value=data.get("results")[0]
                .get("correct_answer")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="B",
                value=data.get("results")[0]
                .get("incorrect_answers")[0]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="C",
                value=data.get("results")[0]
                .get("incorrect_answers")[1]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="D",
                value=data.get("results")[0]
                .get("incorrect_answers")[2]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
        if randomint == 2:
            correct_answer = "b"
            embed.add_field(
                name="A",
                value=data.get("results")[0]
                .get("incorrect_answers")[0]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="B",
                value=data.get("results")[0]
                .get("correct_answer")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="C",
                value=data.get("results")[0]
                .get("incorrect_answers")[1]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="D",
                value=data.get("results")[0]
                .get("incorrect_answers")[2]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
        if randomint == 3:
            correct_answer = "c"
            embed.add_field(
                name="A",
                value=data.get("results")[0]
                .get("incorrect_answers")[0]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="B",
                value=data.get("results")[0]
                .get("incorrect_answers")[1]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="C",
                value=data.get("results")[0]
                .get("correct_answer")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="D",
                value=data.get("results")[0]
                .get("incorrect_answers")[2]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
        if randomint == 4:
            correct_answer = "d"
            embed.add_field(
                name="A",
                value=data.get("results")[0]
                .get("incorrect_answers")[0]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="B",
                value=data.get("results")[0]
                .get("incorrect_answers")[1]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="C",
                value=data.get("results")[0]
                .get("incorrect_answers")[2]
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
            embed.add_field(
                name="D",
                value=data.get("results")[0]
                .get("correct_answer")
                .replace("&#039;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", " &")
                .replace("&eacute;", "é"),
                inline=False
            )
    await ctx.send(embed=embed)
    try:
        message = await client.wait_for("message", timeout=20.0, check=check)
    except asyncio.TimeoutError:
        if not answered:
            await ctx.message.channel.send(
                f"{ctx.author.mention}, You didn\’t answer in time"
            )
    else:
        if not answered:
            if str(message.content).strip().lower() == correct_answer:
                await ctx.message.channel.send("Correct you big brain")
            else:
                await ctx.send(
                    f"Poo Poo Brain xD, Correct answer was {correct_answer.upper()} ({ordlist[randomint-1]} option)"
                )
            answered = True


@client.command(description="Translate a text")
async def translate(ctx, lang: str = "en", *, args):
    embed = discord.Embed(timestamp=ctx.message.created_at)
    embed.set_footer(text="From Yandex")
    session = aiohttp.ClientSession()
    async with ctx.typing():
        if not lang == "help":
            try:
                async with session.get(
                    f"https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20200414T062446Z.1e5abaa65939d784.390d015d69abbe56445b9ba840e7b556c709efd2&text={args}&lang={lang}"
                ) as response:
                    parsed_json = json.loads(await response.text())
                await session.close()
                translation = parsed_json.get("text")[0]
                embed.add_field(name=f"Translation of {args}", value=translation)
            except:
                if parsed_json.get("code") == 501:
                    embed.add_field(
                        name="Error Occured",
                        value="it may be servers fault or you didn’t provide us with the details we need \n we need a language and a text to be translated in that language and the list of available languages can be found at \n [this link](https://tech.yandex.com/translate/doc/dg/concepts/api-overview-docpage)",
                    )
        else:
            async with session.get(
                "https://translate.yandex.net/api/v1.5/tr.json/getLangs?ui=en&key=trnsl.1.1.20200414T062446Z.1e5abaa65939d784.390d015d69abbe56445b9ba840e7b556c709efd2&"
            ) as response:
                parsed_json = json.loads(await response.text())
            await session.close()
            for i in parsed_json.get("langs"):
                parsed_langs = parsed_json.get("langs")[i]
                languages = f"{i}  --->  {parsed_langs} \n"
            embed.add_field(name="Languages", value=languages)
    await ctx.send(embed=embed)


@client.command(
    aliases=["link", "message"],
    description="Generates a link to a message (usefull in mobile)",
)
async def messagelink(ctx, messageid: int = None):
    messageid = messageid or ctx.message.id
    await ctx.send(
        f"https://discord.com/channels/{ctx.message.guild.id}/{ctx.message.channel.id}/{messageid}"
    )


@client.command()
async def mute(ctx, user: discord.Member, reason="No Reason Specified"):
    role = discord.utils.get(
        ctx.guild.roles, name="Muted"
    )  # retrieves muted role returns none if there isn't
    if not role:  # checks if there is muted role
        try:  # creates muted role
            muted = await ctx.guild.create_role(
                name="Muted", reason="To use for muting"
            )
            for (
                channel
            ) in (
                ctx.guild.channels
            ):  # removes permission to view and send in the channels
                await channel.set_permissions(
                    muted,
                    send_messages=False,
                    read_message_history=False,
                    read_messages=False,
                )
        except discord.Forbidden:
            return await ctx.send(
                "I have no permissions to make a muted role"
            )  # self-explainatory
        await user.add_roles(muted)  # adds newly created muted role
        await ctx.send(f"{user.mention} has been muted for {reason}")
    else:
        await user.add_roles(role)  # adds already existing muted role
        await ctx.send(f"{user.mention} has been muted for {reason}")


@client.command(
    aliases=["botinvite", "inv"], description="Sends the invite link for the bot"
)
async def invite(ctx):
    await ctx.send(
        "https://discordapp.com/oauth2/authorize?client_id=707883141548736512&scope=bot&permissions=109640"
    )


@client.command(
    aliases=["pfp", "av", "profilepicture", "profile"],
    description="Sends your or another users avatar",
)
async def avatar(
    ctx, *, avamember: discord.Member = None,
):
    avamember = avamember or ctx.message.author
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)


@client.command(
    name="help",
    aliases=["halp", "h"],
    description="Sends help :)",
    usage="help `[command]`\n\nhelp\nhelp userinfo",
)
async def helpcommand(ctx, command: str = None):
    all_commands = ""
    if command is None:
        for i in client.commands:
            all_commands += f"`{i.name}`, "
        if ctx.guild is None:
        	color = None
        else:
        	color = ctx.guild.me.color
        embed = discord.Embed(
            colour=color,
            title=f"All Commands ({len(client.commands)})",
            description=all_commands,
        )
        await ctx.send(embed=embed)
    else:
        all_commands_list = []
        all_commands_name_list = []
        for i in client.commands:
            all_commands_name_list.append(i.name)
            all_commands_list.append(i)
        if command.strip().lower() in all_commands_name_list:
            command_for_use = all_commands_list[all_commands_name_list.index(command)]
            aliases = ""
            for i in command_for_use.aliases:
                aliases += f"`{i}`, "
            embed = discord.Embed()
            embed.set_author(name=str(command))

            embed.add_field(name="Name", value=command_for_use.name)
            embed.add_field(name="Description", value=command_for_use.description)
            if not len(aliases) == 0:
                embed.add_field(name="Aliases", value=aliases[:-2])
            else:
                pass
            if not command_for_use.usage is None:
                embed.add_field(name="Usage", value=command_for_use.usage)
            else:
                embed.add_field(name="Usage", value=command_for_use.name + " " + " ".join([f"`{i}`" for i in client.get_command(command_for_use.name).signature.split(" ")]))
            embed.add_field(name="Cooldown", value="None")
            await ctx.send(embed=embed)
        else:
            try:
                embed = discord.Embed(
                    title=f'Command "{str(command)}" was not found, try using the command name instead of it\'s alias',
                    description=f"Did you mean `{difflib.get_close_matches(command.strip().lower(), all_commands_name_list, n=1, cutoff=0.2)[0]}`",
                )
            except IndexError:
                embed = discord.Embed(title="Not Found")
            await ctx.send(embed=embed)


@client.command(description="Shows information about the bots server")
async def servers(ctx):
    serverlist = []
    memberlist = []
    for guild in client.guilds:
        serverlist.append(guild)
        for member in guild.members:
            memberlist.append(member)
    servers = len(serverlist)
    members = len(memberlist)
    average = round(int(members) / int(servers))
    await ctx.send(
        f"I'm in {servers:3,} servers and there are {members:3,} members total in all servers combined and {average:3,}  on average in each server"
    )


@client.command(
    aliases=["8ball", "eightball", "eight ball", "question", "answer", "8b"],
    description="Sends a yes/no type answer to a question",
)
async def _8ball(ctx, *, question):
    answers = [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes – definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes Signs point to yes",
        "Reply hazy",
        "try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Dont count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
    ]
    await ctx.send(f"`Question:` {question}\n`Answer:` {secureRandom.choice(answers)}")


@client.command(aliases=["wiki", "searchwiki"])
async def wikipedia(ctx, *, args):
    async with ctx.typing():
        result = wikimodule.summary(args)
        if len(result) < 1997:
            await ctx.send(result)
        else:
            await ctx.send(result[0:1997] + "...")


@client.command(
    name="clear",
    aliases=["remove", "delete", "erase", "c"],
    description=" clears a certain amount of messages",
)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    amount += 1
    deleted = await ctx.channel.purge(limit=amount)
    message = await ctx.send(f"Deleted `{len(deleted)}` messages")
    await asyncio.sleep(2)
    await message.delete()


@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the amount of messages to delete")


@client.command(description="Kicks a user ")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention}")


@client.command(
    aliases=["setnick", "setnickname", "nickname", "changenickname", "chnick"],
    description="Sets a users nickname",
)
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nick):
    await member.edit(nick=nick)
    await ctx.send(f"Nickname was changed for {member.mention} ")


@client.command(description="Bans a user")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention}")


@client.command(
    description="Unbans a previously banned user with their name and discriminator "
)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member: str):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            success = True
    if success:
        await ctx.send(f"Unbanned {user.mention}")
    else:
        await ctx.send("User not found")


@client.command(aliases=["ui", "whois", "wi"], description="Shows info about a user")
async def userinfo(ctx, *, member: discord.Member = None):
    member = member or ctx.message.author

    roles = [role for role in reversed(member.roles)]
    roles = roles[:-1]
    flaglist = [flag for flag in member.public_flags.all()]
    flagstr = ""
    for i in flaglist:
    	flagstr += f"{get_flag(i.name)} "
    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=f"{member}", icon_url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")
    if member.id == 538332632535007244:
        embed.add_field(
            name="Fun Fact:",
            value="He is the owner and the only person that developed this bot",
        )
    embed.add_field(name="ID: ", value=member.id)
    embed.add_field(name="Guild name:", value=member.display_name)
    if not len(flaglist) == 0:
        embed.add_field(name="Badges", value=flagstr)
    
    embed.add_field(
        name="Online Status",
        value=f"Desktop: {get_status(member.desktop_status.name)}\nWeb: {get_status(member.web_status.name)}\nMobile: {get_status(member.mobile_status.name)}",
    )
    embed.add_field(
        name="Created at", value=f'{member.created_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.utcnow() - member.created_at)})'
    )

    embed.add_field(
        name="Joined at:", value=f'{member.joined_at.strftime("%a, %d %B %Y, %H:%M:%S")}  ({humanize.precisedelta(datetime.utcnow() - member.created_at)})'
    )

    embed.add_field(
        name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles])
    )
    embed.add_field(name="Top role:", value=member.top_role.mention)

    if not member.bot:
        member_type = ":blond_haired_man: Human"
    else:
        member_type = ":robot: Robot"
    embed.add_field(name="Type", value=member_type)

    await ctx.send(embed=embed)


client.run(os.environ["token"])
