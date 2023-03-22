import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import mktime
from voicevox import Client
from typing import Optional
from os import getenv, remove
import asyncio
import socket

scheduler = AsyncIOScheduler()

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="choose", description="Allow me to make a choice for you")
    async def choose(self, interaction: discord.Interaction, *choices):
        await interaction.reply(random.choice(choices))

    @commands.command(name="8ball", description="Roll the magic 8ball")
    async def _8ball(self, interaction:discord.Interaction, *args):
        outputs = [
            "It is certain",
            "Without a doubt",
            "You may rely on it",
            "Yes definitely",
            "It is decidedly so",
            "As I see it, yes",
            "Most likely",
            "Yes",
            "Outlook good",
            "Signs point to yes",
            "Reply hazy try again",
            "Better not tell you now",
            "Ask again later",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "Outlook not so good",
            "Very doubtful",
            "My sources say no",
            "My reply is no",
            "Not now",
            "Try again tomorrow",
            "Maybe next week",
            "It's impossible",
            "You're out of luck",
            "Sorry, I can't help you",
            "It's not looking good",
            "I'm afraid not",
            "No chance",
            "No way",
            "Absolutely",
            "Definitely not",
            "Absolutely not",
            "Don't even think about it",
            "Nope",
            "Nah",
            "I doubt it",
            "Not likely",
            "Unlikely",
            "It all depends",
            "I'm not convinced",
            "Sources say no",
            "I don't think so",
            "The outlook is not good",
            "Signs point to no",
            "Chances aren't good",
            "Probably not",
            "Very unlikely",
            "It is what it is",
            "Ask me later",
            "I need more information"
            ]
        
        await interaction.reply(random.choice(outputs))
    
    @commands.command(name="remind", aliases=['remindme', 'reminder'], description="Send a reminder to you at a spefied time")
    async def remind(self, interaction: discord.Interaction, time: str = commands.parameter(description="Time in minutes(m), hours(h), day(d)"), *message):

        if time.lower().endswith("min"):
            stripped = time.replace("min", "")
            delay = timedelta(minutes=float(stripped))
        elif time.lower().endswith("h"):
            stripped = time.replace("h", "")
            delay = timedelta(hours=float(stripped))
        elif time.lower().endswith("d"):
            stripped = time.replace("d", "")
            delay = timedelta(days=float(stripped))
        else:
            return await interaction.send("No correct time format given")

        when = datetime.now() + delay
        reminder = " ".join(message)

        scheduler.add_job(func=self.sendreminder, trigger="date", run_date=when, args=[interaction, reminder])
        await interaction.send(f"I will remind you at <t:{int(mktime(when.timetuple()))}:d><t:{int(mktime(when.timetuple()))}:T> (<t:{int(mktime(when.timetuple()))}:R>)")

    async def sendreminder(self, interaction, reminder):
        await interaction.reply(f"Reminder for:\n{reminder}")

    @commands.command(name="speak", aliases=['speach', 'say', 'talk'], description="Speak Japanese into VC")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def speak(self, interaction: discord.Interaction, speaker: Optional[int] = 2, *text):
        msg = await interaction.reply("Processing...")

        vc = interaction.author.voice.channel

        try:
            vc = await vc.connect()
        except discord.ClientException:
            return await interaction.send("I am already connected to a voice channel in this server.")

        async with Client(base_url=getenv('VM')) as client: 
            if len(text) <= 0:
                return await interaction.reply("no text given")
            
            line = " ".join(text)

            audio_query = await client.create_audio_query(text=line, speaker=speaker) 
            filename = f"{interaction.author.id}.wav"

            with open(filename, "wb") as f: 
                f.write(await audio_query.synthesis(speaker=speaker))
        
        await msg.edit(content="Synthesis complete, playing now")

        vc.play(discord.FFmpegPCMAudio(filename))
        
        while vc.is_playing():
            await asyncio.sleep(1)
        
        await vc.disconnect()
        remove(filename)

    @commands.command(name="speaker", hidden=True)
    @commands.is_owner()
    async def speaker(self, interaction: discord.Interaction):
        await interaction.message.delete()

        vc = interaction.author.voice.channel

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        vc = await vc.connect()

        host = "0.0.0.0"
        port = 8025

        server_socket = socket.socket() 
        server_socket.bind((host, port)) 

        server_socket.listen(2)
        conn, address = server_socket.accept()

        print("Connection from: " + str(address))
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            print("Processing: " + str(data))
            conn.send("Processing...".encode())
            
            async with Client(base_url=getenv('VM')) as client: 
                audio_query = await client.create_audio_query(text=str(data), speaker=2) 
                filename = f"{interaction.author.id}.wav"

                with open(filename, "wb") as f: 
                    f.write(await audio_query.synthesis(speaker=2))

            conn.send("Synthesis complete!".encode())
            vc.play(discord.FFmpegPCMAudio(filename))


        conn.close()
        await vc.disconnect()
        remove(filename)


scheduler.start()

async def setup(bot):
    await bot.add_cog(Misc(bot))