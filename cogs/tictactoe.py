import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

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
        


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
    aliases=['ttt'], 
    description="Play a game of TicTacToe with someone."
    )
    async def tictactoe(self, ctx, opponent:discord.User):

        if opponent == ctx.author:
            return await ctx.send("Can't play TicTacToe with yourself, go find some friends.")

        def check(m):
            return m.author == opponent and (m.content == 'y' or m.content == 'n')

        await ctx.send(f"{opponent.mention}, do you want to play TicTacToe with {ctx.author.display_name}? (y/n)")

        try:
            response = await self.bot.wait_for('message', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(f"{opponent.display_name} did not accept the match.")

        if response.content == 'n':
            return await ctx.send(f"{opponent.display_name} did not accept the match.")

        view = tttView(ctx.author, opponent)

        await ctx.send(content=f"TicTacToe Match between {ctx.author.display_name} and {opponent.display_name}\nCurrent Player: {ctx.author.mention}(X)", view=view)

async def setup(bot):
    await bot.add_cog(TicTacToe(bot))