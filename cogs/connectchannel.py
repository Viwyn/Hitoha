import discord
from discord.ext import commands
import io

class ConnectChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['cc'])
    @commands.is_owner()
    async def connectchannel(self, interaction: discord.Interaction, channelid:int):
        targetChannel = await self.bot.fetch_channel(channelid)
        homeChannel = interaction.channel

        def check(m):
            return (m.channel == targetChannel or m.channel == homeChannel) and m.author != self.bot.user

        await homeChannel.send(f"Started connection with the channel \"{targetChannel.name}\" in the server \"{targetChannel.guild.name}\"")

        while(True):
            response = await self.bot.wait_for('message', timeout=None, check=check)

            if response.channel == homeChannel and response.content == "end":
                await homeChannel.send("Ended connection.")
                break
            elif response.channel == homeChannel:
                attList = []
                if response.attachments:
                    for attachment in response.attachments:
                        attList.append(discord.File(io.BytesIO(await attachment.read()), f'file.{attachment.content_type.split("/")[1]}'))
                    await targetChannel.send(response.content, files=attList)
                else:
                    await targetChannel.send(response.content)

            elif response.channel == targetChannel:
                await homeChannel.send(f"{response.author.display_name}: {response.content}")

async def setup(bot):
    await bot.add_cog(ConnectChannel(bot))