import discord
from discord.ext import commands
import openai
import json
import asyncio
from os import remove

class Convo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.convo_data = {}

    @commands.command(name="convo", description="Start a conversation with me", case_insensitive=True)
    async def convo(self, interaction: discord.Interaction):
        author = interaction.author.id

        if author in self.convo_data:
            del self.convo_data[author]
            await interaction.send("Starting new conversation.")

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
                async with interaction.channel.typing():
                    response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=  self.convo_data[author]["history"]
                    )

                parsed = json.loads(str(response))["choices"][0]["message"]["content"]
                length = len(parsed)

                if length > 2000:
                    print(f"Error, response for {interaction.author.display_name} went over the max limit ({length}). \nSending a txt file instead")
                    with open(f"{interaction.author.id}.txt", "a",encoding='utf-8') as file:
                        file.write(parsed)

                    with open(f"{interaction.author.id}.txt", "rb") as file:
                        await interaction.send(content=f"Sorry,the response went over the max character limit. \nSending a txt file instead", file=discord.File(file, filename="response.txt"))
                        self.convo_data[author]["history"].append({"role": "assistant", "content": parsed})

                    remove(f"{interaction.author.id}.txt")
                
                else:
                    await interaction.send(parsed)
                    self.convo_data[author]["history"].append({"role": "assistant", "content": parsed})

                response = await self.bot.wait_for('message', timeout=30.0, check=check)

                if response.content == "!!end":
                    await interaction.send("Ending conversation")
                    del self.convo_data[author]
                    break

                self.convo_data[author]["history"].append({"role": "user", "content": response.content})


            except asyncio.TimeoutError:
                await interaction.send("*Conversation ended due to inactivity*")
                del self.convo_data[author]
                break


    @commands.command(name="end", hidden=True, case_insensitive=True)
    async def end(self, interaction: discord.Interaction):
        pass

async def setup(bot):
    await bot.add_cog(Convo(bot))
