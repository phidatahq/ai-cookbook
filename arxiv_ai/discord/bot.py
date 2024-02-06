from os import getenv

from discord import Intents, Client, Message
from arxiv_ai.discord.message import handle_message

from utils.log import logger


def run():
    """Runs the ArXiv AI bot."""

    intents = Intents.default()
    intents.message_content = True
    client = Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Logged in as {client.user}")

    @client.event
    async def on_message(message: Message):
        if message.author == client.user:
            return

        user_name: str = message.author.name
        user_message: str = message.content
        server: str = message.guild.name
        channel: str = message.channel.name
        logger.info(f'{user_name} said: "{user_message}" in #{channel}({server})')

        if message.mentions and client.user.mentioned_in(message):
            await handle_message(message=message, client=client)

        return

    client.run(getenv("ARXIV_AI_TOKEN"), root_logger=True)


if __name__ == "__main__":
    run()
