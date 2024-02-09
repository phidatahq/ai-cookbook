from os import getenv
from typing import Set

from discord import Intents, Client, Message
from arxiv_ai.ls.message import handle_mention, handle_message

from utils.log import logger


def run():
    """Runs the ArXiv AI bot."""

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

    client.run(getenv("ARXIV_AI_TOKEN"), root_logger=True)


if __name__ == "__main__":
    run()
