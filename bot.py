import asyncio
import discord
import os
from commands import HelpCommand
from discord.app_commands import CommandTree
from discord.ext import commands
from cogs.searches.Searches import Searches
from cogs.music.Music import Music
from dotenv import load_dotenv

load_dotenv()

DISCORD_KEY = os.getenv('DISCORD_KEY')
if DISCORD_KEY is None:
    raise Exception('You need a Discord API key to run this bot!')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.help_command = HelpCommand.MyHelpCommand()

asyncio.run(bot.load_extension('cogs.searches.Searches'))
asyncio.run(bot.load_extension('cogs.music.Music'))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.hybrid_command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.hybrid_command()
async def glory(ctx):
    await ctx.send('Glory to Novorra!')

bot.run(DISCORD_KEY)
