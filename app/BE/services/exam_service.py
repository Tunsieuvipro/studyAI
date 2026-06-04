"""
app/BE/services/exam_service.py
Dịch vụ quản lý dữ liệu cho Trang tài liệu: Danh sách đề thi, Thống kê và Danh mục phổ biến.
- ĐÃ TÍCH HỢP DOCUMENT_REPO THẬT CHẠY DATABASE MYSQL
"""
from typing import List, Dict
import asyncio
from app.BE.database.repositories.document_repo import DocumentRepository


async def get_stats(user_id: int = 0) -> dict:
    try:
        stats = await DocumentRepository.get_summary_stats()
        return {
            "total":            stats.get("total", 0),
            "pdf_count":        stats.get("pdf_count", 0),
            "word_count":       stats.get("word_count", 0),
            "recent_downloads": stats.get("recent", 0),
        }
    except Exception:
        return {"total": 0, "pdf_count": 0, "word_count": 0, "recent_downloads": 0}


class DocumentService:
    def __init__(self):
        pass

    @staticmethod
    async def get_exams(limit: int = 50, offset: int = 0) -> List[Dict]:
        db_docs = await DocumentRepository.search(limit=limit, offset=offset)

        formatted_exams = []
        cat_mapping_vi = {
            "exam": "Đề thi",
            "summary": "Đề cương",
            "exercise": "Bài tập",
            "other": "Tài liệu"
        }
        for doc in db_docs:
            formatted_exams.append({
                "id":        doc["id"],
                "name":      doc["title"],
                "sub":       doc.get("description") or "Tài liệu học tập/Đề thi mẫu",
                "subject":   doc.get("subject_name") or "Chung",
                "grade":     doc.get("exam_type"), # Trả về trực tiếp kỳ thi (15 phút, 1 tiết, Giữa kỳ, Cuối kỳ)
                "type":      cat_mapping_vi.get(doc.get("doc_category"), "Tài liệu"), # Trả về phân loại tài liệu tương ứng
                "date":      doc["created_at"].strftime("%d/%m/%Y") if doc.get("created_at") else "Chưa rõ",
                "size":      f"{round(doc['file_size_mb'], 1)} MB" if doc.get("file_size_mb") else "0 KB",
                "downloads": doc.get("download_count", 0),
                "views":     doc.get("view_count", 0),
                "file_type": (doc.get("file_type") or "PDF").upper(),
            })
        return formatted_exams

    @staticmethod
    async def get_exams_with_filters(filters: Dict) -> List[Dict]:
        keyword = filters.get("query")
        db_docs = await DocumentRepository.search(keyword=keyword, limit=50)

        formatted_exams = []
        cat_mapping_vi = {
            "exam": "Đề thi",
            "summary": "Đề cương",
            "exercise": "Bài tập",
            "other": "Tài liệu"
        }
        for doc in db_docs:
            formatted_exams.append({
                "id":        doc["id"],
                "name":      doc["title"],
                "sub":       doc.get("description") or "Tài liệu học tập/Đề thi mẫu",
                "subject":   doc.get("subject_name") or "Chung",
                "grade":     doc.get("exam_type"), 
                "type":      cat_mapping_vi.get(doc.get("doc_category"), "Tài liệu"), 
                "date":      doc["created_at"].strftime("%d/%m/%Y") if doc.get("created_at") else "Chưa rõ",
                "size":      f"{round(doc['file_size_mb'], 1)} MB" if doc.get("file_size_mb") else "0 KB",
                "downloads": doc.get("download_count", 0),
                "views":     doc.get("view_count", 0),
                "file_type": (doc.get("file_type") or "PDF").upper(),
            })
        return formatted_exams

    @staticmethod
    async def get_exam_detail(doc_id: int) -> Dict:
        """Lấy thông tin chi tiết đầy đủ của tài liệu (bao gồm cả URL đám mây và tóm tắt AI)."""
        doc = await DocumentRepository.get_by_id(doc_id)
        if not doc:
            return {}
            
        # Tăng số lượt xem tài liệu lên 1 trong database
        await DocumentRepository.increment_view(doc_id)
        
        # Đảm bảo chuyển đổi JSON tags nếu được lưu dưới dạng chuỗi JSON
        tags = doc.get("tags")
        if isinstance(tags, str):
            import json
            try:
                tags = json.loads(tags)
            except Exception:
                tags = [tags] if tags else []
        elif not tags:
            tags = []
            
        return {
            "id": doc["id"],
            "title": doc["title"],
            "description": doc.get("description") or "Tài liệu học tập/Đề thi mẫu",
            "subject_name": doc.get("subject_name") or "Chung",
            "grade_level": doc.get("grade_level") or "Đại học",
            "doc_category": doc.get("doc_category") or "Tài liệu",
            "exam_type": doc.get("exam_type") or "Tài liệu",
            "file_url": doc.get("file_url") or "",
            "file_type": (doc.get("file_type") or "pdf").upper(),
            "file_size_mb": doc.get("file_size_mb") or 0.0,
            "ai_summary": doc.get("ai_summary") or "AI đang phân tích và tóm tắt nội dung này...",
            "tags": tags,
            "view_count": doc.get("view_count", 0) + 1,
            "download_count": doc.get("download_count", 0),
            "created_at": doc["created_at"].strftime("%d/%m/%Y") if doc.get("created_at") else "Chưa rõ"
        }

    @staticmethod
    async def upload_document_desktop(
        local_filepath: str,
        title: str,
        subject_name: str | None,
        grade_level: str | None,
        doc_category: str,
        exam_type: str | None,
        description: str | None,
        uploader_id: int,
        progress_callback = None
    ) -> int:
        """
        Đăng tải tài liệu từ giao diện Desktop lên Cloudinary và lưu thông tin vào MySQL.
        Sau đó thực hiện trích xuất text từ file PDF cục bộ và gọi Gemini tóm tắt / gắn tag ngầm.
        """
        import os
        import cloudinary
        import cloudinary.uploader
        from pypdf import PdfReader
        from app.BE.core.config import settings
        from app.BE.services import ai_service
        
        if progress_callback:
            progress_callback(10, "Khởi tạo kết nối đám mây Cloudinary...")
            
        # 1. Cấu hình thông tin kết nối Cloudinary lấy từ settings (.env)
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        if progress_callback:
            progress_callback(25, "Đang đồng bộ và kiểm tra thông tin môn học...")
            
        # 1.5 Tìm hoặc tạo môn học tự động từ tên môn học nhập vào
        subject_id = None
        if subject_name:
            subject_name = " ".join(subject_name.split()).upper()
            if subject_name:
                from app.BE.database.connection import fetchrow, execute
                # Kiểm tra môn học tồn tại chưa
                row = await fetchrow("SELECT id FROM subjects WHERE name = %s", subject_name)
                if row:
                    subject_id = row["id"]
                else:
                    # Tạo môn học mới nếu chưa có
                    import re
                    import unicodedata
                    
                    # Chuyển đổi tên môn học sang dạng không dấu, viết hoa không khoảng trắng
                    clean_name = unicodedata.normalize('NFKD', subject_name).encode('ASCII', 'ignore').decode('utf-8')
                    base_code = re.sub(r'[^a-zA-Z0-9]', '', clean_name).upper()
                    if not base_code:
                        base_code = "SUBJ"
                        
                    # Đảm bảo duy nhất (Unique) bằng cách dò khóa trong MySQL
                    code = base_code[:10]
                    exists = True
                    counter = 1
                    while exists:
                        dup_row = await fetchrow("SELECT id FROM subjects WHERE code = %s", code)
                        if not dup_row:
                            exists = False
                        else:
                            suffix = str(counter)
                            max_len = 10 - len(suffix)
                            code = f"{base_code[:max_len]}{suffix}"
                            counter += 1
                            
                    await execute("INSERT INTO subjects (name, code) VALUES (%s, %s)", subject_name, code)
                    # Lấy ID của môn học vừa tạo
                    new_row = await fetchrow("SELECT id FROM subjects WHERE code = %s", code)
                    if new_row:
                        subject_id = new_row["id"]
        
        if progress_callback:
            progress_callback(40, "Đang tải dữ liệu tệp tin lên đám mây Cloudinary...")
            
        # Tính dung lượng file (MB)
        file_size_bytes = os.path.getsize(local_filepath)
        size_mb = round(file_size_bytes / (1024 * 1024), 2)
        ext = os.path.splitext(local_filepath)[1].lower().replace(".", "")
        
        # 2. Upload file lên Cloudinary
        # Dùng resource_type="raw" để hỗ trợ giữ nguyên định dạng file gốc (.pdf, .docx)
        loop = asyncio.get_event_loop()
        upload_result = await loop.run_in_executor(
            None,
            lambda: cloudinary.uploader.upload(
                local_filepath,
                resource_type="auto",
                folder="smartstudy/documents"
            )
        )
        
        # Lấy URL công khai của Cloudinary
        cloud_url = upload_result.get("secure_url")
        
        if progress_callback:
            progress_callback(70, "Đang đồng bộ cơ sở dữ liệu MySQL...")
            
        # 3. Tạo bản ghi mới trong MySQL Database
        doc_id = await DocumentRepository.create(
            subject_id=subject_id,
            uploader_id=uploader_id,
            title=title,
            description=description,
            file_url=cloud_url,
            file_type=ext,
            file_size_mb=size_mb,
            grade_level=grade_level,
            doc_category=doc_category,
            exam_type=exam_type
        )
        
        # 4. Kích hoạt tác vụ tóm tắt AI và sinh tags ngầm (Background Task)
        try:
            if progress_callback:
                progress_callback(85, "Gemini AI đang tiến hành đọc hiểu, tóm tắt & sinh tags từ khóa...")
                
            text = ""
            if ext == "pdf":
                def _read_pdf():
                    reader = PdfReader(local_filepath)
                    pdf_text = ""
                    for page in reader.pages[:5]:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                    return pdf_text
                text = await loop.run_in_executor(None, _read_pdf)
            else:
                with open(local_filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read(5000)
            
            # Chỉ gửi 4000 ký tự đầu tiên lên Gemini để tối ưu hóa hiệu năng
            clean_text = text.strip()[:4000]
            if clean_text:
                summary = await ai_service.summarise_document(clean_text)
                tags = await ai_service.tag_document(clean_text)
                
                # Lưu thông tin AI tóm tắt và tags vào database dưới dạng mảng JSON
                import json
                tags_json = json.dumps(tags, ensure_ascii=False)
                await DocumentRepository.update_ai_fields(doc_id, summary, tags_json)
                
            if progress_callback:
                progress_callback(100, "Tải lên và phân tích AI thành công!")
        except Exception as e:
            print(f"[Warning] Trích xuất AI thất bại: {e}")
            if progress_callback:
                progress_callback(95, "Phân tích AI thất bại, tuy nhiên file đã tải lên thành công!")
            
        return doc_id

    @staticmethod
    async def get_popular_subjects() -> List[tuple]:
        try:
            rows = await DocumentRepository.popular_subjects()
            icons = {"toán": "📐", "văn": "📖", "lý": "⚡", "hóa": "🧪",
                     "anh": "🌍", "python": "🐍", "ai": "🤖"}
            out = []
            for item in rows:
                sub_name = item["name"]
                icon = next((v for k, v in icons.items() if k in sub_name.lower()), "📚")
                out.append((f"{icon} {sub_name}", item["doc_count"]))
            return out
        except Exception:
            return [("🤖 Trí tuệ nhân tạo", 0),
                    ("🐍 Lập trình Python", 0),
                    ("📐 Đại số tuyến tính", 0)]

    @staticmethod
    async def increment_download(doc_id: int) -> None:
        """Tăng số lượt tải của tài liệu lên 1."""
        await DocumentRepository.increment_download(doc_id)

    @staticmethod
    async def get_subjects() -> List[dict]:
        """Lấy danh sách tất cả môn học trong cơ sở dữ liệu."""
        from app.BE.database.connection import fetch
        rows = await fetch("SELECT id, name, code FROM subjects ORDER BY name ASC")
        return [dict(r) for r in rows] if rows else []
