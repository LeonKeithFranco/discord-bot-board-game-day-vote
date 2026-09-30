import asyncio
import datetime
import signal

import discord
from discord.ext import commands, tasks

from src.config import settings
from src.date import (
    RUN_TIME,
    date_calc,
    get_all_saturdays_in_month,
    get_target_poll_date,
    get_today,
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send("pong")


@tasks.loop(time=RUN_TIME)
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

    role = discord.utils.get(guild.roles, name=settings.ROLE_NAME)
    if role is None:
        print(f"Role {settings.ROLE_NAME} does not exist")
        return

    await thread.send(f"test message timestamp: {get_today().isoformat()}")

    # if get_target_poll_date(date_calc.target_saturday) != date_calc.target_saturday:
    #     return

    saturdays = get_all_saturdays_in_month(date_calc.target_saturday)

    poll = discord.Poll(
        question="Board games?!", duration=datetime.timedelta(hours=24), multiple=True
    )
    for sat in saturdays:
        poll.add_answer(text=sat.strftime("%b %d"))

    await thread.send(content=f"{role.mention}", poll=poll)


@schedule_poll.before_loop
async def before():
    await bot.wait_until_ready()


async def main():
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
    asyncio.run(main())
