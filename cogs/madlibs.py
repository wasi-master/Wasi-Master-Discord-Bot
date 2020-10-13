import asyncio
import discord
import re
import os
import random
import string
from   discord.ext import commands


class MadLibs(commands.Cog):
    """The classic madlibs
    """
    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot):
        self.prefix = "ml"
        self.bot = bot
        # Setup/compile our regex
        self.regex = re.compile(r"\[\[[^\[\]]+\]\]")



    @commands.command()
    async def madlibs(self, ctx):
        """Let's play MadLibs!"""

        channel = ctx.channel
        author  = ctx.author
        server  = ctx.guild

        # Check if our folder exists
        if not os.path.isdir("./assets/madlibs"):
            msg = 'I\'m not configured for MadLibs yet...'
            await channel.send(msg)
            return

        # Folder exists - let's see if it has any files
        choices = [] # Empty array
        for file in os.listdir("./assets/madlibs/"):
            if file.endswith(".txt"):
                choices.append(file)
        
        if len(choices) == 0:
            # No madlibs...
            msg = 'I\'m not configured for MadLibs yet...'
            await channel.send(msg)
            return

        

        # Get a random madlib from those available
        randnum = random.randint(0, (len(choices)-1))
        randLib = choices[randnum]

        # Let's load our text and get to work
        with open("./assets/madlibs/{}".format(randLib), 'r') as myfile:
            data = myfile.read()

        # Set up an empty arry
        words = []

        # Match
        matches = re.finditer(self.regex, data)

        # Iterate matches
        for match in matches:
            words.append(match.group(0))

        # Create empty substitution array
        subs = []

        # Iterate words and ask for input
        i = 0
        while i < len(words):
            # Ask for the next word
            vowels = "aeiou"
            word = words[i][2:-2]
            if word[:1].lower() in vowels:
                msg = "I need an **{}** (word *{}/{}*).  `{}{} [your word]`".format(words[i][2:-2], str(i+1), str(len(words)), ctx.prefix, self.prefix)
            else:
                msg = "I need a **{}** (word *{}/{}*).  `{}{} [your word]`".format(words[i][2:-2], str(i+1), str(len(words)), ctx.prefix, self.prefix)
            await channel.send(msg)

            # Setup the check
            def check(msg):    
                return msg.author == author and msg.channel == channel

            # Wait for a response
            try:
                talk = await self.bot.wait_for('message', check=check, timeout=60)
            except Exception:
                talk = None

            if not talk:
                # We timed out - leave the loop
                msg = "{}, I'm done waiting... we'll play another time.".format(author.mention)
                await channel.send(msg)
                return

            # Check if the message is to leave
            if talk.content.lower().startswith("stop madlibs"):
                if talk.author is author:
                    msg = "Alright, *{}*.  We'll play another time.".format(author.name)
                    await channel.send(msg)
                    return

            # We got a relevant message
            word = talk.content
            # Let's remove the $ml prefix (with or without space)
            if word.startswith('{}{} '.format(ctx.prefix.lower(), self.prefix.lower())):
                word = word[len(ctx.prefix)+len(self.prefix)+1:]
            if word.startswith('{}{}'.format(ctx.prefix.lower(), self.prefix.lower())):
                word = word[len(ctx.prefix)+len(self.prefix):]
            
            # Check capitalization
            if words[i][:3].isupper():
                # Capitalized
                word = string.capwords(word)

            # Add to our list
            subs.append(word)
            # Increment our index
            i += 1

        # Let's replace
        for asub in subs:
            # Only replace the first occurence
            data = re.sub(self.regex, "**{}**".format(asub), data, 1)


        # Message the output
        await channel.send(data)

    @madlibs.error
    async def madlibs_error(self, ctx, error):
        # Reset playing status and display error
        msg = 'MadLibs Errored: {}'.format(ctx)
        await error.send(msg)

def setup(bot):
    bot.add_cog(MadLibs(bot))
