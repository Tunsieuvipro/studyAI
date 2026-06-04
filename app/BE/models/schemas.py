from __future__ import annotations
from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

#AUTH
class RegisterIn(BaseModel):
    student_id: str  = Field(..., example="K.AI212")
    full_name:  str
    email:      EmailStr
    password:   str  = Field(..., min_length=6)
    gender:     Optional[str] = "other"
    security_question: Optional[str] = None
    security_answer: Optional[str] = None

class LoginIn(BaseModel):
    email:    EmailStr
    password: str

class TokenOut(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

#CÀI ĐẶT
class UserOut(BaseModel):
    id:                 int
    student_id:         str
    full_name:          str
    email:              str
    gender:             Optional[str] = None
    birth_date:         Optional[date] = None
    phone:              Optional[str] = None
    university:         Optional[str] = None
    major:              Optional[str] = None
    avatar_url:         Optional[str] = None
    theme:              str
    created_at:         datetime
    class Config: from_attributes = True

class ProfileUpdateIn(BaseModel):
    """Cài đặt → Chỉnh sửa thông tin"""
    full_name:   str
    gender:      Optional[str]
    birth_date:  Optional[date]
    phone:       Optional[str]
    university:  Optional[str]
    major:       Optional[str]

class PasswordChangeIn(BaseModel):
    """Cài đặt → Đổi mật khẩu"""
    current_password: str
    new_password:     str = Field(..., min_length=6)
    confirm_password: str

#SUBJECT
class SubjectOut(BaseModel):
    id: int; code: str; name: str
    category: str; difficulty: int; credits: int; color: str
    class Config: from_attributes = True

#LICH HỌC
class TimetableEntryIn(BaseModel):
    subject_id: int
    weekday:    int = Field(..., ge=1, le=7)
    start_time: time
    end_time:   time
    room:       Optional[str]
    entry_type: str = Field("LT", pattern="^(LT|BT|TH)$")

class TimetableEntryOut(TimetableEntryIn):
    id:            int
    subject_name:  Optional[str]
    subject_color: Optional[str]
    class Config: from_attributes = True

class BulkTimetableIn(BaseModel):
    semester: str
    entries:  List[TimetableEntryIn]

class WeekCalendarOut(BaseModel):
    """Response gộp TKB + lịch học AI cho 1 tuần."""
    week_start:   date
    week_end:     date
    school_slots: List[dict]
    study_slots:  List[dict]

#AI SCHEDULER
class SchedulerIn(BaseModel):
    week_start:      date
    preferred_slots: Optional[List[str]] = None  # ["morning","evening"]

class StudySessionOut(BaseModel):
    id:             int
    subject_id:     int
    subject_name:   Optional[str]
    subject_color:  Optional[str]
    scheduled_date: date
    start_time:     time
    end_time:       time
    duration_min:   int
    status:         str
    generated_by:   str
    note:           Optional[str]
    class Config: from_attributes = True

class SessionMarkIn(BaseModel):
    status: str = Field(..., pattern="^(done|missed)$")

class SessionRescheduleIn(BaseModel):
    new_date:  date
    new_start: time
    new_end:   time

class SchedulerOut(BaseModel):
    sessions: List[StudySessionOut]
    warnings: List[str] = []
    overload: bool      = False

#TỔNG QUAN NVU HÔM NAY
class TaskIn(BaseModel):
    subject_id:  Optional[int]
    title:       str
    description: Optional[str]
    due_date:    Optional[datetime]
    priority:    int = Field(2, ge=1, le=3)

class TaskOut(TaskIn):
    id:           int
    status:       str
    subject_name: Optional[str]
    created_at:   datetime
    class Config: from_attributes = True

#THỐNG KÊ HÀNG TUẦN
class WeeklyStatsOut(BaseModel):
    week_start:      date
    total_sessions:  int
    done_sessions:   int
    self_study_hrs:  float
    completion_pct:  float   # 0–100

#TÀI LIỆU
class DocumentOut(BaseModel):
    id:             int
    title:          str
    description:    Optional[str]
    file_type:      str
    file_size_mb:   Optional[float]
    grade_level:    Optional[str]
    doc_category:   str
    exam_type:      Optional[str]
    tags:           Optional[List[str]]
    ai_summary:     Optional[str]
    download_count: int
    view_count:     int
    subject_name:   Optional[str]
    subject_code:   Optional[str]
    uploader_name:  Optional[str]
    created_at:     datetime
    class Config: from_attributes = True

class DocumentSummaryStats(BaseModel):
    total:      int
    pdf_count:  int
    word_count: int
    recent:     int

class AISummaryOut(BaseModel):
    summary: str

class AIAnalysisOut(BaseModel):
    analysis: str

class AIPracticeOut(BaseModel):
    questions: str

class AISolveOut(BaseModel):
    answer: str

#TRỢ LÝ AI
class ChatSessionOut(BaseModel):
    id:           int
    title:        str
    last_message: Optional[str]
    updated_at:   datetime
    class Config: from_attributes = True

class ChatMessageOut(BaseModel):
    id:              int
    role:            str
    content:         str
    attachment_url:  Optional[str]
    attachment_name: Optional[str]
    liked:           Optional[bool]
    created_at:      datetime
    class Config: from_attributes = True

class ChatSendIn(BaseModel):
    session_id:      Optional[int] = None   # None → tạo session mới
    message:         str
    attachment_url:  Optional[str] = None
    attachment_name: Optional[str] = None

class ChatSendOut(BaseModel):
    session_id:   int
    user_msg_id:  int
    ai_msg_id:    int
    reply:        str

class LikeIn(BaseModel):
    liked: Optional[bool]   # True=Like, False=Dislike, None=reset

#NOTIFICATION
class NotificationOut(BaseModel):
    id:         int
    title:      str
    body:       Optional[str]
    type:       str
    is_read:    bool
    created_at: datetime
    class Config: from_attributes = True


class EnrollmentCreate(BaseModel):
    subject_id: int
    difficulty: Optional[int] = None
    exam_date:  Optional[date] = None

