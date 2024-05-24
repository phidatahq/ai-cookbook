import re
from phi.assistant import Assistant  # type: ignore
from phi.llm.openai import OpenAIChat  # type: ignore
import discord  # type: ignore
from phi.tools.duckduckgo import DuckDuckGo  # type: ignore
from ratelimit import sliding_window_rate_limit
import redis  # type: ignore
from knowledge_base import knowledge_base

# Constants
MAX_TOKENS = 1500
AI_MODEL = "gpt-4o"
DISCORD_CHAR_LIMIT = 2000
HOST="localhost"
PORT=6379
WINDOW_SIZE=60
LIMIT=10


def setup_event_handlers(bot) -> None:
    """
    Sets up event handlers for a Discord bot.

    Args:
    bot : The instance of the Discord bot to which event handlers are attached.

    This function initializes the bot's reactions to specific Discord events like connecting to Discord
    and receiving messages. It incorporates rate limiting using Redis to manage how frequently users can send messages.
    """

    @bot.event
    async def on_ready():
        print(f"{bot.user} has connected to Discord!")

    @bot.event
    async def on_message(message) -> None:
        if message.author == bot.user:
            return
        # Rate limiting - 10 requests per minute
        redis_connection = redis.Redis(host=HOST , port=PORT, db=0)

        if not sliding_window_rate_limit(message.author.id, WINDOW_SIZE, LIMIT, redis_connection):
            await message.channel.send(
                "You have exceeded the rate limit. Please wait a few minutes before asking again."
            )
            return

        # Handle questions if asked in a thread
        if message.channel.type in (
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        ) and bot.user.mentioned_in(message) and not message.mention_everyone:
            question = message.content.strip()
            if not question:
                await message.channel.send("Please provide a question.")
                return
            await message.channel.send(f"{message.author.mention}, Let me think...")
            try:
                await handle_request(message.channel, question, message.attachments)
            except Exception as e:
                await message.channel.send("Sorry, I couldn't process your request.")
                print(f"Error: {e}")
            return

        # If question is asked in channel it creates a new thread.
        elif bot.user.mentioned_in(message) and not message.mention_everyone:
            mention_pattern = re.compile(
                f"<@!?{bot.user.id}>"
            )  # compile the regex pattern
            question = mention_pattern.sub(
                "", message.content
            ).strip()  # replace the mention pattern with an empty string and also strip any leading or trailing whitespaces.
            if not question:
                await message.channel.send("Please provide a question by tagging me.")
                return
            thread = await message.create_thread(
                name=f"Question: {question[:80]}", auto_archive_duration=60
            )
            await thread.send(f"{message.author.mention}, Let me think...")
            try:
                await handle_request(thread, question, message.attachments)
            except Exception as e:
                await thread.send("Sorry, I couldn't process your request.")
                print(f"Error: {e}")


async def send_long_message(channel, text) -> None:
    """Sends messages to a Discord channel, splitting them if they exceed the limit. Ensures proper formatting of code blocks."""
    #TODO: Handle character split from middle of a word.
    parts = [
        text[i : i + DISCORD_CHAR_LIMIT - 10]
        for i in range(0, len(text), DISCORD_CHAR_LIMIT - 10)
    ]  # -10 to account for the ``` characters and append them.

    """Track if in the message split code block was closed."""
    in_code_block = False
    for part in parts:
        if in_code_block:
            part = "```" + part

        code_blocks = re.findall(r"```", part)
        if len(code_blocks) % 2 != 0:
            part += "```"
            in_code_block = True
        else:
            in_code_block = False

        await channel.send(part)


async def handle_request(channel, question, attachments=None) -> None:
    """Handles the request user sends and also takes care of the attachments."""
    data = [{"type": "text", "text": question}]
    if attachments:
        for attachment in attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                data.append({"type": "image_url", "image_url": {"url": attachment.url}})

    assistant = phidata_assistant()
    assistant.knowledge_base.load(recreate=False)
    response = assistant.run(message=data, stream=False)
    await send_long_message(channel, response)


def phidata_assistant():
    instructions = [
        "You are made by phidata: https://github.com/phidatahq/phidata",
        "You are a code assistant",
        "You are a knowledge base assistant",
        "You have phidata knowledge base, if any question is related to phidata, you should answer it from the knowledge base.",
        "You also have image reading capabilities so you'll be provided with image url if needed.",
        "When you output code, wrap it in three backticks (```).",
    ]


    return Assistant(
        name="phidata_code_bot_run",
        llm=OpenAIChat(
            model=AI_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=1,
        ),
        knowledge_base=knowledge_base,
        instructions=instructions,
        tools=[DuckDuckGo()],
        show_tool_calls=True,
        search_knowledge=True,
        debug_mode=True,
        description="Your name Phidata code assistant, you are designed to help users with coding questions and fix their errors.",
        add_to_system_prompt="You should one respond to questions related to coding and provide code snippets to fix the errors. You shouldn't deviate from the topic of coding.",
    )
