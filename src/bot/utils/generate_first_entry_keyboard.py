from aiogram import types
def build_keyboard() -> types.ReplyKeyboardMarkup:
    kb = [[types.KeyboardButton(text="Начать")]]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)