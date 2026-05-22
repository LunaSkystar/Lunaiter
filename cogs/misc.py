import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3

db_path = "lunaiter_data.db"

def row_count(table_name):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM {table_name};")
    result = c.fetchone()[0]
    conn.close()
    return result

class Misc(commands.Cog):
    """This cog contains some misc commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def number(self, ctx, arg=1000000):
        await ctx.send(f"This is your random number: {random.randrange(arg)}")
    
    @commands.hybrid_command(name="send", description="[MOD ONLY] Make Lunaiter send a message in a specified channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, ctx: commands.Context, channel: discord.TextChannel, message: str):
        await ctx.send(f'Message sent in <#{channel.id}>', ephemeral=True)
        await channel.send(message)

    @commands.command()
    @commands.is_owner()
    async def viewtable(self, ctx, table=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = c.fetchall()
        table_names = [name[0] for name in table_names]

        if table is None:
            if len(table_names) == 0:
                await ctx.send("There are no tables.")
            else:
                await ctx.send("The tables are:\n" + "\n".join(table_names))
        elif table not in table_names:
            await ctx.send(f"There is no table called {table}")
        else:
            c.execute(f"SELECT rowid, * FROM {table}")
            result = c.fetchall()
            if len(result) == 0:
                await ctx.send(f"The table {table} is empty.")
            else:
                response = f"Contents of table {table}:\n"
                for row in result:
                    response += f"{row[0]}. {row[2]} `user: {row[1]}`\n"
                await ctx.send(response)

        conn.close()

async def setup(bot):
    await bot.add_cog(Misc(bot))