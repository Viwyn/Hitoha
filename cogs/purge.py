import discord
from discord.ext import commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge", description="Deletes messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount:int = 10):
        await interaction.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(Purge(bot))