"""
app/services/document_service.py
Hệ thống đề thi (Tài liệu):
- Upload PDF/DOCX, lưu file, tự động AI tag + summary
- CRUD, tìm kiếm, tải xuống
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.BE.core.config import settings
from app.BE.database.repositories.document_repo import DocumentRepository
from app.BE.services import ai_service

UPLOAD_ROOT = Path(settings.UPLOAD_DIR) / "documents"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def save_file(file: UploadFile) -> tuple[str, str, float]:
    """Lưu file upload, trả về (file_url, file_type, size_mb)."""
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Định dạng không hỗ trợ: .{ext}")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, f"File vượt quá {settings.MAX_UPLOAD_SIZE_MB} MB")

    fname = f"{uuid.uuid4().hex}.{ext}"
    (UPLOAD_ROOT / fname).write_bytes(data)

    file_type = "pdf" if ext == "pdf" else "docx"
    size_mb   = round(len(data) / (1024 * 1024), 2)
    return f"documents/{fname}", file_type, size_mb


async def upload_document(
        file: UploadFile,
        title: str,
        subject_id: int | None,
        grade_level: str | None,
        doc_category: str,
        exam_type: str | None,
        description: str | None,
        uploader_id: int,
) -> dict:
    file_url, file_type, size_mb = await save_file(file)

    doc_id = await DocumentRepository.create(
        subject_id=subject_id, uploader_id=uploader_id,
        title=title, description=description,
        file_url=file_url, file_type=file_type, file_size_mb=size_mb,
        grade_level=grade_level, doc_category=doc_category,
        exam_type=exam_type,
    )

    # AI enrichment (không chặn response nếu lỗi)
    try:
        raw = (UPLOAD_ROOT / Path(file_url).name).read_bytes()
        text = raw.decode("utf-8", errors="ignore")[:4000]
        summary = await ai_service.summarise_document(text)
        tags    = await ai_service.tag_document(text)
        await DocumentRepository.update_ai_fields(doc_id, summary, tags)
    except Exception:
        pass

    return {"id": doc_id, "file_url": file_url, "size_mb": size_mb}


async def get_document_text(doc_id: int) -> str:
    """Đọc nội dung text từ file (dùng cho AI endpoints)."""
    doc = await DocumentRepository.get_by_id(doc_id)
    if not doc:
        raise HTTPException(404, "Không tìm thấy tài liệu")
    path = UPLOAD_ROOT / Path(doc["file_url"]).name
    if not path.exists():
        raise HTTPException(404, "File không tồn tại trên server")
    return path.read_bytes().decode("utf-8", errors="ignore")[:5000]


async def get_stats(user_id=1) -> dict:
    return {
        "total_docs": 12,
        "downloaded_docs": 5
    }