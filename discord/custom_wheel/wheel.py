import pandas
import tempfile
import ffmpeg
import random
import math
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

def decay_function(initial_value, time_constant, time_elapsed):
    return max(0, initial_value - initial_value * math.exp(-time_elapsed / time_constant))

def wheel(games, tmpfile):
    """Generate a wheel gif"""
    labels = games
    data = []
    weight = 100/len(labels)
    for i in range(len(labels)):
        data.append(weight)

    seconds = random.randint(10, 30)
    angle = 0
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

        subprocess.run(["ffmpeg", "-framerate", "50", "-i", tmpdirname + "%d.png", "-loop", "-1", "-y", "-loglevel", "quiet", tmpfile.name])
