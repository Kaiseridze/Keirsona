from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand

from bot.services.menu import router as menu_router
from bot.services.quiz import router as quiz_router
from bot.services.start import router as start_router


class BotDispatcher():
    def __init__(self, token: str) -> None: 
        self.__bot = Bot(token)
        self.__dispatcher = Dispatcher()
        self.__register_routers()
    
    def __register_routers(self):
        self.__dispatcher.include_routers(menu_router.router, quiz_router.router, start_router.router)
    
    async def get_bot_commands(self):
        await self.__bot.set_my_commands(
            [
                BotCommand(command="quiz", description="Начать опрос"),
                BotCommand(command="menu", description="Главное меню"),
                BotCommand(command="start", description="Приветствие"),
            ]
        )

    async def run(self):
        await self.get_bot_commands()
        await self.__dispatcher.start_polling(self.__bot) # type: ignore
