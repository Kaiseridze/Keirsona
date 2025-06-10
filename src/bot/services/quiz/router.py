from datetime import datetime, timezone
from typing import Optional, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.quiz.api import QuizAPI
from bot.services.quiz.models import Question, Answer
from bot.keyboards.menu_keyborad import menu_markup
from bot.utils.text_template import return_description

router = Router()
api = QuizAPI()


class QuizStates(StatesGroup):
    question = State()
    gender = State()
    age = State()

def build_gender_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Мужской", callback_data="gender:male")
    builder.button(text="Женский", callback_data="gender:female")
    builder.adjust(2)
    return builder.as_markup()


def build_question_keyboard(current_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="A", callback_data="answer:option1")
    builder.button(text="B", callback_data="answer:option2")
    builder.adjust(2)
    if current_index > 0:
        builder.button(text="Назад", callback_data="nav:prev")
        builder.adjust(1)
    return builder.as_markup()

async def init_quiz(message: Message, state: FSMContext):
    questions = await api.quiz_get_questions()

    # инициализируем FSM
    await state.set_state(QuizStates.question)
    await state.update_data(
        questions=questions,
        answers=[None] * len(questions),  # type: ignore[list-item]
        index=0,
    )
    await state.update_data(start_time=datetime.now(timezone.utc).isoformat())

    first_q = questions[0]
    sent = await message.answer(
        text=(
            f"Вопрос 1/{len(questions)}:\n"
            f"{first_q.question}\n\n"
            f"A: {first_q.answer_1}\n"
            f"B: {first_q.answer_2}"
        ),
        reply_markup=build_question_keyboard(0),
    )
    # сохраняем ID сообщения для последующего удаления
    await state.update_data(current_msg_id=sent.message_id)

@router.message(Command("quiz"))
async def quiz_cmd(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        return await message.answer("Вы уже проходите тест. Чтобы начать заново, введите /menu и выберите «Пройти квиз».")
    await init_quiz(message, state)

@router.callback_query(F.data == "quiz_start")
async def quiz_via_button(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        await call.message.delete()
    except:
        pass

    if await state.get_state() is not None:
        return

    await init_quiz(call.message, state)


@router.callback_query(StateFilter(QuizStates.question), F.data.startswith("answer:") | (F.data == "nav:prev"))
async def process_quiz_navigation(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    idx = data["index"]
    qs = data["questions"]
    answers = data["answers"]
    start = datetime.fromisoformat(data["start_time"])
    total = len(qs)

    if call.data == "nav:prev":
        idx -= 1
    else:
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        _, opt_str = call.data.split(":", 1)
        opt = int(opt_str.replace("option", ""))
        current_q = qs[idx]
        answers[idx] = Answer(
            user_id=call.from_user.id,
            question_id=current_q.id,
            response_option=opt,
            response_time=elapsed
        )
        idx += 1

    await state.update_data(
        index=idx,
        answers=answers,
        start_time=datetime.now(timezone.utc).isoformat()
    )

    if idx >= total:
        try:
            await call.message.delete()
        except:
            pass

        clean_answers = [a for a in answers if a is not None]  # type: ignore
        await api.save_user_results(
            user_id=call.from_user.id,
            answers=clean_answers
        )

        registered = await api.find_user(call.from_user.id)
        if not registered:
            await state.set_state(QuizStates.gender)
            sent = await call.message.answer(
                "Спасибо! Выберите ваш пол:",
                reply_markup=build_gender_keyboard()
            )
            await state.update_data(current_msg_id=sent.message_id)
            return

        profile = await api.get_personality_info(call.from_user.id)
        result_text = return_description(profile=profile)
        await call.message.answer(result_text)
        await call.message.answer("Вы в меню:", reply_markup=menu_markup)
        await state.clear()
        return

    # если ещё вопросы остались
    q = qs[idx]
    text = (
        f"Вопрос {idx+1}/{total}:\n"
        f"{q.question}\n\n"
        f"A: {q.answer_1}\n"
        f"B: {q.answer_2}"
    )
    await call.message.edit_text(text=text, reply_markup=build_question_keyboard(idx))


@router.callback_query(StateFilter(QuizStates.gender), F.data.startswith("gender:"))
async def process_gender_selection(call: CallbackQuery, state: FSMContext):
    await call.answer()
    # удаляем кнопку выбора пола
    try:
        await call.message.delete()
    except:
        pass

    # получаем пол из callback_data
    _, gender_value = call.data.split(":", 1)
    gender_text = "мужской" if gender_value == "male" else "женский"
    await state.update_data(gender=gender_text)

    # переходим к возрасту
    await state.set_state(QuizStates.age)
    sent = await call.message.answer("Теперь укажите ваш возраст (в годах):")
    await state.update_data(current_msg_id=sent.message_id)


@router.message(QuizStates.age)
async def finish_quiz(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
    except ValueError:
        return await message.answer("Возраст должен быть числом.")
    data = await state.get_data()
    gender = data["gender"]
    answers: List[Optional[Answer]] = data["answers"]
    clean_answers = [a for a in answers if a is not None]  # type: ignore

    # сохраняем в API
    await api.save_user_data(
        user_id=message.from_user.id,
        gender=gender,
        age=age
    )
    await api.save_user_results(
        user_id=message.from_user.id,
        answers=clean_answers
    )

    msg_id = data.get("current_msg_id")
    if msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except:
            pass
    profile = await api.get_personality_info(message.from_user.id) # type: ignore

    msg_id = data.get("current_msg_id")
    if msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=msg_id
            )
        except:
            pass

    result_text = return_description(profile=profile)
    await message.answer(result_text)


    await state.clear()
    await message.answer("Вы в меню:", reply_markup=menu_markup)
    await state.clear()

