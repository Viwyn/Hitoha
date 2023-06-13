import discord
from discord.ext import commands

class Calculate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calculate", aliases=['cal'], description="Calculate an equation")
    async def calculate(self, ctx, *eq):
        equation = " ".join(eq)

        equation = equation.replace("^", "**")

        return await ctx.send(eval(equation))
    
async def setup(bot):
    await bot.add_cog(Calculate(bot))