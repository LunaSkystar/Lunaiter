import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from .. import lunaiter_config

intents = discord.Intents.all()
bot = commands.Bot(description="Discord Bot", command_prefix=lunaiter_config.prefix, intents=intents)
rules = dict()

class Ringer(commands.Cog):
    """Ringer allows users to ping certain roles that are added by mods"""

    def __init__(self, bot):
        self.bot = bot

    @bot.tree.command(name="ring", description="Ping a certain role")
    # @app_commands.describe(msg='the message to echo')
    async def ring(self, interaction: discord.Interaction, role: discord.Member, msg: discord.Member):
        all_roles = [r.name for r in interaction.guild.roles]
        from_roles = interaction.user.roles
        if role in all_roles:
            for rol in from_roles:
                if rol.name in rules:  # store (name, id)
                    rtup = [r for r in rules[rol.name] if r[0] == role]
                    if len(rtup) > 0:
                        await interaction.response.send_message(
                            f"<@&{rtup[0][1]}> {interaction.user.name} said {msg}!")
                        break
        else: await interaction.response.send_message(f"{role} is not a valid role", ephemeral=True)

    @bot.tree.command(name="ring_new", description="[MOD ONLY] Add a new role to allow rings")
    @app_commands.checks.has_permissions(manage_roles=True)
    # change to a UI/modal to select multiple roles at once
    async def ringnew(interaction: discord.Interaction, ringer: discord.Member, ringee: discord.Member):
        all_roles = [r.name for r in interaction.guild.roles]
        rtupl = [(r.name, r.id) for r in interaction.guild.roles if r.name == ringee]
        if ringer in all_roles and len(rtupl) > 0:
            rules[ringer] = rtupl[0:1]
            conn = sqlite3.connect("lunaiter_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO rules(ringer, ringee) VALUES (?, ?);", (ringer, ringee))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"{interaction.user.name} created a rule for {ringer}")
        else: await interaction.response.send_message(f"invalid role", ephemeral=True)

    @bot.tree.command(name="ring_add", description="[MOD ONLY] Add a new role to which rings are allowed")
    @app_commands.checks.has_permissions(manage_roles=True)
    # @app_commands.describe(msg='the message to echo')
    async def ringadd(self, interaction: discord.Interaction, ringer: discord.Member, ringee: discord.Member):
        if ringer in rules:
            
            rtupl = [(r.name, r.id) for r in interaction.guild.roles if r.name == ringee]
            rules[ringer] = rules[ringer] + rtupl[0:1]
            await interaction.response.send_message(
                f"added rule for {ringer}", delete_after=5
            )
        else:
            await interaction.response.send_message(
                f"rule for {ringer} does not exist", ephemeral=True
            )

    @bot.tree.command(name="ring_delete", description="[MOD ONLY] Delete a role from the permitted ringers")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def ringdelete(self, interaction: discord.Interaction, ringer: discord.Member):
        if ringer in rules:
            del rules[ringer]
        await interaction.response.send_message(f"rule for {ringer} was removed")

    @bot.tree.command(name="ring_show", description="Show existing rules")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ringshow(self, interaction: discord.Interaction):
        response = "\n".join([f"{r}: {rules[r]}" for r in rules])
        if len(response) > 0:
            await interaction.response.send_message(response, ephemeral=True)
        else:
            await interaction.response.send_message("There are no configured rules")

async def setup(bot):
    await bot.add_cog(Ringer(bot))