from datetime import date, timedelta
from typing import List, Optional
from .base import BaseRepository

class TimetableRepository(BaseRepository):

    @classmethod
    async def get_by_user(cls, user_id: int) -> List[dict]:
        rows  = await cls._fetch(
            f"""
            SELECT te.id, te.title AS subject_name, te.start_date, te.end_date,
                   te.start_time, te.end_time,
                   te.room, te.entry_type, te.note,
                   '#ff9f43' AS subject_color, '' AS subject_code
            FROM   timetable_entries te
            WHERE  te.user_id = %s
            ORDER  BY te.start_date, te.start_time
            """, user_id)
            
        res = []
        for r in rows:
            d = dict(r)
            # Tính toán weekday động dựa trên ngày bắt đầu
            sd = d.get("start_date")
            if sd:
                if isinstance(sd, str):
                    from datetime import datetime
                    d["weekday"] = datetime.strptime(sd, "%Y-%m-%d").date().weekday() + 1
                elif isinstance(sd, date):
                    d["weekday"] = sd.weekday() + 1
                else:
                    d["weekday"] = 1
            else:
                d["weekday"] = 1
            res.append(d)
        return res

    @classmethod
    async def get_week_combined(cls, user_id: int,
                                week_start: date) -> List[dict]:
        """
        Trả về TKB trường + lịch học AI của tuần, đã gộp,
        để hiển thị trên lịch học tập (Tổng quan).
        """
        week_end = week_start + timedelta(days=6)

        rows = await cls._fetch(
            """
            SELECT te.start_date, te.end_date,
                   te.start_time, te.end_time, te.room, te.entry_type,
                   te.title AS subject_name, '' AS subject_code,
                   '#ff9f43' AS subject_color,
                   'school' AS source
            FROM   timetable_entries te
            WHERE  te.user_id = %s
            """, user_id)

        school_rows = []
        for r in rows:
            d = dict(r)
            sd = d.get("start_date")
            if sd:
                if isinstance(sd, str):
                    from datetime import datetime
                    s_date_obj = datetime.strptime(sd, "%Y-%m-%d").date()
                else:
                    s_date_obj = sd
                
                # Tính weekday và entry_date
                weekday = s_date_obj.weekday() + 1
                d["weekday"] = weekday
                d["entry_date"] = week_start + timedelta(days=(weekday - 1))
                school_rows.append(d)

        # Giữ nguyên phần bốc lịch học AI từ study_sessions
        study_rows = await cls._fetch(
            """
            SELECT (WEEKDAY(ss.scheduled_date) + 1) AS weekday,
                   ss.scheduled_date AS entry_date,
                   ss.start_time, ss.end_time,
                   NULL AS room, 'self' AS entry_type,
                   s.name AS subject_name, s.code AS subject_code,
                   s.color AS subject_color,
                   'study' AS source, ss.status, ss.id AS session_id
            FROM   study_sessions ss
                       LEFT JOIN subjects s ON s.id = ss.subject_id
            WHERE  ss.user_id = %s
              AND  ss.scheduled_date BETWEEN %s AND %s
              AND  ss.status != 'missed'
            ORDER  BY ss.scheduled_date, ss.start_time
            """, user_id, week_start, week_end)

        return school_rows + [dict(r) for r in study_rows]

    @classmethod
    async def get_by_date_range(cls, user_id: int,
                                date_from: date, date_to: date) -> List[dict]:
        """Kiểm tra lịch theo ngày """
        rows = await cls._fetch(
            """
            SELECT te.start_date, te.start_time, te.end_time,
                   te.room, te.entry_type,
                   te.title AS subject_name, '' AS subject_code,
                   '#ff9f43' AS subject_color
            FROM   timetable_entries te
            WHERE  te.user_id = %s
            """, user_id)
            
        res = []
        for r in rows:
            d = dict(r)
            sd = d.get("start_date")
            if sd:
                if isinstance(sd, str):
                    from datetime import datetime
                    s_date_obj = datetime.strptime(sd, "%Y-%m-%d").date()
                else:
                    s_date_obj = sd
                
                weekday = s_date_obj.weekday() + 1
                # Kiểm tra xem thứ có nằm trong range không
                if (date_from.weekday() + 1) <= weekday <= (date_to.weekday() + 1):
                    d["weekday"] = weekday
                    res.append(d)
        return res

    @classmethod
    async def create(cls, user_id: int, title: str, start_date, end_date,
                     start_time, end_time, room: str,
                     entry_type: str, note: str) -> int:
        await cls._fetchrow(
            """
            INSERT INTO timetable_entries
            (user_id, title, start_date, end_date, start_time,
             end_time, room, entry_type, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, user_id, title, start_date, end_date, start_time,
            end_time, room, entry_type, note)
        row = await cls._fetchrow(
            "SELECT MAX(id) AS id FROM timetable_entries WHERE user_id = %s", user_id)
        return row["id"] if row else 0

    @classmethod
    async def delete(cls, entry_id: int, user_id: int) -> bool:
        r = await cls._execute(
            "DELETE FROM timetable_entries WHERE id = %s AND user_id = %s",
            entry_id, user_id)
        return r == "DELETE 1"
