"""The bot brains"""
import random
import ffmpeg
import tempfile
from typing import Optional
from dotenv import dotenv_values
import discord
import chat
import react
import graph
import tree_of_threads
from custom_wheel.wheel import wheel

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
    client = discord.Bot(command_prefix="/", intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

        #sync commands
        client.commands.clear()
        await client.sync_commands()
        print("Commands synced")

        # Get all users
        users = get_users(client)
        # print_users(users)

    @client.slash_command(name='chat')
    async def chat_search(interaction: discord.Interaction, query: str):
        """Query GPT3.5"""
        await interaction.response.defer()
        channel = interaction.channel
        threadName = "Chat with GPT3.5"
        thread = await channel.create_thread(name=threadName, type=discord.ChannelType.public_thread)
        chain = tree_of_threads.spawn_chain(thread)
        response = await chat.Chat(interaction.user.name, query, chain)
        await thread.send(response)
        await interaction.followup.send("Thread created", embed=discord.Embed(title=threadName, url=thread.jump_url))

    @client.slash_command(name='graph')
    async def graph_test(interaction: discord.Interaction):
        """Graph a line"""
        await interaction.response.defer()
        fig = graph.graph_test()
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            fig.savefig(tmp.name)
            await interaction.followup.send(file=discord.File(tmp.name))

    @client.slash_command(name='wheel')
    async def wheel_picker(interaction: discord.Interaction, games_seperated_by_space: str):
        """Pick a random game"""
        #generate images
        await interaction.response.defer()
        games = games_seperated_by_space.split(" ")
        with tempfile.NamedTemporaryFile(suffix=".gif") as tmp:
            wheel(games, tmp)
            await interaction.followup.send(file=discord.File(tmp.name))

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        if str(message.author).find("Hilly") != -1:
            await react.react(message)
        is_thread, chain = tree_of_threads.check_for_thread(message.channel.id)
        if is_thread:
            print("Thread exists")
            response = await chat.Chat(message.author.name, message.content, chain)
            await message.channel.send(response)
    # Remember to run your bot with your personal token
    client.run(token)
