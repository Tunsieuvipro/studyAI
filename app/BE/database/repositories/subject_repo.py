"""app/database/repositories/subject_repo.py"""
from typing import Optional, List
from .base import BaseRepository


class SubjectRepository(BaseRepository):

    @classmethod
    async def get_all(cls) -> List[dict]:
        rows = await cls._fetch(
            "SELECT * FROM subjects ORDER BY category, name")
        return [dict(r) for r in rows]

    @classmethod
    async def get_by_id(cls, sid: int) -> Optional[dict]:
        row = await cls._fetchrow("SELECT * FROM subjects WHERE id=%s", sid)
        return dict(row) if row else None

    @classmethod
    async def get_by_code(cls, code: str) -> Optional[dict]:
        row = await cls._fetchrow("SELECT * FROM subjects WHERE code=%s", code)
        return dict(row) if row else None

    @classmethod
    async def create(cls, code: str, name: str, category: str,
                     difficulty: int, credits: int, color: str) -> int:
        row = await cls._fetchrow(
            """INSERT INTO subjects (code,name,category,difficulty,credits,color)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            code, name, category, difficulty, credits, color)
        row = await cls._fetchrow("SELECT LAST_INSERT_ID() AS id")
        return row["id"] if isinstance(row, dict) else row[0]