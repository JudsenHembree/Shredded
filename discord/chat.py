import discord
import openai

MODEL = "gpt-3.5-turbo"

async def chat_for_raw_at(message):
    response = await openai.ChatCompletion.acreate(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Can you imagine that you are a fitness youtuber who is absolutly ripped and has a lot of followers? Your name will be Mike. \
         I'd like you to talk in a very big and strong voice. Try to include Bro-Science in your sentences. Also always end your message with ', and remember tren is king'."},
        {"role": "user", "content": "What's up Mike?"},
    ],
    temperature=0.9,
    max_tokens=250,
    n=1,
    )
    await message.channel.send(response["choices"][0]["message"]["content"])

async def get_last_10_messages(message):
    """ func """
    messages = []
    user_numbers = []
    users = []
    #aliases = []
    async for msg in message.channel.history(limit=10):
        if msg.content.find("<@") != -1:
            user_numbers = msg.content.split("<@")[1:]
            user_numbers = [user_number.split(">")[0] for user_number in user_numbers]
    if user_numbers != []:
        for user in user_numbers:
            userName = await message.guild.fetch_member(user)
            users.append(userName.name)
        #counter = 0
        #for user in users:
            #aliases.append("Person " + str(counter))
    async for msg in message.channel.history(limit=10):
        if user_numbers != []:
            for i in range(len(user_numbers)):
                if msg.content.find("<@" + user_numbers[i] + ">") != -1:
                    msg.content = msg.content.replace("<@" + user_numbers[i] + ">", users[i])
        messages.append(msg.author.name + ": " + msg.content)
    messages_string = ""
    for message in reversed(messages):
        message = message.replace("Homeless_and_shredded", "Mike")
        messages_string += message + "\n"
    return messages_string

async def chat_with_messages(message):
    messages = await get_last_10_messages(message)
    response = await openai.ChatCompletion.acreate(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Can you imagine that you are a jock who is absolutly ripped? Your name will be Mike. \
         I'd like you to talk with a lot of confidence. Try to include Bro-Science in your sentences, but pay attention to the prompt for conversation context. \
         Also always end your message with ', and remember tren is king'."},
        {"role": "user", "content": "I'd like you to continue the conversation from the last 10 messages. \n The messages are as follows: " + messages},
    ],
    temperature=0.9,
    max_tokens=250,
    n=1,
    )
    if response["choices"][0]["message"]["content"].startswith("Mike: ") == True:
        response["choices"][0]["message"]["content"] = response["choices"][0]["message"]["content"].replace("Mike: ", "")
    await message.channel.send(response["choices"][0]["message"]["content"])

async def Shirtless(message):
    response = await openai.ChatCompletion.acreate(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Can you imagine that you are a fitness youtuber who is absolutly ripped and has a lot of followers? Your name will be Mike. \
            I'd like you to talk in a very big and strong voice. Try to include Bro-Science in your sentences. Also always end your message with ', and remember tren is king'."},
        {"role": "user", "content": "Do a physique update right quick Mike."},
    ],
    temperature=0.9,
    max_tokens=250,
    n=1,
    )
    await message.channel.send(response["choices"][0]["message"]["content"], file=discord.File('images_of_mike/beach.jpg'))

async def Chat(message):
    response = await openai.ChatCompletion.acreate(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Be as precise as possible. \
                Try to be factual and not opinionated."},
        {"role": "user", "content": message},
    ],
    max_tokens=250,
    n=1,
    )
    return response["choices"][0]["message"]["content"]
