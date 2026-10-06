import asyncio
import datetime
import logging
import signal

import discord
from discord.ext import commands, tasks

from src.config import settings
from src.date import (
    RUN_TIME,
    advance_date_calc_to_valid_state,
    date_calc,
    get_all_valid_days_in_month,
    get_target_poll_date,
    get_today,
)
from src.log import setup_logging
from src.title import get_random_game_poll_title_with_month

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    logger.info("Logged in as %s", bot.user)


@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send("pong")


@tasks.loop(time=RUN_TIME)
async def schedule_poll():
    guild = discord.utils.get(bot.guilds, name=settings.SERVER_NAME)
    if guild is None:
        logger.warning("Server %s does not exist", settings.SERVER_NAME)
        return

    channel = discord.utils.get(guild.text_channels, name=settings.CHANNEL_NAME)
    if channel is None:
        logger.warning("Channel %s does not exist", settings.CHANNEL_NAME)
        return

    thread = discord.utils.get(channel.threads, name=settings.THREAD_NAME)
    if thread is None:
        thread = await discord.utils.get(
            channel.archived_threads(), name=settings.THREAD_NAME
        )
    if thread is None:
        logger.warning("Thread %s does not exist", settings.THREAD_NAME)
        return

    role = discord.utils.get(guild.roles, name=settings.ROLE_NAME)
    if role is None:
        logger.warning("Role %s does not exist", settings.ROLE_NAME)
        return

    logger.info("Date: %s", get_today().date().isoformat())
    logger.info("Target date: %s", date_calc.target_saturday.isoformat())

    if get_today().date() != get_target_poll_date(date_calc.target_saturday):
        logger.info("Skip sending poll today")
        return

    logger.info("Setting up poll")

    valid_days = get_all_valid_days_in_month(date_calc.target_saturday)

    logger.info("Valid days: %s", valid_days)

    poll = discord.Poll(
        question=get_random_game_poll_title_with_month(date_calc.target_saturday),
        duration=datetime.timedelta(weeks=1),
        multiple=True,
    )
    for day in valid_days:
        poll.add_answer(text=day.strftime("%b %d"))

    logger.info("Poll: %s", poll)

    await thread.send(content=f"{role.mention}", poll=poll)

    logger.info("Sent poll")

    date_calc.select_next_target_saturday()


@schedule_poll.before_loop
async def before():
    await bot.wait_until_ready()


async def main():
    advance_date_calc_to_valid_state()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(bot.close()),
        )

    async with bot:
        schedule_poll.start()
        await bot.start(settings.TOKEN)


if __name__ == "__main__":
    setup_logging()
    logger.info("Starting bot")
    asyncio.run(main())
    logger.info("Shutting down bot")
