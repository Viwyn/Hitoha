import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
from os import getenv
import openai
import asyncio

load_dotenv()
intents = discord.Intents.all()
intents.message_content = True
openai.api_key=getenv("OPENAI")

bot = commands.Bot(command_prefix=getenv('PREFIX'), intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print("Ready!")

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.reply(error)
    print(f"{ctx.author.display_name}: {error}")

@bot.event
async def on_error(e):
    print(e)

async def main():
    async with bot:
        await load()
        await bot.start(getenv('BOT')) #replace HITOHA with bot token

if __name__ == '__main__':
    asyncio.run(main())