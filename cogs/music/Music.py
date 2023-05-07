import asyncio
import discord
import discord.utils
import functools
import requests
import os
from discord.ext import commands
from youtube_dl import YoutubeDL

class Music(commands.Cog):

    FFMPEG_EXEC = os.getenv('FFMPEG_EXEC')

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue = []

    @commands.command()
    async def connect(self, ctx):
        return self.join(ctx)

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send('You must be in a voice channel to play content!')
            return

        self.voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.move_to(channel)

        else:
            self.voice_client = await channel.connect()

    @commands.command()
    async def disconnect(self, ctx):
        if not ctx.voice_client:
            await ctx.send("I'm not already in a voice channel!")
            return

        await ctx.voice_client.disconnect()
        await ctx.voice_client.cleanup()
        self.voice_client = None

    @commands.command()
    async def leave(self, ctx):
        await self.disconnect(ctx)

    @commands.command()
    async def kick(self, ctx):
        await self.disconnect(ctx)

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

        else:
            ctx.voice_client.resume()

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.send('Content is already playing!')

        else:
            ctx.voice_client.resume()

    #Get videos from links or from youtube search
    def search(self, query):
        with YoutubeDL({'format': 'bestaudio/best', 'noplaylist':'True'}) as ydl:
            try:
                requests.get(query)

            except:
                info = ydl.extract_info(f"{query}", download=False)['entries'][0]

            else:
                info = ydl.extract_info(query, download=False)

        return (info, info['formats'][0]['url'])

    @commands.command()
    async def play(self, ctx, *, query):
        video, source = self.search(query)
        self.queue.append((video, source))
        await ctx.send(f'{video["title"]} is now queued.')
        await self.join(ctx)
        if not ctx.voice_client.is_playing():
            self.bot.dispatch('track_end', ctx)

    @commands.command()
    async def skip(self, ctx):
        await ctx.voice_client.stop()

    async def check_play(self, ctx: commands.Context):
        client = ctx.voice_client
        while client and client.is_playing():
            await asyncio.sleep(1)
        
        self.bot.dispatch("track_end", ctx)

    @commands.Cog.listener()
    async def on_track_end(self, ctx: commands.Context):
        if not self.queue:
            await ctx.send('Queue is now empty.')
            return

        video, source = self.queue.pop(0)
        await ctx.send(f'Now playing {video["title"]}.')
        
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ctx.voice_client.play(discord.FFmpegPCMAudio(source, executable=self.FFMPEG_EXEC, **FFMPEG_OPTS), after=functools.partial(lambda x: self.bot.loop.create_task(self.check_play(ctx))))

async def setup(bot):
    await bot.add_cog(Music(bot))
