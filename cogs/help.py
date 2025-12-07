from discord.ext import commands
import discord
from .. import lunaiter_config

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=lunaiter_config.prefix, intents=intents)

class MyHelp(commands.HelpCommand):
    # ;help
    async def send_bot_help(self, mapping):
        await self.context.send("This is help")
    
    # ;help <command>
    async def send_command_help(self, command):
        await self.context.send("This is help command")

    # ;help <group>
    async def send_group_help(self, group):
        await self.context.send("This is help group")
    
   # ;help <cog>
    async def send_cog_help(self, cog):
        await self.context.send("This is help cog")

bot.help_command = MyHelp()

class Help(commands.Cog):
    """This cog is for managing the help command"""

    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Help(bot))
