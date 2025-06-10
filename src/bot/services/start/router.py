import aiogram.utils.markdown as fmt
from aiogram.fsm.context import FSMContext
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    # при старте очищаем любое состояние
    await state.clear()

    # строим inline-клавиатуру с одной кнопкой
    builder = InlineKeyboardBuilder()
    builder.button(text="Пройти опрос", callback_data="quiz_start")
    # если понадобятся ещё кнопки, добавьте builder.button(...)
    keyboard: InlineKeyboardMarkup = builder.as_markup()

    # приветственное сообщение
    welcome = fmt.text(
        fmt.hbold("Тест Кейрси: Определи свой тип личности!"),
        "",
        fmt.text(
            "Привет! Этот тест поможет понять твой психологический тип по методике Дэвида Кейрси. ",
            fmt.hitalic("70 вопросов"),
            " — отвечай интуитивно, не задумываясь слишком долго."
        ),
        "",
        fmt.text(
            "Нажми ",
            fmt.hbold("Пройти опрос"),
            " когда будешь готов(а)."
        ),
        sep="\n"
    )

    # отправляем сообщение с inline-клавиатурой
    await message.answer(
        welcome,
        parse_mode="HTML",
        reply_markup=keyboard
    )
