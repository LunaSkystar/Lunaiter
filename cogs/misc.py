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

    @commands.command()
    async def topic(self, ctx):
        topic_index = random.randrange(row_count("topics"))
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", (topic_index,))
        result = c.fetchone()
        conn.close()
        await ctx.send(result[0])
    
    @commands.hybrid_command(name="send", description="[MOD ONLY] Make Lunaiter send a message in a specified channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await interaction.response.send_message(f'Message sent in <#{channel.id}>', ephemeral=True)
        await channel.send(message)

    @commands.hybrid_command(name="add_topic", description="[MOD ONLY] Add topics to the database")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def addtopic(self, interaction: discord.Interaction, user_id: str, topic: str):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO topics VALUES (?, ?)", (user_id, topic))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f'Added topic "{topic}" from user <@{user_id}>')

    @commands.hybrid_command(name="set_user", description="[ADMIN ONLY] Set user ID for a topic in the database")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_user(self, interaction: discord.Interaction, user_id: str, rowid: int):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE topics SET user_id = ? WHERE rowid = ?", (int(user_id), rowid))
        conn.commit()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", rowid)
        topic = c.fetchall()
        conn.close()
        await interaction.response.send_message(f'Set user {user_id} for topic "{topic}" (rowid {rowid})')

    @commands.hybrid_command(name="remove_topic", description="[MOD ONLY] Remove topics from the database")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def add_topic(self, interaction: discord.Interaction, rowid: int):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", rowid)
        c.execute("DELETE FROM topics WHERE rowid = ?", rowid)
        conn.commit()
        topic = c.fetchall()
        conn.close()
        await interaction.response.send_message(f'Removed topic "{topic}", rowid {rowid}')

    @commands.hybrid_command(name="view_topic", description="[MOD ONLY] View a topic from its row ID")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_topic(self, interaction: discord.Interaction, rowid: str):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(f"SELECT topic FROM topics WHERE rowid = {rowid}")
        topic = c.fetchone()
        conn.close()
        await interaction.response.send_message(f"{rowid}. {topic[0]}")

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