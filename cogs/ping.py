import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        lag = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! \nPing: {lag}ms")
        

async def setup(bot):
    await bot.add_cog(Ping(bot))
