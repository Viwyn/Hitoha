import discord
from discord.ext import commands
from os import remove
import asyncio
import json
from discord import app_commands
from typing import Optional
from os import getenv
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=getenv("GEMINI"))

model = genai.GenerativeModel('gemini-pro')

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.convo_data = {}

    @commands.command(name="ask", description="Ask me a question")
    async def ask(self, ctx, *, question = commands.parameter(description="The question that you want to ask me")):
        if question == "":
            question = "Hello"

        async  with ctx.channel.typing():
            response = await self.askgpt(question)
            
            response = model.generate_content(question, stream=True, safety_settings=[], generation_config=genai.types.GenerationConfig(candidate_count=1))
        
            for chunk in response:
                await ctx.send(chunk.text)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))