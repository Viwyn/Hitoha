import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="Pings me")
    async def ping(self, interaction: discord.Interaction):
        lag = round(self.bot.latency * 1000)
        await interaction.send(f"Pong! \nLatency: {lag}ms")
        

async def setup(bot):
    await bot.add_cog(Ping(bot))
