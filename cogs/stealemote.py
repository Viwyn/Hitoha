import discord
from discord.ext import commands

class StealEmote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Takes the given emoji and adds it to the current server.", brief="Adds the emoji to the server.")
    async def stealemote(self, interaction: discord.Interaction, emote: discord.PartialEmoji, name = None):
        emojiData = await emote.read()
    
        if name == None:
            name = emote.id
    
        newEmoji = await interaction.guild.create_custom_emoji(name=name, image=emojiData)
        await interaction.reply(f"Stolen the emote and named it \"{newEmoji.name}\"")

async def setup(bot):
    await bot.add_cog(StealEmote(bot))