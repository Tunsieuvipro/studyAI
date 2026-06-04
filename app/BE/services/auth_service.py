from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.BE.core.security import (hash_password, verify_password,
                               create_access_token, create_refresh_token,
                               decode_token)
from app.BE.core.config import settings
from app.BE.database.repositories.user_repo import UserRepository
from app.BE.models.schemas import RegisterIn, LoginIn, TokenOut

async def register(payload: RegisterIn) -> dict:
    if await UserRepository.get_by_email(payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email đã được sử dụng")
    if await UserRepository.get_by_student_id(payload.student_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Mã sinh viên đã tồn tại")

    uid = await UserRepository.create(
        payload.student_id, payload.full_name,
        payload.email, hash_password(payload.password),
        payload.gender,
        security_question=payload.security_question,
        security_answer=payload.security_answer)
    return {"id": uid, "message": "Đăng ký thành công"}


async def reset_password_via_security_question(email: str, student_id: str, question: str, answer: str, new_password: str) -> None:
    user = await UserRepository.get_by_email(email)
    if not user or user["student_id"] != student_id:
        raise HTTPException(400, "Thông tin email hoặc mã sinh viên không đúng")
    
    db_question = user.get("security_question")
    db_answer = user.get("security_answer")
    
    if not db_question or not db_answer:
        raise HTTPException(400, "Tài khoản chưa được thiết lập câu hỏi bảo mật")
        
    if db_question != question or db_answer.strip().lower() != answer.strip().lower():
        raise HTTPException(400, "Câu hỏi hoặc câu trả lời bảo mật không chính xác")
        
    await UserRepository.update_password(user["id"], hash_password(new_password))


async def login(payload: LoginIn) -> TokenOut:
    user = await UserRepository.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Email hoặc mật khẩu không đúng")
    if not user["is_active"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản đã bị khoá")

    access  = create_access_token(user["id"], user["email"])
    refresh = create_refresh_token(user["id"])
    exp     = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await UserRepository.save_refresh_token(user["id"], refresh, exp)
    return TokenOut(access_token=access, refresh_token=refresh)


async def refresh(token: str) -> TokenOut:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token không hợp lệ")

    stored = await UserRepository.get_refresh_token(token)
    if not stored:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token đã hết hạn")

    user = await UserRepository.get_by_id(int(payload["sub"]))
    await UserRepository.delete_refresh_token(token)

    new_access  = create_access_token(user["id"], user["email"])
    new_refresh = create_refresh_token(user["id"])
    exp = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await UserRepository.save_refresh_token(user["id"], new_refresh, exp)
    return TokenOut(access_token=new_access, refresh_token=new_refresh)


async def logout(user_id: int) -> None:
    await UserRepository.delete_all_refresh_tokens(user_id)


async def change_password(user_id: int, current: str,
                          new_pw: str, confirm: str) -> None:
    if new_pw != confirm:
        raise HTTPException(400, "Mật khẩu xác nhận không khớp")
    user = await UserRepository.get_by_id(user_id)
    # need password_hash → full fetch
    from app.BE.database.connection import fetchrow
    row = await fetchrow("SELECT password_hash FROM users WHERE id=%s", user_id)
    if not verify_password(current, row["password_hash"]):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng")
    await UserRepository.update_password(user_id, hash_password(new_pw))


async def get_user_profile(user_id: int) -> dict:
    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")
    return user


async def update_user_profile(user_id: int, full_name: str, gender: str, birth_date, phone: str, university: str, major: str) -> None:
    await UserRepository.update_profile(user_id, full_name, gender, birth_date, phone, university, major)


async def update_user_settings(user_id: int, theme: str) -> None:
    await UserRepository.update_settings(user_id, theme)


async def delete_user_account(user_id: int) -> None:
    await UserRepository.delete_all_refresh_tokens(user_id)
    from app.BE.database.connection import execute
    await execute("DELETE FROM users WHERE id=%s", user_id)