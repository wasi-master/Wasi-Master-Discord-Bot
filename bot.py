import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import json
import random
import randomcolor
import requests
import time
import os
import wikipedia as wikimodule

def get_prefix(client, message):
	try:
		with open("prefixes.json", "r") as f:
			prefixes = json.load(f)
		return prefixes[str(message.guild.id)]
	except:
		return ","
	
client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')
memberlist = []
serverlist = []

@client.event
async def on_ready():
    print("Bot is online")
    for guild in client.guilds:
    	serverlist.append(guild)
    	for member in guild.members:
    		memberlist.append(member)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(memberlist)} members in {len(serverlist)} servers"))

@client.event
async def on_guild_join(guild):
	print(f"Bot added to {guild.name}")

	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
	prefixes[str(guild.id)] = ','
	
	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		
@client.event
async def on_guild_remove(guild):
	print(f"Kicked From {guild.name}")

	with open("prefixes.json", "r") as f:
		prefixes = json.load(f)
	prefixes.pop(str(guild.id))
	
	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("You don\'t have the permission")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.send('I can\'t do that')
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Something is missing')
	else:
		await ctx.send(f"error occured:\n {error}")
@client.command()
async def ip(ctx):
	await ctx.send(requests.get('https://api.ipify.org').text))

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
	embed.set_author(name=name, icon_url=album_cover)
	embed.add_field(name='Explict', value=explict)
	embed.add_field(name='Song Name', value=name, inline=True)
	embed.add_field(name='Artist', value=artist_name, inline=True)
	embed.add_field(name='Album', value=album_name, inline=True)
	embed.set_image(url=artist_picture)
	await ctx.send(embed=embed)

@client.command(aliases=['mc'])
async def messagecount(ctx, channel: discord.TextChannel=None):
    channel = channel or ctx.message.channel
    count = 0
    async with ctx.typing():
    	async for i in channel.history(limit=None):
        	count += 1
    await ctx.send(f"There were {count} messages in {channel.mention}")

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

    message=await client.say(embed=page1)

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

    await client.clear_reactions(message)
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
 
@client.command(aliases=["setprefix"])
@has_permissions(manage_roles=True)
async def prefix(ctx, prefix):
	with open("prefixes.json", "r") as f:
		  prefixes = json.load(f)
	prefixes[str(ctx.guild.id)] = prefix
	await ctx.send(f"prefix set to `{prefix}`")
	with open("prefixes.json", "w") as f:
		json.dump(prefixes, f,  indent=4)
		
@client.command(aliases=['speak', 'echo', 's'])
async def say(ctx, *args): 
    mesg = ' '.join(args) 
    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.channel.purge(limit=1)
    return await ctx.send(mesg)


@client.command()
@has_permissions(manage_roles=True)
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
async def howgay(ctx, member: discord.Member):
     embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
     embed.set_author(name='Gay Telling Machine')
     embed.set_footer(text=f"Requested by {ctx.author}")
     embed.add_field(name="How Gay?", value=f"{member.name} is {random.randint(0, 100)}% gay")
     await ctx.send(embed=embed)
     
