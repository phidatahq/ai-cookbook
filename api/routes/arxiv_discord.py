import asyncio
from os import getenv
from typing import Set

from fastapi import APIRouter
from discord import Intents, Client, Message
from arxiv_ai.ls.message import handle_mention, handle_message

from api.routes.endpoints import endpoints
from utils.log import logger

######################################################
## Router for Arxiv Discord Bot
######################################################

intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)
client.active_threads: Set[int] = set()


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if message.mentions and client.user.mentioned_in(message):
        await handle_mention(message=message, client=client)
    else:
        await handle_message(message=message, client=client)

    return


arxiv_discord_router = APIRouter(prefix=endpoints.ARXIV_DISCORD, tags=["ARXIV"])


@arxiv_discord_router.on_event("startup")
async def startup_event():
    logger.info("Starting Arxiv Discord Bot")
    asyncio.create_task(client.start(getenv("ARXIV_AI_TOKEN")))
