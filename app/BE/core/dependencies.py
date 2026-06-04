from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.BE.core.security import decode_token
from app.BE.database.repositories.user_repo import UserRepository

bearer = HTTPBearer()


async def get_current_user(
        cred: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    payload = decode_token(cred.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token không hợp lệ hoặc đã hết hạn")
    user = await UserRepository.get_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    return user


async def get_current_user_id(user: dict = Depends(get_current_user)) -> int:
    return user["id"]


@dataclass
class Pagination:
    limit:  int = 20
    offset: int = 0

def pagination(limit: int = 20, offset: int = 0) -> Pagination:
    return Pagination(limit=min(limit, 100), offset=max(offset, 0))
