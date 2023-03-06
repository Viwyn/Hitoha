import discord
from discord.ext import commands

class End(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="end", hidden=True)
    async def end(self, interaction: discord.Interaction):
        pass

async def setup(bot):
    await bot.add_cog(End(bot))