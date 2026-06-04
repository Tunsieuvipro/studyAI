from datetime import date
from typing import List, Optional
from .base import BaseRepository

class SessionRepository(BaseRepository):

    @classmethod
    async def get_by_week(cls, user_id: int,
                          week_start: date, week_end: date) -> List[dict]:
        rows = await cls._fetch(
            """
            SELECT ss.*, s.name AS subject_name,
                   s.color AS subject_color, s.code AS subject_code
            FROM   study_sessions ss
                       LEFT JOIN subjects s ON s.id = ss.subject_id
            WHERE  ss.user_id=%s
              AND  ss.scheduled_date BETWEEN %s AND %s
            ORDER  BY ss.scheduled_date, ss.start_time
            """, user_id, week_start, week_end)
        return [dict(r) for r in rows]

    @classmethod
    async def get_by_id(cls, session_id: int, user_id: int) -> Optional[dict]:
        row = await cls._fetchrow(
            "SELECT * FROM study_sessions WHERE id=%s AND user_id=%s",
            session_id, user_id)
        return dict(row) if row else None

    @classmethod
    async def bulk_insert(cls, rows: list) -> None:
        await cls._executemany(
            """
            INSERT INTO study_sessions
            (user_id, subject_id, scheduled_date, start_time, end_time,
             duration_min, status, generated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, rows)

    @classmethod
    async def delete_ai_week(cls, user_id: int,
                             week_start: date, week_end: date) -> None:
        await cls._execute(
            """DELETE FROM study_sessions
               WHERE user_id=%s AND generated_by='ai'
                 AND scheduled_date BETWEEN %s AND %s""",
            user_id, week_start, week_end)

    @classmethod
    async def update_status(cls, session_id: int,
                            user_id: int, status: str) -> bool:
        r = await cls._execute(
            """UPDATE study_sessions
               SET status=%s, updated_at=NOW()
               WHERE id=%s AND user_id=%s""",
            status, session_id, user_id)
        return r == "UPDATE 1"

    @classmethod
    async def reschedule(cls, session_id: int, user_id: int,
                         new_date: date, new_start, new_end) -> bool:
        r = await cls._execute(
            """UPDATE study_sessions
               SET scheduled_date=%s, start_time=%s, end_time=%s,
                   status='rescheduled', updated_at=NOW()
               WHERE id=%s AND user_id=%s""",
            new_date, new_start, new_end, session_id, user_id)
        return r == "UPDATE 1"

    @classmethod
    async def weekly_summary(cls, user_id: int,
                             week_start: date, week_end: date) -> dict:
        row = await cls._fetchrow(
            """
            SELECT COUNT(*)                                     AS total,
                   SUM(IF(status='done', 1, 0))                 AS done,
                   COALESCE(SUM(IF(status='done', duration_min, 0)), 0) AS done_min
            FROM   study_sessions
            WHERE  user_id=%s AND scheduled_date BETWEEN %s AND %s
            """, user_id, week_start, week_end)
        return dict(row) if row else {"total": 0, "done": 0, "done_min": 0}
