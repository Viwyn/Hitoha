import discord
from discord.ext import commands
from random import randrange
import asyncio
import mysql.connector
from os import getenv

class Cards():
    def __init__(self, suit, char):
        self.suit = suit
        self.char = char

    def show(self):
        detail = ""
        if self.char in ['j', 'q', 'k', 'a']:
            detail += self.char.upper()
        elif type(self.char) == int:
            detail += str(self.char)

        if self.suit == 'Spades':
            detail += '♠️'
        elif self.suit == 'Hearts':
            detail += '♥️'
        elif self.suit == 'Clubs':
            detail += '♣️'
        elif self.suit == 'Diamonds':
            detail += '♦️'

        return detail

class Deck():
    def __init__(self):
        self.deck = []

        for i in ['Spades', 'Hearts', 'Clubs', 'Diamonds']:
            for j in [2, 3, 4, 5, 6, 7, 8, 9, 10, 'j', 'q', 'k', 'a']:
                self.deck.append(Cards(i, j))

    def draw(self):
        return self.deck.pop(randrange(0, len(self.deck)))

class Hand():
    def __init__(self):
        self.hand = []
        self.value = 0
        self.aces = 0

    def addCard(self, card: Cards):
        self.hand.append(card)
        if card.char == 'a':
            self.value += 11
            self.aces += 1
        elif card.char in ['k', 'q', 'j']:
            self.value += 10
        elif type(card.char) == int:
            self.value += card.char

        self.checkAces()

    def checkAces(self):
        if self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def hit(self, deck: Deck):
        self.addCard(deck.draw())
        self.checkAces()

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="blackjack", aliases=['bj'], help="Start a game of blackjack")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        if bet < 1:
            return await interaction.reply("Unable to bet nothing")

        connection = mysql.connector.connect(host=getenv("DBHOST"),
                                                port=getenv("DBPORT"),
                                                database=getenv("DBNAME"),
                                                user=getenv("DBUID"),
                                                password=getenv("DBPW"))
        cursor = connection.cursor()

        cursor.execute(f"SELECT balance FROM Users WHERE id = {interaction.author.id}")
        bal = cursor.fetchone()

        if bal == None:
            return await interaction.reply("You have not made an account yet, run bal to create your account")
        
        if bal[0] < bet:
            return await interaction.reply("You have insufficent balance")

        d1: Deck = Deck()
        player: Hand = Hand()
        dealer: Hand = Hand()

        dealer.hit(d1)
        dealer.hit(d1)

        player.hit(d1)
        player.hit(d1)
        
        stood = False
        state = None

        message = await interaction.send("Starting a game of blackjack...")

        def check(m):
            return m.author == interaction.author and m.channel == interaction.channel and m.content.lower().strip() in ['hit', 'stand', 'h', 's']

        while True:
            msg = "```\n"
            if stood == False:
                msg += "Dealer:\n" + " ".join(list("??" for x in dealer.hand)) + f" (??)\n\n" 
            else:
                msg += "Dealer:\n" + " ".join(list(x.show() for x in dealer.hand)) + f" ({dealer.value})\n\n" 
                
            msg += f"{interaction.author.display_name}:\n" + " ".join(list(x.show() for x in player.hand)) + f" ({player.value})"

            msg += "\n```"
            await message.edit(content=msg)

            if stood == False:
                try:
                    response = await self.bot.wait_for('message', timeout=60.0, check=check)

                    if response.content.lower().strip() in ['hit', 'h']:
                        player.hit(d1)
                        if player.value >= 21:
                            stood = True

                        if len(player.hand) == 5:
                            stood = True

                        continue
                    else:
                        stood = True
                        continue

                except asyncio.TimeoutError:
                    await interaction.send("*Game forfeited due to inactivity*")
                    break
            else:
                if player.value > 21 and len(dealer.hand) > 2:
                    pass
                elif dealer.value > 21:
                    pass
                elif len(dealer.hand) == 5:
                    pass
                elif dealer.value > player.value and dealer.value < 21:
                    pass
                elif len(player.hand) == 2 and player.value == 21:
                    pass
                elif dealer.value < 21 and dealer.value <= player.value:
                    dealer.hit(d1)
                    continue
                else:
                    dealer.hit(d1)
                    continue

            #check wins
            if len(player.hand) == 5 and player.value <= 21:
                state = 'player'
                break
            elif len(dealer.hand) == 5 and dealer.value <= 21:
                state = 'dealer'
                break
            elif dealer.value == 21 and player.value == 21:
                state = 'tie'
                break
            elif dealer.value == 21 and player.value != 21:
                state = 'dealer'
                break
            elif player.value == 21 and dealer.value != 21:
                state = 'player'
                break
            elif dealer.value < 21 and player.value < 21 and dealer.value > player.value:
                state = 'dealer'
                break
            elif dealer.value < 21 and player.value < 21 and dealer.value < player.value:
                state = 'player'
                break
            elif dealer.value < 21 and player.value > 21:
                state='dealer'
                break
            elif dealer.value > 21 and player.value < 21:
                state='player'
                break
            else:
                pass

        msg = "```\n"
        msg += "Dealer:\n" + " ".join(list(x.show() for x in dealer.hand)) + f" ({dealer.value})\n\n" 
        msg += f"{interaction.author.display_name}:\n" + " ".join(list(x.show() for x in player.hand)) + f" ({player.value})"
        msg += "\n```"

        if state == 'player':
            msg += f'\n{interaction.author.display_name} Wins!'
            msg += f'\n+{bet}'
            cursor.execute(f"UPDATE Users SET balance = {bal[0]+bet} WHERE id = {interaction.author.id}")
            cursor.execute(f"UPDATE Users SET bjwin = bjwin + 1 WHERE id = {interaction.author.id}")
        elif state == 'dealer':
            msg += f'\nHitoha Wins!'
            msg += f'\n-{bet}'
            cursor.execute(f"UPDATE Users SET balance = {bal[0]-bet} WHERE id = {interaction.author.id}")
            cursor.execute(f"UPDATE Users SET bjloss = bjloss + 1 WHERE id = {interaction.author.id}")
        elif state == 'tie':
            msg += "\nGame ended in a tie!"

        
        await message.edit(content=msg)
        connection.commit()
        cursor.close()
        connection.close()


async def setup(bot):
    await bot.add_cog(Games(bot))