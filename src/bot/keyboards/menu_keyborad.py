from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()

builder.row(
    InlineKeyboardButton(text="Пройти опрос", callback_data="quiz_start"),
    InlineKeyboardButton(text="Показать мой тип личности",   callback_data="menu:profile"),
)

builder.row(
    InlineKeyboardButton(text="Прислать PDF", callback_data="menu:convert"),
)

menu_markup = builder.as_markup()