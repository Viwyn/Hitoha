import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from random import shuffle
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.now_playing = {}

        self.queue_data = {}
        self.ytdl_options = {"format": "bestaudio", "noplaylist": "True", 'quiet': True}
        self.ffmpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

    async def yt_search(self, search, ctx):
        print(f"Searching: {search} ({ctx.author.display_name})")
        await ctx.send(f"Searching for \"{search}\"")
        with YoutubeDL(self.ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(f"ytsearch5:{search}", download= False)['entries']
            except Exception as e:
                print(e)
                return False
            
        videos = []

        for video in info[:5]:
            videos.append({"source": video['formats'][0]["url"], "title": video["title"]})

        return videos

    async def yt_search_url(self, search, ctx):
        print(f"Searching: {search} ({ctx.author.display_name})")
        await ctx.send(f"Searching for \"{search}\"")
        with YoutubeDL(self.ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(search, download= False)
            except Exception as e:
                print(e)
                return False
            
        print(f"Found: {info['title']}")
        return dict({"source": info['formats'][0]["url"], "title": info["title"]})
    
    async def yt_search_playlist(self, plsearch, ctx):
        print(f"Searching for playlist: {plsearch} ({ctx.author.display_name})")
        await ctx.send(f"Searching for \"{plsearch}\"")
        with YoutubeDL(self.ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(plsearch, download= False)
            except Exception as e:
                print(e)
                return False
            
        print(f"Found: {len(info['entries'])} videos.")

        videos = []

        for entry in info['entries']:
            print(f"Added {entry['title']} to queue ({ctx.author.display_name})")
            videos.append({"source": entry['formats'][0]["url"], "title": entry["title"]})

        return videos
        # return {"source": info['formats'][0]["url"], "title": info["title"]}
    
    async def next_song(self, guild: int):
        if self.queue_data[guild]["looping"]:
            song = self.queue_data[guild]["now_playing"]["source"]
            self.queue_data[guild]["channel"].play(discord.PCMVolumeTransformer((discord.FFmpegPCMAudio(song, **self.ffmpeg_options)), volume=0.1), after=lambda e: self.bot.loop.create_task(self.next_song(guild)))

        elif len(self.queue_data[guild]["queue"]) > 0 and self.queue_data[guild]["is_playing"]:
            self.queue_data[guild]["is_playing"] = True

            song = self.queue_data[guild]["queue"][0]['source']

            self.queue_data[guild]["channel"].play(discord.PCMVolumeTransformer((discord.FFmpegPCMAudio(song, **self.ffmpeg_options)), volume=0.1), after=lambda e: self.bot.loop.create_task(self.next_song(guild)))

            self.queue_data[guild]["now_playing"] = self.queue_data[guild]["queue"].pop(0)

        else:
            await self.queue_data[guild]["channel"].disconnect()
            del self.queue_data[guild]

    async def play_song(self, ctx):
        if len(self.queue_data[ctx.guild.id]["queue"]) > 0:
            self.queue_data[ctx.guild.id]["is_playing"] = True

            song = self.queue_data[ctx.guild.id]["queue"][0]['source']

            if self.queue_data[ctx.guild.id]["channel"] == None or not self.queue_data[ctx.guild.id]["channel"].is_connected():
                await self.queue_data[ctx.guild.id]["channel"].connect(timeout=60.0, reconnect=True)
                
                if self.queue_data[ctx.guild.id]["channel"] == None:
                    await ctx.send("Could not join the voice channel")
                    return

            elif self.queue_data[ctx.guild.id]["channel"].channel == ctx.author.voice.channel:
                pass
            else:
                return await ctx.reply("Im already connected to a voice channel in this server")
            
            await ctx.send(f"Now Playing: {self.queue_data[ctx.guild.id]['queue'][0]['title']}")

            self.queue_data[ctx.guild.id]["channel"].play(discord.PCMVolumeTransformer((discord.FFmpegPCMAudio(song, **self.ffmpeg_options)), volume=0.1), after=lambda e: self.bot.loop.create_task(self.next_song(ctx.guild.id)))

            self.queue_data[ctx.guild.id]["now_playing"] = self.queue_data[ctx.guild.id]["queue"].pop(0)

    @commands.command(name= "play", aliases=["p"], description="Plays a song from youtube")
    async def play(self, ctx, *search):
        search_query = " ".join(search)
        guild = ctx.guild.id

        if search_query.startswith("https:") or search_query.startswith("http:"):
            pass
        else:
            return await ctx.send("Not a URL use search instead")

        vc = ctx.author.voice
        if vc is None:
            await ctx.reply("Connect to a voice channel first")
        else:
            vc = vc.channel

            if guild in self.queue_data:
                pass
            else:
                self.queue_data[guild] = {"queue": [], "channel": await vc.connect(timeout=60.0, reconnect=True), "looping": False, "is_playing": False, "is_paused": False}

            song = False
            if any(ss in search_query for ss in ['list', 'playlist']):
                song = await self.yt_search_playlist(search_query, ctx)
            else:
                song = await self.yt_search_url(search_query, ctx) 

            if song == False:
                await ctx.reply("Could not get the song, try a different search")
            else:
                if type(song) == list:
                    self.queue_data[guild]["queue"].extend(song)
                    await ctx.send(f"Added {len(song)} songs from the playlist to queue")
                else:
                    self.queue_data[guild]["queue"].append(song)
                    await ctx.send(f"Added song {song['title']} to position {len(self.queue_data[ctx.guild.id]['queue'])}")

                if self.queue_data[guild]["is_playing"] == False:
                    await self.play_song(ctx)

    @commands.command(name="search", aliases=['s'], description="Searches for a song on Youtube")
    async def search(self, ctx, *search):
        search_query = " ".join(search)
        guild = ctx.guild.id

        vc = ctx.author.voice
        if vc is None:
            await ctx.reply("Connect to a voice channel first")
        else:
            vc = vc.channel

            if guild in self.queue_data:
                pass
            else:
                self.queue_data[guild] = {"queue": [], "channel": await vc.connect(timeout=60.0, reconnect=True), "looping": False, "is_playing": False, "is_paused": False}

            def check(m):
                return m.author == ctx.author and (m.content in ['1', '2', '3', '4', '5'])

            songs = await self.yt_search(search_query, ctx)
            
            text = ""
            for no, song in enumerate(songs):
                text += f"{no+1}) {song['title']}\n"

            msg = await ctx.reply(text)

            try:
                response = await self.bot.wait_for('message', timeout=30.0, check=check)
                song = songs[int(response.content)-1]
                self.queue_data[guild]["queue"].append(song)
                await ctx.send(f"Added song {song['title']} to position {len(self.queue_data[ctx.guild.id]['queue'])}")

                if self.queue_data[guild]["is_playing"] == False:
                    await self.play_song(ctx)
            except asyncio.TimeoutError:
                return await ctx.send("You did not pick a video.")

    @commands.command(name="pause", description="Pauses the currently playing song")
    async def pause(self, ctx):
        if ctx.guild.id not in self.queue_data:
            return await ctx.reply("I am not currently in a voice channel")
        
        if self.queue_data[ctx.guild.id]["is_playing"]:
            self.queue_data[ctx.guild.id]["is_playing"] = False
            self.queue_data[ctx.guild.id]["is_paused"] = True
            self.queue_data[ctx.guild.id]["channel"].pause()
            await ctx.send("I paused the song")
        elif self.queue_data[ctx.guild.id]["is_paused"]:
            await ctx.reply("I am already paused")
        else:
            await ctx.reply("Currently not playing any song")

    @commands.command(name="resume", description="Resumes the current playing song")
    async def resume(self, ctx):
        if ctx.guild.id not in self.queue_data:
            return await ctx.reply("I am not currently in a voice channel")

        if self.queue_data[ctx.guild.id]["is_paused"]:
            self.queue_data[ctx.guild.id]["is_playing"] = True
            self.queue_data[ctx.guild.id]["is_paused"] = False
            self.queue_data[ctx.guild.id]["channel"].resume()
            await ctx.send("I resumed the song")
        else:
            await ctx.reply("I am not currently paused")

    @commands.command(name="skip", description="Skips the current playing song")
    async def skip(self, ctx):
        if ctx.guild.id in self.queue_data:
            if ctx.author.voice.channel is None:
                return await ctx.reply("Please join a voice channel")

            if ctx.author.voice.channel is not self.queue_data[ctx.guild.id]["channel"].channel:
                return await ctx.reply("I am not in the same voice channel as you")
            
            if len(self.queue_data[ctx.guild.id]["queue"]) > 0:
                self.queue_data[ctx.guild.id]["channel"].stop()
                await ctx.send("I skipped to the next song")
            else:
                self.queue_data[ctx.guild.id]["channel"].stop()

        else:
            await ctx.reply("I am not currently playing any song in this server")

    @commands.command(name="queue", aliases=["q"], description="Shows a list of songs in queue")
    async def queue(self, ctx):
        song_list = "Up Next: \n"

        for no, song in enumerate(self.queue_data[ctx.guild.id]["queue"][:5]):
            song_list += str(no+1) + ") " + song["title"] + "\n"

        if song_list != "Up Next: \n":
            await ctx.send(song_list)
        else:
            await ctx.send("No songs in queue")

    @commands.command(name="clear", description="Clears the song queue")
    async def clear(self, ctx):
        if ctx.guild.id in self.queue_data and self.queue_data[ctx.guild.id]["is_playing"]:
            self.queue_data[ctx.guild.id]["channel"].stop()
        
        self.queue_data[ctx.guild.id]["queue"] = []
        await ctx.send("Cleared the song queue")

    @commands.command(name="leave", aliases=["stop", "fuckoff"], description="Disconnects me from the vc")
    async def leave(self, ctx):
        if ctx.guild.id in self.queue_data:
            await self.queue_data[ctx.guild.id]["channel"].disconnect()
            await self.clear(ctx)

    @commands.command(name="np", aliases=["nowplaying"], description="Shows the current song playing")
    async def np(self, ctx):
        await ctx.send(f"Now Playing: \n{self.queue_data[ctx.guild.id]['now_playing']['title']}")

    @commands.command(name="loop", description="Loops the current playing song.")
    async def loop(self, ctx):
        vc = ctx.author.voice

        if ctx.guild.id not in self.queue_data:
            return await ctx.send("No songs are currently playing")

        if vc is None:
            return await ctx.reply("Connect to a voice channel first")

        if self.queue_data[ctx.guild.id]["looping"]:
            self.queue_data[ctx.guild.id]["looping"] = False
            await ctx.send(f"Stopped looping.")
        else:
            self.queue_data[ctx.guild.id]["looping"] = True
            await ctx.send(f"Looping {self.queue_data[ctx.guild.id]['now_playing']['title']}")

    @commands.command(name="shuffle", description="Shuffles the song queue")
    async def shuffle(self, ctx):
        vc = ctx.author.voice

        if vc is None:
            return await ctx.reply("Connect to a voice channel first")

        if ctx.guild.id not in self.queue_data:
            return await ctx.send("There are no song queues for this server")

        shuffle(self.queue_data[ctx.guild.id]["queue"])

        await ctx.send("Queue is now shuffled")

    @commands.command(name="move", description="Moves the position of songs in the queue")
    async def move(self, ctx, target:int, loc:int):
        vc = ctx.author.voice

        if vc is None:
            return await ctx.reply("Connect to a voice channel first")

        if ctx.guild.id not in self.queue_data:
            return await ctx.send("There are no song queues for this server")
        
        await ctx.send(f"Moving {self.queue_data[ctx.guild.id]['queue'][target-1]['title']} to index {loc}")

        self.queue_data[ctx.guild.id]["queue"].insert(loc-1, self.queue_data[ctx.guild.id]["queue"].pop(target-1))

async def setup(bot):
    await bot.add_cog(Music(bot))
