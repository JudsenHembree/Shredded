"""A Discord bot that uses OpenAI's GPT-3 to chat with users."""
import sys
import os
from getopt import getopt
from dotenv import dotenv_values
import bot

if __name__ == '__main__':
    DEVELOPER_MODE = False
    #get opt arguments
    short_options = "d"
    long_options = ["developer"]
    try:
        arguments, values = getopt(sys.argv[1:], short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    for current_argument, current_value in arguments:
        if current_argument in ("-d", "--developer"):
            print("Running in developer mode")
            DEVELOPER_MODE = True

    if DEVELOPER_MODE:
        bot.run_discord_bot(developer_mode=True)
    else:
        bot.run_discord_bot()
