import arxiv
from arxiv import Result as ArxivResult
from discord import Client, Message

from utils.log import logger


async def summarize(arxiv_url: str, message: Message, client: Client):
    logger.info(f"Summarizing: {arxiv_url}")

    # -*- Get Result from ArXiv
    try:
        paper_id = arxiv_url.split("/")[-1]
        paper: ArxivResult = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
    except Exception as e:
        logger.error(e)
        await message.reply("Sorry, could not find this paper.")
        return

    try:
        thread = await message.create_thread(name=paper.title)
    except Exception as e:
        logger.error(e)
        await message.reply("Sorry, I was not able to create a thread.")
        return

    await thread.send(f"Reading up on: `{paper.title}` ...")


async def handle_message(message: Message, client: Client):
    user_name: str = message.author.name
    user_message: str = message.content
    server: str = message.guild.name
    channel: str = message.channel.name
    message_parts = message.content.split(" ")
    logger.info(f'{user_name} said: "{user_message}" in #{channel}({server})')

    if len(message_parts) != 3:
        await message.reply(
            "Hi, please use `@ArxivAI discuss <paper>` or `@ArxivAI summary <paper>` to interact with " "me."
        )
        return

    if message_parts[1].lower() not in ["discuss", "summary"]:
        await message.reply(
            "Hi, please use `@ArxivAI discuss <paper>` or `@ArxivAI summary <paper>` to interact with " "me."
        )
        return

    if not message_parts[2].startswith("https://arxiv.org/abs/"):
        await message.reply(
            "Please provide a valid arXiv paper URL. Example: `https://arxiv.org/abs/1706.03762`"
        )

    if message_parts[1].lower() == "summary":
        return await summarize(arxiv_url=message_parts[2], message=message, client=client)

    return
