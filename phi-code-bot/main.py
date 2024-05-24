import os
from dotenv import load_dotenv
from bot import bot

load_dotenv()

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
