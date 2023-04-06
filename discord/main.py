import bot
import openai
import utils
import chat
from dotenv import dotenv_values

if __name__ == '__main__':
    config = dotenv_values(".env")
    print(config)
    openai.api_key = config["OPENAI_KEY"]
    bot.run_discord_bot()
