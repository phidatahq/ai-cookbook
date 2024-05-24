import discord  # type: ignore
from discord.ext import commands  # type: ignore
from events import setup_event_handlers


# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

setup_event_handlers(bot)
