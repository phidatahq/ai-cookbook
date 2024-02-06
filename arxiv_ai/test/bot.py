"""

https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot
"""

from os import getenv
import discord
from discord.ext import commands
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
    "Runnig ArXiv AI"
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: {user_message} in {channel}")

        logger.info(f"Received Message: {message.content}")

        if message.content.startswith("/"):
            await bot.process_commands(message)
        else:
            await send_message(message, user_message)

    @bot.command()
    async def discuss(ctx):
        try:
            paper = str(ctx.message.content).split(" ")[1]

        except IndexError:
            await ctx.reply(
                "Please provide a paper to discuss. Example: `/discuss https://arxiv.org/abs/2402.01833`"
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
    async def summarize(ctx):
        try:
            paper = str(ctx.message.content).split(" ")[1]

        except IndexError:
            await ctx.reply(
                "Please provide a paper to summarize. Example: `/summarize https://arxiv.org/abs/2402.01833`"
            )
            return

        logger.info(f"Summarizing: {paper}")
        pprint(ctx.__dict__)

        channel = bot.get_channel(int(ctx.message.channel.id))

        if type(channel) == discord.channel.Thread:
            await channel.send("If you want to summarize another paper, please message on the channel.")
            return

        thread = await channel.create_thread(
            name=paper, type=discord.ChannelType.public_thread, auto_archive_duration=60
        )

        await thread.send(f"Looking up {paper}. I will get back to you soon.")

        await thread.send(f"Summarizing {paper}")

        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper.split("/")[-1]])))
            await thread.send(paper.summary)

        except Exception as e:
            logger.error(e)
            await thread.send("Sorry, arXiv is not able to process your request at the moment.")

    bot.run(ARXIV_AI_TOKEN, root_logger=True)


if __name__ == "__main__":
    run()
