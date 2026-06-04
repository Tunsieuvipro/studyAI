from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import List, Dict, Optional

from app.BE.core.config import settings
from app.BE.database.repositories.timetable_repo import TimetableRepository
from app.BE.database.repositories.session_repo    import SessionRepository
from app.BE.database.repositories.enrollment_repo import EnrollmentRepository

from app.BE.models.schemas import SchedulerOut, StudySessionOut

# ── helpers ───────────────────────────────────────────────────────────────────

def _tm(t: time) -> int:   return t.hour * 60 + t.minute
def _mt(m: int)  -> time:  return time(m // 60, m % 60)

DAY_START = 7 * 60
DAY_END   = 22 * 60 + 30


@dataclass
class _Block:
    weekday: int
    date:    date
    start:   time
    end:     time

    @property
    def dur(self) -> int:
        return _tm(self.end) - _tm(self.start)


@dataclass
class _SubjectMeta:
    subject_id:    int
    name:          str
    color:         str
    difficulty:    int
    days_to_exam:  int
    priority:      float = 0.0
    slots_needed:  int   = 0


# ── Priority formula ──────────────────────────────────────────────────────────

def _priority(difficulty: int, days_to_exam: int) -> float:
    """priority = 0.6×norm_diff + 0.4×urgency"""
    norm = difficulty / 5.0
    urg  = 1.0 / (days_to_exam + 1)
    return round(0.6 * norm + 0.4 * urg, 4)


# ── Free-slot finder ──────────────────────────────────────────────────────────

def _find_free(week_start: date, busy: List[_Block],
               preferred: Optional[List[str]]) -> List[_Block]:
    PREFERRED_WINDOWS = {
        "morning":   [(7,0,  9,0), (9,0,  11,0)],
        "afternoon": [(13,0, 15,0), (15,0, 17,0)],
        "evening":   [(19,0, 21,0), (21,0, 22,30)],
    }

    busy_map: Dict[int, List] = {d: [] for d in range(1, 8)}
    for b in busy:
        busy_map[b.weekday].append(
            (_tm(b.start), _tm(b.end) + settings.BREAK_MIN))

    free: List[_Block] = []
    SLOT = settings.SLOT_DURATION_MIN

    for wd in range(1, 8):
        day = week_start + timedelta(days=wd - 1)
        merged, cursor = [], DAY_START
        for s, e in sorted(busy_map[wd]):
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append([s, e])
        for bs, be in merged:
            if bs - cursor >= SLOT:
                free.append(_Block(wd, day, _mt(cursor), _mt(min(bs, DAY_END))))
            cursor = max(cursor, be)
        if DAY_END - cursor >= SLOT:
            free.append(_Block(wd, day, _mt(cursor), _mt(DAY_END)))

    # filter preferred periods
    if preferred:
        allowed = []
        for p in preferred:
            for r in PREFERRED_WINDOWS.get(p, []):
                allowed.append((r[0]*60+r[1], r[2]*60+r[3]))
        if allowed:
            free = [b for b in free
                    if any(lo <= _tm(b.start) < hi for lo, hi in allowed)]

    return free


def _split(block: _Block, dur: int, brk: int) -> List[_Block]:
    out, cursor, end = [], _tm(block.start), _tm(block.end)
    while end - cursor >= dur:
        out.append(_Block(block.weekday, block.date,
                          _mt(cursor), _mt(cursor + dur)))
        cursor += dur + brk
    return out


# ── Main entry ────────────────────────────────────────────────────────────────

async def generate_schedule(user_id: int, week_start: date,
                            preferred: Optional[List[str]] = None) -> SchedulerOut:
    SLOT = settings.SLOT_DURATION_MIN
    BRK  = settings.BREAK_MIN

    # 1. Lấy TKB trường
    entries  = await TimetableRepository.get_by_user(user_id)
    busy_raw = [
        _Block(e["weekday"],
               week_start + timedelta(days=e["weekday"]-1),
               e["start_time"], e["end_time"])
        for e in entries
    ]

    # 2. Tìm slot trống + chia nhỏ
    free_raw = _find_free(week_start, busy_raw, preferred)
    all_slots: List[_Block] = []
    for sl in free_raw:
        all_slots.extend(_split(sl, SLOT, BRK))

    # Cap per day
    daily: Dict[int,int] = {}
    capped = []
    for sl in all_slots:
        cnt = daily.get(sl.weekday, 0)
        if cnt * SLOT < settings.MAX_STUDY_MIN_PER_DAY:
            capped.append(sl); daily[sl.weekday] = cnt + 1
    all_slots = capped
    total_free = len(all_slots)

    # 3. Enrollments + priority
    rows = await EnrollmentRepository.get_by_user(user_id)
    today = date.today()
    subjects: List[_SubjectMeta] = []
    for r in rows:
        dl    = (r["exam_date"] - today).days if r["exam_date"] else 365
        dl    = max(0, dl)
        pri   = _priority(r["eff_difficulty"], dl)
        subjects.append(_SubjectMeta(
            subject_id=r["subject_id"], name=r["subject_name"],
            color=r["subject_color"], difficulty=r["eff_difficulty"],
            days_to_exam=dl, priority=pri))

    warnings, overload = [], False
    if not subjects or not all_slots:
        return SchedulerOut(sessions=[], warnings=["Không có môn học hoặc slot trống."])

    # 4. Phân bổ slot
    total_pri = sum(s.priority for s in subjects) or 1
    for s in subjects:
        s.slots_needed = max(1, round(s.priority / total_pri * total_free))
    while sum(s.slots_needed for s in subjects) > total_free:
        lowest = min(subjects, key=lambda x: x.priority)
        if lowest.slots_needed > 1: lowest.slots_needed -= 1
        else: break

    # 5. Assign
    slot_iter    = iter(all_slots)
    to_insert    = []
    sessions_out = []

    for subj in sorted(subjects, key=lambda x: -x.priority):
        for _ in range(subj.slots_needed):
            try: sl = next(slot_iter)
            except StopIteration: break
            to_insert.append((user_id, subj.subject_id, sl.date,
                              sl.start, sl.end, SLOT, "planned", "ai"))

            # 🚨 SỬA LẠI ĐOẠN ĐẨY DATA RA FE Ở ĐÂY CHO KHỚP CẢ KEY LẪN ĐỊNH DẠNG CHUỖI:
            sessions_out.append(StudySessionOut(
                id=0,
                user_id=user_id,
                subject_id=subj.subject_id,
                subject_name=subj.name,
                subject_color=subj.color,

                # 🔥 CHÍ MẠNG 1: Ép date thành chuỗi định dạng dd/MM/yyyy để giao diện FE lọc được
                scheduled_date=sl.date.strftime("%d/%m/%Y"),
                start_date=sl.date.strftime("%d/%m/%Y"), # Sinh thêm key này cho chắc cú giao diện đọc trúng!

                # 🔥 CHÍ MẠNG 2: Ép time thành chuỗi HH:mm
                start_time=sl.start.strftime("%H:%M"),
                end_time=sl.end.strftime("%H:%M"),

                duration_min=SLOT,
                status="planned",
                generated_by="ai",
                note=None
            ))

    # 6. Lưu DB
    week_end = week_start + timedelta(days=6)
    await SessionRepository.delete_ai_week(user_id, week_start, week_end)
    if to_insert:
        await SessionRepository.bulk_insert(to_insert)

    # 7. Warnings
    fill = len(sessions_out) / (total_free or 1)
    if fill >= settings.OVERLOAD_THRESHOLD:
        overload = True
        warnings.append(f"⚠️ Lịch đang dày ({round(fill*100)}%). Cân nhắc giảm bớt môn.")
    for s in subjects:
        if s.days_to_exam <= 3:
            warnings.append(f"🔥 Môn {s.name} còn {s.days_to_exam} ngày thi!")

    return SchedulerOut(sessions=sessions_out, warnings=warnings, overload=overload)