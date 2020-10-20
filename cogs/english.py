import json, asyncio
import discord
from discord.ext import commands


class English(commands.Cog):
    """Commands for the english language
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["synonym"], description="Sends synomyms for a word")
    async def synonyms(self, ctx, *, word):
        api_key = "dict.1.1.20200701T101603Z.fe245cbae2db542c.ecb6e35d1120ee008541b7c1f962a6d964df61dd"

        async with ctx.typing():
            embed = discord.Embed(timestamp=ctx.message.created_at)
            embed.set_author(name=f"Synonyms for {word}")
            async with self.bot.session.get(
                f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={api_key}&lang=en-en&text={word.lower()}"
            ) as response:
                data = await response.json()

            num = 0
            try:
                synonyms = data.get("def")[0].get("tr")
                for i in synonyms:
                    num += 1
                    embed.add_field(
                        name=f"Synonym {num}", value=i.get("text"), inline=True
                    )
            except:
                embed.add_field(name="No synonyms found", value="‌Command Aborted")
        await ctx.send(embed=embed)

    @commands.command(
        aliases=[
            "urbandict",
            "urbandefine",
            "urbandefinition",
            "ud",
            "urbandictionary",
        ],
        description="Searches The Urban Dictionary (nsfw only)",
    )
    async def urban(self, ctx, *, word):
        if not ctx.channel.is_nsfw():
            await ctx.send(
                "You can use this only in nsfw channels because the results may include nsfw content"
            )
        else:
            params = {"term": word}
            headers = {
                "x-rapidapi-host": "mashape-community-urban-dictionary.p.rapidapi.com",
                "x-rapidapi-key": "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d",
            }
            num = 0
            embed = discord.Embed(timestamp=ctx.message.created_at)
            embed.set_footer(text="From Urban Dictionary")

            async with ctx.typing():
                async with self.bot.session.get(
                    "https://mashape-community-urban-dictionary.p.rapidapi.com/define",
                    params=params,
                    headers=headers,
                ) as response:
                    parsed_json = json.loads(await response.text())

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

    @commands.command(
        aliases=["def", "df"], description="Returns the defination of a word"
    )
    async def define(self, ctx, word: str):
        num = 0

        async with self.bot.session.get(
            f"https://owlbot.info/api/v1/dictionary/{word}?format=json"
        ) as r:
            text = await r.text()
        fj = json.loads(text)
        if len(fj) > 1:
            results = fj
            term = results[num]
            try:
                embed = discord.Embed(
                    title=word, description=term["defenition"], color=0x2F3136
                )
            except KeyError:
                await ctx.send("No definition found")
                return
            embed.add_field(name="Type", value=term["type"])
            if not term["example"] is None:
                embed.add_field(
                    name="Example",
                    value=term["example"].replace("<b>", "**").replace("</b>", "**"),
                )
            embed.set_footer(text=f"Definition {num + 1}/{len(results)}")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\u25c0\ufe0f")
            await message.add_reaction("\u23f9\ufe0f")
            await message.add_reaction("\u25b6\ufe0f")
            while True:

                def check(reaction, user):
                    return (
                        user.id == ctx.author.id
                        and reaction.message.channel.id == ctx.channel.id
                    )

                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", check=check, timeout=120
                    )
                except asyncio.TimeoutError:
                    #  e.set_footer(icon_url=str(ctx.author.avatar_url), text="Timed out")
                    #  await message.edit(embed=embed)
                    try:
                        return await message.clear_reactions()
                    except:
                        await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                        await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                        #  break
                        return
                else:
                    if reaction.emoji == "\u25c0\ufe0f":
                        try:
                            message.remove_reaction("\u25c0\ufe0f", ctx.author)
                        except discord.Forbidden:
                            pass
                        num -= 1
                        try:
                            term = results[num]
                        except IndexError:
                            pass
                        embed = discord.Embed(
                            title=word, description=term["defenition"], color=0x2F3136
                        )
                        embed.add_field(name="Type", value=term["type"])
                        if not term["example"] is None:
                            embed.add_field(
                                name="Example",
                                value=term["example"]
                                .replace("<b>", "**")
                                .replace("</b>", "**"),
                            )
                        embed.set_footer(text=f"Definition {num + 1}/{len(results)}")
                        await message.edit(embed=embed)
                    elif reaction.emoji == "\u25b6\ufe0f":
                        try:
                            await message.remove_reaction("\u25b6\ufe0f", ctx.author)
                        except discord.Forbidden:
                            pass
                        num += 1
                        try:
                            term = results[num]
                        except IndexError:
                            pass
                        embed = discord.Embed(
                            title=word, description=term["defenition"], color=0x2F3136
                        )
                        embed.add_field(name="Type", value=term["type"])
                        if not term["example"] is None:
                            embed.add_field(
                                name="Example",
                                value=term["example"]
                                .replace("<b>", "**")
                                .replace("</b>", "**"),
                            )
                        embed.set_footer(text=f"Definition {num + 1}/{len(results)}")
                        await message.edit(embed=embed)
                    elif reaction.emoji == "\u23f9\ufe0f":
                        embed = discord.Embed(
                            title=word, description=term["defenition"], color=0x2F3136
                        )
                        embed.add_field(name="Type", value=term["type"])
                        embed.add_field(
                            name="Example",
                            value=term["example"]
                            .replace("<b>", "**")
                            .replace("</b>", "**"),
                        )
                        await message.edit(embed=embed)
                        try:
                            return await message.clear_reactions()
                        except:
                            await message.remove_reaction("\u25b6\ufe0f", ctx.guild.me)
                            await message.remove_reaction("\u23f9\ufe0f", ctx.guild.me)
                            await message.remove_reaction("\u25c0\ufe0f", ctx.guild.me)
                            break
                            return
                    else:
                        pass
            #  await ctx.send(embed=embeds[0])
        elif len(fj) == 1:
            term = fj[0]
            try:
                embed = discord.Embed(
                    title=word, description=term["defenition"], color=0x2F3136
                )
            except:
                await ctx.send("Word not found")
                return
            embed.add_field(name="Type", value=term["type"])
            if not (term["example"] is None or len(term["example"]) == 0):
                embed.add_field(
                    name="Example",
                    value=term["example"].replace("<b>", "**").replace("</b>", "**"),
                )
            #  embeds.append(embed)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Word not found")

    @commands.command(aliases=["tr"], description="Translate a text")
    async def translate(self, ctx, lang: str, *, text: str):

        async with self.bot.session.get(
            "https://pkgstore.datahub.io/core/language-codes/language-codes_json/data/97607046542b532c395cf83df5185246/language-codes_json.json"
        ) as r:
            languages = json.loads(await r.text())
        for i in languages:
            if i["English"].lower() == lang.lower():
                lang = i["alpha2"]
                break
            else:
                lang = lang
                continue
        if lang == "zh":
            language = "zh-CN"
        result = await ctx.bot.translate_api.translate(text, dest=lang)
        source = ""
        for i in languages:
            if i["alpha2"] == result.src:
                src = i["English"]
                break
            else:
                src = result.src
                continue
        for i in languages:
            if i["alpha2"] == result.dest:
                dest = i["English"]
                break
            else:
                dest = result.dest
                continue
        embed = discord.Embed(
            title=f"Translation", description=result.text, color=0x2F3136
        )
        if not result.text == result.pronunciation:
            embed.add_field(name="Pronunciation", value=result.pronunciation)
        embed.set_footer(
            text=f"Translated from {src.split(';')[0]} to {dest.split(';')[0]}"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(English(bot))
