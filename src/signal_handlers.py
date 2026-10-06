import asyncio

from discord.ext.commands import Bot

_background_tasks: set[asyncio.Task] = set()


def request_shutdown(bot: Bot) -> None:
    _background_tasks.add(asyncio.create_task(bot.close()))
