"""
Facilitates diet tracking and metrics
"""

import pymongo
import time
from typing import Optional
from tempfile import NamedTemporaryFile
from discord.ext import commands
from discord.commands import (
        SlashCommandGroup, 
        ApplicationContext
        )
from discord.ui import Modal
from discord import Option
import discord
import matplotlib.pyplot as plt
import numpy as np

class NomModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = kwargs.get("title", "Document your meal")
        self.add_item(discord.ui.InputText(label="Net Calories for this meal", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Protein", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Lunch, Breakfast, Dinner?", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Describe the meal if you want.", style=discord.InputTextStyle.long))
        self.val0 = None
        self.val1 = None
        self.val2 = None
        self.val3 = None

    async def callback(self, interaction: discord.Interaction):
        try:
            self.val0 = self.children[0].value
            self.val1 = self.children[1].value
        except Exception as e:
            print(e)
        if self.val0 is None:
            await interaction.response.send_message("Calories is required", ephemeral=True)
            return
        embed = discord.Embed(title="NomNomNom")
        embed.add_field(name="cals: ", value=self.val0)
        if self.val1 is not None:
            embed.add_field(name="protein: ", value=self.val1)
        if self.val2 is not None:
            embed.add_field(name="meal: ", value=self.val2)
        if self.val3 is not None:
            embed.add_field(name="description: ", value=self.val3)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        # call stop to close the modal
        self.stop()

class NomCog(commands.Cog):
    """CONSUME"""
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient()
        self.db = self.mongo_client["nom_db"]

    Consume = SlashCommandGroup("nom", "EAT")
    @Consume.command(name="nom", description="EAT")
    async def nom(self, ctx: ApplicationContext):
        """Log a meal"""
        chat = NomModal(title="Consumption")
        await ctx.send_modal(chat)
        await chat.wait()
        cals_val = chat.val0
        protein_val = chat.val1
        meal_type = chat.val2
        meal_sum = chat.val3
        if cals_val is None:
            await ctx.send("Please fill out cals")
            return
        try:
            cals_val = int(cals_val)
        except Exception as e:
            print(e)
            await ctx.send("Please enter a number for cals")
            return
        if protein_val is not None:
            try:
                protein_val = int(protein_val)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for protein")
                return
        if meal_type is not None:
            try:
                meal_type = int(meal_type)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for meal type")
                return
        if meal_sum is not None:
            try:
                meal_sum = str(meal_sum)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a string for meal sum")
                return
        # log it make a func
        try:
            self.log_meal(usr=ctx.author.name, cals=cals_val, protein=protein_val, meal_type=meal_type, meal_sum=meal_sum)
        except Exception as e:
            print(e)
            await ctx.send("Failed to log meal")
            return

    def log_meal(self, usr: str, cals:int, protein:Optional[int], meal_type:Optional[int], meal_sum: Optional[str]):
        # get date for column
        date = time.strftime("%Y_%m_%d")
        time_of_day = time.strftime("%H:%M:%S")
        unix_time = time.time()
        collist = self.db.list_collection_names()
        if date in collist:
          print("The collection exists.")
        else:
            print("Creating collection")
            self.db.create_collection(date)
        log = {}
        log["user"] = usr
        log["cals"] = cals
        log["time_of_day"] = time_of_day
        log["unix_time"] = unix_time
        log["date"] = date
        if protein is not None:
            log["protein"] = protein
        if meal_type is not None:
            log["meal_type"] = meal_type
        if meal_sum is not None:
            log["meal_sum"] = meal_sum
        # log it
        self.db[date].insert_one(log)

    def get_users_meals(self, usr: str):
        # get date for column
        date = time.strftime("%Y_%m_%d")
        collist = self.db.list_collection_names()
        if date in collist:
          print("The collection exists.")
        else:
            print("Creating collection")
            self.db.create_collection(date)
        # get meals
        meals = self.db[date].find({"user": usr})
        # sort meals by unix time
        meals = meals.sort("unix_time", 1)
        return meals
    
    @Consume.command(name="show_noms", description="what have I eaten")
    async def show_noms(self, ctx: ApplicationContext):
        """Show what you've eaten"""
        await ctx.defer()
        usr = ctx.author.name
        # get meals
        meals = self.get_users_meals(usr)
        if meals is None:
            return None
        charted = plt.figure()
        ax = charted.add_subplot(111)
        ax.set_title("Calories Consumed")
        ax.set_xlabel("Meal")
        ax.set_ylabel("Calories")
        y = np.array([])
        # plot the meals
        count = 1
        total_cals = 0
        for meal in meals:
            try:
                cals = int(meal["cals"])
                total_cals += cals
                y = np.append(y, total_cals)
            except Exception as e:
                print(e)
                return None
        for meal in y:
            print(meal)
        # plot the target
        ax.axhline(y=self.get_cal_target(usr), color="r", linestyle="-", label="target")
        # plot the meals
        ax.plot(y, color="b", linestyle="-", label="meals")
        # set y axis min max
        ax.set_ylim(bottom=0, top=6000)
        # set x axis min max
        ax.set_xlim(left=0, right=10)
        # fill the area beneath the curve
        ax.fill_between(np.arange(0, len(y)), y, color="b", alpha=0.3)
        # set the legend
        ax.legend()
        # save the chart
        with NamedTemporaryFile(suffix=".png") as f:
            charted.savefig(f.name)
            await ctx.followup.send(file=discord.File(f.name))
        # get rid of the chart
        plt.close(charted)

    @Consume.command(name="set_cal_target", description="Daily Calorie Target",
                    options=[Option(input_type=int, name="target", 
                                   description="daily caloric target", 
                                   required=True)])
    async def set_cal_target(self, ctx: ApplicationContext, target: int):
        """Set your daily calorie target"""
        await ctx.defer()
        # set column to be the username + target
        collist = self.db.list_collection_names()
        if not ctx.author.name + "_target" in collist:
            self.db.create_collection(ctx.author.name + "_target")
        # log it
        self.db[ctx.author.name + "_target"].insert_one({"user": ctx.author.name, "target": target, "date": time.time()})
        await ctx.followup.send("Calorie target set to " + str(target) + " calories for " + ctx.author.name)

    def get_cal_target(self, usr: str):
        collist = self.db.list_collection_names()
        if not usr + "_target" in collist:
            print("No target set")
            return 0
        else:
            # get the most recent target
            target = self.db[usr + "_target"].find({"user": usr}).sort("date", -1).limit(1)[0]["target"]
            try:
                target = int(target)
            except Exception as e:
                print(e)
                return 0
            return target

def setup(bot):
    """Add the cog to the bot"""
    bot.add_cog(NomCog(bot))
