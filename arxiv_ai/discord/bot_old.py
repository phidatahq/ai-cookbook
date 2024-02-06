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


def run():
    """Runs the ArXiv AI bot."""

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Logged in as {client.user}")

    @client.event
    async def on_message(message: Message):
        if message.author == client.user:
            return

        user_name = str(message.author)
        user_message = str(message.content)
        server = str(message.guild)
        channel = str(message.channel)

        if message.mentions and client.user.mentioned_in(message):
            logger.info(f'{user_name} said: "{user_message}" in #{channel}({server})')
            msg = await message.reply(
                "Hey there! Please use `/discuss` or `/summary` to interact with me. "
                "For example: /discuss https://arxiv.org/abs/..."
            )
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
        try:
            arxiv_url = str(message.content).split(" ")[1]
            logger.info(f"Summarizing: {arxiv_url}")
        except IndexError:
            await ctx.reply(
                "Please provide a paper to summarize. Example: `/summary https://arxiv.org/abs/1706.03762`"
            )
            return

        # -*- Check that the channel is not a thread
        channel = bot.get_channel(int(ctx.message.channel.id))
        if isinstance(channel, discord.channel.Thread):
            await ctx.reply("If you want to summarize another paper, please message on the channel.")
            return

        # -*- Get Result from ArXiv
        try:
            paper_id = arxiv_url.split("/")[-1]
            paper: ArxivResult = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
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

        await thread.send(
            f"Reading up on the paper titled: `{paper.title}`. \n\nI will get back to you soon..."
        )
        # await thread.send(paper.summary)
        # thread = await channel.create_thread(name=arxiv_url, type=discord.ChannelType.public_thread)
        # await thread.send(f"Summarizing {arxiv_paper}")

    bot.run(getenv("ARXIV_AI_TOKEN"), root_logger=True)


if __name__ == "__main__":
    run()
