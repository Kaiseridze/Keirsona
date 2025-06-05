from dataclasses import dataclass

@dataclass
class Question:
    id: int
    question: str
    answer_1: str
    answer_2: str
