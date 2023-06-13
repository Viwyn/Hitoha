import discord
from discord.ext import commands
import requests
import random
import typing

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Rule34", description="Gets a Rule34 image")
    async def rule34(self, ctx, count: typing.Optional[int] = 1, *tags):
        if "18+" not in list(role.name for role in ctx.author.roles) and ctx.author.id != 241138170610188288:
            return await ctx.send("You do not have the 18+ role.")
        
        if count > 15:
            return await ctx.send("Amount cannot be more than 15 at a time")

        url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"

        payload = {"limit": 30, "tags": " ".join(tags), "json": 1}

        response = requests.get(url, params=payload)

        try:
            response.json()
        except requests.JSONDecodeError as e:
            return await ctx.reply("There was an error with the search, try again with different tags")


        for post in random.sample(response.json(), count):
            tags = list("`" + tag + "`" for tag in post["tags"].split(" "))

            embed = discord.Embed(title="__Details__", color=discord.Color.random())

            embed.set_image(url=post["file_url"])
            embed.set_author(name="Rule34", url=post["file_url"])
            embed.set_thumbnail(url=post["preview_url"])

            embed.add_field(name="__**Tags**__", value=(" ".join(tags[:15]) + f"..and {len(tags) - 15} more." if len(tags)>15 else " ".join(tags[:15])), inline=False)
            embed.add_field(name="__**ID**__", value=post["id"])
            embed.add_field(name="__**Rating**__", value=post["rating"].capitalize(), inline=True)

            embed.set_footer(icon_url=ctx.author.display_avatar, text=f"Requested by: {ctx.author.display_name}")

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NSFW(bot))
