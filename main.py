import asyncio
import signal

import discord
from discord.ext import commands, tasks

from src.config import settings
from src.date import get_today

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send("pong")


# @tasks.loop(time=RUN_TIME)
@tasks.loop(minutes=5)
async def schedule_poll():
    guild = discord.utils.get(bot.guilds, name=settings.SERVER_NAME)
    if guild is None:
        print(f"Server {settings.SERVER_NAME} does not exist")
        return

    channel = discord.utils.get(guild.text_channels, name=settings.CHANNEL_NAME)
    if channel is None:
        print(f"Channel {settings.CHANNEL_NAME} does not exist")
        return

    thread = discord.utils.get(channel.threads, name=settings.THREAD_NAME)
    if thread is None:
        print(f"Thread {settings.THREAD_NAME} does not exist")
        return

    await thread.send(f"test message timestamp: {get_today().isoformat()}")


@schedule_poll.before_loop
async def before():
    await bot.wait_until_ready()


async def main():
    loop = asyncio.get_running_loop()
    shutdown_task = asyncio.create_task(bot.close())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: shutdown_task,
        )

    async with bot:
        schedule_poll.start()
        await bot.start(settings.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
