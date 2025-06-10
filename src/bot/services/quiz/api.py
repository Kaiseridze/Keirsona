from typing import Any, List

from bot.services.quiz.models import Answer, Question
from db.cursor import Cursor


class QuizAPI:
    def __init__(self): 
        self.db = Cursor()
    
    async def find_user(self, user_id: int) -> bool:
        result = await self.db.fetch_one("SELECT id from users WHERE id = ?", (user_id,))
        return True if result else False

    async def quiz_get_questions(self):
        rows = await self.db.fetch_all("SELECT * FROM questions")
        return [Question(*row) for row in rows]
    
    async def save_user_results(
        self,
        user_id: int,
        answers: List[Answer],
    ) -> None:
        
        records = [answer.as_tuple(user_id) for answer in answers]
        await self.db.execute_many(
            "INSERT INTO user_responses (user_id, question_id, response_option, response_time) VALUES (?, ?, ?, ?) " \
            "ON CONFLICT(user_id, question_id) DO UPDATE SET response_option = excluded.response_option, response_time = excluded.response_time",
            records
        )
    
    async def save_user_data(self, user_id: int, gender: str, age: int):
        await self.db.execute("INSERT INTO users (id, gender, age) VALUES (?, ?, ?)", (user_id, gender, age))

    async def calculate_and_store_result(self, user_id: int) -> str:
        # 1. Собираем ответы пользователя и считаем баллы по шкалам 1–8
        rows = await self.db.fetch_all(
            """
            SELECT qsm.scale_id, qsm.option_number, ur.response_option
            FROM user_responses ur
            JOIN question_scale_mapping qsm ON ur.question_id = qsm.question_id
            WHERE ur.user_id = ?
            """,
            (user_id,)
        )
        scores = {i: 0 for i in range(1, 9)}
        for scale_id, opt_num, resp in rows:
            if resp == opt_num:
                scores[scale_id] += 1

        # 2. Получаем ограничения для каждого типа и отбираем «валидные»
        ranges = await self.db.fetch_all(
            "SELECT type_id, scale_id, min_score, max_score FROM type_scale_ranges"
        )
        type_ranges: dict[int, list[tuple[int,int,int]]] = {}
        for type_id, scale_id, min_s, max_s in ranges:
            type_ranges.setdefault(type_id, []).append((scale_id, min_s, max_s))

        valid = [
            t for t, conds in type_ranges.items()
            if all(min_s <= scores[sid] <= max_s for sid, min_s, max_s in conds)
        ]

        # 3. Решаем, какой код выдавать
        if valid:
            row = await self.db.fetch_one(
                "SELECT type_code FROM personality_types WHERE id = ?", (valid[0],)
            )
            mbti = row["type_code"] if row else "????"
        else:
            # жёсткая логика «большинства» по парам (1 vs 2), (3 vs 4), …
            mbti = (
                ("E" if scores[1] >= scores[2] else "I") +
                ("S" if scores[3] >= scores[4] else "N") +
                ("T" if scores[5] >= scores[6] else "F") +
                ("J" if scores[7] >= scores[8] else "P")
            )

        # 4. Сохраняем результат
        await self.db.execute(
            """
            INSERT INTO user_results
                (user_id, type_id,
                 e_score, i_score, s_score, n_score,
                 t_score, f_score, j_score, p_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                type_id=excluded.type_id,
                e_score=excluded.e_score,
                i_score=excluded.i_score,
                s_score=excluded.s_score,
                n_score=excluded.n_score,
                t_score=excluded.t_score,
                f_score=excluded.f_score,
                j_score=excluded.j_score,
                p_score=excluded.p_score
            """,
            (user_id, mbti, *(scores[i] for i in range(1, 9)))
        )

        return mbti

    async def get_personality_by_type_code(self, type_code: str) -> dict: # type: ignore
        row = await self.db.fetch_one(
            """
            SELECT type_name, description, strengths, weaknesses,
                   professional_qualities, percentage
            FROM personality_types
            WHERE type_code = ?
            """,
            (type_code,)
        )
        if not row:
            return {
                "type_code": type_code,
                "type_name": "",
                "description": "",
                "strengths": "",
                "weaknesses": "",
                "professional_qualities": "",
                "percentage": 0.0
            } # type: ignore
        return {"type_code": type_code, **dict(row)} # type: ignore
    
    async def get_personality_info(self, user_id: int) -> dict[Any, Any]:
        mbti_code = await self.calculate_and_store_result(user_id)
        profile = await self.get_personality_by_type_code(mbti_code)
        return profile
