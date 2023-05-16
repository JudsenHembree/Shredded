import discord
import responses
import random
import chat
import react
from dotenv import dotenv_values

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

USERS = {}

def get_users(client):
        return client.get_all_members()

def print_users(users):
    for user in users:
        print(user)

# Send messages
async def send_message(message, user_message, is_private):
    try:
        await message.author.send("Big Mike is here") if is_private else await message.channel.send("Big Mike is there")

    except Exception as e:
        print(e)


def run_discord_bot():
    # Get the token from the .env file
    config = dotenv_values(".env")
    TOKEN = config['BOT_TOKEN']
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        USERS = get_users(client)
        print_users(USERS)

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

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)
