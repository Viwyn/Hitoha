import discord
from discord.ext import commands
import random

class Choose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, interaction: discord.Interaction, *choices):
        await interaction.reply(random.choice(choices))

async def setup(bot):
    await bot.add_cog(Choose(bot))