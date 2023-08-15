"""
Facilitates diet tracking and metrics
"""

import pymongo
import time
from typing import Optional, Any, Dict, List
from tempfile import NamedTemporaryFile
from discord.ext import commands
from discord.commands import (
        SlashCommandGroup, 
        ApplicationContext
        )
from bson.binary import Binary
from discord.ui import Modal
from discord import Option
import discord
import matplotlib.pyplot as plt
import numpy as np

class Meal:
    def __init__(self, mongo_cursor: Optional[Any]) -> None:
        if mongo_cursor is None:
            self.unix_time = time.time()
            self.date = time.strftime("%Y_%m_%d")
            self.time_of_day = time.strftime("%H:%M:%S")
            self.user = ""
            self.cals = 0
            self.protein = 0
            self.meal_type = ""
            self.meal_sum = ""
        else:
            self.unix_time = float(mongo_cursor["unix_time"])
            self.date = str(mongo_cursor["date"])
            self.time_of_day = str(mongo_cursor["time_of_day"])
            self.user = str(mongo_cursor["user"])
            self.cals = int(mongo_cursor["cals"])
            self.protein = int(mongo_cursor["protein"])
            self.meal_type = str(mongo_cursor["meal_type"])
            self.meal_sum = str(mongo_cursor["meal_sum"])

    def __str__(self) -> str:
        string = ""
        string += "user: " + self.user + "\n"
        string += "cals: " + str(self.cals) + "\n"
        string += "protein: " + str(self.protein) + "\n"
        string += "meal_type: " + self.meal_type + "\n"
        string += "meal_sum: " + self.meal_sum + "\n"
        return string

class WeighIn:
    def __init__(self, mongo_cursor: Optional[Any]) -> None:
        if mongo_cursor is None:
            self.unix_time = time.time()
            self.date = time.strftime("%Y_%m_%d")
            self.time_of_day = time.strftime("%H:%M:%S")
            self.user = ""
            self.weight = 0
            self.mood = 0
            self.mood_sum = ""
        else:
            self.unix_time = float(mongo_cursor["unix_time"])
            self.date = str(mongo_cursor["date"])
            self.time_of_day = str(mongo_cursor["time_of_day"])
            self.user = str(mongo_cursor["user"])
            self.weight = int(mongo_cursor["weight"])
            self.mood = int(mongo_cursor["mood"])
            self.mood_sum = str(mongo_cursor["mood_sum"])

    def __str__(self) -> str:
        string = ""
        string += "user: " + self.user + "\n"
        string += "weight: " + str(self.weight) + "\n"
        string += "mood: " + str(self.mood) + "\n"
        string += "mood_sum: " + self.mood_sum + "\n"
        return string

class Targets:
    def __init__(self, mongo_cursor: Optional[Any]) -> None:
        if mongo_cursor is None:
            self.unix_time = time.time()
            self.date = time.strftime("%Y_%m_%d")
            self.time_of_day = time.strftime("%H:%M:%S")
            self.user = ""
            self.cal_target = 0
            self.weight_target = 0
        else:
            self.unix_time = float(mongo_cursor["unix_time"])
            self.date = str(mongo_cursor["date"])
            self.time_of_day = str(mongo_cursor["time_of_day"])
            self.user = str(mongo_cursor["user"])
            self.cal_target = int(mongo_cursor["cal_target"])
            self.weight_target = int(mongo_cursor["weight_target"])

    def __str__(self) -> str:
        string = ""
        string += "user: " + self.user + "\n"
        string += "cal_target: " + str(self.cal_target) + "\n"
        string += "weight_target: " + str(self.weight_target) + "\n"
        return string

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
            self.val2 = self.children[1].value
            self.val3 = self.children[1].value
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

