import asyncio
import discord
import requests
import os
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
from youtube_dl import YoutubeDL

class Music(commands.Cog):

    FFMPEG_EXEC = os.getenv('FFMPEG_EXEC')

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def connect(self, ctx: commands.Context):
        channel = ctx.author.voice.channel
        if not channel:
            return await ctx.send('You must be in a voice channel to play content!')

        player: wavelink.Player = ctx.voice_client
        if player:
            return await player.move_to(channel)

        return await channel.connect(cls=wavelink.Player())

    @commands.command()
    async def join(self, ctx: commands.Context):
        return await self.connect(ctx)

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player:
            return await ctx.send("I'm not already in a voice channel!")

        await player.disconnect()
        return await player.cleanup()

    @commands.command()
    async def leave(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        return await player.disconnect()

    @commands.command()
    async def kick(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        return await player.disconnect()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player.current:
            return await ctx.send("There's nothing to pause!")
        
        if player.is_paused():
            await ctx.send(f'Now resuming {player.current.title}.')
            return await player.resume()

        await ctx.send(f'Now pausing {player.current.title}.')
        return await player.pause()

    @commands.command()
    async def resume(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player.current:
            return await ctx.send("There's nothing to resume!")
        
        if player.is_paused():
            await ctx.send(f'Now resuming {player.current.title}.')
            return await player.resume()

        return await ctx.send('Content is already playing!')

    @commands.command()
    async def skip(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if player.queue.is_empty and not player.is_playing():
            return await ctx.send("There's nothing to skip!")

        await ctx.send(f'Skipping {player.current.title}.')
        return await player.stop()

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
    async def play(self, ctx: commands.Context, *, query: str):
        decoded = spotify.decode_url(query)
        if decoded:
            match decoded['type']:
                case spotify.SpotifySearchType.unusable:
                    return await ctx.send('That Spotify URL is invalid!')
                case _:
                    try:
                        result = await spotify.SpotifyTrack.search(query=decoded['id'], type=decoded['type'])
                        tracks = result if isinstance(result, list) else [result]

                    except spotify.SpotifyRequestError as error:
                        print(error)
                        return await ctx.send('Oops, critical error occurred. Harrass <@406869765127143439> to fix it!')

        else:
            try:
                tracks = [await wavelink.YouTubeTrack.search(query, return_first=True)]

            except wavelink.NoTracksError as error:
                return await ctx.send('Search did not return any results.')

        print(tracks)

        if not tracks:
            return await ctx.send('Search did not return any results.')

        await asyncio.wait_for(self.connect(ctx), timeout=5)
        player: wavelink.Player = ctx.voice_client
        if player.is_playing():
            for track in tracks:
                await ctx.send(f'{track.title} is now queued.')
                await player.queue.put_wait(track)

            return

        
        if not decoded:
            await self.display_youtube_link(ctx, tracks[0])

        await ctx.send(f'Now playing {tracks[0].title}.')
        await player.play(tracks[0], populate=True)

        if len(tracks) > 1:
            player.queue.extend(tracks[1:])

        player.autoplay = True

    @commands.command()
    async def queue(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        for i, track in enumerate(player.queue):
            await ctx.send(f'{i}. {track.title}')


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        print('Wavelink track ended')
        player = payload.player
        if player.queue.is_empty:
            track = await player.auto_queue.get_wait()
            return await player.play(track)
 
        track = await player.queue.get_wait()
        return await player.play(track)

    async def display_youtube_link(self, ctx: commands.Context, track: wavelink.GenericTrack):
        embed = discord.Embed(
            title=track.title,
            url=track.uri,
        )
        #embed.description = track.length
        video_id = track.uri.split('watch?v=')[1]
        thumbnail = f'https://img.youtube.com/vi/{video_id}/0.jpg'
        embed.set_thumbnail(url=thumbnail)
        embed.set_author(name=track.author)
        return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
