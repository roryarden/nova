import asyncio
import discord
import os
import platform
import wavelink
from commands import HelpCommand
from discord.app_commands import CommandTree
from discord.ext import commands
from cogs.searches.Searches import Searches
from cogs.music.Music import Music
from dotenv import load_dotenv
from wavelink.ext import spotify

# @bot.event

# @bot.hybrid_command()
# async def ping(ctx):
#     await ctx.send('Pong!')

# @bot.hybrid_command()
# async def glory(ctx):
#     await ctx.send('Glory to Novorra!')

class Bot(commands.Bot):

    SPOTIFY_ID = os.getenv('SPOTIFY_ID')
    SPOTIFY_SECRET = os.getenv('SPOTIFY_SECRET')

    def __init__(self) -> None:
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(intents=intents, command_prefix='/')

    async def on_ready(self):
        print(f'Logged in as {self.user}.')
        await self.tree.sync()

    async def setup_hook(self) -> None:
        node = wavelink.Node(uri='http://localhost:2333', password='lolwat')
        spotify_client = spotify.SpotifyClient(client_id=self.SPOTIFY_ID, client_secret=self.SPOTIFY_SECRET)
        await wavelink.NodePool.connect(client=self, nodes=[node], spotify=spotify_client)


def main():
    print(platform.system())
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if not load_dotenv():
        raise Exception('ERROR: Failed to load python-dotenv!')
    
    # Load environment variables
    DISCORD_KEY = os.getenv('DISCORD_KEY')
    if DISCORD_KEY is None:
        raise Exception('You need a Discord API key to run this bot!')
    
    bot = Bot()
    
    bot.help_command = HelpCommand.MyHelpCommand()
    asyncio.run(bot.load_extension('cogs.searches.Searches'))
    asyncio.run(bot.load_extension('cogs.music.Music'))

    # Run the bot using our secret Discord API key!
    bot.run(DISCORD_KEY)


if __name__ == '__main__':
    main()
