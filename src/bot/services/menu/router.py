from io import BytesIO

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot.services.quiz.api import QuizAPI
from bot.utils.text_template import return_description
from bot.utils.pdf_generator import create_personality_pdf
from bot.keyboards.menu_keyborad import menu_markup

api = QuizAPI()
router = Router()


@router.message(Command("menu"))
async def show_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("current_msg_id")
    if msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=msg_id
            )
        except Exception:
            pass

    await state.clear()
    await message.answer(text="Вы в меню", reply_markup=menu_markup)


@router.callback_query(F.data == "menu:profile")
async def show_profile(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        await call.message.delete()
    except:
        pass

    user_id = call.from_user.id
    if not await api.find_user(user_id):
        return await call.message.answer(
            "Сначала пройдите квиз – выберите «Пройти квиз».",
            reply_markup=menu_markup
        )

    profile = await api.get_personality_info(user_id)

    text = return_description(profile=profile)
    await call.message.answer(text)
    await state.clear()
    await call.message.answer("Вы в меню:", reply_markup=menu_markup)

@router.callback_query(F.data == "menu:convert")
async def send_profile_pdf(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        await call.message.delete()
    except:
        pass

    user_id = call.from_user.id
    if not await api.find_user(user_id):
        return await call.message.answer(
            "Сначала пройдите квиз – выберите «Пройти квиз».",
            reply_markup=menu_markup
        )

    profile = await api.get_personality_info(user_id)
        # генерируем PDF и упаковываем в BufferedInputFile
    pdf_buffer: BytesIO = create_personality_pdf(profile)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_file = BufferedInputFile(pdf_bytes,
                                 filename=f"{call.from_user.first_name}_report.pdf")

    # отправляем PDF
    await call.message.answer_document(pdf_file,
                                       caption="Ваш подробный отчёт в PDF")

    await state.clear()
    await call.message.answer("Вы в меню:", reply_markup=menu_markup)