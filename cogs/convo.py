import discord
from discord.ext import commands
import openai
import json
import asyncio

class Convo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.convo_data = {}

    @commands.command(name="convo", description="Start a conversation with me")
    async def convo(self, interaction: discord.Interaction):
        author = interaction.author.id

        if author in self.convo_data:
            return await interaction.send("You are already having a conversation with me")

        channel = interaction.channel.id

        convo_info = {"channel": channel, 
                    "history": [
                        {"role": "system", "content": "You are a discord bot called Hitoha that was coded by Riaru to have conversations with users"},
                        {"role": "user", "content": "Hello"}
                    ]}
        
        def check(m):
            return m.author.id == author and m.channel.id == channel

        self.convo_data[author] = convo_info

        
        while(True):
            try:
                response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=  self.convo_data[author]["history"]
                )

                parsed = json.loads(str(response))["choices"][0]["message"]["content"]
                await interaction.send(parsed)
                self.convo_data[author]["history"].append({"role": "assistant", "content": parsed})

                response = await self.bot.wait_for('message', timeout=30.0, check=check)
                self.convo_data[author]["history"].append({"role": "user", "content": response.content})


            except asyncio.TimeoutError:
                await interaction.send("*Conversation ended due to inactivity*")
                del self.convo_data[author]
                break

async def setup(bot):
    await bot.add_cog(Convo(bot))
