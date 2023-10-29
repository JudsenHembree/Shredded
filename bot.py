"""The bot brains"""
from typing import Optional
from dotenv import dotenv_values
import discord

intents = discord.Intents.default()
intents = discord.Intents.all()

USERS = {}

def get_users(client):
    """Get all users in the server"""
    return client.get_all_members()

def print_users(users):
    """Print all users"""
    for user in users:
        print(user)

def run_discord_bot(developer_mode: Optional[bool] = False):
    """Run the discord bot"""
    # Get the token from the .env file
    config = dotenv_values(".env")
    token = config['BOT_TOKEN']
    if developer_mode:
        token = config['BOT_TOKEN_DEV']
    if token is None:
        print("No token found in .env file")
        return
    client = discord.Bot(intents=intents)
    cog_list = ['cogs.wheel', 'cogs.intro_music',
                'cogs.chat', 'cogs.fit']
    for cog in cog_list:
        client.load_extension(cog)

    heart = client.load_extension('cogs.heartbeat')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        #sync commands
        await client.sync_commands()
        print("Commands synced")

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

    # Remember to run your bot with your personal token
    client.run(token)
