import pandas as pd
import discord
import numpy as np
import matplotlib.pyplot as plt

def graph_test():
    """Graph a line"""
    x = np.linspace(0, 10, 100)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    return fig
