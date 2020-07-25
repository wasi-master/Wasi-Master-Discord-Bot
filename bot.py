import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import has_permissions
import json
import random
import randomcolor
import requests
import time
import wikipedia as wikimodule
from datetime import datetime
import asyncio
import codecs
import os
import pathlib
import urllib.parse
import base64 as base64module

def get_prefix(client, message):
	try:
		with open("prefixes.json", "r") as f:
			prefixes = json.load(f)
		return prefixes[str(message.guild.id)]
	except:
		return ","
		
def convert_sec_to_min(seconds):
    min, sec = divmod(seconds, 60)
    return "%02d:%02d" % (min, sec)

def get_p(prog, num=0):
	numlist = list(range(0, 101, 5))
	text= ""
	for i in numlist:
		num +=1
		if prog > i and numlist[num] > prog:
			text += "⬤"
		else:
			text += "—"
	return f"```{text}```"
		
client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')


    
@tasks.loop(seconds=3600)
async def update_server_count():
	memberlist = []
	serverlist = []
	for guild in client.guilds:
		serverlist.append(guild)
		for member in guild.members:
			memberlist.append(member)
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(memberlist)} members in {len(serverlist)} servers"))

@client.event
async def on_ready():
    print("Bot is online")
    update_server_count.start()
    client.load_extension('jishaku')

@client.event
async def on_guild_join(guild):
	owner = client.get_user(538332632535007244)
	await owner.send(f"Added to {guild.name}")
	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = ','
	
	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		
@client.event
async def on_guild_remove(guild):
	owner = client.get_user(538332632535007244)
	await owner.send(f"Removed from {guild.name}")
	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
	prefixes.pop(str(guild.id))

	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		

@client.event
async def on_command_error(ctx, error):
	if "CheckFailure" in str(error):
		await ctx.send(f"You don\'t have the permission to use {ctx.command}")
	elif "MissingPermissions" in str(error):
		await ctx.send('I can\'t do that')
	elif "MissingRequiredArgument" in str(error):
		await ctx.send('Something is missing')
	elif "You are missing" in str(error):
		pass
	elif "is not found" in str(error).lower():
		pass
	elif "Cannot send messages to this user" in str(error):
		pass
	
	else:
		await ctx.send(f"error occured:\n {error}")
		raise error

@client.command()
async def progress(ctx, p: int):
	await ctx.send(get_p(p))

