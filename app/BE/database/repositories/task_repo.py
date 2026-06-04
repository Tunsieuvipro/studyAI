from datetime import datetime
from typing import List, Optional
from .base import BaseRepository

class TaskRepository(BaseRepository):

    @classmethod
    async def get_today(cls, user_id: int) -> List[dict]:
        now = datetime.now()
        rows = await cls._fetch(
            """
            SELECT t.*, s.name AS subject_name, s.code AS subject_code
            FROM   tasks t
                       LEFT JOIN subjects s ON s.id = t.subject_id
            WHERE  t.user_id = %s
              AND (DATE(t.due_date) = %s
                OR (t.due_date < %s AND t.status = 'pending'))
            ORDER  BY t.priority DESC, t.due_date ASC
            """, user_id, now.date(), now)
        return [dict(r) for r in rows]

    @classmethod
    async def get_all(cls, user_id: int, status: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> List[dict]:
        extra = "AND t.status = %s" if status else ""
        args  = [user_id, status, limit, offset] if status else [user_id, limit, offset]
        li    = 3 if status else 2
        of    = 4 if status else 3
        rows  = await cls._fetch(
            f"""
            SELECT t.*, s.name AS subject_name
            FROM   tasks t
            LEFT JOIN subjects s ON s.id = t.subject_id
            WHERE  t.user_id = %s {extra}
            ORDER  BY ISNULL(t.due_date) ASC, t.due_date ASC
            LIMIT  %s OFFSET %s
            """, *args)
        return [dict(r) for r in rows]

    @classmethod
    async def create(cls, user_id: int, subject_id: Optional[int],
                     title: str, description: Optional[str],
                     due_date, priority: int) -> int:
        row = await cls._fetchrow(
            """
            INSERT INTO tasks (user_id, subject_id, title, description, due_date, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, user_id, subject_id, title, description, due_date, priority)
        # Lấy lại ID lớn nhất vừa đẻ ra của User này trong bảng tasks
        row = await cls._fetchrow(
            "SELECT MAX(id) AS id FROM tasks WHERE user_id = %s", user_id)
        return row["id"] if row else 0

    @classmethod
    async def set_status(cls, task_id: int, user_id: int, status: str) -> bool:
        r = await cls._execute(
            "UPDATE tasks SET status = %s, updated_at = NOW() WHERE id = %s AND user_id = %s",
            status, task_id, user_id)
        return r == "UPDATE 1"

    @classmethod
    async def delete(cls, task_id: int, user_id: int) -> bool:
        r = await cls._execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s", task_id, user_id)
        return r == "DELETE 1"

    @classmethod
    async def mark_overdue_batch(cls) -> int:
        r = await cls._execute(
            """UPDATE tasks SET status='overdue', updated_at=NOW()
               WHERE due_date < NOW() AND status='pending'""")
        return int(r.split()[-1])
