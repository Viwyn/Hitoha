import discord
from discord.ext import commands
import openai
import json

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ask(self, ctx, *question):
        response = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a discord bot called Aphrodite that was coded by Riaru that replies to questions asked by users only. Knowledge cutoff: {knowledge_cutoff}"},
            {"role": "user", "content": " ".join(question)}
            ]    
        )
    
        parsed = json.loads(str(response))["choices"][0]["message"]["content"]
        await ctx.reply(parsed)

async def setup(bot):
    await bot.add_cog(Ask(bot))