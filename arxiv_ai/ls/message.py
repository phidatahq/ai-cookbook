from typing import List

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

    if len(summary) < 1900:
        await thread.send(summary)
    else:
        chunked_summary = await chunk_text(summary)
        for i, chunk in enumerate(chunked_summary, 1):
            await thread.send(chunk)

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
    thread_id: int = thread.id

    # -*- Make sure thread owner is the bot
    if thread.owner != client.user:
        return

    if thread_id in client.active_threads:
        await message.reply(
            "Sorry, I am already working on a request in this thread. Please wait for the current request to finish. And then ask your question."
        )
        return

    client.active_threads.add(thread_id)

    user_name: str = message.author.name
    user_message: str = message.content
    server: str = message.guild.name
    channel: str = message.channel.name
    logger.info(f'{user_name} said: "{user_message}" in thread: {channel} ({server})')

    # -*- Start the LLM summarization
    discussion_assistant = get_discussion_assistant(user_id=user_name, thread_id=str(thread_id))

    try:
        if discussion_assistant is None:
            await message.reply("Sorry, I was not able to create a thread. Please try again.")
            client.active_threads.remove(thread_id)
            return
        await thread.send("... working ...")
        logger.info(f"Message: {user_message}")
        response = discussion_assistant.run(message=user_message, stream=False)

        if len(response) < 1900:
            await message.reply(response)
        else:
            chunked_response = await chunk_text(response)
            for i, chunk in enumerate(chunked_response, 1):
                await thread.send(chunk)
    except Exception as e:
        logger.error(e)
        await message.reply("Sorry, I was not able to process your request. Please try again.")
        client.active_threads.remove(thread_id)
        return

    client.active_threads.remove(thread_id)


async def chunk_text(text, max_length=1900):
    """
    Chunk a large text into parts, each not exceeding max_length characters,
    ensuring each chunk (except the last one) ends with a full stop. This version
    keeps the original formatting of the input text.

    :param text: The text to be chunked.
    :param max_length: Maximum length of each chunk.
    :return: A list of text chunks.
    """
    chunks: List = []
    current_chunk: str = ""
    current_length: int = 0

    words = text.split(" ")  # Split by space to keep punctuation attached to words
    for word in words:
        # Include space in length calculation if current_chunk is not empty
        word_length_with_space = len(word) + (1 if current_chunk else 0)

        if current_length + word_length_with_space <= max_length:
            # Add a space before the word if current_chunk is not empty
            current_chunk += " " + word if current_chunk else word
            current_length += word_length_with_space
        else:
            # End the chunk at the last full stop
            last_full_stop = current_chunk.rfind(".")
            if last_full_stop != -1 and current_length != max_length:
                # Include the sentence ending in the current chunk
                chunks.append(current_chunk[: last_full_stop + 1])
                # Start a new chunk with the remaining text and the current word
                current_chunk = current_chunk[last_full_stop + 1 :].lstrip() + " " + word
                current_length = len(current_chunk)
            else:
                # Add the chunk as is and start a new one
                chunks.append(current_chunk)
                current_chunk = word
                current_length = len(word)

    # Add the last chunk without looking for a full stop
    if current_chunk:
        chunks.append(current_chunk)

    return chunks
