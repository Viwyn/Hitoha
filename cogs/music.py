import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from random import shuffle

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.now_playing = {}

        self.queue_data = {}
        self.ytdl_options = {"format": "bestaudio", "noplaylist": "True", 'quiet': True}
        self.ffmpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

    async def yt_search(self, search, interaction: discord.Interaction):
        print(f"Searching: {search} ({interaction.author.display_name})")
        await interaction.send(f"Searching for \"{search}\"")
        with YoutubeDL(self.ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(f"ytsearch:{search}", download= False)['entries'][0]
            except Exception as e:
                print(e)
                return False
            
        print(f"Found: {info['title']}")
        return {"source": info['formats'][0]["url"], "title": info["title"]}
    
    async def next_song(self, guild: int):
        if self.queue_data[guild]["looping"]:
            song = self.queue_data[guild]["now_playing"]["source"]
            self.queue_data[guild]["channel"].play(discord.FFmpegPCMAudio(song, **self.ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.next_song(guild)))

        elif len(self.queue_data[guild]["queue"]) > 0 and self.queue_data[guild]["is_playing"]:
            self.queue_data[guild]["is_playing"] = True

            song = self.queue_data[guild]["queue"][0]['source']

            self.queue_data[guild]["channel"].play(discord.FFmpegPCMAudio(song, **self.ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.next_song(guild)))

            self.queue_data[guild]["now_playing"] = self.queue_data[guild]["queue"].pop(0)

        else:
            await self.queue_data[guild]["channel"].disconnect()
            del self.queue_data[guild]

    async def play_song(self, interaction: discord.Interaction):
        if len(self.queue_data[interaction.guild.id]["queue"]) > 0:
            self.queue_data[interaction.guild.id]["is_playing"] = True

            song = self.queue_data[interaction.guild.id]["queue"][0]['source']

            if self.queue_data[interaction.guild.id]["channel"] == None or not self.queue_data[interaction.guild.id]["channel"].is_connected():
                await self.queue_data[interaction.guild.id]["channel"].connect()
                
                if self.queue_data[interaction.guild.id]["channel"] == None:
                    await interaction.send("Could not join the voice channel")
                    return

            elif self.queue_data[interaction.guild.id]["channel"].channel == interaction.author.voice.channel:
                pass
            else:
                return await interaction.reply("Im already connected to a voice channel in this server")
            
            await interaction.send(f"Now Playing: {self.queue_data[interaction.guild.id]['queue'][0]['title']}")

            self.queue_data[interaction.guild.id]["channel"].play(discord.FFmpegPCMAudio(song, **self.ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.next_song(interaction.guild.id)))

            self.queue_data[interaction.guild.id]["now_playing"] = self.queue_data[interaction.guild.id]["queue"].pop(0)

    @commands.command(name= "play", aliases=["p"], help="Plays a song from youtube")
    async def play(self, interaction: discord.Interaction, *search):
        search_query = " ".join(search)
        guild = interaction.guild.id

        vc = interaction.author.voice
        if vc is None:
            await interaction.reply("Connect to a voice channel first")
        else:
            vc = vc.channel

            if guild in self.queue_data:
                pass
            else:
                self.queue_data[guild] = {"queue": [], "channel": await vc.connect(), "looping": False, "is_playing": False, "is_paused": False}

            
            song = await self.yt_search(search_query, interaction)
            if song == False:
                await interaction.reply("Could not get the song, try a different search")
            else:
                self.queue_data[guild]["queue"].append(song)
                await interaction.send(f"Added song {song['title']} to position {len(self.queue_data[interaction.guild.id]['queue'])}")

                if self.queue_data[guild]["is_playing"] == False:
                    await self.play_song(interaction)

    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.queue_data:
            return await interaction.reply("I am not currently in a voice channel")
        
        if self.queue_data[interaction.guild.id]["is_playing"]:
            self.queue_data[interaction.guild.id]["is_playing"] = False
            self.queue_data[interaction.guild.id]["is_paused"] = True
            self.queue_data[interaction.guild.id]["channel"].pause()
            await interaction.send("I paused the song")
        elif self.queue_data[interaction.guild.id]["is_paused"]:
            await interaction.reply("I am already paused")
        else:
            await interaction.reply("Currently not playing any song")

    @commands.command(name="resume", help="Resumes the current playing song")
    async def resume(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.queue_data:
            return await interaction.reply("I am not currently in a voice channel")

        if self.queue_data[interaction.guild.id]["is_paused"]:
            self.queue_data[interaction.guild.id]["is_playing"] = True
            self.queue_data[interaction.guild.id]["is_paused"] = False
            self.queue_data[interaction.guild.id]["channel"].resume()
            await interaction.send("I resumed the song")
        else:
            await interaction.reply("I am not currently paused")

    @commands.command(name="skip", help="Skips the current playing song")
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.id in self.queue_data:
            if interaction.author.voice.channel is None:
                return await interaction.reply("Please join a voice channel")

            if interaction.author.voice.channel is not self.queue_data[interaction.guild.id]["channel"].channel:
                return await interaction.reply("I am not in the same voice channel as you")
            
            if len(self.queue_data[interaction.guild.id]["queue"]) > 0:
                self.queue_data[interaction.guild.id]["channel"].stop()
                await interaction.send("I skipped to the next song")
            else:
                self.queue_data[interaction.guild.id]["channel"].stop()

        else:
            await interaction.reply("I am not currently playing any song in this server")

    @commands.command(name="queue", aliases=["q"], help="Shows a list of songs in queue")
    async def queue(self, interaction: discord.Interaction):
        song_list = "Up Next: \n"

        for no, song in enumerate(self.queue_data[interaction.guild.id]["queue"][:5]):
            song_list += str(no+1) + ") " + song["title"] + "\n"

        if song_list != "Up Next: \n":
            await interaction.send(song_list)
        else:
            await interaction.send("No songs in queue")

    @commands.command(name="clear", help="Clears the song queue")
    async def clear(self, interaction: discord.Interaction):
        if interaction.guild.id in self.queue_data and self.queue_data[interaction.guild.id]["is_playing"]:
            self.queue_data[interaction.guild.id]["channel"].stop()
        
        self.queue_data[interaction.guild.id]["queue"] = []
        await interaction.send("Cleared the song queue")

    @commands.command(name="leave", aliases=["stop", "fuckoff"], help="Disconnects me from the vc")
    async def leave(self, interaction:discord.Interaction):
        if interaction.guild.id in self.queue_data:
            await self.queue_data[interaction.guild.id]["channel"].disconnect()
            await self.clear(interaction)

    @commands.command(name="np", aliases=["nowplaying"], help="Shows the current song playing")
    async def np(self, interaction: discord.Interaction):
        await interaction.send(f"Now Playing: \n{self.queue_data[interaction.guild.id]['now_playing']['title']}")

    @commands.command(name="loop", help="Loops the current playing song.")
    async def loop(self, interaction: discord.Interaction):
        vc = interaction.author.voice

        if interaction.guild.id not in self.queue_data:
            return await interaction.send("No songs are currently playing")

        if vc is None:
            return await interaction.reply("Connect to a voice channel first")

        if self.queue_data[interaction.guild.id]["looping"]:
            self.queue_data[interaction.guild.id]["looping"] = False
            await interaction.send(f"Stopped looping.")
        else:
            self.queue_data[interaction.guild.id]["looping"] = True
            await interaction.send(f"Looping {self.queue_data[interaction.guild.id]['now_playing']['title']}")

    @commands.command(name="shuffle", help="Shuffles the song queue")
    async def shuffle(self, interaction: discord.Interaction):
        vc = interaction.author.voice

        if vc is None:
            return await interaction.reply("Connect to a voice channel first")

        if interaction.guild.id not in self.queue_data:
            return await interaction.send("There are no song queues for this server")

        shuffle(self.queue_data[interaction.guild.id]["queue"])

        await interaction.send("Queue is now shuffled")

    @commands.command(name="move", help="Moves the position of songs in the queue")
    async def move(self, interaction: discord.Interaction, target:int, loc:int):
        vc = interaction.author.voice

        if vc is None:
            return await interaction.reply("Connect to a voice channel first")

        if interaction.guild.id not in self.queue_data:
            return await interaction.send("There are no song queues for this server")
        
        await interaction.send(f"Moving {self.queue_data[interaction.guild.id]['queue'][target-1]['title']} to index {loc}")

        self.queue_data[interaction.guild.id]["queue"].insert(loc-1, self.queue_data[interaction.guild.id]["queue"].pop(target-1))

async def setup(bot):
    await bot.add_cog(Music(bot))
