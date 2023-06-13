import discord
from discord.ext import commands
import openai
from os import remove

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(Ask(bot))