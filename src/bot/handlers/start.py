from aiogram import Router, types
from aiogram.filters.command import Command

router = Router()

@router.message(Command('start'))
async def start_command(message: types.Message):
    kb = [[types.KeyboardButton(text="Да")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Привет, {message.from_user.first_name}! Хочешь пройти опрос?", reply_markup=keyboard) # type: ignore

