import discord
from discord.ext import commands
import json
import re
from urllib.parse import quote


from discord.ext.commands import BucketType

class Data(commands.Cog):
    """Commands to get some data
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lc"])
    async def lyrics(self, ctx, song_name: str):
        song_name = quote(song_name)
        async with self.bot.session.get(f"https://some-random-api.ml/lyrics?title={song_name}") as cs:
            fj = await cs.json()
        embed = discord.Embed(
                title=fj["title"],
                description=fj["lyrics"],
                url = list(fj["links"].values())[0]
                )
        embed.set_thumbnail(url=list(fj["thumbnail"].values())[0])
        embed.set_author(name=fj["author"])
        await ctx.send(embed=embed)
    
    @commands.command(aliases=["pd"])
    async def pokedex(self, ctx, pokemon:str):
        pokemon = quote(pokemon)
        async with self.bot.session.get(f"https://some-random-api.ml/pokedex?pokemon={pokemon}") as cs:
            fj = await cs.json()
        stats = fj["stats"]
        embed = discord.Embed(
            title=fj["name"].title(),
            description=fj["description"]
            )
        embed.add_field(name="Type", value=", ".join(fj["type"]))
        embed.add_field(name="Abilities", value=", ".join(fj["abilities"]))
        embed.add_field(name="Stats", value=f"Height: {fj['height']}\nWeight: {fj['weight']}\nGender Ratio:\n    Male: {fj['gender']['male']}\n    Female:{fj['gender']['female']}")
        embed.add_field(name="More Stats", value=f"HP: {stats['hp']}\nAttack: {fj['attack']}\nDefense: {stats['defense']}\nSpecial Attack: {stats['sp_atk']}\nSpecial Defense: {stats['sp_def']}\nSpeed: {stats['speed']}\n**Total**: {stats['total']}")
        embed.add_field(name="Evoloution", value="\n".join(fj["family"]["evolutionLine"]).replace(fj["family"]["evolutionLine"][fj["evolutionStage"]-1], f'**{fj["family"]["evolutionLine"][fj["evolutionStage"]-1]}**'))
        embed.set_thumbnail(url=fj["sprites"]["animated"])
        await ctx.send(embed=embed)

    @commands.command(description="Find details about a music")
    async def music(self, ctx, *, music_name: str):
        url = "https://deezerdevs-deezer.p.rapidapi.com/search"
        querystring = {"q": music_name}

        headers = {
            "x-rapidapi-host": "deezerdevs-deezer.p.rapidapi.com",
            "x-rapidapi-key": "1cae29cc50msh4a78ebc8d0ba862p17824ejsn020a7c093c4d",
        }
        async with ctx.typing():
            async with self.bot.session.get(
                url, headers=headers, params=querystring
            ) as response:
                formatted_response = json.loads(await response.text())

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

        embed = discord.Embed(color=0x2F3136)
        embed.set_author(name=name, icon_url=artist_picture)
        embed.add_field(name="Explict", value=explict)
        embed.add_field(name="Song Name", value=name, inline=True)
        embed.add_field(name="Artist", value=artist_name, inline=True)
        embed.add_field(name="Album", value=album_name, inline=True)
        embed.set_image(url=album_cover)
        await ctx.send(embed=embed)

    @commands.command(description="Coronavirus Stats")
    async def covid(self, ctx, *, area: str = "Global"):
        num = 0
        formatted_json = None

        async with ctx.typing():
            async with self.bot.session.get("https://api.covid19api.com/summary") as r:
                fj = json.loads(await r.text())

        if not area.lower() == "global":
            for i in fj["Countries"]:
                num += 1
                if i["Slug"].lower() == area.lower():
                    formatted_json = fj["Countries"][num - 1]
                    break
                else:
                    continue
        else:
            formatted_json = fj["Global"]
        if not formatted_json is None:
            embed = discord.Embed(
                title=f"Covid 19 Stats ({area.title()})", color=0x2F3136
            )
            embed.add_field(
                name="New Cases", value=f"{formatted_json['NewConfirmed']:,}"
            )
            embed.add_field(
                name="Total Cases", value=f"{formatted_json['TotalConfirmed']:,}"
            )
            embed.add_field(name="New Deaths", value=f"{formatted_json['NewDeaths']:,}")
            embed.add_field(
                name="Total Deaths", value=f"{formatted_json['TotalDeaths']:,}"
            )
            embed.add_field(
                name="New Recovered", value=f"{formatted_json['NewRecovered']:,}"
            )
            embed.add_field(
                name="Total Recovered", value=f"{formatted_json['TotalRecovered']:,}"
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Country not found")

    @commands.command(
        aliases=["randomfact", "rf", " f"], description="Get a random fact"
    )
    async def fact(
        self,
        ctx,
    ):

        async with self.bot.session.get(
            "https://uselessfacts.jsph.pl/random.json?language=en"
        ) as resp:
            fj = json.loads(await resp.text())
        embed = discord.Embed(
            title="Random Fact", description=fj["text"], color=0x2F3136
        )
        await ctx.send(embed=embed)

    @commands.command(description="See details about a movie")
    async def movie(self, ctx, *, query):

        url = f"http://www.omdbapi.com/?i=tt3896198&apikey=4e62e2fc&t={query}"
        async with self.bot.session.get(url) as response:
            fj = json.loads(await response.text())
        if fj["Response"] == "True":
            embed = discord.Embed(
                title=fj["Title"], description=fj["Plot"], color=0x2F3136
            )
            if re.search("(http(s?):)(.)*\.(?:jpg|gif|png)", fj["Poster"]):
                embed.set_image(url=fj["Poster"])
            embed.add_field(name="Released On", value=fj["Released"])
            embed.add_field(name="Rated", value=fj["Rated"])
            mins = []
            embed.add_field(name="Duration", value=f"{fj['Runtime']}")
            embed.add_field(name="Genre", value=fj["Genre"])
            embed.add_field(
                name="Credits",
                value=f"**Director**: {fj['Director']}\n**Writer**: {fj['Writer']}\n**Casts**: {fj['Actors']}",
            )
            embed.add_field(name="Language(s)", value=fj["Language"])
            embed.add_field(
                name="IMDB",
                value=f"Rating: {fj['imdbRating']}\nVotes: {fj['imdbVotes']}",
            )
            embed.add_field(
                name="Production", value=f"[{fj['Production']}]({fj['Website']})"
            )
            await ctx.send(embed=embed)

        else:
            await ctx.send("Movie Not Found")

    @commands.command(name="gender", description="Get a gender by providing a name")
    @commands.cooldown(1, 30, BucketType.user)
    async def gender(self, ctx, *, name: str):

        url = f"https://gender-api.com/get?name={name.replace(' ', '%20')}&key=tKYMESVFrAEhpCpuwz"
        async with self.bot.session.get(url) as r:
            fj = json.loads(await r.text())
        if fj["gender"] == "male":
            gender = "Male"
            color = 2929919
        elif fj["gender"] == "female":
            gender = "Female"
            color = 16723124
        else:
            gender = "Unknown"
            color = 6579300
        positive = str(fj["accuracy"]) + "%"
        negative = str(100 - fj["accuracy"]) + "%"
        if not gender == "Unknown":
            text = f"The name {fj['name_sanitized']} has a **{positive}** chance of being a  **{gender}** and a {negative} chance of not being a {gender}"
        else:
            text = f"The name {fj['name_sanitized']} is not in our database"
        embed = discord.Embed(title=fj["name_sanitized"], description=text, color=color)
        await ctx.send(embed=embed)

    @commands.command()
    async def weather(self, ctx, *, location: str):

        apiKey = "cbe36b072a1ef0a4aa566782989eb847"
        location = location.replace(" ", "")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&APPID={apiKey}"
        async with self.bot.session.get(url) as r:
            fj = json.loads(await r.text())
        if not fj["cod"] == "404":
            embed = discord.Embed(
                title=fj["name"],
                description=f'**{fj["weather"][0]["main"]}**\n{fj["weather"][0]["description"]}',
                color=0x2F3136,
            )
            embed.add_field(
                name="Temperature",
                value=f'Main: {round(fj["main"]["temp"] - 273.15, 2)}°C\nFeels Like: {round(fj["main"]["feels_like"] - 273.15, 2)}°C',
            )
            embed.add_field(
                name="Wind",
                value=f'Speed: {fj["wind"]["speed"]}Kmh\nDirection: {fj["wind"]["deg"]}°',
            )
            embed.add_field(name="Cloudyness", value=str(fj["clouds"]["all"]) + "%")
            # embed.add_field(name="Sun", value=f'Sunrise: {datetime.datetime.fromtimestamp(fj["sys"]["sunrise"]).strftime("%I:%M:%S")}\nSunset: {datetime.datetime.fromtimestamp(fj["sys"]["sunset"]).strftime("%I:%M:%S")}')
            await ctx.send(embed=embed)
        elif fj["cod"] == "404":
            await ctx.send("Location not found")
        else:
            await ctx.send("Error")


def setup(bot):
    bot.add_cog(Data(bot))
