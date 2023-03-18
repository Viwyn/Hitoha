import discord
from discord.ext import commands
from discord.ui import View

class PfpView(View):
    def __init__(self, embed, embed0):
        super().__init__(timeout = 10)
        self.embed = embed
        self.embed0 = embed0

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Personal Profile Picture", custom_id="personal", disabled=True)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        otherButton = [x for x in self.children if x.custom_id == "server"][0]
        if (otherButton.style == discord.ButtonStyle.success):
            otherButton.disabled = False
            button.disabled = True
            
        await interaction.response.edit_message(embed = self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="server")
    async def server_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        for child in self.children:
            if child is discord.ui.Button:
                child.disabled = True

    #button0 = discord.ui.Button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="pfpbutton0")

class Avatar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
    aliases=['avatar'], 
    description="Gets the profile picture of the user, defaults to author if no user is specified.", 
    brief="Gets a profile picture.",
    case_insensitive=True)
    async def pfp(self, interaction: discord.Interaction, user:discord.User = None):
    
        if user == None:
            user = interaction.author
    
        name = user.display_name
    
        if (user.accent_color):
            embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.from_rgb(user.accent_color.r, user.accent_color.g, user.accent_color.b))
        else:
            embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.random())
    
        embed.set_footer(text= f"Requested by {interaction.author.display_name}", icon_url=interaction.author.display_avatar.url)
    
        embed0 = embed.copy()
    
        if user.avatar:
            embed.set_image(url=user.avatar.url)
        else:
            embed.set_image(url=user.default_avatar.url)
    
        
        member = await interaction.guild.fetch_member(user.id)
    
        if member.guild_avatar != None:
            embed0.set_image(url=member.guild_avatar.url)
        else:
            embed0 = None
    
        view = PfpView(embed=embed, embed0=embed0)
    
        await interaction.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Avatar(bot))