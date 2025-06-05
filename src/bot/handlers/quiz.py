from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from src.db.quiz_instance import QuizInstance
from src.bot.utils.generate_keyboard import build_keyboard

router = Router()

@router.message(F.text.casefold() == "да")
async def start_quiz(message: types.Message, state: FSMContext):
    quiz = QuizInstance()
    questions = quiz.get_all_questions()
    if not questions:
        await message.answer('Нам искренне жаль, но мы сломались. Вопросов пока нет :(')
        return

    await state.set_data({
        "index": 0,
        "questions": questions,
        "finished": False
    })

    question = questions[0]
    keyboard = build_keyboard(question.answer_1, question.answer_2, index=0)
    await message.answer(f"Вопрос {question.id}: {question.question}", reply_markup=keyboard)


@router.message()
async def handle_quiz_flow(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    index = data.get("index", 0)
    finished = data.get("finished", False)

    if not questions:
        await message.answer("Опрос завершён. Напишите «да» или нажмите «Начать заново», чтобы пройти ещё раз.")
        return


    if message.text == "Начать заново":
        await state.set_data({
            "index": 0,
            "questions": questions,
            "finished": False
        })
        question = questions[0]
        keyboard = build_keyboard(question.answer_1, question.answer_2, index=0)
        await message.answer(f"Вопрос {question.id}: {question.question}", reply_markup=keyboard)
        return

    if message.text == "← Назад":
        if finished:
            # Возврат с финального экрана
            index = len(questions) - 1
            await state.update_data(index=index, finished=False)
            question = questions[index]
            keyboard = build_keyboard(question.answer_1, question.answer_2, index)
            await message.answer(f"Вопрос {question.id}: {question.question}", reply_markup=keyboard)
        elif index > 0:
            index -= 1
            await state.update_data(index=index)
            question = questions[index]
            keyboard = build_keyboard(question.answer_1, question.answer_2, index)
            await message.answer(f"Вопрос {question.id}: {question.question}", reply_markup=keyboard)
        else:
            await message.answer("Вы на первом вопросе.")
        return


    if finished:
        if message.text == "Скачать PDF":
            await state.clear()
            await message.answer("Вот ваш PDF (заглушка).")
        else:
            await message.answer("Вы завершили опрос. Используйте кнопки ниже.")
        return


    question = questions[index]
    if message.text not in [question.answer_1, question.answer_2]:
        await message.answer("Пожалуйста, нажимайте только на кнопки ниже.")
        return


    if index + 1 < len(questions):
        index += 1
        await state.update_data(index=index)
        question = questions[index]
        keyboard = build_keyboard(question.answer_1, question.answer_2, index)
        await message.answer(f"Вопрос {question.id}: {question.question}", reply_markup=keyboard)
    else:

        await state.update_data(finished=True)
        kb = [
            [types.KeyboardButton(text="← Назад")],
            [types.KeyboardButton(text="Скачать PDF")],
            [types.KeyboardButton(text="Начать заново")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Опрос завершён. Спасибо за участие!", reply_markup=keyboard)
