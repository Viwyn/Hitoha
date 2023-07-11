import discord
from discord.ext import commands
from discord.ui import View
from discord import app_commands
from typing import Optional

class PfpView(View):
    def __init__(self, embed, embed0):
        super().__init__(timeout = 10)
        self.embed = embed
        self.embed0 = embed0

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Personal Profile Picture", custom_id="personal", disabled=True)
    async def button_callback(self, ctx, button: discord.ui.Button):
        otherButton = [x for x in self.children if x.custom_id == "server"][0]
        if (otherButton.style == discord.ButtonStyle.success):
            otherButton.disabled = False
            button.disabled = True
            
        await ctx.response.edit_message(embed = self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="server")
    async def server_button_callback(self, ctx, button: discord.ui.Button):
        if (self.embed0 == None):
            button.label = "Not Found"
            button.style = discord.ButtonStyle.danger
            button.disabled = True
            await ctx.response.edit_message(view=self)
        else:
            otherButton = [x for x in self.children if x.custom_id == "personal"][0]
            otherButton.disabled = False
            button.disabled = True
            await ctx.response.edit_message(embed = self.embed0, view=self)

    async def on_timeout(self):
        for child in self.children:
            if child is discord.ui.Button:
                child.disabled = True

    #button0 = discord.ui.Button(style=discord.ButtonStyle.success, label="Server Profile Picture", custom_id="pfpbutton0")

class Profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
    aliases=['avatar'], 
    description="Gets the profile picture of the user, defaults to author if no user is specified.", 
    brief="Gets a profile picture.",
    case_insensitive=True)
    async def pfp(self, ctx, user:discord.User = None):
    
        if user == None:
            user = ctx.author
    
        name = user.display_name
    
        if (user.accent_color):
            embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.from_rgb(user.accent_color.r, user.accent_color.g, user.accent_color.b))
        else:
            embed = discord.Embed(title = f"Showing avatar for __{name}__", color=discord.Color.random())
    
        embed.set_footer(text= f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    
        embed0 = embed.copy()
    
        if user.avatar:
            embed.set_image(url=user.avatar.url)
        else:
            embed.set_image(url=user.default_avatar.url)
    
        
        member = await ctx.guild.fetch_member(user.id)
    
        if member.guild_avatar != None:
            embed0.set_image(url=member.guild_avatar.url)
        else:
            embed0 = None
    
        view = PfpView(embed=embed, embed0=embed0)
    
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="profile", description="Gets the profile details of a user")
    @app_commands.describe(member="Specify a user")
    async def slash_profile(self, interaction:discord.Interaction, member:Optional[discord.Member] = None):
        await interaction.response.defer()

        if not member:
            member =  interaction.user

        user = await self.bot.fetch_user(member.id)
        
        #creating embed
        embed = discord.Embed(color=user.accent_color if user.accent_color else discord.Color.random(), title="**Profile Details**")
        if user.avatar: #setting thumbnail
            embed.set_thumbnail(url=user.avatar.with_size(256).url)
        else:
            embed.set_thumbnail(url=user.default_avatar.with_size(256).url)

        embed.set_author(name=user.name, icon_url=user.display_avatar.with_size(128).url)

        #names
        embed.add_field(name="__Username__", value=user.name)
        if user.global_name != user.name:
            embed.add_field(name="__Display Name__", value=user.global_name)
        if member.nick:
            embed.add_field(name="__Server Nickname__", value=member.nick, inline=False)

        #mentions
        embed.add_field(name="__Mention__", value=user.mention, inline=False)

        #adding id
        embed.add_field(name="__ID__", value=f"```java\n{user.id}```", inline=False)

        #dates
        embed.add_field(name="__Date Account Created__", value=f"<t:{int(user.created_at.timestamp())}>")
        embed.add_field(name="__Date Joined Server__", value=f"<t:{int(member.joined_at.timestamp())}>")

        #roles
        roles = list(role.mention for role in member.roles)
        embed.add_field(name="__Roles__", value=" ".join(roles), inline=False)

        if user.banner: #adding banner
            embed.set_image(url=user.banner.url)

        await interaction.followup.send(content="", embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))