@client.command(aliases=['tenor'])
async def gif(ctx, *, query: str):
	apikey= "8ZQV38KW9TWP"
	lmt = 1
	search_term = query
	async with ctx.typing():
		r = requests.get("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt))
		gifs = json.loads(r.text)
		gif: str = gifs['results'][0]['media'][0]['gif']['url']
		await ctx.send(gifs)
		
@client.command()
async def ip(ctx):
	ip = requests.get("https://api.ipify.org").text
	await ctx.message.author.send(ip)

@client.command()
async def base64(ctx, task, *, text):
	if task.strip().lower() == 'encode':
		data = text
		encodedBytes = base64module.b64encode(data.encode("utf-8")) 
		encodedStr = str(encodedBytes, "utf-8") 
		await ctx.send(encodedStr)
	elif task.strip().lower() == 'decode':
		data = text
		message_bytes = base64module.b64decode(data)
		message = message_bytes.decode('ascii')
		await ctx.send(message)
	else:
		await ctx.send("Must have either encode or decode")
		
@client.command()
async def support(ctx):
	await ctx.send("https://discord.gg/5jn3bQX")
	
@client.command()
async def remind(ctx, *, text):
	user = ctx.message.author
	textlist = text.strip().split("|")
	texttosend = str(textlist[1])
	timetowait = int(textlist[0].strip())
	await ctx.send(f"Gonna remind you `{texttosend}` in `{timetowait}` seconds")
	await asyncio.sleep(timetowait)
	await user.send(texttosend)
	
@client.command(aliases=["sui"])
async def secretuserinfo(ctx, id: int=None):
	id = id or ctx.message.author.id
	member = client.get_user(id)
	embed = discord.Embed()
	embed.set_author(name=member.name)
	embed.set_image(url=member.avatar_url)
	embed.add_field(name="Account Created At", value=member.created_at.strftime("%a, %d %B %Y, %H:%M:%S"))
	embed.add_field(name="Bot?", value=member.bot)
	await ctx.send(embed=embed)
	
@client.command(aliases=["messagecount", "mc", "countmessages"])
async def message_count(ctx, channel: discord.TextChannel=None):
    channel = channel or ctx.message.channel
    count = 0
    async with ctx.typing():
    	async for _ in channel.history(limit=None):
    		count += 1
    try:
    	await ctx.send(f"There are {count} messages in {channel.mention}")
    except:
    	await ctx.send(f"There are {count} messages")
@client.command(aliases=["makememe"])
async def meme(ctx, *, text):
	base_url = "https://memegen.link/api/templates"
	text = text.strip().replace(" ", "-").replace("?", "~q").replace("#", "~h").replace("%", "~p").replace("/", "~s").replace("\'", "\"")
	textlist = text.split(":")[1].split("||")
	template = text.split(":")[0].strip().replace(" ", "").lower()
	if len(textlist) == 2:
		url = f"{base_url}/{template}/{textlist[0]}/{textlist[1]}"
	elif len(textlist) == 1:
		url = f"{base_url}/{template}/{textlist[0]}"
	else:
		await ctx.send("invalid format")
	async with ctx.typing():
		response = requests.get(url)
	response_json = json.loads(response.text)
	try:
		masked_url = response_json['direct']['masked']
	except:
		await ctx.send(response.text)
	embed = discord.Embed()
	embed.set_author(name=template.title())
	embed.set_image(url=masked_url)
	await ctx.send(embed=embed)
	
@client.command(aliases=['yt'])
async def youtube(ctx, *, args):
	search_terms = args
	max_results = 1
	results = []
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
	            #res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
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
	        return results[: max_results]
	    return results
	videos = search()
	embed = discord.Embed(title=videos[0]['title'])
	embed.add_field(name="Channel", value=videos[0]['channel'])
	embed.add_field(name="Duration", value=videos[0]['duration'])
	embed.add_field(name="Views", value=videos[0]['views'])
	embed.add_field(name="Watch", value=f"[Click Here to open or long press to copy](https://youtube.com/{videos[0]['url_suffix']})")
	try:
		embed.set_image(url=f"https://img.youtube.com/vi/{videos[0]['id']}/hqdefault.jpg")
	except:
		try:
			embed.set_image(url=videos[0]['thumbnails'][1])
		except:
			try:
				embed.set_image(url=videos[0]['thumbnails'][2])
			except:
				embed.set_image(url=videos[0]['thumbnails'][3])
	await ctx.send(embed=embed)
	
@client.command(aliases=['guildinfo', 'si', 'gi'])
async def serverinfo(ctx):
	guild = ctx.message.guild
	owner = client.get_user(guild.owner_id)
	embed=discord.Embed()
	embed.set_author(name=guild.name)
	embed.add_field(name='ID:', value=guild.id)
	embed.add_field(name="Region", value=str(guild.region).capitalize())
	embed.add_field(name="Emojis", value=len(guild.emojis))
	embed.set_thumbnail(url=guild.icon_url)
	embed.add_field(name="Owners ID", value=guild.owner_id)
	embed.add_field(name="Owners Name", value=owner.name)
	embed.add_field(name="Verification Level", value=str(guild.verification_level).capitalize())
	await ctx.send(embed=embed)
@client.command()
async def info(ctx):
	total = 0
	with codecs.open('bot.py', 'r', 'utf-8') as f:
		for i, l in enumerate(f):
			if l.strip().startswith('#') or len(l.strip()) == 0:  # skip commented lines.
				pass
			else:
				total += 1
	await ctx.send(f'{ctx.message.author.mention}, I am made of {total:,} lines of Python, And I\'m just  a simple bot made by Wasi Master#4245')

@client.command(aliases=['spt'])
async def spotify(ctx, member: discord.Member=None):
	member = member or ctx.message.author
	activity = ctx.message.guild.get_member(member.id)
	successfull= False
	for activity in activity.activities:
		if isinstance(activity, discord.Spotify):
			search_terms = activity.artist + " - " + activity.title
			max_results = 1
			results = []
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
			            #res["long_desc"] = video_data["descriptionSnippet"]["runs"][0]["text"]
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
			        return results[: max_results]
			    return results
			videos = search()
			embed = discord.Embed(color=activity.color)
			embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg")
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
			embed.add_field(name="Spotify Link", value=f"[Click Here](https://open.spotify.com/track/{activity.track_id})")
			embed.add_field(name="Youtube Link", value=f"[Click Here](https://youtube.com/{videos[0]['url_suffix']})")
			embed.add_field(name="Time", value=f"{convert_sec_to_min((datetime.now() - activity.start).total_seconds())}/{str(activity.duration)[2:-7]}")
			embed.set_footer(text="Track ID:" + activity.track_id)
			await ctx.send(embed=embed)
			successfull = True
		else:
			successfull = False
	if not successfull:
		await ctx.send("Not listening to spotify :(")
'''{(((datetime.now() - activity.end)).total_seconds()/100)/((datetime.now() - activity.start).total_seconds())}'''
@client.command()
@commands.has_permissions()
async def leaveserver(ctx):
	if ctx.message.author.id == 538332632535007244:
		await ctx.send("Bye Bye")
		ctx.message.guild.leave()
	else:
		await ctx.send("You are not the owner :grin:")
    
@client.command()
async def music(ctx, *, args):
	url = "https://deezerdevs-deezer.p.rapidapi.com/search"
	querystring = {"q":args}
	
	headers = {
	    'x-rapidapi-host': "deezerdevs-deezer.p.rapidapi.com",
	    'x-rapidapi-key': "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d"
	    }
	async with ctx.typing():
		response = requests.get(url, headers=headers, params=querystring)
		formatted_response = json.loads(response.text)
	
	data = formatted_response.get("data")[0]
	
	#song
	name = data.get("title")
	explict = data.get("explicit_lyrics")
	#artist
	artist = data.get("artist")
	artist_name = artist.get("name")
	artist_picture = artist.get("picture_xl")
	#album
	album = data.get("album")
	album_name = album.get("title")
	album_cover = album.get("cover_xl")
	
	embed = discord.Embed()
	embed.set_author(name=name, icon_url=artist_picture)
	embed.add_field(name='Explict', value=explict)
	embed.add_field(name='Song Name', value=name, inline=True)
	embed.add_field(name='Artist', value=artist_name, inline=True)
	embed.add_field(name='Album', value=album_name, inline=True)
	embed.set_image(url=album_cover)
	await ctx.send(embed=embed)
	
@client.command()
async def debug(ctx):
	guild_number = 0
	for guild in client.guilds:
		guild_number += 1
	await ctx.send(f"in {guild_number} guilds")
	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
		await ctx.send(f"The prefixes file has {len(prefixes)} servers")

@client.command()
async def dm(ctx, *, args):
	await ctx.message.author.send(args)
	
@client.command()
async def paginator(ctx):
    page1=discord.Embed(
        title='Page 1/3',
        description='Description',
        colour=discord.Colour.orange()
    )
    page2=discord.Embed(
        title='Page 2/3',
        description='Description',
        colour=discord.Colour.orange()
    )
    page3=discord.Embed(
        title='Page 3/3',
        description='Description',
        colour=discord.Colour.orange()
    )

    pages=[page1,page2,page3]

    message=await client.send(embed=page1)

    await client.add_reaction(message,'\u23ee')
    await client.add_reaction(message,'\u25c0')
    await client.add_reaction(message,'\u25b6')
    await client.add_reaction(message,'\u23ed')

    i=0
    emoji=''

    while True:
        if emoji=='\u23ee':
            i=0
            await client.edit_message(message,embed=pages[i])
        if emoji=='\u25c0':
            if i>0:
                i-=1
                await client.edit_message(message,embed=pages[i])
        if emoji=='\u25b6':
            if i<2:
                i+=1
                await client.edit_message(message,embed=pages[i])
        if emoji=='\u23ed':
            i=2
            await client.edit_message(message,embed=pages[i])

        res=await client.wait_for_reaction(message=message,timeout=30)
        if res==None:
            break
        if str(res[1])!='Wasi Master#5154': #Example: 'MyBot#1111'
            emoji=str(res[0].emoji)
            await client.remove_reaction(message,res[0].emoji,res[1])

    await client._reactions(message)
@client.command(aliases=['randcolor', 'randomcol', 'randcol', 'randomcolor', 'rc'])
async def randomcolour(ctx):
	async with ctx.typing():
		rand_color = randomcolor.RandomColor()
		generated_color = rand_color.generate()[0]
		hex = generated_color.replace('#', '')
		response = requests.get(f"http://www.thecolorapi.com/id?hex={hex}")
		data = json.loads(response.text)
		color_name = data.get("name").get("value")
		link = f"http://singlecolorimage.com/get/{hex}/1x1"
		rgb = data.get("rgb").get("value")
		hex = data.get("hex").get("value")
	embed = discord.Embed(timestamp=ctx.message.created_at, color=int(hex.replace("#", ""), 16))
	embed.set_author(name=color_name)
	embed.set_image(url=link)
	embed.set_thumbnail(url=link)
	embed.set_footer(text=f"Made for {ctx.author}")
	embed.add_field(name="Hex", value=hex)
	embed.add_field(name="RGB", value=rgb)
	await ctx.send(embed=embed)
 
@client.command(aliases=[ 'col'])
async def colour(ctx, color: str):
	async with ctx.typing():
		generated_color = color
		hex = generated_color.replace('#', '')
		response = requests.get(f"http://www.thecolorapi.com/id?hex={hex}")
		data = json.loads(response.text)
		color_name = data.get("name").get("value")
		link = f"http://singlecolorimage.com/get/{hex}/1x1"
		rgb = data.get("rgb").get("value")
		hex = data.get("hex").get("value")
	embed = discord.Embed(timestamp=ctx.message.created_at, color=int(hex.replace("#", ""), 16))
	embed.set_author(name=color_name)
	embed.set_image(url=link)
	embed.set_thumbnail(url=link)
	embed.set_footer(text=f"Made for {ctx.author}")
	embed.add_field(name="Hex", value=hex)
	embed.add_field(name="RGB", value=rgb)
	await ctx.send(embed=embed)
 
 
@client.command(aliases=["setprefix"])
@has_permissions(manage_guild=True)
async def prefix(ctx, prefix):
	with open("prefixes.json", "r") as f:
		  prefixes = json.load(f)
	prefixes[str(ctx.guild.id)] = prefix
	await ctx.send(f"prefix set to `{prefix}`")
	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		
@client.command(aliases=['speak', 'echo', 's'])
async def say(ctx, *, args): 
    mesg = args
    channel = ctx.message.channel
    try:
    	if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
    		await ctx.message.channel.purge(limit=1)
    except:
    	pass
    await channel.send(mesg)

@commands.command(aliases=["wmsd"])
async def wasimasterspecialdm(ctx, id:int=None, *, args):
	if ctx.message.author.id == 538332632535007244:
		user = client.get_user(id)
		await user.send(args)
	else:
		await ctx.send("Command Not Found")

@client.command()
async def role(ctx, member: discord.Member, role: discord.Role):
        if role in member.roles: #checks all roles the member has
            await member.remove_roles(role)
            embed = discord.Embed(colour=16711680, timestamp=ctx.message.created_at)
            embed.set_author(name=f'Role Changed for {member}')
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Removed Role", value=f'@{role}')
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(colour=65280, timestamp=ctx.message.created_at)
            embed.set_author(name=f'Role Changed for {member}')
            embed.set_footer(text=f"Done by {ctx.author}")
            embed.add_field(name="Added Role", value=f'@{role}')
            await ctx.send(embed=embed)
   
@client.command(aliases=['hg', 'howlesbian', 'hl'])
async def howgay(ctx, member: discord.Member=None):
     member = member or ctx.message.author
     embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
     embed.set_author(name='Gay Telling Machine')
     embed.set_footer(text=f"Requested by {ctx.author}")
     embed.add_field(name="How Gay?", value=f"{member.name} is {random.randint(0, 100)}% gay")
     await ctx.send(embed=embed)
     
@client.command(aliases=['search'])
async def google(ctx, *, args):
    result = "http://www.google.com/search?q=" + args.replace(" ", "+") + "&safe=active"
    await ctx.send(result)
    	
@client.command(aliases=['pick', 'choice', 'ch']) 
async def choose(ctx, *, args): 
    mesg = args
    mesglist = mesg.split(",")
    num = 0
    embed = discord.Embed(timestamp=ctx.message.created_at)
    embed.set_author(name=f'Choice Machine')
    embed.set_footer(text=f"Asked by {ctx.author}")
    for i in mesglist:
        num += 1
        embed.add_field(name=f"Choice {num}", value=f"{i}")
    embed.add_field(name="‌", value="‌")
    embed.add_field(name=f"**Chosen**", value=f"{random.choice(mesglist)}")
    await ctx.send(embed=embed)
    
@client.command()
async def emoji(ctx):
    msg = await ctx.send("working")
    reactions = ['joy']
    for emoji in reactions: 
        await ctx.add_reaction(msg, emoji)
             
  
@client.command(aliases=['p'])
async def ping(ctx):
    start = time.perf_counter()
    embed = discord.Embed(timestamp=ctx.message.created_at)
    embed.set_author(name='Ping')
    embed.set_footer(text=f"Asked by {ctx.author}")
    embed.add_field(name="Websocket Latency", value=f'{round(client.latency * 1000)}ms')
    message = await ctx.send(embed=embed)
    end = time.perf_counter()
    message_ping = (end - start) * 1000
    embed.set_author(name='Ping')
    embed.set_footer(text=f"Asked by {ctx.author}")
    embed.add_field(name="Response latency", value=f"{round(message_ping)}ms")
    await message.edit(embed=embed)
    
	
@client.command(aliases=['synonym'])
async def synonyms(ctx, *, args):
	api_key = "dict.1.1.20200701T101603Z.fe245cbae2db542c.ecb6e35d1120ee008541b7c1f962a6d964df61dd"
	async with ctx.typing():
		embed = discord.Embed(timestamp=ctx.message.created_at)
		embed.set_author(name=f"Synonyms for {args}")
		response = requests.get(f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={api_key}&lang=en-en&text={args.lower()}")
		data = response.json()
		num = 0
		try:
			synonyms = data.get("def")[0].get("tr")
			for i in synonyms:
				num += 1
				embed.add_field(name=f"Synonym {num}", value=i.get("text"), inline=True)
		except:
			embed.add_field(name="No synonyms found", value="‌Command Aborted")
	await ctx.send(embed=embed)


@client.command(aliases=['urbandict', 'urbandefine', 'urbandefinition', 'ud', 'urbandictionary'])
async def urban(ctx, *, args):
	if not ctx.channel.is_nsfw():
	    await ctx.send("You can use this only in nsfw channels because the results may include nsfw content")
	else:
		params = {"term": args}
		headers ={"x-rapidapi-host": "mashape-community-urban-dictionary.p.rapidapi.com","x-rapidapi-key": "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d"}
		num = 0
		embed = discord.Embed(timestamp=ctx.message.created_at)
		embed.set_footer(text="From Urban Dictionary")
		async with ctx.typing():
			response = requests.get("https://mashape-community-urban-dictionary.p.rapidapi.com/define", params=params, headers=headers);
			try:
				parsed_json = json.loads(response.text)
				data = parsed_json.get("list")
				for i in data:
					num += 1
					if not len(i.get("definition")) > 1024:
						embed.add_field(name=f"Definition {num}", value=i.get("definition").replace("[", "**").replace("]", "**"))
					else:
						embed.add_field(name=definition[0:1024], value="‌")
			except:
				embed.add_field(name="Error Occured", value="Command Aborted")
			await ctx.send(embed=embed)

@client.command()  
async def getusers(ctx, role: discord.Role):
	embed = discord.Embed()
	embed.set_footer(text=f"Asked by {ctx.author}")
	async with ctx.typing():
	    empty = True
	    for member in ctx.message.guild.members:
	        if role in member.roles:
	            embed.add_field(name="{0.name}".format(member), value="{0.id}".format(member))
	            empty = False
	if empty:
	    await ctx.send("Nobody has the role {}".format(role.mention))
	else:
	    await ctx.send(embed=embed)
  
@client.command()
async def allnickname(ctx, role: discord.Role, *, args):
	embed = discord.Embed()
	embed.set_footer(text=f"Asked by {ctx.author}")
	async with ctx.typing():
	    empty = True
	    for member in ctx.message.guild.members:
	    	try:
	    		name = member.name
	    		await member.edit(nick=f"{name}{args}")
	    		embed.add_field(name=name, value="succes")
	    	except:
	    		name = member.name
	    		embed.add_field(name=name, value="failure")
	    
	    await ctx.send(embed=embed)
     			
@client.command()
async def define(ctx, *, args):
	embed = discord.Embed(timestamp=ctx.message.created_at)
	embed.set_footer(text="From Merriam Webster")
	async with ctx.typing():
		with open("dictionary.json", "r" ) as f:
			parsed_json = json.load(f)
			definition = parsed_json.get(args.lower())
	if not definition == None:
		if not len(definition) > 1024:
			await ctx.send(embed=embed)
		else:
			await ctx.send("Definition too long")
	else:
		await ctx.send("No definition found")
		
@client.command()
async def quiz(ctx):
	quiz = True
	def check(message = discord.Message):
		if not message.author.bot:
			return message.author == ctx.message.author and str(message.content).strip().lower() == correct_answer
	
	embed = discord.Embed()
	embed.set_author(name=f"{ctx.author}\'s Quiz")
	embed.set_footer(text="From Open Trivia DB")
	async with ctx.typing():
		response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
		data = json.loads(response.text)
		
		question = data.get("results")[0].get("question").replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é")
		embed.add_field(name=question, value="‌")
		
		difficulty =  data.get('results')[0].get('difficulty')
		embed.add_field(name="difficulty", value=difficulty)
		
		category = data.get('results')[0].get('category').replace("Entertainment: ", "")
		embed.add_field(name="Category", value=category)
		correct_answer = ""
		randomint = random.randint(0, 4)
		if randomint == 1:
			correct_answer = "a"
			embed.add_field(name="A", value=data.get("results")[0].get("correct_answer").replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[0].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[1].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 2:
			correct_answer = "b"
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("correct_answer").replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[1].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 3:
			correct_answer = "c"
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[1].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("correct_answer").replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 4:
			correct_annswer = "d"
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[1].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[2].replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("correct_answer").replace("&#39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
	await ctx.send(embed=embed)
	try:
		reaction, user = await client.wait_for('message', timeout=20.0, check=check)
	except asyncio.TimeoutError:
		await ctx.message.channel.send('You didn\’t answer in time ')
	else:
		await ctx.message.channel.send('Correct you big brain')
	finally:
		await ctx.message.channel.send("Stopped listening to that message\'s reactions")
@client.command()
async def lol(ctx):
  await ctx.send("send your name in 69 seconds")

  def check(m):
    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

  try:
    name = await bot.wait_for('message', check=check, timeout=69)
  except asyncio.TimeoutError:
    await ctx.send(f"you didnt respond :( {ctx.author}!")
  else:
    await ctx.send(f"i see {ctx.author} your name is {name.content}")
    		      
@client.command()
async def translate(ctx, lang, *, args):
	embed = discord.Embed(timestamp=ctx.message.created_at)
	embed.set_footer(text="From Yandex")
	async with ctx.typing():
		if not lang == "help":
			try:
				response = requests.get(f"https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20200414T062446Z.1e5abaa65939d784.390d015d69abbe56445b9ba840e7b556c709efd2&text={args}&lang={lang}")
				parsed_json = json.loads(response.text)
				translation = parsed_json.get('text')[0]
				embed.add_field(name=f"Translation of {args}", value=translation)
			except:
				if parsed_json.get("code") == 501:
					embed.add_field(name="Error Occured", value="it may be our fault or you didn’t provide us with the details we need \n we need a language and a text to be translated in that language and the list of available languages can be found at \n https://tech.yandex.com/translate/doc/dg/concepts/api-overview-docpage/")
		else:
			response = requests.get(f"https://translate.yandex.net/api/v1.5/tr.json/getLangs?ui=en&key=trnsl.1.1.20200414T062446Z.1e5abaa65939d784.390d015d69abbe56445b9ba840e7b556c709efd2&")
			parsed_json = json.loads(response.text)
			for i in parsed_json.get("langs"):
				parsed_langs = parsed_json.get("langs")[i]
				languages = f"{i}  --->  {parsed_langs} \n" 
			embed.add_field(name="Languages", value=languages)
	await ctx.send(embed=embed)

@client.command(aliases=['link', 'message'])
async def messagelink(ctx):
	await ctx.send(f"https://discord.com/channels/{ctx.message.guild.id}/{ctx.message.channel.id}/{ctx.message.id}")
@client.command()
async def mute(ctx, user : discord.Member, reason="No Reason Specified"):
    role = discord.utils.get(ctx.guild.roles, name="Muted") # retrieves muted role returns none if there isn't 
    hell = discord.utils.get(ctx.guild.text_channels, name="🔥hell🔥") # retrieves channel named hell returns none if there isn't
    if not role: # checks if there is muted role
        try: # creates muted role 
            muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            for channel in ctx.guild.channels: # removes permission to view and send in the channels 
                await channel.set_permissions(muted, send_messages=False,
                                              read_message_history=False,
                                              read_messages=False)
        except discord.Forbidden:
            return await ctx.send("I have no permissions to make a muted role") # self-explainatory
        await user.add_roles(muted) # adds newly created muted role
        await ctx.send(f"{user.mention} has been sent to hell for {reason}")
    else:
        await user.add_roles(role) # adds already existing muted role
        await ctx.send(f"{user.mention} has been sent to hell for {reason}")
       
    if not hell: # checks if there is a channel named hell
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_message_history=False),
                      ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                      muted: discord.PermissionOverwrite(read_message_history=True)} # permissions for the channel
        try: # creates the channel and sends a message
            channel = await ctx.create_channel('🔥hell🔥', overwrites=overwrites)
            await channel.send("Welcome to hell.. You will spend your time here until you get unmuted. Enjoy the silence.")
        except discord.Forbidden:
            return await ctx.send("I have no permissions to make 🔥hell🔥")
            
@client.command(aliases=['bi'])
async def botinvite(ctx):
    await ctx.send("https://discordapp.com/oauth2/authorize?client_id=707883141548736512&scope=bot&permissions=109640")

@client.command(aliases=['pfp', 'av', 'profilepicture', 'pp', 'profile'])
async def avatar(ctx, *,  avamember : discord.Member=None,):
    avamember = avamember or ctx.message.author
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)


@client.command(aliases=['halp'])
async def help(ctx):
	user = ctx.message.author
	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
		try:
			prefix = prefixes[str(ctx.message.guild.id)]
		except:
			prefix = ","
	embed = discord.Embed(colour=ctx.guild.me.color, timestamp=ctx.message.created_at)
	embed.set_author(name='Help')
	embed.set_footer(text=f"Requested by {ctx.author}")
	embed.add_field(name=f"{prefix}help", value='shows this help message')
	embed.add_field(name=f"{prefix}ping", value='shows the latency of the bot')
	embed.add_field(name=f"{prefix}8ball `<question>`", value='genarates a answer to a question')
	embed.add_field(name=f"{prefix}clear `<amount>`", value='clears a amount of messages')
	embed.add_field(name=f"{prefix}kick `<@mention>`", value='kicks a member')
	embed.add_field(name=f"{prefix}ban `<@mention>`", value='bans a member')
	embed.add_field(name=f"{prefix}userinfo `<@mention>`", value='shows info about a user')
	embed.add_field(name=f"{prefix}say `<string>`", value='the bot says anything you type after, say')
	embed.add_field(name=f"{prefix}avatar `<@mention>`", value='shows the avatar of the user that you mention after ,avatar')
	embed.add_field(name=f"{prefix}choose `<items separated by commas>`", value='chooses an item from the items you say and separate by commas after ,choose')
	embed.add_field(name=f"{prefix}invite", value='sends the bot invite lnk')
	embed.add_field(name=f"{prefix}howgay `<@mention>`", value='shows how gay a user is')
	embed.add_field(name=f"{prefix}role `<@mention>`", value='Changes role for a user')
	embed.add_field(name=f"{prefix}prefix `<prefix>`", value='Used to set a custom prefix')
	embed.add_field(name=f"{prefix}google `<query>`", value='Used to search google without having to open google and search manually')
	embed.add_field(name=f"{prefix}synonyms `<word>`", value='Returns the synonyms of a word')
	embed.add_field(name=f"{prefix}urbandictionary `<word>`", value='Retyrns the definitions of a word found in urban dictionary')
	embed.add_field(name=f"{prefix}define `<word>`", value='Returns the definitions of a word found in merriam webster')
	embed.add_field(name=f"{prefix}translate `<language>` `<text>`", value='Returns the translation of a text found in Yandex')
	embed.add_field(name=f"{prefix}quiz", value='Used to get a quiz (not fully made)')
	embed.add_field(name=f"{prefix}link", value='Used to get a link to the message')
	embed.add_field(name=f"{prefix}dm `<text>`", value='Used to send the person writing this command a dm which can be used to remember something')
	embed.add_field(name=f"{prefix}getusers `<@role>`", value="used to get users that have a specefic oile")
	await ctx.send("Help has been sent to your dm")
	await user.send(embed=embed)
    
@help.error
async def help_error(ctx, error):
	if "Cannot send messages to this user" in str(error):
		with open("prefixes.json", "r") as f:
			prefixes = json.load(f)
			try:
				prefix = prefixes[str(ctx.message.guild.id)]
			except:
				prefix = ","
		embed = discord.Embed(colour=ctx.guild.me.color, timestamp=ctx.message.created_at)
		embed.set_author(name='Help')
		embed.set_footer(text=f"Requested by {ctx.author}")
		embed.add_field(name=f"{prefix}help", value='shows this help message')
		embed.add_field(name=f"{prefix}ping", value='shows the latency of the bot')
		embed.add_field(name=f"{prefix}8ball `<question>`", value='genarates a answer to a question')
		embed.add_field(name=f"{prefix}clear `<amount>`", value='clears a amount of messages')
		embed.add_field(name=f"{prefix}kick `<@mention>`", value='kicks a member')
		embed.add_field(name=f"{prefix}ban `<@mention>`", value='bans a member')
		embed.add_field(name=f"{prefix}userinfo `<@mention>`", value='shows info about a user')
		embed.add_field(name=f"{prefix}say `<string>`", value='the bot says anything you type after, say')
		embed.add_field(name=f"{prefix}avatar `<@mention>`", value='shows the avatar of the user that you mention after ,avatar')
		embed.add_field(name=f"{prefix}choose `<items separated by commas>`", value='chooses an item from the items you say and separate by commas after ,choose')
		embed.add_field(name=f"{prefix}invite", value='sends the bot invite lnk')
		embed.add_field(name=f"{prefix}howgay `<@mention>`", value='shows how gay a user is')
		embed.add_field(name=f"{prefix}role `<@mention>`", value='Changes role for a user')
		embed.add_field(name=f"{prefix}prefix `<prefix>`", value='Used to set a custom prefix')
		embed.add_field(name=f"{prefix}google `<query>`", value='Used to search google without having to open google and search manually')
		embed.add_field(name=f"{prefix}synonyms `<word>`", value='Returns the synonyms of a word')
		embed.add_field(name=f"{prefix}urbandictionary `<word>`", value='Retyrns the definitions of a word found in urban dictionary')
		embed.add_field(name=f"{prefix}define `<word>`", value='Returns the definitions of a word found in merriam webster')
		embed.add_field(name=f"{prefix}translate `<language>` `<text>`", value='Returns the translation of a text found in Yandex')
		embed.add_field(name=f"{prefix}quiz", value='Used to get a quiz (not fully made)')
		embed.add_field(name=f"{prefix}link", value='Used to get a link to the message')
		embed.add_field(name=f"{prefix}dm `<text>`", value='Used to send the person writing this command a dm which can be used to remember something')
		embed.add_field(name=f"{prefix}getusers `<@role>`", value="used to get users that have a specefic oile")
		await ctx.send("Help has been sent to your dm")
		await ctx.send(embed=embed)
	else:
		await ctx.send(f"error occured: {str(error)}")
    
@client.command()
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
    	await ctx.send(f"I\'m in {servers:3,} servers and there are {members:3,} members total d there are {members:3,} members total and {average:3,}  on average in each server")

@client.command(aliases=['8ball', 'eightball', 'eight ball', 'ask', 'question','answer', '8b'])
async def _8ball(ctx, *, question):
    answers = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'You may rely on it',
               'As I see it, yes', 'Most likely', 'Outlook good', 'Yes Signs point to yes', 'Reply hazy', 'try again',
               'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
               'Dont count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
    await ctx.send(f'`Question:` {question}\n`Answer:` {random.choice(answers)}')

@client.command(aliases=['wiki', 'searchwiki'])
async def wikipedia(ctx, *, args):
	async with ctx.typing():
		result = wikimodule.summary(args)
		if len(result) < 1997:
			await ctx.send(result)
		else:
			await ctx.send(result[0:1997] + "...")

@client.command(aliases=['remove', 'delete', 'erase', '', 'c', 'clear'])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount : int):
    amount += 1
    deleted = await ctx.channel.purge(limit=amount)
    message = await ctx.send(f"deleted `{len(deleted)}` messages")
    await asyncio.sleep(2)
    await message.delete()
    
