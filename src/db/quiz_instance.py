from src.db.cursor import Cursor
from src.db.models.Question import Question

class QuizInstance(Cursor):
    def __init__(self):
        super().__init__()
    
    def get_all_questions(self) -> list[Question]:
        data = self.cursor.execute("SELECT * FROM questions;")
        rows = data.fetchall()
        self.connection.close()
        return [Question(*row) for row in rows]
