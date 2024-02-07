import arxiv
from arxiv import Result as ArxivPaper
from discord import Client, Message
from discord.enums import ChannelType
from discord.threads import Thread
from arxiv_ai.ls.discuss import get_discussion_assistant
from arxiv_ai.ls.summary import get_summary_assistant

from utils.log import logger


async def discuss(arxiv_url: str, message: Message, client: Client):
    logger.info(f"Discussing: {arxiv_url}")

    # -*- Get Result from ArXiv
    try:
        paper_id = arxiv_url.split("/")[-1]
        paper: ArxivPaper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
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

    # -*- Create run in the database
    thread_id: int = thread.id
    user_name: str = message.author.name
    discussion_assistant = get_discussion_assistant(user_id=user_name, thread_id=str(thread_id), paper=paper)
    if discussion_assistant is None:
        await message.reply("Sorry, I was not able to create a thread. Please try again.")
        return
    discussion_assistant.create_run()

    # -*- Follow up
    await thread.send(f"How can I help with: `{paper.title}`")


async def summarize(arxiv_url: str, message: Message, client: Client):
    logger.info(f"Summarizing: {arxiv_url}")

    # -*- Get Result from ArXiv
    try:
        paper_id = arxiv_url.split("/")[-1]
        paper: ArxivPaper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
    except Exception as e:
        logger.error(e)
        await message.reply("Sorry, could not find this paper.")
        return

    if paper is None:
        await message.reply("Sorry, could not find this paper.")
        return

    try:
        thread = await message.create_thread(name=paper.title)
    except Exception as e:
        logger.error(e)
        await message.reply("Sorry, I was not able to create a thread.")
        return

    await thread.send(f"Reading up on: `{paper.title}`")

    # -*- Start the LLM summarization
    thread_id: int = thread.id
    user_name: str = message.author.name
    summary_assistant = get_summary_assistant(user_id=user_name, thread_id=str(thread_id), paper=paper)
    summary = summary_assistant.run(stream=False)
    await thread.send(summary)

    # -*- Follow up
    await thread.send("-----\n\nHow can I help with this paper?")


async def handle_mention(message: Message, client: Client):
    user_name: str = message.author.name
    user_message: str = message.content
    server: str = message.guild.name
    channel: str = message.channel.name
    message_parts = message.content.split()
    logger.info(f'{user_name} said: "{user_message}" in #{channel} ({server})')

    # -*- Check that the channel is not a thread. This prevents the bot from creating threads in threads.
    if message.channel.type != ChannelType.text:
        await message.reply("Please message me in a channel to start a discussion.")
        return

    if len(message_parts) != 3:
        await message.reply(
            "Hi, please use `@ArxivAI discuss <paper>` or `@ArxivAI summary <paper>` to interact with me."
        )
        return

    if message_parts[1].lower() not in ["discuss", "summary"]:
        await message.reply(
            "Hi, please use `@ArxivAI discuss <paper>` or `@ArxivAI summary <paper>` to interact with me."
        )
        return

    if not message_parts[2].startswith("https://arxiv.org/abs/"):
        await message.reply(
            "Please provide a valid arXiv paper URL. Example: `https://arxiv.org/abs/1706.03762`"
        )

    if message_parts[1].lower() == "summary":
        return await summarize(arxiv_url=message_parts[2], message=message, client=client)
    elif message_parts[1].lower() == "discuss":
        return await discuss(arxiv_url=message_parts[2], message=message, client=client)
    else:
        await message.reply(
            "Hi, please use `@ArxivAI discuss <paper>` or `@ArxivAI summary <paper>` to interact with me."
        )

    return


async def handle_message(message: Message, client: Client):
    # -*- Check that this message in a thread
    if message.channel.type != ChannelType.public_thread:
        return

    thread: Thread = message.channel
    # -*- Make sure thread owner is the bot
    if thread.owner != client.user:
        return

    user_name: str = message.author.name
    user_message: str = message.content
    server: str = message.guild.name
    channel: str = message.channel.name
    logger.info(f'{user_name} said: "{user_message}" in thread: {channel} ({server})')

    # -*- Start the LLM summarization
    thread_id: int = thread.id
    user_name: str = message.author.name
    discussion_assistant = get_discussion_assistant(user_id=user_name, thread_id=str(thread_id))
    if discussion_assistant is None:
        await message.reply("Sorry, I was not able to create a thread. Please try again.")
        return
    response = discussion_assistant.run(user_message, stream=False)
    await thread.send(response)

    # -*- Follow up
    await thread.send("-----\n\nAny more questions?")
