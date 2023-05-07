import discord
import random
from .ImageSearcher import ImageSearcher
from .SearchEngines import SearchEngine
from discord.ext import commands

class Searches(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._searcher = ImageSearcher()
        self._max_results = 4

    @commands.group(invoke_without_command=True, nsfw=True)
    async def search(self, ctx, *args):
        await self.one(ctx, *args)

    @search.command()
    async def one(self, ctx, *args):
        await self._search(ctx, ' '.join(args), 1, True)

    @search.command()
    async def many(self, ctx, *args):
        await self._search(ctx, ' '.join(args), self._max_results, True)

    @search.command()
    async def porn(self, ctx, *args):
        if not ctx.channel.is_nsfw():
            await ctx.send('That content is prohibited here! Please use a NSFW channel.')
        else:
            await self._search(ctx, ' '.join(args), 1, False)

    @search.command()
    async def google(self, ctx, *args):
        params = {'safe': 'off' if ctx.channel.is_nsfw() else 'active'}
        await self._new_search(ctx, SearchEngine.GOOGLE, ' '.join(args), 4, params)

    @search.command()
    async def bing(self, ctx, *args):
        params = {'safesearch': 'off' if ctx.channel.is_nsfw() else 'moderate'}
        await self._new_search(ctx, SearchEngine.BING, ' '.join(args), 4, params)

    async def _new_search(self, ctx, engine: SearchEngine, query: str, count: int, params: dict[str, str]):
        links = self._searcher.new_search(engine, query, count, params=params)
        embeds = [self._create_embed(link) for link in links]

        if embeds:
            await ctx.send(embeds=embeds)
        else:
            await ctx.send('No images found!')

    async def _search(self, ctx, query: str, count: int, safe: bool):
        links = self._searcher.search(query, count, safe)
        embeds = [self._create_embed(link) for link in links]

        if embeds:
            await ctx.send(embeds=embeds)
        else:
            await ctx.send('No images found!')

    def _create_embed(self, link: str) -> discord.Embed:
        embed = discord.Embed(url='https://images.google.com/')
        embed.set_image(url=link)
        return embed

async def setup(bot):
    await bot.add_cog(Searches(bot))
