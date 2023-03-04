import discord
from discord.ext import commands

class Calculate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calculate", aliases=['cal'], description="Calculate an equation")
    async def calculate(self, interaction: discord.Interaction, eq):
        return await interaction.send(eval(eq))
    
async def setup(bot):
    await bot.add_cog(Calculate(bot))