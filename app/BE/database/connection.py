import aiomysql
from urllib.parse import urlparse
from app.BE.core.config import settings

_pool = None

def _parse_db_url():
    """Tách DATABASE_URL an toàn tuyệt đối bằng urlparse, chấp mọi loại lỗi chuỗi."""
    try:
        # Lấy chuỗi kết nối thực tế đã được Pydantic parse từ .env
        db_url = settings.DATABASE_URL

        # Sử dụng thư viện chuẩn của Python để parse URL thay vì split thủ công dễ sập
        result = urlparse(db_url)

        host = result.hostname or "localhost"
        port = result.port or 3306
        user = result.username or "root"
        password = result.password or ""
        db = result.path.lstrip("/")

        return host, port, user, password, db
    except Exception as e:
        # Nếu có lỗi, in ra để debug ngay lập tức nhưng gán mock an toàn để app không sập cứng
        print(f"[Critical] Lỗi parse DATABASE_URL: {e}. Đang dùng cấu hình dự phòng!")
        return "localhost", 3306, "root", "18102006", "smartstudyai_db"

async def init_pool():
    global _pool
    host, port, user, password, db = _parse_db_url()
    try:
        _pool = await aiomysql.create_pool(
            host=host, port=port, user=user, password=password, db=db,
            minsize=2, maxsize=15, autocommit=True,
        )
        print("[Success] Kết nối cơ sở dữ liệu MySQL thành công xé gió! 🎉")
    except Exception as e:
        print(f"[Warning] Không thể kết nối đến MySQL thực tế: {e}")
        # Không gán _pool để hệ thống tự kích hoạt cơ chế Mock ở FE chống sập app

async def close_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None

async def _get():
    if _pool is None:
        await init_pool()
    return _pool

# ── Helpers ────────────────────────────────────────────────────────────

async def fetchrow(q: str, *a):
    pool = await _get()
    if pool is None: return None
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(q, a)
            return await cur.fetchone()

async def fetch(q: str, *a):
    pool = await _get()
    if pool is None: return []
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(q, a)
            return await cur.fetchall()

async def execute(q: str, *a):
    pool = await _get()
    if pool is None: return 0
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(q, a)
            return cur.lastrowid

async def executemany(q: str, params: list):
    pool = await _get()
    if pool is None: return 0
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(q, params)
            await conn.commit()
            return cur.rowcount