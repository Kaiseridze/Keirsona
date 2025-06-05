from src.db.cursor import Cursor

class UserInstance(Cursor):
    def __init__(self):
        super().__init__()
    
    def find_user(self, user_id: int) -> bool:
        self.cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone() is not None
    
    def add_user(self, user_id: int) -> None:
        self.cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        self.connection.commit()
        self.connection.close()
