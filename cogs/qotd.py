import discord
from discord.ext import commands, tasks
import datetime
import sqlite3

prefix = ";"
intents = discord.Intents.all()
bot = commands.Bot(description="Discord Bot", command_prefix=prefix, intents=intents)

class Buttons(discord.ui.View):
    def __init__(self, suggestion):
        super().__init__()
        self.suggestion = suggestion

    @discord.ui.button(label="Accept",style=discord.ButtonStyle.green)
    async def accept_qotd(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Suggestion accepted!", ephemeral=True)
        conn = sqlite3.connect("lunaiter_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO qotd VALUES (?, ?)", (self.suggestion, 0))
        conn.commit()
        conn.close()
        
    @discord.ui.button(label="Deny",style=discord.ButtonStyle.red)
    async def deny_qotd(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Suggestion denied.", ephemeral=True)

class Qotd(commands.Cog):
    """This cog is for everything related to Question of the Day"""

    def __init__(self, bot):
        self.bot = bot
        self.send_qotd.start()

    def cog_unload(self):
        self.send_qotd.cancel()

    @bot.tree.command(name="qotd_suggest", description="Suggest a question for the Learners Unite daily question!")
    async def qotd_suggest(self, interaction: discord.Interaction, question: str): 
        try:
            staff_chat = await bot.fetch_channel(1044523629859311666)
            qotd = discord.Embed(title="New QotD suggestion!", description=question, colour=0x875794)
            await staff_chat.send(embed=qotd, view=Buttons(suggestion=question))
            await interaction.response.send_message('Your question is now suggested and will be reviwed by the staff team as soon as possible!', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error occurred while fetching the channel: {e}", ephemeral=True)

    @tasks.loop(time=datetime.time(hour=11))
    async def send_qotd(self):
        qotd_channel = bot.get_channel(1038052696143437874)
        conn = sqlite3.connect("lunaiter_data.db")
        c = conn.cursor()
        c.execute("SELECT Question FROM qotd WHERE TimesUsed = ?", (0,))
        result = c.fetchall()
        conn.close()
        question = result[0]
        embed = discord.Embed(title="The daily question is here!", description=question[0], colour=0x875794)
        message = await qotd_channel.send("<@&1111265430263320686>", embed=embed)
        message.create_thread(name=question, auto_archive_duration=10080)


async def setup(bot):
    await bot.add_cog(Qotd(bot))