"""
https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot
"""
from os import getenv

from arxiv import Result as ArxivResult
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import context
from rich.pretty import pprint
import arxiv
import responses

from utils.log import logger


async def send_message(message, user_message):
    try:
        response = responses.handle_message(user_message)
        await message.channel.send(response)
    except Exception as e:
        logger.error(e)
        await message.channel.send("Sorry, I am not able to process your request at the moment.")


async def send_discussion(paper, thread):
    try:
        response = responses.handle_discussion(paper)
        await thread.send(response)
    except Exception as e:
        logger.error(e)
        await thread.send("Sorry, I am not able to process your request at the moment.")


async def continue_discussion(message: Message):
    logger.info(f"Continuing discussion: {message}")


def run():
    """Runs the ArXiv AI bot."""

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user}")

    @bot.event
    async def on_message(message: Message):
        if message.author == bot.user:
            return

        user_name = str(message.author)
        user_message = str(message.content)
        server = str(message.guild)
        channel = str(message.channel)

        if message.content.startswith("/"):
            logger.info(f'{user_name} said: "{user_message}" in #{channel}({server})')
            await bot.process_commands(message)
        elif message.mentions and bot.user.mentioned_in(message):
            logger.info(f'{user_name} said: "{user_message}" in #{channel}({server})')
            await message.reply(
                "Hey there! Please use `/discuss` or `/summary` to interact with me. "
                "For example: `/discuss https://arxiv.org/abs/1706.03762`"
            )
        else:
            await continue_discussion(message)
        return

    @bot.command()
    async def discuss(ctx):
        try:
            paper = str(ctx.message.content).split(" ")[1]
        except IndexError:
            await ctx.reply(
                "Please provide a paper to discuss. Example: `/discuss https://arxiv.org/abs/1706.03762`"
            )
            return

        logger.info(f"Discussing: {paper}")
        pprint(ctx.__dict__)

        channel = bot.get_channel(int(ctx.message.channel.id))

        if type(channel) == discord.channel.Thread:
            await channel.send("If you want to discuss another paper, please message on the channel.")
            return

        thread = await channel.create_thread(
            name=paper, type=discord.ChannelType.public_thread, auto_archive_duration=60
        )

        await thread.send(f"Looking up {paper}. I will get back to you soon.")
        await send_discussion(paper, thread)

    @bot.command()
    async def summary(ctx: context.Context):
        # pprint(ctx.__dict__)
        message: Message = ctx.message
        content = message.content

        # TODO: implement /summary redo

        # -*- Check that the channel is not a thread. This prevents the bot from creating threads on threads.
        channel = bot.get_channel(int(ctx.message.channel.id))
        if isinstance(channel, discord.channel.Thread):
            await ctx.reply("If you want to summarize another paper, please message on the channel.")
            return

        # -*- Check that the message is in the correct format
        if len(content.split()) != 2:
            await ctx.reply(
                "Please use the format `/summary [paper]`. "
                "Example: `/summary https://arxiv.org/abs/1706.03762`"
            )
            return

        # -*- Get the arXiv URL
        arxiv_url = content.split()[1]
        if not arxiv_url.startswith("https://arxiv.org/abs/"):
            await ctx.reply(
                "Please provide a valid arXiv paper. Example: `/summary https://arxiv.org/abs/1706.03762`"
            )
            return
        logger.info(f"Summarizing: {arxiv_url}")

        # -*- Get Result from ArXiv
        try:
            paper_id = arxiv_url.split("/")[-1]
            paper: ArxivResult = next(arxiv.Client(num_retries=2).results(arxiv.Search(id_list=[paper_id])))
        except Exception as e:
            logger.error(e)
            await ctx.reply("Sorry, could not find this paper.")
            return

        try:
            thread = await message.create_thread(name=paper.title)
        except Exception as e:
            logger.error(e)
            await message.reply("Sorry, I was not able to create a thread.")
            return

        await thread.send(f"Reading up on: `{paper.title}`")

        # -*- Start the LLM summarization
        # ...

    bot.run(getenv("ARXIV_AI_TOKEN"), root_logger=True)


if __name__ == "__main__":
    run()
