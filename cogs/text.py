import discord
from uwuify import uwu
import json
import asyncio
import aiohttp
import time 
from better_profanity import profanity
import string
import humanize
import unicodedata
import os
import gtts
import difflib
import urllib
import random
import numpy as np

from  discord.ext import commands
from  discord.ext.commands import BucketType


def tts(lang: str, text: str):
    speech = gtts.gTTS(text=text, lang=lang, slow=False)
    speech.save("tts.mp3")
    return


def accuracy(s, t):
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 2
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    return int(Ratio*100)



class Text(commands.Cog):
    """Commands that take a input as text and send a output as text
    """
    def __init__(self, bot):
        self.bot = bot
        marks = map(chr, range(768, 879))
        self.marks = list(marks)
        self.words = []
        
    def _zalgo(self, text):
        words = text.split()
        zalgo = ' '.join(''.join(c + ''.join(random.choice(self.marks)
                for _ in range(i // 2 + 1)) * c.isalnum()
                for c in word)
                for i, word in enumerate(words))
        return zalgo


    @commands.command(aliases=["trc"])
    async def typeracer(self, ctx):
        if not self.words:
            await ctx.send("Loading my words, this may take a moment")
            async with self.bot.session.get("https://raw.githubusercontent.com/derekchuank/high-frequency-vocabulary/master/10k.txt") as cs:
                self.words = (await cs.read()).splitlines()
        wordlength = random.randint(30,40)
        words = random.sample(self.words, wordlength)
        words = list(filter(lambda m: not profanity.contains_profanity(m), words))
        original_text = " ".join(words)
        bot_message = await ctx.send(f"```{original_text}```")
        start = bot_message.created_at
        try:
            message = await self.bot.wait_for("message", check=lambda m:m.author==ctx.author and m.channel == ctx.channel, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention} wow, you are slowest typer ever to be alive")
        else:
            end = message.created_at
            time = (end-start).total_seconds()
            if time < 8:
                return await ctx.send("Imagine cheating bruh")
            elif time < 15 and message.content == original_text:
                return await ctx.send("Imagine cheating bruh")
            mistakes = []
            right_words = 0
            given_words = message.content.split()
            for u_word, b_word in zip(given_words, words):
                u_word, b_word = u_word.strip(), b_word.strip()
                if u_word != b_word:
                    mistakes.append(b_word)
                    continue
                right_words += 1
            wpm = time/wordlength
            fixed_wpm = float(str(right_words)+"."+str(random.randint(0,9)+str(random.randint(0,9))+str(random.randint(0,9))))
            acc = accuracy(message.content, original_text)
            if len(mistakes) < 5 and len(mistakes) < 0:
                mistk = ", ".join(mistakes)
            elif len(mistakes) > 5:
                mistk = ", ".join(mistakes) + "..."
            else:
                mistk = "None, wow"
            await ctx.send(f"```ini\n[WPM] {round(wpm, 3)}\n[FIXED WPM] {fixed_wpm}\n[ACCURACY] {acc}\n[MISTAKES] {mistk}\n[WORDS GIVEN] {len(words)}\n[WORDS FROM {ctx.author.display_name.upper()}] {len(given_words)}\n[CHARACTERS GIVEN] {len(original_text)}\n[CHARACTERS FROM {ctx.author.display_name.upper()}] {len(message.content)}```")

    @commands.command()
    async def randomcase(ctx, inp):
        case = [str.upper, str.lower]
        await ctx.send("".join(case[round(random.random())](s) for s in inp))


    @commands.command()
    @commands.cooldown(1, 15, BucketType.default)
    async def mystbin(self, ctx, *, text):
        if text.startswith("```"):
            if text.startswith("```\n"):
                syntax = text
            else:
                syntax = text.split("\n")[0].replace("```", "")
        paste = await ctx.bot.mystbin_client.post(text, syntax=syntax)
        embed = discord.Embed(
                title="Paste Succesfull", 
                description=paste.url
            )
    
    @commands.command()
    @commands.cooldown(1, 15, BucketType.default)
    async def hastebin(self, data):
        data = bytes(data, 'utf-8')
        async with self.bot.session.post('https://hastebin.com/documents', data = data) as r:
            res = await r.json()
            key = res["key"]
            url = "https://hastebin.com/{key}"
        embed = discord.Embed(
                title="Paste Succesfull", 
                description=url)
    
    @commands.command(description="Spoilers a text letter by letter")
    @commands.cooldown(1, 15, BucketType.channel)
    async def spoiler(self, ctx, *, text: str):
        result = ""
        for i in text:
            result += f"||{i}||"
        if len(result) > 2000:
            await ctx.send("Too long")
        else:
            await ctx.send(f"```{result}```")

    @commands.command(description="Reverses a text")
    async def reverse(self, ctx, *, string: str):
        result = ""
        for i in reversed(list(string)):
            result += i
        embed = discord.Embed(
            title="Reverse",
            description=f"**Original**:\n{string}\n**Reversed**:\n{result}",
        )
        await ctx.send(result, embed=embed)

    @commands.command(
        aliases=["bsr"], description="Box shaped spoilers and repeats a text"
    )
    @commands.cooldown(1, 15, BucketType.channel)
    async def boxspoilerrepeat(self, ctx, width: int, height: int, *, text: str):
        content = ""
        for i in range(height):
            content += f"||{text}||" * width + "\n"
        if len(content) > 2000:
            await ctx.send("Too long")
        else:
            await ctx.send(f"```{content}```")

    @commands.command(description="Repeats a text")
    @commands.cooldown(1, 15, BucketType.channel)
    async def repeat(self, ctx, amount: int, *, text: str):
        if not len(text * amount) > 2000:
            message = await ctx.send(f"```{text * amount}```")
            await asyncio.sleep(4)
            await message.delete()
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        else:
            await ctx.send("Text too long")

    @commands.command(description="Morse code :nerd:")
    async def morse(self, ctx, *, text: str):
        MORSE_CODE_DICT = {
            "A": ".-",
            "B": "-...",
            "C": "-.-.",
            "D": "-..",
            "E": ".",
            "F": "..-.",
            "G": "--.",
            "H": "....",
            "I": "..",
            "J": ".---",
            "K": "-.-",
            "L": ".-..",
            "M": "--",
            "N": "-.",
            "O": "---",
            "P": ".--.",
            "Q": "--.-",
            "R": ".-.",
            "S": "...",
            "T": "-",
            "U": "..-",
            "V": "...-",
            "W": ".--",
            "X": "-..-",
            "Y": "-.--",
            "Z": "--..",
            "1": ".----",
            "2": "..---",
            "3": "...--",
            "4": "....-",
            "5": ".....",
            "6": "-....",
            "7": "--...",
            "8": "---..",
            "9": "----.",
            "0": "-----",
            ", ": "--..--",
            ".": ".-.-.-",
            "?": "..--..",
            "/": "-..-.",
            "-": "-....-",
            "(": "-.--.",
            ")": "-.--.-",
        }
        message = text
        cipher = ""
        for letter in message:
            if letter != " ":
                cipher += MORSE_CODE_DICT[letter.upper()] + " "
            else:
                cipher += " "
        await ctx.send(
            embed=discord.Embed(
                title=str(ctx.author), description=cipher, color=0x2F3136
            )
        )

    @commands.command(description="English to morse")
    async def unmorse(self, ctx, *, text: str):
        MORSE_CODE_DICT = {
            "A": ".-",
            "B": "-...",
            "C": "-.-.",
            "D": "-..",
            "E": ".",
            "F": "..-.",
            "G": "--.",
            "H": "....",
            "I": "..",
            "J": ".---",
            "K": "-.-",
            "L": ".-..",
            "M": "--",
            "N": "-.",
            "O": "---",
            "P": ".--.",
            "Q": "--.-",
            "R": ".-.",
            "S": "...",
            "T": "-",
            "U": "..-",
            "V": "...-",
            "W": ".--",
            "X": "-..-",
            "Y": "-.--",
            "Z": "--..",
            "1": ".----",
            "2": "..---",
            "3": "...--",
            "4": "....-",
            "5": ".....",
            "6": "-....",
            "7": "--...",
            "8": "---..",
            "9": "----.",
            "0": "-----",
            ", ": "--..--",
            ".": ".-.-.-",
            "?": "..--..",
            "/": "-..-.",
            "-": "-....-",
            "(": "-.--.",
            ")": "-.--.-",
        }
        message = text
        message += " "
        decipher = ""
        citext = ""
        for letter in message:
            if letter != " ":
                i = 0
                citext += letter.upper()
            else:
                i += 1
                if i == 2:
                    decipher += " "
                else:
                    decipher += list(MORSE_CODE_DICT.keys())[
                        list(MORSE_CODE_DICT.values()).index(citext)
                    ]
                    citext = ""
        await ctx.send(
            embed=discord.Embed(
                title=str(ctx.author), description=decipher, color=0x2F3136
            )
        )

    @commands.command(
        description="See the meaning of a texting abbreviation",
        aliases=["avs", "abs", "whatdoesitmean" "wdim"],
    )
    async def abbreviations(self, ctx, text: commands.clean_content):
        with open("assets/abs.json") as f:
            fj = json.load(f)
        abs_str = [i for i in fj[0]]
        if text.upper() in abs_str:
            result = fj[0][text.upper()]
            embed = discord.Embed(title=text, description=result, color=0x2F3136)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Abbreviation for {text} not found",
                description=f"Did you mean any of these?\n{', '.join(difflib.get_close_matches(text, abs_str, n=5, cutoff=0.2))}",
                color=0x2F3136,
            )
            return await ctx.send(embed=embed)

    @commands.command(description="Converts a text to speech (TTS)", aliases=["tts"])
    @commands.cooldown(1, 5, BucketType.user)
    async def texttospeech(self, ctx, lang: str, *, text: str):
        msg = await ctx.send("Generating <a:typing:597589448607399949>")
        await self.bot.loop.run_in_executor(None, tts, lang, text)
        await msg.delete()
        await ctx.send(
            f"{ctx.author.mention} Here you go:", file=discord.File("tts.mp3")
        )
        os.remove("tts.mp3")

    @commands.command(
        description="Character Info :nerd:",
        aliases=["chrinf", "unicode", "characterinfo"],
    )
    async def charinfo(self, ctx, *, characters: str):
        def to_string(c):
            #  l.append("a")
            digit = f"{ord(c):x}"
            name = unicodedata.name(c, "Name not found.")
            return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"

        msg = "\n".join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send("Output too long to display.")
        await ctx.send(msg)

    @commands.command(aliases=["fancy", "emf", "banner"], description="Emojify a text")
    async def emojify(self, ctx, *, text: str):
        list_ = []
        fixed = {
            "?": ":grey_question:",
            "!": ":grey_exclamation:",
            "#": ":hash:",
            "*": ":asterisk:",
            "∞": ":infinity:",
        }
        for word in text:
            if word.isdigit():
                list_.append(f":{humanize.apnumber(word)}:")
            elif word == " ":
                list_.append("   ")
            elif word in fixed:
                list_.append(fixed[word])
            elif word in list(string.ascii_letters):
                list_.append(f":regional_indicator_{word.lower()}:")
        try:
            m = await ctx.send(" ".join(list_))
            try:
                await self.bot.wait_for("message_delete", check=lambda m: m == ctx.message, timeout=60)
                await m.delete()
            except asyncio.TimeoutError:
                pass
        except discord.HTTPException:
            await ctx.send("Message too long")

    @commands.command(aliases=["uwu"], description="uwuifies a given text")
    async def uwuify(self, ctx, *, text: commands.clean_content):
        await ctx.send(uwu(text))

    @commands.command(pass_context=True, no_pm=True)
    async def ascii(self, ctx, *, text : str = None):
        if text == None:
            await ctx.channel.send('Usage: `{}ascii [font (optional)] [text]`\n(font list at http://artii.herokuapp.com/fonts_list)'.format(ctx.prefix))
            return

        # Get list of fonts
        fonturl = "http://artii.herokuapp.com/fonts_list"
        async with bot.session.get(fonturl) as r:
            response = await r.text()
        fonts = response.split()

        font = None
        # Split text by space - and see if the first word is a font
        parts = text.split()
        if len(parts) > 1:
            # We have enough entries for a font
            if parts[0] in fonts:
                # We got a font!
                font = parts[0]
                text = ' '.join(parts[1:])
    
        url = "http://artii.herokuapp.com/make?{}".format(urllib.parse.urlencode({'text':text}))
        if font:
            url += '&font={}'.format(font)
        async with bot.session.get(url) as r:
            response = await r.text()
        await ctx.channel.send("```Markup\n{}```".format(response))
    @commands.command()
    async def zalgo(self, ctx, *, message):
        """Ỉ s̰hͨo̹u̳lͪd͆ r͈͍e͓̬a͓͜lͨ̈l̘̇y̡͟ h͚͆a̵͢v͐͑eͦ̓ i͋̍̕n̵̰ͤs͖̟̟t͔ͤ̉ǎ͓͐ḻ̪ͨl̦͒̂ḙ͕͉d͏̖̏ ṡ̢ͬö̹͗m̬͔̌e̵̤͕ a̸̫͓͗n̹ͥ̓͋t̴͍͊̍i̝̿̾̕v̪̈̈͜i̷̞̋̄r̦̅́͡u͓̎̀̿s̖̜̉͌..."""
        words = message.split()
        try:
            iterations = len(words)-1
            words = words[:-1]
        except IndexError:
            iterations = 1
            
        if iterations > 100:
            iterations = 100
        if iterations < 1:
            iterations = 1
            
        zalgo = " ".join(words)
        for i in range(iterations):
            if len(zalgo) > 2000:
                break
            zalgo = self._zalgo(zalgo)
        
        zalgo = zalgo[:2000]
        await ctx.send(zalgo)
def setup(bot):
    bot.add_cog(Text(bot))
