import asyncio
import logging
import sys
from os import getenv

import dotenv

from bot.dispatcher import BotDispatcher

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main() -> None:
    if TOKEN is None:
        return
    bot = BotDispatcher(token=TOKEN)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())