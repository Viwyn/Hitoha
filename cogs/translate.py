import discord
from discord.ext import commands
from os import getenv
import requests
import langcodes
from discord import app_commands
from typing import Optional

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def translate(self, text, to_lang, from_lang = None):
        key = getenv("AZURETRANS")
        url = "https://api.cognitive.microsofttranslator.com/translate"
        location = "southeastasia"

        params = {
            'api-version': '3.0',
            'to': [to_lang]
        }

        if from_lang:
            params['from'] = from_lang

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
        }

        body = [{
            'text': text
        }]

        request = requests.post(url, params=params, headers=headers, json=body)
        return(request.json())
    
    def getLangName(self, lang: str, tolang: str):
        return(f"{langcodes.Language.get(lang).display_name(tolang)}({lang.upper()})")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        lang = None

        if reaction.emoji == "🇺🇸":
            lang = "en"
        elif reaction.emoji == "🇯🇵":
            lang = "ja"
        elif reaction.emoji == "🇰🇷":
            lang = "ko"
        elif reaction.emoji == "🇮🇩":
            lang = "id"
        elif reaction.emoji == "🇨🇳":
            lang = "zh"
        elif reaction.emoji == "🇩🇪":
            lang = "de"
        elif reaction.emoji == "🇷🇺":
            lang = "ru"

        if lang and not user.bot:
            reacted = [user async for user in reaction.users()]
            if self.bot.user in reacted:
                return
            response = self.translate(reaction.message.content, lang)

            ori_lang = response[0]['detectedLanguage']['language']
            translation = response[0]['translations'][0]['text']

            embed = discord.Embed(title=f"__{self.getLangName(ori_lang, lang)} → {self.getLangName(lang, lang)}__", 
                                color=discord.Color.random(),
                                description=f"{translation}")

            embed.set_author(icon_url="https://connectoricons-prod.azureedge.net/releases/v1.0.1623/1.0.1623.3210/microsofttranslator/icon.png",
                            name="Translator")
            
            embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar)

            await reaction.message.add_reaction(reaction.emoji)
            await reaction.message.reply(embed=embed, mention_author=False)


    @app_commands.command(name="translate", description="Translates text")
    @app_commands.choices(ori_lang=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Chinese", value="zh"),
        app_commands.Choice(name="Japanese", value="ja"),
        app_commands.Choice(name="Korean", value="ko"),
        app_commands.Choice(name="Indonesian", value="id"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Russian", value="ru"),        
    ])
    @app_commands.choices(to_lang=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Chinese", value="zh"),
        app_commands.Choice(name="Japanese", value="ja"),
        app_commands.Choice(name="Korean", value="ko"),
        app_commands.Choice(name="Indonesian", value="id"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Russian", value="ru"),        
    ])
    async def slash_translate(self, interaction:discord.Interaction, ori_lang:Optional[app_commands.Choice[str]], to_lang:app_commands.Choice[str], msg:str):
        response = self.translate(msg, to_lang.value, ori_lang)

        ori_lang = response[0]['detectedLanguage']['language']
        translation = response[0]['translations'][0]['text']

        await interaction.response.send_message(f"### __Translated__\n{interaction.user.mention}: {translation}", allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(Translate(bot))

