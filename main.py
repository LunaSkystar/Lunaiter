import datetime
import sqlite3
import discord
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv('token.env')

LUNAITER_TOKEN = os.getenv('LUNAITER_TOKEN')
prefix = ";"
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents, description="A bot by lunaskystar for Learners Unite")
cogs = ["cogs.misc", "cogs.joindates", "cogs.ringer", "cogs.qotd", "cogs.translate_cog"]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    try:
        for cog in os.listdir('./cogs'):
            if cog.endswith('.py'):
                await bot.load_extension(f'cogs.{cog[:-3]}')
        print("Cog loaded:", cog)
    except Exception as e:
        print(f"Failed to load cog {cog}: {e}")

    if not check_unverified_members.is_running():
        check_unverified_members.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound) and ctx.message.content != ";-;":
        await ctx.send("Wrong command. Please try ;help for more information")
#   bot-area, bots, lunaiter
    channels = [1028354604225802261, 1028598060378492979, 1228453461218295869]
    if ctx.channel.id in channels:
        await ctx.send(str(error))

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    print("Command tree synced!")
    await ctx.send("Command tree synced!")

@bot.command()
@commands.is_owner()
async def reload_cogs(ctx):
    for ext in cogs:
        await bot.reload_extension(ext)
        print(f"{ext} has loaded.")

@bot.event
async def on_message(message):
#    username = str(message.author).split("#")[0]
#    user_message = str(message.content)
#    channel = str(message.channel.name)
#    if user_message.startswith(prefix):
#        print(f"{username}: {user_message} ({channel})")
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    channel_id = message.channel.id
    if channel_id == 1028609884666732554:
        await message.add_reaction("<:neko_wave:1095663898872528967>")
    
#@bot.event
#async def on_member_update(before, after):
#    member_role = discord.utils.get(after.guild.roles, name="Member")
#    if member_role not in before.roles and member_role in after.roles:
#        roles_to_add = [
#        1086738958542708888, 
#        1086738199482736722, 
#        1086740494563954759,
#        1086745963441434684,
#        1086746237597929521,
#        1086747241550729367]
#        for role_id in roles_to_add:
#            role = after.guild.get_role(role_id)
#            await asyncio.sleep(1) # adds a delay of 1 second
#             await after.add_roles(role)
    
@tasks.loop(hours=24)
async def check_unverified_members():
    guild = bot.get_guild(1028328656478679041)
    current_time = discord.utils.utcnow()
    conn = sqlite3.connect("lunaiter_data.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM join_dates WHERE join_date >= ?", (current_time - datetime.timedelta(days=4),))
    result = c.fetchall()
    # c.execute("DELETE FROM join_dates WHERE join_date >= ?", ((current_time - datetime.timedelta(days=4)),))
    conn.close()
    member_role = discord.utils.get(guild.roles, id=1028329664533512313)
    bot_role = discord.utils.get(guild.roles, id=1028384019320164455)
    inbox_channel = bot.get_channel(1322210269866233887)
    for row in result:
        member = guild.get_member(row[0])
        if member is not None:
            if member_role not in member.roles and bot_role not in member.roles:
                # await member.kick(reason="Didn't verify within 4 days")
                await asyncio.sleep(1)
                await inbox_channel.send(f"Member <@{row[0]}> unverified for too long")

bot.run(LUNAITER_TOKEN)