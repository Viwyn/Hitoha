import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import mktime
from typing import Optional
from os import getenv, remove
import asyncio
import azure.cognitiveservices.speech as speechsdk


scheduler = AsyncIOScheduler()

speech_key = getenv("AZURE")
service_region = "southeastasia"
        
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

speech_config.speech_synthesis_voice_name = "ja-JP-AoiNeural"


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_options = {"options": "-vn"}

    @commands.command(name="choose", description="Allow me to make a choice for you")
    async def choose(self, ctx, *choices):
        await ctx.reply(random.choice(choices))

    @commands.command(name="8ball", description="Roll the magic 8ball")
    async def _8ball(self, ctx, *args):
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
        
        await ctx.reply(random.choice(outputs))
    
    @commands.command(name="remind", aliases=['remindme', 'reminder'], description="Send a reminder to you at a spefied time")
    async def remind(self, ctx, time: str = commands.parameter(description="Time in minutes(m), hours(h), day(d)"), *message):

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
            return await ctx.send("No correct time format given")

        when = datetime.now() + delay
        reminder = " ".join(message)

        scheduler.add_job(func=self.sendreminder, trigger="date", run_date=when, args=[ctx, reminder])
        await ctx.send(f"I will remind you at <t:{int(mktime(when.timetuple()))}:d><t:{int(mktime(when.timetuple()))}:T> (<t:{int(mktime(when.timetuple()))}:R>)")

    async def sendreminder(self, ctx, reminder):
        await ctx.reply(f"Reminder for:\n{reminder}")

    @commands.command(name="speak", aliases=['speach', 'say', 'talk'], description="Speak Japanese into VC")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def speak(self, ctx, speaker: Optional[int] = 2, *text):
        msg = await ctx.reply("Processing...")

        vc = ctx.author.voice.channel

        try:
            vc = await vc.connect()
        except discord.ClientException:
            return await ctx.send("I am already connected to a voice channel in this server.")

        filename = str(ctx.author.id) + ".wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = speech_synthesizer.speak_text_async(" ".join(text)).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            await msg.edit(content="Synthesis complete, playing now")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            await ctx.reply("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                await ctx.reply("Error details: {}".format(cancellation_details.error_details))
        
        vc.play(discord.FFmpegPCMAudio(filename, **self.ffmpeg_options))
        
        while vc.is_playing():
            await asyncio.sleep(1)
        
        await vc.disconnect()
        remove(filename)

scheduler.start()

async def setup(bot):
    await bot.add_cog(Misc(bot))