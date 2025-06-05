import sqlite3
import dotenv
import os

dotenv.load_dotenv()

class Cursor:
    def __init__(self):
        self.__db_path = os.getenv('DB_PATH')
        self.connection = sqlite3.connect(str(self.__db_path))
        self.cursor = self.connection.cursor()
    


