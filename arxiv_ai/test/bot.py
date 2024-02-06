"""

https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot
"""
from os import getenv
import discord
from discord.ext import commands

from utils.log import logger


def run():
    "Runnig ArXiv AI"
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user}")

    @bot.command()
    async def discuss(ctx):
        logger.info(f"ctx: {ctx.__dict__}")
        logger.info(f"discussing: {ctx.message.content}")
        await ctx.reply("Hi 🙉")

    @bot.event
    async def on_message(message):
        logger.info(f"Received Message: {message.content}")
        await bot.process_commands(message)

    bot.run(getenv("ARXIV_AI_TOKEN"), root_logger=True)


if __name__ == "__main__":
    run()