@clear_messages.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the amount of messag esto delete')

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
     await member.kick(reason=reason)
     await ctx.send(f'Kicked {member.mention}')

@client.command(aliases=['setnick', 'setnickname', 'nickname','changenickname', 'chnick'])
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention} ')
    
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')
        
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@client.command()
async def invite(ctx):
    await ctx.send('https://discordapp.com/oauth2/authorize?client_id=707883141548736512&scope=bot&permissions=109640')
    
@client.command(aliases=['ui', 'whois', 'wi'])
async def userinfo(ctx, member: discord.Member=None):
    member = member or ctx.message.author
 
    
    roles = [role for role in member.roles]

    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
    embed.set_author(name=f"User Info - {member}")
    embed.set_footer(text=f"Requested by {ctx.author}")
    if member.id == 538332632535007244:
        embed.add_field(name="Fun Fact:", value="He is the owner and the only person that developed this bot")
    embed.add_field(name="ID: ", value=member.id)
    embed.add_field(name="Guild name:", value=member.display_name)
    embed.add_field(name="Online Status", value=f"Desktop: {member.desktop_status}\nWeb: {member.web_status}\nMobile:{member.mobile_status}")
    embed.add_field(name="Created at", value=member.created_at.strftime("%a, %d %B %Y, %H:%M:%S"))

    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %d %B %Y, %H:%M:%S"))

    embed.add_field(name=f"Roles ({len(roles)})", value="".join([role.mention for role in roles]))
    embed.add_field(name="Top role:", value=member.top_role.mention)

    embed.add_field(name="Is a bot?", value=member.bot)

    await ctx.send(embed=embed)

client.run(os.environ['token'])