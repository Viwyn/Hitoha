import discord
from discord.ext import commands

class Cards():
    def __init__(self, suit, char):
        self.suit = suit
        self.char = char

        if type(char) == int:
            value = char
        elif char in ['j', 'q', 'k']

        self.value = 0

    

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="blackjack", aliases=['blackjack'], help="Start a game of blackjack")
    async def blackjack(self, interaction: discord.Interaction):
        pass

async def setup(bot):
    await bot.add_cog(Games(bot))