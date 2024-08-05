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
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
            response = model.generate_content(question, stream=True, safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }, 
            generation_config=genai.types.GenerationConfig(candidate_count=1))
        
            for chunk in response:
                await ctx.send(chunk.text)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))