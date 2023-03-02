import discord
from discord.ext import commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount:int):
        await interaction.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(Purge(bot))