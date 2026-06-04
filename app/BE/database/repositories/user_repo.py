from typing import Optional
from datetime import datetime
from .base import BaseRepository

class UserRepository(BaseRepository):

    #Read
    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional[dict]:
        row = await cls._fetchrow(
            """
            SELECT id, student_id, full_name, email, gender, birth_date,
                   phone, university, major, avatar_url,
                   theme, is_active, created_at
            FROM   users WHERE id = %s
            """, user_id)
        return dict(row) if row else None

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[dict]:
        row = await cls._fetchrow("SELECT * FROM users WHERE email = %s", email)
        return dict(row) if row else None

    @classmethod
    async def get_by_student_id(cls, sid: str) -> Optional[dict]:
        row = await cls._fetchrow(
            "SELECT * FROM users WHERE student_id = %s", sid)
        return dict(row) if row else None

    #Create
    @classmethod
    async def create(cls, student_id: str, full_name: str,
                     email: str, password_hash: str, gender: str = "other",
                     security_question: Optional[str] = None,
                     security_answer: Optional[str] = None) -> int:
        await cls._fetchrow(
            """
            INSERT INTO users (student_id, full_name, email, password_hash, gender, security_question, security_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, student_id, full_name, email, password_hash, gender, security_question, security_answer)
        user = await cls.get_by_email(email)
        return user["id"] if user else 0


    # Update profile (Cài đặt → Chỉnh sửa)
    @classmethod
    async def update_profile(cls, user_id: int, full_name: str,
                             gender: str, birth_date, phone: str,
                             university: str, major: str) -> None:
        await cls._execute(
            """
            UPDATE users
            SET    full_name=%s, gender=%s, birth_date=%s,
                   phone=%s, university=%s, major=%s, updated_at=NOW()
            WHERE  id=%s
            """, full_name, gender, birth_date, phone, university, major, user_id)

    @classmethod
    async def update_avatar(cls, user_id: int, avatar_url: str) -> None:
        await cls._execute(
            "UPDATE users SET avatar_url=%s, updated_at=NOW() WHERE id=%s",
            avatar_url, user_id)

    @classmethod
    async def update_password(cls, user_id: int, new_hash: str) -> None:
        await cls._execute(
            "UPDATE users SET password_hash=%s, updated_at=NOW() WHERE id=%s",
            new_hash, user_id)


    #Settings (Cài đặt → Giao diện)
    @classmethod
    async def update_settings(cls, user_id: int, theme: str) -> None:
        await cls._execute(
            """
            UPDATE users
            SET theme=%s, updated_at=NOW()
            WHERE id=%s
            """, theme, user_id)


    #Refresh token
    @classmethod
    async def save_refresh_token(cls, user_id: int,
                                 token: str, expires_at: datetime) -> None:
        await cls._execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            user_id, token, expires_at)

    @classmethod
    async def get_refresh_token(cls, token: str) -> Optional[dict]:
        row = await cls._fetchrow(
            "SELECT * FROM refresh_tokens WHERE token=%s AND expires_at > NOW()", token)
        return dict(row) if row else None

    @classmethod
    async def delete_refresh_token(cls, token: str) -> None:
        await cls._execute("DELETE FROM refresh_tokens WHERE token=%s", token)

    @classmethod
    async def delete_all_refresh_tokens(cls, user_id: int) -> None:
        await cls._execute(
            "DELETE FROM refresh_tokens WHERE user_id=%s", user_id)
