"""
A simple heartbeat to make sure Mike is alive and well
"""

import pymongo
import time
from typing import Optional, Any, Dict, List
from tempfile import NamedTemporaryFile
from discord.ext import commands, tasks
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

class MikesHeart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient()
        self.db = self.mongo_client["mike_heartbeats"]
        self.heart = 0
        self.message = None
        self.send_heart.start()

    def beat(self):
        """Update the heartbeat"""
        #set heart to seconds
        self.heart = int(time.monotonic()) % 60
        # write to database
        self.db["heartbeats"].insert_one({"time": self.heart})

    # beat every second
    @tasks.loop(seconds=1)
    async def send_heart(self):
        """Send a heartbeat"""
        if self.message is None:
            self.message = await self.bot.get_channel(1156062269566890084).send(f"{self.heart}")
        else:
            self.beat()
            await self.message.edit(content=f"{self.heart}")

    @send_heart.before_loop
    async def before_send_heart(self):
        await self.bot.wait_until_ready()

    @send_heart.after_loop
    async def after_send_heart(self):
        # remove the message
        if self.message is not None:
            await self.message.delete()

    @send_heart.error
    async def send_heart_error(self, error):
        print(f"Oh no, an error occurred while sending a heartbeat. Error: {error}")


def setup(bot):
    """Add the cog to the bot"""
    bot.add_cog(MikesHeart(bot))
