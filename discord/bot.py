import discord
import responses
import random
import chat

intents = discord.Intents.default()
intents.message_content = True

# Send messages
async def send_message(message, user_message, is_private):
    try:
        await message.author.send("Big Mike is here") if is_private else await message.channel.send("Big Mike is there")

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTA5Mjk4MjEyMTQ2OTA1NDk5Nw.GSCwE1.rd2ZPjFOvgezRv3bDtdhTUb-F2m2Hi28OAyyZU'
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # If the user message contains a '?' in front of the text, it becomes a private message
        if client.user in message.mentions:
            if random.random() < 0.1:
                await chat.chat_with_messages(message)
            else:
                await chat.Shirtless(message)

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)
