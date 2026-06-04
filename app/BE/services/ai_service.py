"""
app/BE/services/ai_service.py
Wrapper gọi Google Gemini API – Dùng cho:
  - Trợ lý AI (Chat đa lượt, đồng bộ với PySide6 UI của Frontend)
  - Tài liệu (Tóm tắt, phân tích, tạo đề luyện tập, gắn tag tự động)
- ĐÃ FIX LỖI SAI CẤU TRÚC PAYLOAD VÀ ĐỒNG BỘ ĐẦY ĐỦ HÀM ĐỂ GIAO DIỆN GỌI
"""
from __future__ import annotations

import json
from typing import List, Optional

import httpx
from app.BE.core.config import settings
from app.BE.database.repositories.chat_repo import ChatRepository

# Endpoint chuẩn chính thức của Google Gemini API
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"



def _convert_messages_to_gemini(messages: List[dict]) -> List[dict]:
    """
    Chuyển đổi cấu trúc mảng chat từ:
    - Định dạng thô: {"role": "user/assistant", "content": "text"}
    - Định dạng Gemini: {"role": "user/model", "parts": [{"text": "text"}]}
    """
    gemini_messages = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_messages.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    return gemini_messages


async def _call(system: str, messages: List[dict], max_tokens: int = 1024) -> str:
    """Gọi API thực tế lên Google Gemini hoặc Groq AI tùy thuộc vào API Key trong cấu hình."""
    if settings.GROQ_API_KEY:
        # Sử dụng Groq API (định dạng OpenAI chuẩn)
        groq_messages = [{"role": "system", "content": system}]
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            groq_messages.append({
                "role": role,
                "content": msg["content"]
            })

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": groq_messages,
            "temperature": 0.7,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            
            response_json = r.json()
            choices = response_json.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        return ""
    else:
        # Sử dụng Google Gemini API
        gemini_contents = _convert_messages_to_gemini(messages)

        payload = {
            "contents": gemini_contents,
            "systemInstruction": {
                "parts": [{"text": system}]
            },
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }

        headers = {"Content-Type": "application/json"}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            
            response_json = r.json()
            candidates = response_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts if "text" in p)
        return ""


# ── ĐỒNG BỘ CÁC HÀM ĐỂ ÔNG FRONTEND GỌI TRÊN GIAO DIỆN ────────────────────────

async def get_chat_response(message: str, history: Optional[List[dict]] = None) -> str:
    """
    Hàm cầu nối thay thế hoàn toàn file AI giả của Frontend.
    Nhận tin nhắn mới từ khung chat giao diện, đính kèm lịch sử và trả về câu rep từ Gemini.
    """
    chat_history = history or []
    return await chat_reply(history=chat_history, new_message=message)


async def get_study_suggestions(subjects: List[str]) -> str:
    """
    Trả về gợi ý học tập chi tiết, có ưu tiên theo deadline, dựa trên
    danh sách nhiệm vụ được truyền vào (dạng '- tên | Hạn: dd/mm/yyyy (urgency)').
    """
    try:
        if not subjects:
            return "Bạn chưa có nhiệm vụ nào đang chờ. Hãy thêm nhiệm vụ mới hoặc ôn lại kiến thức cũ nhé!"

        task_list = "\n".join(subjects)

        prompt = (
            f"Tôi là sinh viên, đây là danh sách nhiệm vụ học tập của tôi hôm nay:\n"
            f"{task_list}\n\n"
            f"Dựa vào mức độ khẩn cấp và deadline ở trên, hãy:\n"
            f"1. Chỉ ra nhiệm vụ CẦN LÀM NGAY nhất (nêu đúng tên).\n"
            f"2. Gợi ý cách tiếp cận cụ thể để hoàn thành hiệu quả.\n"
            f"Trả lời bằng tiếng Việt, thân thiện, tối đa 3 câu, không dùng ký tự markdown."
        )

        result = await _call(
            (
                "Bạn là trợ lý học tập thông minh. Luôn trả lời bằng tiếng Việt, "
                "ngắn gọn, cụ thể, đề cập đúng tên nhiệm vụ người dùng cung cấp. "
                "Không dùng ký hiệu markdown như **, ## hay gạch đầu dòng."
            ),
            [{"role": "user", "content": prompt}],
            max_tokens=400   # Đủ cho 3 câu hoàn chỉnh tiếng Việt
        )

        result = result.strip()

        # Kiểm tra bị cắt đứt — câu cuối phải kết thúc bằng dấu câu
        if result and result[-1] not in (".", "!", "?", "…", "💪", "🎯", "📚"):
            # Cắt đến dấu câu cuối cùng hợp lệ
            for end_char in ("!", ".", "?"):
                last_pos = result.rfind(end_char)
                if last_pos > len(result) // 2:   # Dấu câu phải ở nửa sau câu
                    return result[:last_pos + 1]
            # Fallback nếu không tìm thấy dấu câu
            first_task = subjects[0].split("|")[0].strip().lstrip("- ")
            return f'Hãy ưu tiên hoàn thành "{first_task}" trước nhé! Chia nhỏ công việc ra từng bước để làm hiệu quả hơn. 💪'

        return result

    except Exception:
        first_task = subjects[0].split("|")[0].strip().lstrip("- ") if subjects else "nhiệm vụ học tập"
        return f'Hãy tập trung hoàn thành "{first_task}" hôm nay nhé! Mỗi bước nhỏ đều đưa bạn đến gần mục tiêu hơn. 🎯'






