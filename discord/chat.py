import discord
from dotenv import dotenv_values

async def Chat(user, message, chain):
    """Chat with GPT3.5"""
    response = await chain.apredict(Message=user + ": " + message)
    return response
