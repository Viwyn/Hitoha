import discord
from discord.ext import commands
import openai
from os import remove
import asyncio
import json

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.convo_data = {}

    @commands.command(name="ask", description="Ask me a question")
    async def ask(self, ctx, *, question = commands.parameter(description="The question that you want to ask me")):
        if question == "":
            question = "Hello"

        async with ctx.channel.typing():
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a discord bot called Hitoha that was coded by Riaru that replies to questions asked by users only."},
                {"role": "user", "content": " ".join(question)}
                ]    
            )

            parsed = response["choices"][0]["message"]["content"]
            length = len(parsed)

            if length > 2000:
                print(f"Error, response for {ctx.author.display_name} went over the max limit ({length}). \nSending a txt file instead")
                with open(f"{ctx.author.id}.txt", "a",encoding='utf-8') as file:
                    file.write(parsed)

                with open(f"{ctx.author.id}.txt", "rb") as file:
                    await ctx.send(content=f"Sorry,the response went over the max character limit. \nSending a txt file instead", file=discord.File(file, filename="response.txt"))

                remove(f"{ctx.author.id}.txt")

            else:
                await ctx.reply(parsed)

    @commands.command(name="convo", description="Start a conversation with me")
    async def convo(self, ctx):
        author = ctx.author.id

        if author in self.convo_data:
            del self.convo_data[author]
            await ctx.send("Starting new conversation.")

        channel = ctx.channel.id

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
                async with ctx.channel.typing():
                    response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=  self.convo_data[author]["history"]
                    )

                parsed = json.loads(str(response))["choices"][0]["message"]["content"]
                length = len(parsed)

                if length > 2000:
                    print(f"Error, response for {ctx.author.display_name} went over the max limit ({length}). \nSending a txt file instead")
                    with open(f"{ctx.author.id}.txt", "a",encoding='utf-8') as file:
                        file.write(parsed)

                    with open(f"{ctx.author.id}.txt", "rb") as file:
                        await ctx.send(content=f"Sorry,the response went over the max character limit. \nSending a txt file instead", file=discord.File(file, filename="response.txt"))
                        self.convo_data[author]["history"].append({"role": "assistant", "content": parsed})

                    remove(f"{ctx.author.id}.txt")
                
                else:
                    await ctx.send(parsed)
                    self.convo_data[author]["history"].append({"role": "assistant", "content": parsed})

                response = await self.bot.wait_for('message', timeout=30.0, check=check)

                if response.content == "!!end":
                    await ctx.send("Ending conversation")
                    del self.convo_data[author]
                    break

                self.convo_data[author]["history"].append({"role": "user", "content": response.content})


            except asyncio.TimeoutError:
                await ctx.send("*Conversation ended due to inactivity*")
                del self.convo_data[author]
                break


    @commands.command(name="end", hidden=True)
    async def end(self, ctx):
        pass

    @commands.command(hidden=True)
    async def createthread(self, ctx):
        thread = await ctx.message.create_thread(name=ctx.author.name, reason="Conversation with Hitoha")
        await thread.add_user(ctx.author)

        def check(m):
            return m.content == "end"

        response = await self.bot.wait_for('message', timeout=30.0, check=check)

        if response.content == "end":
            await thread.delete()   

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))