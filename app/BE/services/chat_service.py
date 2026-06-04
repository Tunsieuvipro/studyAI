from __future__ import annotations

from typing import Optional
from fastapi import HTTPException

from app.BE.database.repositories.chat_repo import ChatRepository
from app.BE.services import ai_service
from app.BE.models.schemas import ChatSendIn, ChatSendOut


async def send_message(user_id: int, payload: ChatSendIn) -> ChatSendOut:
    # 1. Tạo session mới nếu cần
    session_id = payload.session_id
    if not session_id:
        # Tạo tiêu đề tạm từ 6 từ đầu
        preview = payload.message[:40].strip()
        session_id = await ChatRepository.create_session(user_id, preview or "Hội thoại mới")

    # 2. Lưu tin user
    await ChatRepository.send_message(
        session_id=session_id, role="user",
        content=payload.message,
        attachment_url=payload.attachment_url,
        attachment_name=payload.attachment_name,
    )

    # 3. Lấy lịch sử (tối đa 20 lượt) để gửi Claude
    history = await ChatRepository.get_history_for_api(session_id, last_n=20)
    # để mảng tuân theo đúng trục thời gian từ cũ đến mới cho AI đọc hiểu.
    history.reverse()
    # Tiến hành lưu tin nhắn mới của user vào Database
    user_msg_id = await ChatRepository.send_message(
        session_id=session_id,
        role="user", # Giữ nguyên 'user' ở tầng Service, hàm chuyển đổi sang Gemini sẽ tự lo ở tầng AI
        content=payload.message,
        attachment_url=payload.attachment_url,
        attachment_name=payload.attachment_name,
    )

    # 4. Gọi
    try:
        reply = await ai_service.chat_reply(
            history=history,
            new_message=payload.message,
        )
    except Exception as e:
        reply = "⚠️ AI đang gặp sự cố, vui lòng thử lại sau."

    # 5. Lưu tin AI
    ai_msg_id = await ChatRepository.send_message(
        session_id=session_id, role="assistant", content=reply)

    # 6. Cập nhật tiêu đề session nếu là session mới (dùng 6 từ đầu user)
    if not payload.session_id:
        short_title = payload.message[:60].strip() or "Hội thoại mới"
        await ChatRepository.update_session_title(session_id, user_id, short_title)

    return ChatSendOut(
        session_id=session_id,
        user_msg_id=user_msg_id,
        ai_msg_id=ai_msg_id,
        reply=reply,
    )


async def get_session_messages(session_id: int, user_id: int,
                               limit: int = 100) -> list:
    """Trả về toàn bộ tin nhắn trong 1 session."""
    sessions = await ChatRepository.get_sessions(user_id, limit=200)
    ids = [s["id"] for s in sessions]
    if session_id not in ids:
        raise HTTPException(403, "Không có quyền truy cập session này")
    return await ChatRepository.get_messages(session_id, limit=limit)