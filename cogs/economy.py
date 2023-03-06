import discord
from discord.ext import commands
import mysql.connector
from mysql.connector import Error
from os import getenv

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", help="Shows the balance of the user")
    async def balance(self, interaction: discord.Interaction, user: discord.User = None):
        if user == None:
            user = interaction.author

        id = user.id

        try:
            connection = mysql.connector.connect(host=getenv("DBHOST"),
                                                port=getenv("DBPORT"),
                                                database=getenv("DBNAME"),
                                                user=getenv("DBUID"),
                                                password=getenv("DBPW"))
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM Users WHERE id = {id}")
                record = cursor.fetchone()

                if record == None:
                    cursor.execute(f"INSERT INTO Users VALUES ({id}, 1000)")
                    cursor.execute(f"SELECT * FROM Users WHERE id = {id}")
                    record = cursor.fetchone()

                await interaction.send(f"{user.display_name}'s balance: {record[1]}")

        except Error as e:
            await interaction.send(f"Error, {e}")

        finally:
            if connection.is_connected():
                connection.commit()
                cursor.close()
                connection.close()

async def setup(bot):
    await bot.add_cog(Economy(bot))