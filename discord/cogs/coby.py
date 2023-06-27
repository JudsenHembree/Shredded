"""
Mess with coby when he posts a message
"""
from discord.ext import commands

class Coby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Coby(bot))
