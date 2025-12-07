import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from .. import lunaiter_config

intents = discord.Intents.all()
bot = commands.Bot(description="Discord Bot", command_prefix=lunaiter_config.prefix, intents=intents)

class Joindates(commands.Cog):
    """This cog handles join dates of new users so they can be kicked automatically after 4 days of being unverified."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # Adding user to database on join
    async def on_member_join(self, member):
        conn = sqlite3.connect("../lunaiter_data.db")
        c = conn.cursor()
        join_date = member.joined_at.strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO join_dates VALUES (?, ?)", (member.id, join_date))
        conn.commit()
        conn.close()

    @commands.Cog.listener() # Remove from database when verified
    async def on_member_update(self, before, after):
        member_role = discord.utils.get(after.guild.roles, id=1028329664533512313)
        if member_role not in before.roles and member_role in after.roles:
            conn = sqlite3.connect("../lunaiter_data.db")
            c = conn.cursor()
            c.execute("DELETE FROM join_dates WHERE user_id = ?", (before.id,))
            conn.commit()
            conn.close()
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_role = discord.utils.get(member.guild.roles, id=1028329664533512313)
        if member_role not in member.roles:
            conn = sqlite3.connect("../lunaiter_data.db")
            c = conn.cursor()
            c.execute("DELETE FROM join_dates WHERE user_id = ?", (member.id,))
            conn.commit()
            conn.close()

    @bot.tree.command(name="clearjoindates", description="[ADMIN ONLY] Cleans up the join dates table")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clearjoindates(self, interaction: discord.Interaction):
        amount = 0
        guild = self.bot.get_guild(1028328656478679041)
        member_role = discord.utils.get(member.guild.roles, id=1028329664533512313)
        conn = sqlite3.connect("../lunaiter_data.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM join_dates")
        result = c.fetchall()
        print(result)
        for i in result:
            if guild.get_member(i[0]) is None:
                c.execute("DELETE FROM join_dates WHERE user_id = ?", i)
                amount += 1
            else:
                member = guild.get_member(i[0])
                if member_role in member.roles:
                    c.execute("DELETE FROM join_dates WHERE user_id = ?", i)
                    amount += 1
        conn.commit()
        conn.close()
        await interaction.response.send_message(amount, "join dates cleared!")

async def setup(bot):
    await bot.add_cog(Joindates(bot))