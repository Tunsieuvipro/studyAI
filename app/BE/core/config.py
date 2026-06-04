import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ENV_FILE_PATH = os.path.join(ROOT_DIR, ".env")

class Settings(BaseSettings):
    #App
    APP_NAME:    str  = "StudyAI"
    APP_VERSION: str  = "1.0.0"
    DEBUG:       bool = False

    #Database
    DATABASE_URL: str = "mysql+aiomysql://root:18102006@localhost:3306/smartstudyai_db"

    #JWT
    SECRET_KEY:                    str = "change-me-in-production"
    ALGORITHM:                     str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:   int = 60 * 24   # 1 ngày
    REFRESH_TOKEN_EXPIRE_DAYS:     int = 30

    #Gemini
    GEMINI_API_KEY:    str = ""
    GEMINI_MODEL:      str = "gemini-1.5-flash"
    GEMINI_MAX_TOKENS: int = 2048

    #Groq
    GROQ_API_KEY:    str = ""
    GROQ_MODEL:      str = "llama-3.1-8b-instant"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY:    str = ""
    CLOUDINARY_API_SECRET: str = ""

    # File upload
    UPLOAD_DIR:         str       = "uploads"
    MAX_UPLOAD_SIZE_MB: int       = 50
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "docx", "png", "jpg", "jpeg"]

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Scheduler tunable
    MAX_STUDY_MIN_PER_DAY: int   = 240    # tối đa 4h tự học / ngày
    SLOT_DURATION_MIN:     int   = 90     # mỗi block học 90 phút
    BREAK_MIN:             int   = 30     # nghỉ giữa 2 block
    OVERLOAD_THRESHOLD:    float = 0.85   # >85% → cảnh báo

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",           # Bỏ qua nếu trong .env có biến thừa
        env_ignore_empty=True     # Nếu biến trong .env trống thì mới dùng giá trị mặc định
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()