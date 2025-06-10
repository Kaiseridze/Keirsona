import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, List, Sequence

import aiosqlite
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

class Cursor:
    db_path: str

    def __init__(self, db_path: str | None = None) -> None:
        path = db_path or os.getenv("DB_PATH")
        if not path:
            raise ValueError("Environment variable DB_PATH is not set")
        self.db_path = str(Path(path))

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        logger.debug("Opening DB connection at %s", self.db_path)
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
            await conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            await conn.rollback()
            logger.error("Transaction rolled back due to error: %s", e, exc_info=True)
            raise
        finally:
            await conn.close()
            logger.debug("Connection closed")

    async def fetch_all(
        self,
        query: str,
        params: Sequence[Any] = ()
    ) -> List[aiosqlite.Row]:

        async with self.connection() as conn:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()
            return list(rows)

    async def fetch_one(
        self,
        query: str,
        params: Sequence[Any] = ()
    ) -> aiosqlite.Row | None:
        
        async with self.connection() as conn:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            await cursor.close()
            return row

    async def execute(self, query: str, params: Sequence[Any] = ()) -> None:
        async with self.connection() as conn:
            await conn.execute(query, params)

    async def execute_many(
        self,
        query: str,
        params_list: Sequence[Sequence[Any]]
    ) -> None:
                
        async with self.connection() as conn:
            await conn.executemany(query, params_list)
