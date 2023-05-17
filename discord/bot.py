"""The bot brains"""
import random
from typing import Optional
from dotenv import dotenv_values
import discord
from discord import app_commands
from discord.ext import commands
import chat
import react

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

USERS = {}

def get_users(client):
    """Get all users in the server"""
    return client.get_all_members()

def print_users(users):
    """Print all users"""
    for user in users:
        print(user)

def run_discord_bot():
    """Run the discord bot"""
    # Get the token from the .env file
    config = dotenv_values(".env")
    token = config['BOT_TOKEN']
    if token is None:
        print("No token found in .env file")
        return
    client = commands.Bot(command_prefix="/", intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

        #sync commands
        client.tree.clear_commands(guild=client.guilds[0])
        await client.tree.sync()
        print("Commands synced")

        # Get all users
        users = get_users(client)
        # print_users(users)

    @client.tree.command(name='chat')
    @app_commands.describe(query="Input for gpt3.5")
    async def chat_search(interaction: discord.Interaction, query: str):
        """Query GPT3.5"""
        await interaction.response.defer()
        response = await chat.Chat(query)
        await interaction.followup.send(response)

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        if str(message.author).find("Hilly") != -1:
            await react.react(message)
        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        if client.user in message.mentions:
            if random.random() < 0.1:
                await chat.chat_with_messages(message)
            else:
                await chat.Shirtless(message)

    # Remember to run your bot with your personal token
    client.run(token)
