from datetime import date, timedelta
from typing import List
from .base import BaseRepository


class StatsRepository(BaseRepository):

    @classmethod
    async def compute_and_upsert(cls, user_id: int, week_start: date) -> dict:
        week_end = week_start + timedelta(days=6)
        agg = await cls._fetchrow(
            """
            SELECT COUNT(*)                                              AS total,
                   SUM(IF(status='done', 1, 0))                          AS done,
                   COALESCE(SUM(IF(status='done', duration_min, 0)), 0) / 60.0 AS hrs
            FROM   study_sessions
            WHERE  user_id=%s AND scheduled_date BETWEEN %s AND %s
            """, user_id, week_start, week_end)

        total = agg["total"] or 0
        done  = agg["done"]  or 0
        hrs   = float(agg["hrs"] or 0)
        pct   = round(done / total * 100, 2) if total else 0

        await cls._execute(
            """
            INSERT INTO weekly_stats
            (user_id, week_start, total_sessions, done_sessions,
             self_study_hrs, completion_pct)
            VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_sessions = VALUES(total_sessions),
                    done_sessions  = VALUES(done_sessions),
                    self_study_hrs = VALUES(self_study_hrs),
                    completion_pct = VALUES(completion_pct)
            """, user_id, week_start, total, done, hrs, pct)

        return {"week_start": week_start, "total_sessions": total,
                "done_sessions": done, "self_study_hrs": round(hrs, 1),
                "completion_pct": pct}

    @classmethod
    async def get_history(cls, user_id: int, weeks: int = 8) -> List[dict]:
        rows = await cls._fetch(
            """SELECT * FROM weekly_stats WHERE user_id=%s
               ORDER BY week_start DESC LIMIT %s""",
            user_id, weeks)
        return [dict(r) for r in rows]