from aiogram import types
def build_keyboard(answer_1: str, answer_2: str, index: int) -> types.ReplyKeyboardMarkup:
    kb = [
        [types.KeyboardButton(text=answer_1)],
        [types.KeyboardButton(text=answer_2)]
    ]
    if index > 0:
        kb.append([types.KeyboardButton(text="← Назад")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)