@client.command(aliases=['search'])
async def google(ctx, *, args):
    result = "http://www.google.com/search?q=" + args.replace(" ", "+")
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
    embed = discord.Embed(timestamp=ctx.message.created_at)
    embed.set_author(name='Ping')
    embed.set_footer(text=f"Asked by {ctx.author}")
    embed.add_field(name="Ping", value=f'Pong! I got your message after {round(client.latency * 1000)}ms')
    await ctx.send(embed=embed)

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
	embed = discord.Embed()
	embed.set_author(name=f"{ctx.author}\'s Quiz")
	embed.set_footer(text="From Open Trivia DB")
	async with ctx.typing():
		response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
		data = json.loads(response.text)
		
		question = data.get("results")[0].get("question").replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é")
		embed.add_field(name=question, value="‌")
		
		difficulty =  data.get('results')[0].get('difficulty')
		embed.add_field(name="difficulty", value=difficulty)
		
		category = data.get('results')[0].get('category').replace("Entertainment: ", "")
		embed.add_field(name="Category", value=category)
		
		randomint = random.randint(0, 4)
		if randomint == 1:
			embed.add_field(name="A", value=data.get("results")[0].get("correct_answer").replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[0].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[1].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 2:
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("correct_answer").replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[1].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 3:
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[1].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("correct_answer").replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("incorrect_answers")[2].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
		if randomint == 4:
			embed.add_field(name="A", value=data.get("results")[0].get("incorrect_answers")[0].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="B", value=data.get("results")[0].get("incorrect_answers")[1].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="C", value=data.get("results")[0].get("incorrect_answers")[2].replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
			embed.add_field(name="D", value=data.get("results")[0].get("correct_answer").replace("&%39;", "\'").replace("&quot;", "\"").replace("&amp;", " &").replace("&eacute;", "é"))
	await ctx.send(embed=embed)
    		
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
@has_permissions(manage_roles=True)
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

@client.command(aliases=['av', 'profilepicture', 'pp', 'profile'])
async def avatar(ctx, *,  avamember : discord.Member=None,):
	avamember = avamember or ctx.message.author
	userAvatarUrl = avamember.avatar_url
	await ctx.send(userAvatarUrl)


@client.command(aliases=['halp'])
async def help(ctx):	
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
	embed.add_field(name=f"{prefix}synonyms `<word>`", value='Returns the synonyms of a word')
	embed.add_field(name=f"{prefix}urbandictionary `<word>`", value='Retyrns the definitions of a word found in urban dictionary')
	embed.add_field(name=f"{prefix}define `<word>`", value='Returns the definitions of a word found in merriam webster')
	embed.add_field(name=f"{prefix}translate `<language>` `<text>`", value='Returns the translation of a text found in Yandex')
	embed.add_field(name=f"{prefix}quiz", value='Used to get a quiz (not fully made)')
	embed.add_field(name=f"{prefix}link", value='Used to get a link to the message')
	embed.add_field(name=f"{prefix}dm `<text>`", value='Used to send the person writing this command a dm which can be used to remember something')
	embed.add_field(name=f"{prefix}getusers `<@role>`", value="used to get users that have a specefic oile")
	await ctx.send(embed=embed)
    
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
    	await ctx.send(f"I\'m in {servers} servers and there are {members} members total d there are {members} members total and {average}  on average in each server")

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

@client.command(aliases=['remove', 'delete', 'erase', 'clear', 'c'])
@has_permissions(manage_messages=True)
async def clear_messages(ctx, amount : int):
    amount += 1
    deleted = await ctx.channel.purge(limit=amount)
    message = await ctx.send(f"deleted `{len(deleted)}`' messages")
    time.sleep(4)
    await ctx.channel.purge(message=message)
    
@clear_messages.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the amount of messag esto delete')

@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
     await member.kick(reason=reason)
     await ctx.send(f'Kicked {member.mention}')

@client.command(aliases=['setnick', 'setnickname', 'nickname','changenickname', 'chnick'])
@has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention} ')
    
@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')
        
@client.command()
@has_permissions(ban_members=True)
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
async def userinfo(ctx, member: discord.Member):

    roles = [role for role in member.roles]
    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
    embed.set_author(name=f"User Info - {member}")
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID: ", value=member.id)
    embed.add_field(name="Guild name:", value=member.display_name)

    embed.add_field(name="Created at", value=member.created_at.strftime("%a, %d %B %Y, %H:%M:%S"))

    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %d %B %Y, %H:%M:%S"))

    embed.add_field(name=f"Roles ({len(roles)})", value="".join([role.mention for role in roles]))
    embed.add_field(name="Top role:", value=member.top_role.mention)

    embed.add_field(name="Is a bot?", value=member.bot)

    await ctx.send(embed=embed)

client.run(os.environ['token'])