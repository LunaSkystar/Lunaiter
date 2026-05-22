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

class Topics(commands.Cog):
    """This cog contains topic commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def topic(self, ctx):
        topic_index = random.randrange(row_count("topics"))
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", (topic_index,))
        result = c.fetchone()
        conn.close()
        await ctx.send(result[0])

    @commands.hybrid_command(name="topic_add", description="[MOD ONLY] Add topics to the database")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def addtopic(self, ctx: commands.Context, user_id: str, topic: str):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO topics VALUES (?, ?)", (user_id, topic))
        conn.commit()
        conn.close()
        await ctx.send(f'Added topic "{topic}" from user <@{user_id}>')

    @commands.hybrid_command(name="topic_author", description="[ADMIN ONLY] Set user ID for a topic in the database")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_user(self, ctx: commands.Context, user_id: str, rowid: int):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE topics SET user_id = ? WHERE rowid = ?", (int(user_id), rowid))
        conn.commit()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", rowid)
        topic = c.fetchall()
        conn.close()
        await ctx.send(f'Set user {user_id} for topic "{topic}" (rowid {rowid})')

    @commands.hybrid_command(name="topic_remove", description="[MOD ONLY] Remove topics from the database")
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

    @commands.hybrid_command(name="topic_view", description="[MOD ONLY] View a topic from its row ID")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_topic(self, interaction: discord.Interaction, rowid: str):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(f"SELECT topic FROM topics WHERE rowid = {rowid}")
        topic = c.fetchone()
        conn.close()
        await interaction.response.send_message(f"{rowid}. {topic[0]}")

async def setup(bot):
    await bot.add_cog(Topics(bot))