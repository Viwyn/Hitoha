import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import mktime

scheduler = AsyncIOScheduler()

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="choose", case_insensitive=True, description="Allow me to make a choice for you")
    async def choose(self, interaction: discord.Interaction, *choices):
        await interaction.reply(random.choice(choices))

    @commands.command(name="8ball", case_insensitive=True, description="Roll the magic 8ball")
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
    
    @commands.command(name="remind", aliases=['remindme', 'reminder'], description="Send a reminder to you at a spefied time", case_insensitive=True)
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

scheduler.start()

async def setup(bot):
    await bot.add_cog(Misc(bot))