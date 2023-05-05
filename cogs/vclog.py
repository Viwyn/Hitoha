import discord
from discord.ext import commands

class Vclog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != 656411689029337098:
            return

        VoiceLogChannel = await self.bot.fetch_channel(844384020465057844)

        if before.channel == after.channel:
            return
        elif before.channel == None:
            await VoiceLogChannel.send(f'{member.name} joined [**{after.channel}**]')
        elif after.channel == None:
            await VoiceLogChannel.send(f'{member.name} left [**{before.channel}**]')
        else:
            await VoiceLogChannel.send(f'{member.name} moved from [**{before.channel}**] to [**{after.channel}**]')

async def setup(bot):
    await bot.add_cog(Vclog(bot))
