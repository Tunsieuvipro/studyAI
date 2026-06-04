"""app/database/repositories/enrollment_repo.py"""
from typing import List, Optional
from .base import BaseRepository


class EnrollmentRepository(BaseRepository):

    @classmethod
    async def get_by_user(cls, user_id: int,
                          semester: Optional[str] = None) -> List[dict]:
        extra = "AND e.semester=%s" if semester else ""
        args  = [user_id, semester] if semester else [user_id]
        rows  = await cls._fetch(
            f"""
            SELECT e.*, s.name AS subject_name, s.color AS subject_color,
                   s.code AS subject_code,
                   COALESCE(e.difficulty, s.difficulty) AS eff_difficulty
            FROM   enrollments e
            JOIN   subjects s ON s.id = e.subject_id
            WHERE  e.user_id=%s {extra}
            ORDER  BY s.name
            """, *args)
        return [dict(r) for r in rows]

    @classmethod
    async def upsert(cls, user_id: int, subject_id: int,
                     difficulty: Optional[int], exam_date,
                     semester: str) -> int:
        row = await cls._fetchrow(
            """
            INSERT INTO enrollments (user_id, subject_id, difficulty, exam_date, semester)
            VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    difficulty = VALUES(difficulty),
                    exam_date  = VALUES(exam_date)
            """,
            user_id, subject_id, difficulty, exam_date, semester)
        last_id_row = await cls._fetchrow("SELECT LAST_INSERT_ID() AS id")

        if not last_id_row or last_id_row["id"] == 0:
            fallback = await cls._fetchrow(
                "SELECT id FROM enrollments WHERE user_id=%s AND subject_id=%s AND semester=%s",
                user_id, subject_id, semester
            )
            return fallback["id"] if fallback else 0

        return last_id_row["id"] if last_id_row else 0

    @classmethod
    async def delete(cls, eid: int, user_id: int) -> bool:
        r = await cls._execute(
            "DELETE FROM enrollments WHERE id=%s AND user_id=%s", eid, user_id)
        return r == "DELETE 1"

    @classmethod
    async def update_priority(cls, eid: int, score: float) -> None:
        await cls._execute(
            "UPDATE enrollments SET priority_score=%s WHERE id=%s", score, eid)