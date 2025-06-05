import asyncio
import os
import dotenv

from src.bot.dispatcher.bot_app import BotApp

async def main():
    dotenv.load_dotenv()
    token = os.getenv('BOT_TOKEN')

    if not token: 
        raise ValueError
    
    bot = BotApp(token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())