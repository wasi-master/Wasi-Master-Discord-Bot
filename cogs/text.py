import discord
from uwuify import uwu
import json
import asyncio
import string
import humanize
import unicodedata
import os
import gtts
import difflib
import urllib
import random

from  discord.ext import commands
from  discord.ext.commands import BucketType


def tts(lang: str, text: str):
    speech = gtts.gTTS(text=text, lang=lang, slow=False)
    speech.save("tts.mp3")
    return

def _zalgo(text):
    words = text.split()
    zalgo = ' '.join(''.join(c + ''.join(random.choice(self.marks)
            for _ in range(i // 2 + 1)) * c.isalnum()
            for c in word)
            for i, word in enumerate(words))
    return zalgo

class Text(commands.Cog):
    """Commands that take a inpu as text and send a output as text
    """
    def __init__(self, bot):
        self.bot = bot
        marks = map(chr, range(768, 879))
        self.marks = list(marks)

        
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
            await ctx.send(" ".join(list_))
        except:
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
            zalgo = _zalgo(zalgo)
        
        zalgo = zalgo[:2000]
        await ctx.send(zalgo)
def setup(bot):
    bot.add_cog(Text(bot))
