import discord
from discord.ext import commands
import requests
import random
import typing
from os import getenv

class Image(commands.Cog):
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

    @commands.command()
    async def sauce(self, ctx, imgurl: typing.Optional[str] = None, similarityreq: typing.Optional[int] = 75):
        if imgurl == None and len(ctx.message.attachments) == 0:
            return await ctx.send("Please provide a link or an attachment")
        
        if ctx.message.attachments and not imgurl:
            imgurl = ctx.message.attachments[0].url

        url = "https://saucenao.com/search.php?"
        params = {"numres": 5, "db": 999, "api_key": getenv("SAUCENAO"), "output_type": 2, "url": imgurl}

        response = requests.get(url, params=params)

        results = list(result for result in response.json()["results"])
        results.sort(key=lambda x: x["header"]["similarity"], reverse=True)

        embed = discord.Embed(title="__**Details**__", color=discord.Color.random())
        embed.set_thumbnail(url=imgurl)
        embed.set_author(name="SauceNAO",url="https://saucenao.com/", icon_url="https://i.altapps.net/icons/saucenao-43064.png")

        for result in results:
            try:
                index_name = result["header"]["index_name"].split(": ")[1].split(" - ")[0]
                similarity = result["header"]["similarity"]

                if float(similarity) < similarityreq:
                    continue

                details = ""

                if result["header"]["index_id"] in [9, 25]:
                    details += f"**Creator**: `{result['data']['creator']}`\n"
                    details += f"**Material**: `{result['data']['material']}`\n"
                    details += f"**Characters**: `{result['data']['characters']}`\n"
                elif result["header"]["index_id"] in [5, 6]:
                    details += f"**Artist**: `{result['data']['member_name']}`\n"
                    details += f"**Title**: `{result['data']['title']}`\n"

                links = list("[Source](" + link + ")" for link in result['data']['ext_urls'])
            except KeyError as e:
                print(f"Key Error! - {result}")
                continue

            embed.add_field(name=f"__{index_name} [{similarity}%]__", 
                            value=f"{details}" + "\n".join(links))

        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Image(bot))
