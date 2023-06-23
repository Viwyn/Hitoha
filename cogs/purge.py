import discord
from discord.ext import commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge", description="Deletes messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int = 10):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} message(s) has been deleted.")

async def setup(bot):
    await bot.add_cog(Purge(bot))