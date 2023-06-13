import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="Pings me")
    async def ping(self, ctx):
        lag = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! \nLatency: {lag}ms")

    @commands.command(name="pong", description="Pings me")
    async def pong(self, ctx):
        lag = round(self.bot.latency * 1000)
        await ctx.send(f"Ping! \nLatency: {lag}ms")
        
async def setup(bot):
    await bot.add_cog(Ping(bot))