class weigh_in_modal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = kwargs.get("title", "Document your weight.")
        self.add_item(discord.ui.InputText(label="How much do you weigh?", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="How do you feel on a scale of 1-10?", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Describe your mood if you want.", style=discord.InputTextStyle.short))
        self.val0 = None
        self.val1 = None
        self.val2 = None

    async def callback(self, interaction: discord.Interaction):
        try:
            self.val0 = self.children[0].value
            self.val1 = self.children[1].value
            self.val2 = self.children[2].value
        except Exception as e:
            print(e)
        if self.val0 is None:
            await interaction.response.send_message("Weight is required. Fess up loser.", ephemeral=True)
            return
        embed = discord.Embed(title="Weigh In")
        embed.add_field(name="Weight: ", value=self.val0)
        if self.val1 is not None:
            embed.add_field(name="Mood 1-10: ", value=self.val1)
        if self.val2 is not None:
            embed.add_field(name="Mood summary: ", value=self.val2)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        # call stop to close the modal
        self.stop()

class targets_modal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = kwargs.get("title", "Set your fitness goals.")
        self.add_item(discord.ui.InputText(label="How much do you want to weigh?", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="How many calories do you want to eat?", style=discord.InputTextStyle.short))
        self.val0 = None
        self.val1 = None

    async def callback(self, interaction: discord.Interaction):
        try:
            self.val0 = self.children[0].value
            self.val1 = self.children[1].value
        except Exception as e:
            print(e)
        if self.val0 is None:
            await interaction.response.send_message("Weight is required. Fess up loser.", ephemeral=True)
            return
        if self.val1 is None:
            await interaction.response.send_message("Calories is required", ephemeral=True)
            return
        embed = discord.Embed(title="Targets")
        embed.add_field(name="Target Weight: ", value=self.val0)
        embed.add_field(name="Target Calories: ", value=self.val1)
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
        print("nom")
        # create a meal
        meal = Meal(None)
        meal.user = ctx.author.name

        # create a modal for the meal
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
            meal.cals = int(cals_val)
        except Exception as e:
            print(e)
            await ctx.send("Please enter a number for cals")
            return
        if protein_val is not None:
            try:
                meal.protein = int(protein_val)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for protein")
                return
        if meal_type is not None:
            try:
                meal.meal_type = str(meal_type)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for meal type")
                return
        if meal_sum is not None:
            try:
                meal.meal_sum = str(meal_sum)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a string for meal sum")
                return

        # log it
        try:
            self.log_meal(meal)
        except Exception as e:
            print(e)
            await ctx.send("Failed to log meal")
            return

    @Consume.command(name="weigh_in", description="How thick are you")
    async def weigh_in(self, ctx: ApplicationContext):
        """Weigh in"""
        print("weigh_in")
        # create a weigh in
        weigh_in = WeighIn(None)
        weigh_in.user = ctx.author.name

        # create a modal for the weigh in
        chat = weigh_in_modal(title="IT'S TIME TO WEIGH IN")
        await ctx.send_modal(chat)
        await chat.wait()

        weight_val = chat.val0
        mood_val = chat.val1
        mood_sum = chat.val2

        if weight_val is None:
            await ctx.send("Please fill out weight.")
            return
        try:
            weigh_in.weight = int(weight_val)
        except Exception as e:
            print(e)
            await ctx.send("Please enter a number for cals")
            return
        if mood_val is not None:
            try:
                weigh_in.mood = int(mood_val)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for protein")
                return
        if mood_sum is not None:
            try:
                weigh_in.mood_sum = str(mood_sum)
            except Exception as e:
                print(e)
                await ctx.send("Please enter a number for meal type")
                return
        # log it make a func
        try:
            self.log_weigh_in(weigh_in)
        except Exception as e:
            print(e)
            await ctx.send("Failed to log meal")
            return

    def log_meal(self, meal: Meal):
        print("Logging meal")
        collist = self.db.list_collection_names()
        collection_name = "meals"
        if collection_name not in collist:
            print("Creating collection")
            self.db.create_collection(collection_name)
        # log it
        self.db[collection_name].insert_one(meal.__dict__)

    def log_targets(self, target: Targets):
        print("Logging targets")
        collist = self.db.list_collection_names()
        collection_name = "targets"
        if collection_name not in collist:
            print("Creating collection")
            self.db.create_collection(collection_name)
        # log it
        self.db[collection_name].insert_one(target.__dict__)

    def log_weigh_in(self, weigh_in: WeighIn):
        print("Logging weigh in")
        # get date for column
        collist = self.db.list_collection_names()
        collection_name = "weigh_ins"
        if collection_name in collist:
          print("The collection exists.")
        else:
          print("Creating collection")
          self.db.create_collection(collection_name)
        # log it
        self.db[collection_name].insert_one(weigh_in.__dict__)

    def get_users_meals(self, usr: str) -> Optional[List[Meal]]:
        print("Getting meals for " + usr)
        collist = self.db.list_collection_names()
        if not "meals" in collist:
            print("No meals logged")
            return None

        # get the meals sort by unix time
        meals = self.db["meals"].find({"user": usr})
        print(meals)
        meals = meals.sort("unix_time", -1)
        if meals is None:
            print("No meals logged")
            return None

        # convert to list of Meal objects
        meal_list = []
        date = time.strftime("%Y_%m_%d")
        for meal in meals:
            if meal["date"] == date:
                meal_list.append(Meal(meal))
            else:
                break
        return meal_list

    def get_users_weigh_ins(self, usr: str) -> Optional[List[WeighIn]]:
        print("Getting weigh ins for " + usr)
        collist = self.db.list_collection_names()
        if not "weigh_ins" in collist:
            print("No weigh ins logged")
            return None

        # get the meals sort by unix time
        weigh_ins = self.db["weigh_ins"].find({"user": usr})
        weigh_ins = weigh_ins.sort("unix_time", 1)
        if weigh_ins is None:
            print("No weigh_ins logged")
            return None

        # convert to list of Meal objects
        weight_list = []
        for weight in weigh_ins:
            weight_list.append(WeighIn(weight))
        return weight_list
    
    @Consume.command(name="show_noms", description="what have I eaten")
    async def show_noms(self, ctx: ApplicationContext):
        """Show what you've eaten"""
        await ctx.defer()
        print("show_noms")
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
        x = np.array([])

        # set the first point to 0
        x = np.append(x, 0)
        y = np.append(y, 0)
        # plot the meals
        meal_num = 1
        total_cals = 0
        for meal in meals:
            print(meal)
            try:
                total_cals += meal.cals
                y = np.append(y, total_cals)
                x = np.append(x, meal_num)
                meal_num += 1
            except Exception as e:
                print(e)
                return None
        # plot the target
        target = self.get_targets(usr)
        if target is not None:
            ax.axhline(y=target.cal_target, color="r", linestyle="-", label="target")
        # plot the meals
        ax.plot(x, y, color="b", linestyle="-", label="meals")
        # set y axis min max
        ax.set_ylim(bottom=0, top=4000)
        # set x axis min max
        ax.set_xlim(left=x[0], right=len(x))
        # make the x axis labels the meal numbers
        ax.set_xticks(x)
        # fill the area beneath the curve
        ax.fill_between(x, y, 0, color="b", alpha=0.2)
        # set the legend
        ax.legend()
        # save the chart
        with NamedTemporaryFile(suffix=".png") as f:
            charted.savefig(f.name)
            await ctx.followup.send(file=discord.File(f.name))
        # get rid of the chart
        plt.close(charted)

    @Consume.command(name="show_weight_prog", description="Weight Progress")
    async def show_weight_prog(self, ctx: ApplicationContext):
        """gaining or losing represent it as a scatter plot"""
        await ctx.defer()
        print("show_weight_prog")
        usr = ctx.author.name
        # get meals
        weigh_ins = self.get_users_weigh_ins(usr)
        if weigh_ins is None:
            return None
        charted = plt.figure()
        ax = charted.add_subplot(111)
        ax.set_title("Weight Progress")
        ax.set_xlabel("Weigh In")
        ax.set_ylabel("Weight in lbs")
        y = np.array([])
        x = np.array([])
        # plot the meals
        weigh_in_num = 1
        for weigh_in in weigh_ins:
            print(weigh_in)
            try:
                y = np.append(y, weigh_in.weight)
                x = np.append(x, weigh_in_num)
                weigh_in_num += 1
            except Exception as e:
                print(e)
                return None
        # plot the target
        target = self.get_targets(usr)
        if target is not None:
            ax.axhline(y=target.weight_target, color="r", linestyle="-", label="target")

        # plot the weigh ins as a scatter plot
        ax.scatter(x, y, color="b", label="weigh ins")

        # plot the trend line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), color="b", linestyle="-", label="trend")

        # set y axis min max
        ax.set_ylim(bottom=0, top=400)
        # set x axis min max
        ax.set_xlim(left=x[0], right=len(x))
        # make the x axis labels the meal numbers
        ax.set_xticks(x)
        with NamedTemporaryFile(suffix=".png") as f:
            charted.savefig(f.name)
            await ctx.followup.send(file=discord.File(f.name))
        # get rid of the chart
        plt.close(charted)

    @Consume.command(name="set_targets", description="Daily Calorie Target/Weight Target")
    async def set_targets(self, ctx: ApplicationContext):
        """Set your daily calorie target"""
        print("set_targets")
        # set column to be the username + target
        collist = self.db.list_collection_names()
        if not "targets" in collist:
            self.db.create_collection("targets")

        # create a modal for the Targets
        chat = targets_modal(title="Set your targets")
        await ctx.send_modal(chat)
        await chat.wait()

        weight_val = chat.val0
        cal_val = chat.val1

        # send the 
        targets = Targets(None)
        targets.user = ctx.author.name
        if weight_val is not None and cal_val is not None:
            targets.weight_target = int(weight_val)
            targets.cal_target = int(cal_val)
        
        # log it
        try:
            self.log_targets(targets)
        except Exception as e:
            print(e)
            await ctx.send("Failed to log targets")
            return
        await ctx.send("Targets set to " + str(targets.weight_target) + " lbs and " + str(targets.cal_target) + " calories")

    def get_targets(self, usr: str) -> Optional[Targets]:
        print("Getting targets for " + usr)
        collist = self.db.list_collection_names()
        if not "targets" in collist:
            print("No targets set")
            return None
        if not self.db["targets"].find({"user": usr}):
            print("No targets set for " + usr)
            return None
        # get the most recent target
        target = self.db["targets"].find({"user": usr})
        target = target.sort("unix_time", -1)
        if target is None:
            print("No targets set for " + usr)
            return None
        return Targets(target[0])

def setup(bot):
    """Add the cog to the bot"""
    bot.add_cog(NomCog(bot))
