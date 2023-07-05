"""
A Wheel picker as requested by @Tyler
"""
import tempfile
import random
import math
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from discord import Option, ApplicationContext, File
from discord.ext import commands
from discord.commands import SlashCommandGroup

def decay_function(initial_value, time_constant, time_elapsed):
    return max(0, initial_value - initial_value * math.exp(-time_elapsed / time_constant))

class Wheel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    wheel = SlashCommandGroup(name="wheel", description="Wheel picker")

    @wheel.command(name='test', description="Test command",
                   options=[Option(input_type=str, name="test", 
                                   description="Test", required=True)])
    async def test(self, ctx: ApplicationContext, test: str):
        """Test command"""
        await ctx.defer()
        await ctx.followup.send(test)


    @wheel.command(name="wheel_picker", description="Generate a wheel gif",
                   options=[Option(input_type=str, name="games", description="Games seperated \
                                   by a space", required=True)])
    async def wheel_picker(self, ctx: ApplicationContext, games: str):
        """Generate a wheel gif"""
        await ctx.defer()
        tmpfile = tempfile.NamedTemporaryFile(suffix=".gif") # the gif file
        labels = games.split(" ")
        data = []
        weight = 100/len(labels)
        for _ in range(len(labels)):
            data.append(weight)

        seconds = random.randint(10, 30)
        angle = random.randint(0, 360)
        speed = 100
        count = 0
        fig, ax = plt.subplots()

        with tempfile.TemporaryDirectory() as tmpdirname:
            for _ in range(seconds):
                start = speed
                speed = decay_function(speed, seconds, 1)
                stop = speed
                angles = np.interp(np.linspace(0,50,50), [0, 50], [start, stop])
                inner_count = 0
                for _ in range(50):
                    if angles[inner_count] < 1:
                        break
                    ax.clear()
                    fig.patch.set_facecolor('black')
                    ax.pie(data, labels=labels, startangle=angle, labeldistance=0.5, rotatelabels=True)
                    plt.arrow(0, 2.5, 0, -1, color="red", width=0.1)
                    plt.draw()
                    angle += angles[inner_count]
                    plt.savefig(tmpdirname + str(count) + ".png")
                    inner_count += 1
                    count += 1
            del fig
            subprocess.run(["ffmpeg", "-framerate", "50", "-i", tmpdirname +
                            "%d.png", "-loop", "-1", "-y", "-loglevel",
                            "quiet", tmpfile.name], check=True)
        await ctx.followup.send(file=File(tmpfile.name))

def setup(bot):
    bot.add_cog(Wheel(bot))
