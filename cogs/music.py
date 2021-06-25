import discord
from discord.ext import commands
from youtubesearchpython.__future__ import VideosSearch

from utils.musicbot import MusicBot
from utils.paginator import Paginator
from utils.queue import Queue
from utils.song import Song
from utils.ytdlsource import YTDLSource


def song_after(e):
    if e:
        print(f"Player error: {e}")
    else:
        on_song_end()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.message.reply("Joined", channel.name)

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays music from a url or searches youtube"""
        async with ctx.typing():
            if not url.startswith(("http://", "https://")):
                search = VideosSearch(url, limit=1)
                results = (await search.next())["result"]
                url = results[0]["link"]

            player, playlist = await YTDLSource.from_url(
                url, asyncio_loop=self.bot.loop
            )
            # ctx.voice_client.play(player, after=song_after)
            ctx.voice_client.play(player)
            if playlist:
                self.queues[ctx.voice_client.channel.id] == playlist

        await ctx.message.reply(f"Now playing: {player.title}")

    @commands.command(name="pause", help="Pauses the song")
    async def pause(self, ctx):
        volume = int(ctx.voice_client.source.volume * 100)
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.message.reply("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx):
        volume = int(ctx.voice_client.source.volume * 100)
        voice_client = ctx.voice_client
        if voice_client.is_paused():
            voice_client.resume()

        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play_song command"
            )

    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx):
        volume = int(ctx.voice_client.source.volume * 100)
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()

        else:
            await ctx.message.reply("The bot is not playing anything at the moment.")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.message.reply("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100

        await ctx.message.reply(f"Changed volume to {volume}%")

    @commands.command()
    async def disconnect(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

        await ctx.message.reply("Stopped and Disconnected")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.message.reply("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def setup(bot):
    """Adds the cog to the bot"""

    bot.add_cog(Music(bot))
