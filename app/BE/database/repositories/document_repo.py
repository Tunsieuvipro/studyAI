from typing import List, Optional
from .base import BaseRepository


class DocumentRepository(BaseRepository):

    # ── Stats card (128 tổng | 36 PDF | 24 Word | 18 tải gần đây) ────────────

    @classmethod
    async def get_summary_stats(cls) -> dict:
        row = await cls._fetchrow(
             """
            SELECT COUNT(*)                                              AS total,
                   COALESCE(SUM(IF(file_type='pdf', 1, 0)), 0)           AS pdf_count,
                   COALESCE(SUM(IF(file_type='docx', 1, 0)), 0)          AS word_count,
                   COALESCE(SUM(download_count), 0)                      AS recent,
                   COALESCE(SUM(view_count), 0)                          AS view_count
            FROM documents WHERE is_approved=TRUE
            """)
        return dict(row) if row else {"total": 0, "pdf_count": 0, "word_count": 0, "recent": 0, "view_count": 0}

    # ── List / Search ─────────────────────────────────────────────────────────

    @classmethod
    async def search(cls, subject_id: Optional[int] = None,
                     grade_level: Optional[str] = None,
                     doc_category: Optional[str] = None,
                     file_type: Optional[str] = None,
                     keyword: Optional[str] = None,
                     limit: int = 20, offset: int = 0) -> List[dict]:
        conds = ["d.is_approved=TRUE"]
        args: list = []

        if subject_id:
            args.append(subject_id);  conds.append("d.subject_id=%s")
        if grade_level:
            args.append(grade_level); conds.append("d.grade_level=%s")
        if doc_category:
            args.append(doc_category); conds.append("d.doc_category=%s")
        if file_type:
            args.append(file_type);   conds.append("d.file_type=%s")
        if keyword:
            args.append(f"%{keyword}%")
            conds.append("(d.title LIKE %s OR d.description LIKE %s)")
            args.append(f"%{keyword}%")

        where = " AND ".join(conds)
        args += [limit, offset]
        li, of = len(args)-1, len(args)

        rows = await cls._fetch(
            f"""
              SELECT d.id, d.title, d.description, d.file_type,
                     d.file_size_mb, d.grade_level, d.doc_category,
                     d.exam_type, d.tags, d.ai_summary,
                     d.download_count, d.view_count, d.created_at,
                     s.name AS subject_name, s.code AS subject_code,
                     u.full_name AS uploader_name
              FROM   documents d
                         LEFT JOIN subjects s ON s.id = d.subject_id
                         LEFT JOIN users    u ON u.id = d.uploader_id
              WHERE  {where}
              ORDER  BY d.created_at DESC
                  LIMIT  %s OFFSET %s
            """, *args)
        return [dict(r) for r in rows]

    @classmethod
    async def get_by_id(cls, doc_id: int) -> Optional[dict]:
        row = await cls._fetchrow(
            """
            SELECT d.*, s.name AS subject_name, s.code AS subject_code
            FROM   documents d
                       LEFT JOIN subjects s ON s.id = d.subject_id
            WHERE  d.id=%s
            """, doc_id)
        return dict(row) if row else None

    # ── Popular categories (sidebar) ──────────────────────────────────────────

    @classmethod
    async def popular_subjects(cls, limit: int = 5) -> List[dict]:
        rows = await cls._fetch(
            """
            SELECT s.id, s.name, s.code, COUNT(d.id) AS doc_count
            FROM   documents d
                       JOIN   subjects  s ON s.id = d.subject_id
            WHERE  d.is_approved=TRUE
            GROUP  BY s.id, s.name, s.code
            ORDER  BY doc_count DESC
                LIMIT  %s
            """, limit)
        return [dict(r) for r in rows]

    # ── Create ────────────────────────────────────────────────────────────────

    @classmethod
    async def create(cls, subject_id: Optional[int], uploader_id: Optional[int],
                     title: str, description: Optional[str], file_url: str,
                     file_type: str, file_size_mb: float,
                     grade_level: Optional[str], doc_category: str,
                     exam_type: Optional[str]) -> int:
        await cls._fetchrow(
            """
            INSERT INTO documents
            (subject_id, uploader_id, title, description, file_url,
             file_type, file_size_mb, grade_level, doc_category, exam_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, subject_id, uploader_id, title, description, file_url,
            file_type, file_size_mb, grade_level, doc_category, exam_type)
        last_id_row = await cls._fetchrow("SELECT LAST_INSERT_ID() AS id")
        return last_id_row["id"] if last_id_row else 0

    @classmethod
    async def update_ai_fields(cls, doc_id: int,
                               summary: str, tags: List[str]) -> None:
        await cls._execute(
            "UPDATE documents SET ai_summary=%s, tags=%s WHERE id=%s",
            summary, tags, doc_id)

    @classmethod
    async def increment_download(cls, doc_id: int) -> None:
        await cls._execute(
            "UPDATE documents SET download_count=download_count+1 WHERE id=%s", doc_id)

    @classmethod
    async def increment_view(cls, doc_id: int) -> None:
        await cls._execute(
            "UPDATE documents SET view_count=view_count+1 WHERE id=%s", doc_id)

    @classmethod
    async def delete(cls, doc_id: int, uploader_id: int) -> bool:
        r = await cls._execute(
            "DELETE FROM documents WHERE id=%s AND uploader_id=%s",
            doc_id, uploader_id)
        return r == "DELETE 1"