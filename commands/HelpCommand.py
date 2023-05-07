from discord.ext import commands

class MyHelpCommand(commands.HelpCommand):

    # $help
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        await channel.send('Help text')
