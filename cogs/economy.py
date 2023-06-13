import discord
from discord.ext import commands
import mysql.connector
from mysql.connector import Error
from os import getenv

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal"], description="Shows the balance of the user")
    async def balance(self, ctx, user: discord.User = None):
        if user == None:
            user = ctx.author

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
                    print(f"Created value for user {user.display_name}")
                    cursor.execute(f"SELECT * FROM Users WHERE id = {id}")
                    record = cursor.fetchone()

                await ctx.send(f"{user.display_name}'s balance: {record[1]}")

        except Error as e:
            await ctx.send(f"Error, {e}")

        finally:
            if connection.is_connected():
                connection.commit()
                cursor.close()
                connection.close()

    @commands.command(name="addbalance", aliases=["addbal"], description="Adds a user's balance", hidden=True)
    @commands.is_owner()
    async def addbalance(self, ctx, user: discord.User, amount:int):
        if user == None:
            user = ctx.author

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

                ori = 0

                if record == None:
                    ori = 1000
                    cursor.execute(f"INSERT INTO Users VALUES ({id}, {1000})")
                    print(f"Created value for user {user.display_name}")
                
                cursor.execute(f"SELECT balance FROM Users WHERE id = {id}")
                ori += cursor.fetchone()[0]
                cursor.execute(f"UPDATE Users SET balance = '{amount+ori}' WHERE `Users`.`id` = {id};")
                await ctx.send(f"Added {amount} to {user.display_name}")

        except Error as e:
            await ctx.send(f"Error, {e}")

        finally:
            if connection.is_connected():
                connection.commit()
                cursor.close()
                connection.close()

    @commands.command(name="setbalance", aliases=["setbal"], description="Setss a user's balance", hidden=True)
    @commands.is_owner()
    async def setbalance(self, ctx, user: discord.User, amount:int):
        if user == None:
            user = ctx.author

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
                    cursor.execute(f"INSERT INTO Users VALUES ({id}, {1000})")
                    print(f"Created value for user {user.display_name}")
                
                cursor.execute(f"SELECT balance FROM Users WHERE id = {id}")
                ori += cursor.fetchone()[0]
                cursor.execute(f"UPDATE Users SET balance = '{amount}' WHERE `Users`.`id` = {id};")
                await ctx.send(f"Set {user.display_name}'s balance to {amount}")

        except Error as e:
            await ctx.send(f"Error, {e}")

        finally:
            if connection.is_connected():
                connection.commit()
                cursor.close()
                connection.close()

async def setup(bot):
    await bot.add_cog(Economy(bot))