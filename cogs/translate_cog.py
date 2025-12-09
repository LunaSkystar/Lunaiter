import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

class Translate(commands.Cog):
    """This cog translates everything that's not english and sends a translation to message logs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        user_message = str(message.content)
        lang_channel = self.bot.get_channel(1028600519884812288) #languages-literature
        log_channel = self.bot.get_channel(1096853274176536636)
        username = str(message.author).split("#")[0]
        if message.author == self.bot.user:
            return
        try: lang = detect(user_message)
        except: return
        if lang != "en" and message.channel == lang_channel:
            translation = GoogleTranslator(source=lang, target="en").translate(user_message)
            if translation.lower() == user_message.lower():
                return
            msg = discord.Embed(
                title=f"Message translated from #{message.channel.name}", 
                url=message.jump_url, 
                description=f"**Before:** {user_message}\n**After:** {translation}", 
                color=0xb58ed3, 
                timestamp=message.created_at)
            msg.set_footer(text=f"ID: {message.author.id}")
            msg.set_author(name=username, icon_url=message.author.avatar)
            await log_channel.send(embed=msg)
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        staff_role = discord.utils.get(reaction.message.guild.roles, id=1071480426427859045)
        if reaction == "🌐" and staff_role in user.roles:
            user_message = str(reaction.message.content)
            lang_channel = self.bot.get_channel(1028600519884812288) #languages-literature
            log_channel = self.bot.get_channel(1096853274176536636)
            try: lang = detect(user_message)
            except: return
            if lang != "en":
                if reaction.message.channel == lang_channel or reaction.message.channel in lang_channel.threads:
                    translation = GoogleTranslator(source=lang, target="en").translate(user_message)
                    if translation.lower() == user_message.lower():
                        return
                    msg = discord.Embed(
                        title=f"Message translated from #{reaction.message.channel.name}", 
                        url=reaction.message.jump_url, 
                        description=f"**Before:** {user_message}\n**After:** {translation}", 
                        color=0xb58ed3, 
                        timestamp=reaction.message.created_at
                    )
                    msg.set_footer(text=f"ID: {reaction.message.author.id}")
                    msg.set_author(name=reaction.message.author.username, icon_url=reaction.message.author.avatar)
                    await log_channel.send(embed=msg)
                await reaction.remove(user)

        
async def setup(bot):
    await bot.add_cog(Translate(bot))