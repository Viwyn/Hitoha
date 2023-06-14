import discord
from discord.ext import commands
from os import getenv
import requests
import langcodes

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def translate(self, text, to_lang):
        key = getenv("AZURETRANS")
        url = "https://api.cognitive.microsofttranslator.com/translate"
        location = "southeastasia"

        params = {
            'api-version': '3.0',
            'to': [to_lang]
        }

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
            lang = "in"
        elif reaction.emoji == "🇨🇳":
            lang = "zh"
        elif reaction.emoji == "🇩🇪":
            lang = "de"
        elif reaction.emoji == "🇷🇺":
            lang = "ru"

        if lang:
            response = self.translate(reaction.message.content, lang)

            ori_lang = response[0]['detectedLanguage']['language']
            translation = response[0]['translations'][0]['text']

            embed = discord.Embed(title=f"__{self.getLangName(ori_lang, lang)} → {self.getLangName(lang, lang)}__", 
                                color=discord.Color.random(),
                                description=f"### {translation}")

            embed.set_author(icon_url="https://connectoricons-prod.azureedge.net/releases/v1.0.1623/1.0.1623.3210/microsofttranslator/icon.png",
                            name="Translator")
            
            embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar)

            await reaction.message.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(Translate(bot))

