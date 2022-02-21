import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from os import getenv
import aiohttp
import asyncio
import io

load_dotenv()

client = commands.Bot(command_prefix='!!')

owner_id = 241138170610188288

@client.event
async def on_ready():
    print("Ready!")

@client.command()
async def ping(ctx):
    await ctx.send("Pong!")

class PfpView(View):
    def __init__(self, embed, embed0):
        super().__init__(timeout = 10)
        self.embed = embed
        self.embed0 = embed0

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Personal Profile Picture", custom_id="personal", disabled=True)
    async def button_callback(self, button, interaction):
        otherButton = [x for x in self.children if x.custom_id == "server"][0]
        if (otherButton.style == discord.ButtonStyle.success):
            otherButton.disabled = False
            button.disabled = True
            
        await interaction.response.edit_message(embed = self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="server")
    async def server_button_callback(self, button, interaction):
        if (self.embed0 == None):
            button.label = "Not Found"
            button.style = discord.ButtonStyle.danger
            button.disabled = True
            await interaction.response.edit_message(view=self)
        else:
            otherButton = [x for x in self.children if x.custom_id == "personal"][0]
            otherButton.disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed = self.embed0, view=self)

    async def on_timeout(self):
        self.clear_items()
        return

    #button0 = discord.ui.Button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="pfpbutton0")

@client.command(
aliases=['avatar'], 
description="Gets the profile picture of the user, defaults to author if no user is specified.", 
brief="Gets a profile picture.")
async def pfp(ctx, user:discord.User = None):

    if user == None:
        user = ctx.author

    name = user.display_name

    if (user.accent_color):
        embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.from_rgb(user.accent_color.r, user.accent_color.g, user.accent_color.b))
    else:
        embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.random())

    embed.set_footer(text= f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

    embed0 = embed.copy()

    embed.set_image(url=user.display_avatar.url)
    
    member = await ctx.guild.fetch_member(user.id)

    if member.guild_avatar != None:
        embed0.set_image(url=member.guild_avatar.url)
    else:
        embed0 = None

    view = PfpView(embed=embed, embed0=embed0)

    await ctx.send(embed=embed, view=view)

@client.command(description="Takes the given emoji and adds it to the current server.", brief="Adds the emoji to the server.")
async def stealemote(ctx, emote:discord.PartialEmoji, name = None):
    emojiData = await emote.read()

    if name == None:
        name = emote.id

    newEmoji = await ctx.guild.create_custom_emoji(name=name, image=emojiData)
    await ctx.reply(f"Stolen the emote and named it \"{newEmoji.name}\"")

class tttButton(Button):
    def __init__(self, x:int, y:int):
        super().__init__(style=discord.ButtonStyle.gray, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction):
        view:tttView = self.view
        content = ""

        state = view.board[self.x][self.y]

        if state in (-1, 1):
            return

        if (interaction.user == view.current and interaction.user == view.player1):
            self.style = discord.ButtonStyle.success
            self.label = "X"
            view.current = view.player2
            view.board[self.x][self.y] = -1
            content = f"TicTacToe Match between {view.player1.display_name} and {view.player2.display_name}\nCurrent Player: {view.player2.mention}(O)"

        elif (interaction.user == view.current and interaction.user == view.player2):
            self.style = discord.ButtonStyle.danger
            self.label = "O"
            view.current = view.player1
            view.board[self.x][self.y] = 1
            content = f"TicTacToe Match between {view.player1.display_name} and {view.player2.display_name}\nCurrent Player: {view.player1.mention}(X)"
        else:
            pass

        self.disabled = True
        winner = view.checkWinner()
        if winner is not None:
            if winner is view.player1:
                content = f"TicTacToe Match between {view.player1.display_name} and {view.player2.display_name}\n{view.player1.mention} Wins!"
            elif winner is view.player2:
                content = f"TicTacToe Match between {view.player1.display_name} and {view.player2.display_name}\n{view.player2.mention} Wins!"
            else:
                content = f"TicTacToe Match between {view.player1.display_name} and {view.player2.display_name}\nGame Ended in a Tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class tttView(View):
    def __init__(self, p1:discord.User, p2:discord.User):
        super().__init__(timeout=500)
        self.player1 = p1 # -1
        self.player2 = p2 # 1
        self.current = p1
        self.board = [
            [0, 0, 0], 
            [0, 0, 0], 
            [0, 0, 0]
            ]

        for i in range(3):
            for j in range(3):
                self.add_item(tttButton(i, j))

    def checkWinner(self):
        #check horizontals
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.player2
            elif value == -3:
                return self.player1

        #check verticals
        for i in range(3):
            value = self.board[0][i] + self.board[1][i] + self.board[2][i]
        
            if value == 3:
                return self.player2
            elif value == -3:
                return self.player1

        #check diags
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
                return self.player2
        elif diag == -3:
            return self.player1

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
                return self.player2
        elif diag == -3:
            return self.player1

        if all(j != 0 for i in self.board for j in i):
            return -1

        return None

    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
        

@client.command(
aliases=['ttt'], 
description="Play a game of TicTacToe with someone."
)
async def tictactoe(ctx, opponent:discord.User):
    
    if opponent == ctx.author:
        return await ctx.send("Can't play TicTacToe with yourself, go find some friends.")

    def check(m):
        return m.author == opponent and (m.content == 'y' or m.content == 'n')

    await ctx.send(f"{opponent.mention}, do you want to play TicTacToe with {ctx.author.display_name}? (y/n)")

    try:
        response = await client.wait_for('message', timeout=20.0, check=check)
    except asyncio.TimeoutError:
        return await ctx.send(f"{opponent.display_name} did not accept the match.")

    if response.content == 'n':
        return await ctx.send(f"{opponent.display_name} did not accept the match.")

    view = tttView(ctx.author, opponent)

    await ctx.send(content=f"TicTacToe Match between {ctx.author.display_name} and {opponent.display_name}\nCurrent Player: {ctx.author.mention}(X)", view=view)

@client.command()
@commands.is_owner()
async def msgchannel(ctx, channelid:int, *words):
    if (len(words) == 0):
        return await ctx.send("Cannot send empty message.")

    channel = await client.fetch_channel(channelid)
    await channel.send(" ".join(words))

@client.command(aliases=['cc'])
@commands.is_owner()
async def connectchannel(ctx, channelid:int):
    targetChannel = await client.fetch_channel(channelid)
    homeChannel = ctx.channel

    def check(m):
        return (m.channel == targetChannel or m.channel == homeChannel) and m.author != client.user

    await homeChannel.send(f"Started connection with the channel \"{targetChannel.name}\" in the server \"{targetChannel.guild.name}\"")

    while(True):
        response = await client.wait_for('message', timeout=None, check=check)

        if response.channel == homeChannel and response.content == "end":
            await homeChannel.send("Ended connection.")
            break
        elif response.channel == homeChannel:
            attList = []
            if response.attachments:
                for attachment in response.attachments:
                    attList.append(discord.File(io.BytesIO(await attachment.read()), f'file.{attachment.content_type.split("/")[1]}'))
                await targetChannel.send(response.content, files=attList)
            else:
                await targetChannel.send(response.content)

        elif response.channel == targetChannel:
            await homeChannel.send(f"{response.author.display_name}: {response.content}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount:int):
    await ctx.channel.purge(limit=amount)

@client.command(aliases=['cal'])
async def calculate(ctx, eq):
    return await ctx.send(eval(eq))

@client.event
async def on_command_error(ctx, error):
    await ctx.reply(error)

client.run(getenv('APHRODITE0'))