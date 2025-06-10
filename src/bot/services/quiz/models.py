from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Question:
    id: int
    question: str
    answer_1: str
    answer_2: str

@dataclass
class Answer:
    user_id: int
    question_id: int
    response_option: int
    response_time: Optional[float] = None
    def as_tuple(self, user_id: int) -> Tuple[int, int, int, Optional[float]]:
        return (user_id, self.question_id, self.response_option, self.response_time)