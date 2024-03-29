import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as DateFormatter
import numpy as np
from datetime import datetime
from io import BytesIO

class Expenses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tabulate", description="Calculate expenses in the channel.")
    @app_commands.choices(hidden=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=0)
        ])
    async def slash_tabulate(self, interaction:discord.Interaction, hidden:Optional[app_commands.Choice[int]]):
        if not isinstance(interaction.channel, discord.Thread):
            return await interaction.response.send_message("This command is only available in threads, create a thread and run the command again.")
        await interaction.response.defer(ephemeral=False if not hidden else bool(hidden.value))

        chat_history = [message async for message in interaction.channel.history(limit=None, oldest_first=True) if message.author == self.bot.user and message.embeds]
        
        income = 0
        expense = 0
        type_count = {
            "Food": 0,
            "Bills": 0,
            "Shopping": 0,
            "Personal Care": 0,
            "Entertainment": 0,
            "Others": 0,
        }
        date_count = {}

        for msg in chat_history:
            for embed in msg.embeds:
                data = embed.to_dict()

                if "title" not in data or data["title"] != "Expenses" or data["author"]["name"] != interaction.user.name:
                    continue

                if data["fields"][0]["value"] == "Spending":
                    value = abs(float(data["fields"][1]["value"]))
                    expense += value
                    type_count[data["fields"][3]["value"]] += value
                    date = datetime.strptime(data["footer"]["text"].split(" ")[1], '%d/%m/%Y')
                    if date in date_count:
                        date_count[date] += value
                    else:
                        date_count[date] = value
                else:
                    income += abs(float(data["fields"][1]["value"]))

        if expense == 0:
            return await interaction.followup.send("Apologies, I was unable to find your expenses in this thread. Please use the `expense` command to keep track of your expenses.")

        #creating pie chart
        data_stream_pie = BytesIO()

        chart_data = {k:v for k, v in type_count.items() if v != 0}

        data = np.array(list(chart_data.values()))
        labels = list(chart_data.keys())
        # explode = tuple(0.1 for key in chart_data.keys())
        explode = tuple(0 for key in chart_data.keys())

        fig, ax = plt.subplots(figsize=(7, 3.5))

        def data_display(x):
            return '{:.1f}%\n({:.2f})'.format(x, expense*x/100)

        patches, texts, pcts = ax.pie(data, labels=labels, explode=explode, shadow=True, pctdistance=0.7, autopct=data_display, textprops={'size': 'large'}, startangle=90)

        plt.setp(pcts, color='white')
        plt.setp(texts, fontweight=600, color='white')

        ax.set_title(f"Expenses data for {interaction.user.name.capitalize()}", fontsize=20, color='white')
        plt.legend(title="Categories", bbox_to_anchor=(1.75, 1), loc='upper right', borderaxespad=0)

        plt.savefig(data_stream_pie, format="png", transparent=True)
        plt.close()

        data_stream_pie.seek(0)
        chart = discord.File(data_stream_pie, filename="pie_chart.png")

        #embed for pie chart
        embed_pie = discord.Embed(title=f"Expenses data for {interaction.user.name.capitalize()}", 
                                color=discord.Color.random())

        embed_pie.add_field(name="__Income__", value="+" + "{:.2f}".format(income))
        embed_pie.add_field(name="__Expense__", value="-" + "{:.2f}".format(expense))
        embed_pie.add_field(name="__Net__", value="{:.2f}".format(income-expense), inline=False)
        
        embed_pie.set_image(url="attachment://pie_chart.png")

        embed_pie.set_footer(text=f"Date requested: {interaction.created_at.strftime('%d/%m/%Y')}", icon_url=interaction.user.display_avatar.url)
        
        #ploting line graph
        data_stream_graph = BytesIO()

        sorted_dates = dict((key, value) for key, value in sorted(date_count.items(), key=lambda x: x[0]))

        plt.plot_date(sorted_dates.keys(), sorted_dates.values(), 'b')
        
        #formatting x axis labels
        date_format = DateFormatter.DateFormatter('%d/%m')
        plt.gca().xaxis.set_major_formatter(date_format)

        plt.xlabel("Date")
        plt.ylabel("Amount Spent")
        plt.title("Amount Spent per Day")
        plt.xticks(rotation=50)

        plt.savefig(data_stream_graph, format="png")
        plt.close()

        data_stream_graph.seek(0)
        graph = discord.File(data_stream_graph, filename="line_graph.png")

        #embed for chart
        embed_chart = discord.Embed(color=discord.Color.random())

        embed_chart.set_image(url="attachment://line_graph.png")

        #send reply to command
        await interaction.followup.send(content="Ok here is the data", embeds=[embed_pie, embed_chart], files=[chart, graph], ephemeral=False if not hidden else bool(hidden.value))

    @app_commands.command(name="expense", description="Add a expense to the channel")
    @app_commands.describe(method="Method of payment")
    @app_commands.describe(amount="Amount that was spent/gained")
    @app_commands.describe(reason="Reason for transaction")
    @app_commands.describe(date="Date of expense (dd/mm/yyyy)")
    @app_commands.describe(notes="Additional things to note.")
    @app_commands.choices(method=[
        app_commands.Choice(name="Cash", value=0),
        app_commands.Choice(name="Card", value=1),
        app_commands.Choice(name="E-Wallet", value=2),
    ])
    @app_commands.choices(exp_type=[
        app_commands.Choice(name="Spending", value=-1),
        app_commands.Choice(name="Gaining", value=1),
    ])
    @app_commands.choices(reason=[
        app_commands.Choice(name="Food", value="food"),
        app_commands.Choice(name="Bills", value="bills"),
        app_commands.Choice(name="Shopping", value="shopping"),
        app_commands.Choice(name="Personal Care", value="care"),
        app_commands.Choice(name="Entertainment", value="entertainment"),
        app_commands.Choice(name="Others", value="others"),
    ])
    async def slash_expense(
        self, 
        interaction:discord.Interaction, 
        amount:app_commands.Range[float, 0, None], 
        exp_type:app_commands.Choice[int], 
        method:app_commands.Choice[int], 
        reason:app_commands.Choice[str],
        date:Optional[str],
        notes:Optional[str]
        ):
        if not isinstance(interaction.channel, discord.Thread):
            return await interaction.response.send_message("This command is only available in threads, create a thread and run the command again.")
        
        await interaction.response.defer()

        if date:
            try:
                dateoftrans = datetime.strptime(date, "%d/%m/%Y").date()
            except ValueError:
                return await interaction.followup.send("Error, entered date was not valid")
        else:
            dateoftrans = interaction.created_at.date()

        embed = discord.Embed(title=f"Expenses", 
                                color=discord.Color.green() if exp_type.value > 0 else discord.Color.red(),
        )

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name="**__Type__**", value=exp_type.name, inline=False)
        embed.add_field(name="**__Amount__**", value="{:.2f}".format(amount*exp_type.value))
        embed.add_field(name="**__Payment Method__**", value=method.name)
        embed.add_field(name="**__Reason__**", value=reason.name, inline=False)

        if notes:
            embed.add_field(name="**__Notes__**", value=notes, inline=False)
        
        embed.set_footer(text=f"Date: {dateoftrans.strftime('%d/%m/%Y')}")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Expenses(bot))
