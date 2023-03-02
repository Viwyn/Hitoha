import discord
from discord.ext import commands

class MsgChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def msgchannel(self, interaction: discord.Interaction, channelid:int, *words):
        if (len(words) == 0):
            return await interaction.send("Cannot send empty message.")

        channel = await self.bot.fetch_channel(channelid)
        await channel.send(" ".join(words))

async def setup(bot):
    await bot.add_cog(MsgChannel(bot))