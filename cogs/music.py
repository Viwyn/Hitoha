import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.queue = []
        self.ytdl_options = {"format": "bestaudio", "noplaylist": "True"}
        self.ffmpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

        self.vc = None

    def yt_search(self, search):
        with YoutubeDL(self.ytdl_options) as ytdl:
            
                info = ytdl.extract_info(f"ytsearch:{search}", download= False)['entries'][0]
                print(info)
            
        return {"source": info['formats'][0]["url"], "title": info["title"]}
    

    @commands.command()
    async def play(self, interaction: discord.Interaction, *search):
        await interaction.send(self.yt_search(" ".join(search)))




async def setup(bot):
    await bot.add_cog(Music(bot))
