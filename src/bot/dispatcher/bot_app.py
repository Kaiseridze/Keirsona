from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types.bot_command import BotCommand

from ..handlers import start, quiz

class BotApp:
    def __init__(self, token: str):
        self.__session = AiohttpSession()
        self.__dispatcher = Dispatcher()
        self.__bot = Bot(token=token, session=self.__session)
        self.__register_routers()

    def __register_routers(self):
        return self.__dispatcher.include_routers(start.router, quiz.router)
    
    async def get_commands(self):
        await self.__bot.set_my_commands([
            BotCommand(command="start", description="Начать работу")
        ])
    async def run(self):
        await self.get_commands()
        await self.__dispatcher.start_polling(self.__bot) # type: ignore