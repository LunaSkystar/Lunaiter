import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
from .. import lunaiterconfig

intents = discord.Intents.all()
bot = commands.Bot(description="Discord Bot", command_prefix=lunaiterconfig.prefix, intents=intents)

def row_count(table_name):
    conn = sqlite3.connect("../lunaiter-data.db")
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM {table_name};")
    result = c.fetchone()[0]
    conn.close()
    return result

class Misc(commands.Cog):
    """This cog contains some misc commands"""

    def __init__(self, bot):
        self.bot = bot

#    @bot.hybrid_command(name='help', description="Get a list of commands and what they do")
#    async def help(self, ctx: commands.Context, arg=None):
#        if arg is None:
#            help_message = discord.Embed(title="Help", description="Here's a list of commands", color=0xb58ed3)
#            help_message.add_field(name="General commands", value="- `;help` gives you a list of commands\n- `;topic` gives you a random topic to talk about\n- `;number` gives you a random number between 0 and 1 million")
#            help_message.add_field(name="Mod only", value="- `/topiclist` gives you the complete list of topics you can get with the `;topic` command\n- `/addtopic` adds a topic to the database\n- `/remove_topic` removes specified topic from the database")
#            help_message.add_field(name="Admin only", value="- `/set_user` sets the user id for specified topic in the database\n- `;viewtable` shows the tables in the SQL database")
#            help_message.add_field(name="Owner only", value="- `;sync` syncs the slash commands")
#            help_message.add_field(name="Ringer", value="- `/ring` pings a certain role\n- `/ringshow` shows existing ringer rules")
#            help_message.add_field(name="Mod only (ringer)", value="- `/ringadd` adds a new role to which rings are allowed\n- `/ringnew` adds a new role to allow rings\n- `/ringdelete` deletes a role from the permitted ringers")
#            await ctx.send(embed=help_message)
#        else: 
#            ctx.send("You can't get command specific help from this command yet, please try again with just `;help`")

    @bot.command()
    async def number(self, ctx, arg=1000000):
        await ctx.send(f"This is your random number: {random.randrange(arg)}")

    @bot.command()
    async def topic(self, ctx):
        topic_index = random.randrange(row_count("topics"))
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", (topic_index,))
        result = c.fetchone()
        conn.close()
        await ctx.send(result[0])
    
    @bot.tree.command(name="send", description="[MOD ONLY] Make Lunaiter send a message in a specified channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await interaction.response.send_message(f'Message sent in <#{channel.id}>', ephemeral=True)
        await channel.send(message)

    @bot.tree.command(name="add_topic", description="[MOD ONLY] Add topics to the database")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def addtopic(self, interaction: discord.Interaction, user_id: str, topic: str):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute("INSERT INTO topics VALUES (?, ?)", (user_id, topic))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f'Added topic "{topic}" from user <@{user_id}>')

    @bot.tree.command(name="set_user", description="[ADMIN ONLY] Set user ID for a topic in the database")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_user(self, interaction: discord.Interaction, user_id: str, rowid: int):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute("UPDATE topics SET user_id = ? WHERE rowid = ?", (int(user_id), rowid))
        conn.commit()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", rowid)
        topic = c.fetchall()
        conn.close()
        await interaction.response.send_message(f'Set user {user_id} for topic "{topic}" (rowid {rowid})')

    @bot.tree.command(name="remove_topic", description="[MOD ONLY] Remove topics from the database")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def add_topic(self, interaction: discord.Interaction, rowid: int):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute("SELECT topic FROM topics WHERE rowid = ?", rowid)
        c.execute("DELETE FROM topics WHERE rowid = ?", rowid)
        conn.commit()
        topic = c.fetchall()
        conn.close()
        await interaction.response.send_message(f'Removed topic "{topic}", rowid {rowid}')

    @bot.tree.command(name="view_topic", description="[MOD ONLY] View a topic from its row ID")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_topic(self, interaction: discord.Interaction, rowid: str):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute(f"SELECT topic FROM topics WHERE rowid = {rowid}")
        topic = c.fetchone()
        conn.close()
        await interaction.response.send_message(f"{rowid}. {topic[0]}")

    @bot.command()
    @commands.is_owner()
    async def viewtable(self, ctx, table=None):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = c.fetchall()
        table_names = [name[0] for name in table_names]

        if table is None:
            await ctx.send("The tables are:\n" + "\n".join(table_names))
            return
            
        if table not in table_names:
            await ctx.send(f"There is no table called {table}")
            return
            
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

    @bot.command()
    @commands.is_owner()
    async def clearjoindates(self, ctx):
        conn = sqlite3.connect("../lunaiter-data.db")
        c = conn.cursor()
        # current_time = discord.utils.utcnow()
        c.execute("SELECT user_id FROM join_dates")
        result = c.fetchall()
        guild = self.bot.get_guild(1028328656478679041)
        users = 0
        for user_id in result:
            if guild.get_member(user_id) is None:
                await ctx.send(f"User with ID {user_id} cleared from join dates")
                users += 1
                c.execute("DELETE FROM join_dates WHERE user_id = ?", (user_id))
                conn.commit()
        conn.close()
        if users > 0:
            await ctx.send(f"{users} join dates cleared!")
        else: 
            await ctx.send("No join dates cleared")

async def setup(bot):
    await bot.add_cog(Misc(bot))