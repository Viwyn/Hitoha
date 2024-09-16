import discord
from discord.ext import commands

from datetime import datetime
from json import dumps

from requests import get

class Wynn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wynnstats", description="Get the stats of the player in Wynncraft")
    async def wynnstats(self, ctx, username):
        wynn_api_url = "https://api.wynncraft.com/v3/player/"

        player_data = get(wynn_api_url + username + "?fullResult").json()
        head_url = "https://mc-heads.net/avatar/" + player_data['uuid']

        char_data = player_data['characters'][player_data['activeCharacter']]

        embed = discord.Embed(title=player_data['username'],
                        url="https://wynncraft.com/stats/player/" + player_data['uuid'],
                        colour=discord.Color(int(player_data['legacyRankColour']['main'][1:], 16)) if player_data['legacyRankColour'] else discord.Colour.light_gray(),
                        description=f"**Rank**: {player_data['supportRank'].capitalize() if player_data['supportRank'] else "None"} \n**Playtime**: {player_data['playtime']}h \n**Guild**: {player_data['guild'] if player_data['guild'] else "None"} \n**Online**: {str(player_data['online'])} \n**Server**: {player_data['server']}",
                        timestamp=datetime.now())

        embed.set_author(name="Wynncraft Stats",
                    url="https://wynncraft.com/",
                    icon_url="https://styles.redditmedia.com/t5_2wcp4/styles/communityIcon_mya835x0wmod1.png")

        profession_levels = ""

        for profession, level in char_data['professions'].items():
            profession_levels += f"**{profession.capitalize()}**: {level['level']} ({level['xpPercent']}%)\n"

        embed.add_field(name="__**Active Character**__",
                value=f"**Type**: {char_data['type'].capitalize()} \n**Combat**: {char_data['level']} ({char_data['xpPercent']}%) \n{profession_levels}",
                inline=False)

        embed.set_thumbnail(url=head_url)

        embed.set_footer(text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="howfarisriricomparedto", description="Compares the levels of the player to riri")
    async def howfarisriricomparedto(self, ctx, username):
        wynn_api_url = "https://api.wynncraft.com/v3/player/"

        riri_data = get(wynn_api_url + "riaru" + "?fullResult").json()
        riri_char_data = riri_data['characters'][riri_data['activeCharacter']]

        player_data = get(wynn_api_url + username + "?fullResult").json()
        player_char_data = player_data['characters'][player_data['activeCharacter']]

        embed = discord.Embed(colour=discord.Color(int(player_data['legacyRankColour']['main'][1:], 16)) if player_data['legacyRankColour'] else discord.Colour.light_gray(),
                        description=f"__**Comparing {riri_data['username']} to {player_data['username']}**__",
                        timestamp=datetime.now())
        
        embed.set_author(name="Wynncraft Stats",
                    url="https://wynncraft.com/",
                    icon_url="https://styles.redditmedia.com/t5_2wcp4/styles/communityIcon_mya835x0wmod1.png")

        profession_names = ""
        riri_profession_levels = ""
        player_profession_levels = ""

        for profession, level in riri_char_data['professions'].items():
            profession_names += f"**{profession.capitalize()}**:\n"
            riri_profession_levels += f"{level['level']}\n"

        for profession, level in player_char_data['professions'].items():
            player_profession_levels += f"{level['level']}\n"

        embed.add_field(name=f"__**Levels**__",
                value=f"**Type**: \n**Combat**: \n{profession_names}",
                inline=True)
        
        embed.add_field(name=f"__**{riri_data['username']}**__",
                value=f"{riri_char_data['type'].capitalize()} \n{riri_char_data['level']} \n{riri_profession_levels}",
                inline=True)
        
        embed.add_field(name=f"__**{player_data['username']}**__",
                value=f"{player_char_data['type'].capitalize()} \n{player_char_data['level']} \n{player_profession_levels}",
                inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Wynn(bot))