async def get_study_suggestions_rich(context: dict) -> str:
    """
    Hàm AI gợi ý học tập cao cấp — nhận context đa chiều (tasks+notes, lịch học,
    thống kê, thời điểm ngày) và trả về lời khuyên như một personal study coach.
    """
    try:
        tasks_text    = "\n".join(context.get("tasks", []))
        schedule_text = context.get("schedule", "")
        stats_text    = context.get("stats", "")
        time_text     = context.get("time", "")
        now_text      = context.get("now", "")

        prompt = (
            "Bạn là StudyCoach AI — cố vấn học tập thông minh dựa trên nền tảng Gemini của Google. "
            "Hãy đọc và phân tích kỹ lưỡng các thông tin thực tế của sinh viên dưới đây, sau đó đưa ra lời khuyên "
            "học tập cá nhân hóa, thực tế, truyền cảm hứng và cực kỳ có ích (tối đa 3 câu ngắn gọn, bằng tiếng Việt):\n\n"
            "--- THÔNG TIN THỜI GIAN & THỜI ĐIỂM TRONG NGÀY ---\n"
            f"Bây giờ là: {now_text}. Bối cảnh: {time_text}\n\n"
            "--- DANH SÁCH NHIỆM VỤ HỌC TẬP THỰC TẾ ---\n"
            f"{tasks_text}\n\n"
            "--- LỊCH HỌC TRÊN TRƯỜNG ---\n"
            f"{schedule_text if schedule_text else 'Hôm nay không có lịch học.'}\n\n"
            "--- THỐNG KÊ KẾT QUẢ HỌC TẬP TUẦN NÀY ---\n"
            f"{stats_text if stats_text else 'Chưa có buổi học nào ghi nhận.'}\n\n"
            "--- YÊU CẦU ĐẶC BIỆT KHI BẠN TRẢ LỜI (MANDATORY): ---\n"
            "1. Chỉ ra chính xác nhiệm vụ quan trọng nhất cần làm ngay hôm nay. Đề cập đúng tên nhiệm vụ đó.\n"
            "2. Gợi ý cụ thể, chi tiết cách học/làm bài hiệu quả DỰA VÀO GHI CHÚ nội dung của nhiệm vụ đó (ví dụ: chia nhỏ bước, tập trung lý thuyết, thực hành code, vẽ sơ đồ,...).\n"
            "3. Tuyệt đối KHÔNG DÙNG bất kỳ ký hiệu markdown nào như **, ##, gạch đầu dòng, dấu hoa thị hay bảng biểu. Trả lời bằng văn bản thuần túy (Plain Text).\n"
            "4. Đảm bảo câu trả lời thân thiện như một người bạn lớn truyền động lực. Câu trả lời phải từ 2 đến 3 câu hoàn chỉnh."
        )

        result = await _call(
            system="Bạn là trợ lý học tập cá nhân thông minh. Chỉ trả lời bằng tiếng Việt chuẩn, không dùng markdown.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )

        result = result.strip()

        # Đảm bảo kết quả không bị cắt ngang giữa chừng
        if result and result[-1] not in (".", "!", "?", "…", "💪", "🎯", "📚", "✨"):
            for end_char in ("!", ".", "?"):
                last_pos = result.rfind(end_char)
                if last_pos > len(result) // 2:
                    return result[:last_pos + 1]
            
            # Cắt ngắn fallback lấy phần trước dấu chấm cuối cùng
            first_task = "nhiệm vụ ưu tiên"
            tasks = context.get("tasks", [])
            if tasks:
                first_task = tasks[0].split(".")[0].replace("Nhiệm vụ:", "").strip()
            return f'Hãy tập trung giải quyết "{first_task}" hôm nay nhé! Hãy bắt đầu bằng những bước nhỏ nhất để tạo đà học tập. 💪'

        return result

    except Exception as e:
        print(f"[AI Rich Suggestion] Lỗi API: {e} (Chuyển tiếp sang Local Fallback)")
        raise e


# ── Trợ lý AI – chat đa lượt ─────────────────────────────────────────────────

TUTOR_SYSTEM = (
    "Bạn là StudyAI – trợ lý học tập thông minh dựa trên nền tảng Gemini của Google. "
    "Luôn trả lời bằng tiếng Việt, ngắn gọn, chính xác. "
    "Khi giải bài toán hãy trình bày từng bước rõ ràng. "
    "Khi được đính kèm file, hãy đọc nội dung được trích xuất để hỗ trợ."
)

async def chat_reply(history: List[dict], new_message: str,
                     file_text: Optional[str] = None) -> str:
    user_content = new_message
    if file_text:
        user_content += f"\n\n[Nội dung file đính kèm]:\n{file_text[:3000]}"
    messages = history + [{"role": "user", "content": user_content}]
    return await _call(TUTOR_SYSTEM, messages,
                       max_tokens=settings.GEMINI_MAX_TOKENS)


# ── Tài liệu – xử lý đề thi ─────────────────────────────────────────────────

async def summarise_document(text: str) -> str:
    return await _call(
        "Bạn là trợ lý học tập. Tóm tắt tài liệu/đề thi thành 4–6 gạch đầu dòng "
        "ngắn gọn bằng tiếng Việt. Chỉ trả về danh sách gạch đầu dòng.",
        [{"role": "user", "content": text[:4000]}],
        max_tokens=512,
    )

async def analyse_document(text: str) -> str:
    return await _call(
        "Bạn là giáo viên AI. Phân tích cấu trúc đề thi: các chủ đề trọng tâm, "
        "phân bổ điểm, dạng câu hỏi, gợi ý ôn tập. Trả lời bằng tiếng Việt.",
        [{"role": "user", "content": text[:4000]}],
        max_tokens=1000,
    )

async def tag_document(text: str) -> List[str]:
    raw = await _call(
        "Đọc nội dung đề thi và trả về JSON array tối đa 6 tag ngắn (tiếng Việt). "
        "Ví dụ: [\"Giới hạn hàm số\",\"Đạo hàm\",\"Tích phân\"]. Không giải thích và KHÔNG bọc mã trong ký tự ```json.",
        [{"role": "user", "content": text[:2000]}],
        max_tokens=200,
    )
    # Dọn dẹp markdown nếu có để tránh lỗi ép kiểu JSON
    clean_raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        tags = json.loads(clean_raw)
        return [str(t) for t in tags if isinstance(t, str)]
    except Exception:
        return []

async def generate_practice(text: str, num: int = 5) -> str:
    return await _call(
        f"Bạn là giáo viên AI. Dựa vào đề thi mẫu, tạo {num} câu hỏi luyện tập "
        "tương tự kèm gợi ý giải ngắn. Đánh số từng câu. Trả lời bằng tiếng Việt.",
        [{"role": "user", "content": text[:4000]}],
        max_tokens=2000,
    )

async def solve_question(question: str) -> str:
    return await _call(
        "Bạn là gia sư AI. Giải thích câu hỏi sau từng bước rõ ràng bằng tiếng Việt.",
        [{"role": "user", "content": question}],
        max_tokens=1500,
    )


# ── Gợi ý học tập hôm nay (sidebar Trợ lý AI) ───────────────────────────────

async def daily_suggestions(subjects: List[str], history_titles: List[str]) -> List[str]:
    prompt = (
        f"Môn học đang học: {', '.join(subjects)}.\n"
        f"Chủ đề đã chat gần đây: {', '.join(history_titles[:5])}.\n"
        "Gợi ý 3 chủ đề nên ôn tập hôm nay. "
        "Trả về JSON array 3 chuỗi ngắn (tên chủ đề). Không giải thích và KHÔNG bọc mã trong ký tự ```json."
    )
    raw = await _call(
        "Bạn là trợ lý học tập.",
        [{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    clean_raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_raw)[:3]
    except Exception:
        return []


# ── DỊCH VỤ DATABASE CHAT AI TỰ ĐỘNG ──────────────────────────────────────────

async def load_chat_sessions(user_id: int) -> list:
    """Lấy danh sách các phiên chat của người dùng từ MySQL DB."""
    try:
        return await ChatRepository.get_sessions(user_id=user_id)
    except Exception as e:
        print(f"[ERROR] load_chat_sessions thất bại: {e}")
        return []

async def load_session_messages(session_id: int) -> list:
    """Lấy toàn bộ lịch sử tin nhắn của một phiên chat từ MySQL DB."""
    try:
        return await ChatRepository.get_messages(session_id=session_id)
    except Exception as e:
        print(f"[ERROR] load_session_messages thất bại: {e}")
        return []

async def create_chat_session(user_id: int, title: str) -> int:
    """Tạo một phiên chat mới lưu vào MySQL và trả về session_id."""
    try:
        return await ChatRepository.create_session(user_id=user_id, title=title)
    except Exception as e:
        print(f"[ERROR] create_chat_session thất bại: {e}")
        return 0

async def save_chat_message(session_id: int, role: str, content: str) -> int:
    """Lưu tin nhắn (của user hoặc model) vào MySQL DB."""
    try:
        return await ChatRepository.add_message(session_id=session_id, role=role, content=content)
    except Exception as e:
        print(f"[ERROR] save_chat_message thất bại: {e}")
        return 0

async def delete_chat_session(session_id: int, user_id: int) -> bool:
    """Xóa phiên chat và toàn bộ tin nhắn đi kèm khỏi MySQL DB."""
    try:
        return await ChatRepository.delete_session(session_id=session_id, user_id=user_id)
    except Exception as e:
        print(f"[ERROR] delete_chat_session thất bại: {e}")
        return False

async def get_chat_response_db(session_id: int, user_message: str, file_path: Optional[str] = None) -> str:
    """
    Gọi Gemini sinh câu trả lời dựa trên ngữ cảnh lịch sử thật lấy từ database
    và tự động trích xuất nội dung văn bản từ tệp đính kèm cục bộ (nếu có) để gửi kèm làm ngữ cảnh.
    """
    try:
        file_text = ""
        if file_path:
            import os
            from pypdf import PdfReader
            ext = file_path.split(".")[-1].lower()
            try:
                if ext == "pdf":
                    reader = PdfReader(file_path)
                    pdf_text = ""
                    # Đọc tối đa 5 trang đầu tiên để tiết kiệm token và tránh quá tải quota
                    for page in reader.pages[:5]:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                    file_text = pdf_text.strip()
                elif ext in ("doc", "docx"):
                    try:
                        import docx
                        doc = docx.Document(file_path)
                        file_text = "\n".join([p.text for p in doc.paragraphs[:100]])
                    except Exception:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_text = f.read(4000)
                elif ext in ("txt", "py", "js", "html", "css", "json"):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_text = f.read(4000)
                else:
                    file_text = f"[Tệp đính kèm: {os.path.basename(file_path)}]"
            except Exception as fe:
                print(f"[AI Service] Lỗi trích xuất file: {fe}")
                file_text = f"[Lỗi đọc tệp đính kèm: {fe}]"

        # Lấy lịch sử tin nhắn của session_id này từ DB (tải tối đa 35 tin gần nhất)
        all_history = await ChatRepository.get_history_for_api(session_id=session_id, last_n=35)
        
        # Nếu tổng số tin nhắn (bao gồm cả câu hỏi vừa lưu) <= 1: Đây là câu đầu tiên, gửi thẳng
        if len(all_history) <= 1:
            return await chat_reply(history=[], new_message=user_message, file_text=file_text)
        else:
            # Lấy các tin nhắn TRƯỚC câu hỏi hiện tại (bỏ đi phần tử cuối cùng vừa lưu của câu hỏi hiện tại để tránh trùng lặp)
            # và giới hạn tối đa 15 tin nhắn cũ gần nhất làm ngữ cảnh
            history_context = all_history[:-1]  # Loại bỏ câu hỏi hiện tại vừa lưu
            if len(history_context) > 15:
                history_context = history_context[-15:]  # Chỉ lấy tối đa 15 câu gần nhất
                
            return await chat_reply(history=history_context, new_message=user_message, file_text=file_text)
    except Exception as e:
        err_msg = str(e)
        print(f"[ERROR] get_chat_response_db thất bại: {err_msg}")
        if "429" in err_msg or "Too Many Requests" in err_msg:
            return (
                "⚠️ **[Giới hạn API Key]** Trợ lý AI đang bị quá tải (Lỗi 429 - Too Many Requests).\n\n"
                "**Lý do:** API Key Gemini miễn phí hiện tại của bạn đã dùng hết hạn ngạch ngày hôm nay của Google.\n\n"
                "**Cách khắc phục:**\n"
                "1. Vui lòng truy cập **https://aistudio.google.com/** để tạo một API Key mới miễn phí trong 10 giây.\n"
                "2. Mở file `.env` ở thư mục gốc dự án và dán đè Key mới vào dòng `GEMINI_API_KEY=...`.\n"
                "3. Khởi động lại ứng dụng là có thể tiếp tục trò chuyện bình thường ngay lập tức! 💪"
            )
        return f"Lỗi kết nối AI: {err_msg}"