from typing import List, Optional
from .base import BaseRepository


class ChatRepository(BaseRepository):

    # ── Sessions (Lịch sử hội thoại) ─────────────────────────────────────────

    @classmethod
    async def get_sessions(cls, user_id: int,
                           limit: int = 20, offset: int = 0) -> List[dict]:
        rows = await cls._fetch(
            """
            SELECT cs.id, cs.title, cs.created_at, cs.updated_at,
                   (SELECT content FROM chat_messages
                    WHERE session_id=cs.id ORDER BY created_at DESC LIMIT 1)
                   AS last_message
            FROM   chat_sessions cs
            WHERE  cs.user_id=%s
            ORDER  BY cs.updated_at DESC
                LIMIT  %s OFFSET %s
            """, user_id, limit, offset)
        return [dict(r) for r in rows]

    @classmethod
    async def create_session(cls, user_id: int, title: str = "Hội thoại mới") -> int:
        return await cls._execute(
            "INSERT INTO chat_sessions (user_id, title) VALUES (%s, %s)",
            user_id, title)

    @classmethod
    async def update_session_title(cls, session_id: int,
                                   user_id: int, title: str) -> None:
        await cls._execute(
            "UPDATE chat_sessions SET title=%s, updated_at=NOW() WHERE id=%s AND user_id=%s",
            title, session_id, user_id)

    @classmethod
    async def touch_session(cls, session_id: int) -> None:
        await cls._execute(
            "UPDATE chat_sessions SET updated_at=NOW() WHERE id=%s", session_id)

    @classmethod
    async def delete_session(cls, session_id: int, user_id: int) -> bool:
        # Xóa toàn bộ tin nhắn thuộc phiên chat trước để tránh lỗi khóa ngoại
        await cls._execute("DELETE FROM chat_messages WHERE session_id=%s", session_id)
        # Xóa phiên chat chính
        await cls._execute("DELETE FROM chat_sessions WHERE id=%s AND user_id=%s", session_id, user_id)
        return True

    # ── Messages ──────────────────────────────────────────────────────────────

    @classmethod
    async def get_messages(cls, session_id: int,
                           limit: int = 100, offset: int = 0) -> List[dict]:
        rows = await cls._fetch(
            """
            SELECT id, role, content, attachment_url, attachment_name, liked, created_at
            FROM   chat_messages
            WHERE  session_id=%s
            ORDER  BY created_at ASC
                LIMIT  %s OFFSET %s
            """, session_id, limit, offset)
        return [dict(r) for r in rows]

    @classmethod
    async def add_message(cls, session_id: int, role: str,
                          content: str,
                          attachment_url: Optional[str] = None,
                          attachment_name: Optional[str] = None) -> int:
        last_id = await cls._execute(
            """
            INSERT INTO chat_messages
              (session_id, role, content, attachment_url, attachment_name)
            VALUES (%s, %s, %s, %s, %s)
            """, session_id, role, content, attachment_url, attachment_name)
        await cls.touch_session(session_id)
        return last_id

    @classmethod
    async def set_liked(cls, message_id: int, liked: Optional[bool]) -> None:
        """Like (True) / Dislike (False) / reset (None) một phản hồi AI."""
        await cls._execute(
            "UPDATE chat_messages SET liked=%s WHERE id=%s", liked, message_id)

    # ── Lấy lịch sử để gửi kèm API ───────────────────────────────────

    @classmethod
    async def get_history_for_api(cls, session_id: int,
                                  last_n: int = 20) -> List[dict]:
        """Trả về list {"role": ..., "content": ...} để nhét vào messages[]."""
        rows = await cls._fetch(
            """
            SELECT role, content FROM chat_messages
            WHERE  session_id=%s
            ORDER  BY created_at DESC
                LIMIT  %s
            """, session_id, last_n)
        return [{"role": r["role"], "content": r["content"]}
                for r in reversed(rows)]

    @classmethod
    async def send_message(cls, session_id, role, content, attachment_url, attachment_name):
        pass