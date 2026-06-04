import qasync
from datetime import datetime
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QVBoxLayout, QWidget, QSizePolicy
)

from app.FE.config import COLORS, FONTS
from app.FE.views.AI_AssistantPage.qss_AI_Assiistant import *
from app.FE.views.AI_AssistantPage.chat_bubble import UserBubbleWidget, AIBubbleWidget
from app.FE.views.AI_AssistantPage.history_panel import HistoryPanelWidget

def qfont(font_tuple):
    """Hàm tiện ích để tạo QFont từ tuple cấu hình trong file config."""
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class AIAssistantPage(QFrame):
    """Trang trợ lý AI cung cấp giao diện chat và các công cụ hỗ trợ học tập thông minh."""
    TOOLS = [
        ("🧮", "#FEF3C7", "Giải toán",           "Giải bài tập, chứng minh"),
        ("📄", "#DCFCE7", "Tóm tắt tài liệu",    "Tóm tắt nhanh nội dung"),
        ("🌐", "#EDE9FE", "Dịch thuật",           "Dịch văn bản, tài liệu"),
        ("💡", "#DBEAFE", "Hỏi đáp kiến thức",   "Giải đáp mọi câu hỏi"),
        ("📝", "#FFE4E6", "Tạo đề ôn tập",        "Tạo đề cương, trắc nghiệm"),
    ]

    QUICK_PROMPTS = [
        "Giải bài toán này giúp mình",
        "Tóm tắt nội dung tài liệu",
        "Lập kế hoạch học tập",
        "Giải thích khái niệm",
        "Ôn tập trắc nghiệm",
    ]

    def __init__(self, master, ai_service=None, user_id: int = 1):
        super().__init__(master)
        self.ai_service = ai_service
        self.user_id = user_id         # ID người dùng thật truyền từ hệ thống chính
        self.current_session_id = None # Phiên chat hiện tại (None = Chưa tạo phiên)
        self.is_new_session = True     # Đánh dấu phiên chat mới tinh chưa gửi câu nào
        self.selected_file_path = None
        self.selected_file_name = None

        self.setStyleSheet(STYLE_PAGE)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Cột trái (khung chat chính)
        self.left_col = QFrame()
        self.left_col.setStyleSheet(STYLE_TRANSPARENT)
        self.left_layout = QVBoxLayout(self.left_col)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(15)

        # Cột phải (thanh lịch sử)
        self.history_widget = HistoryPanelWidget(
            ai_service=self.ai_service,
            user_id=self.user_id,
            on_session_selected=self.select_session_async,
            on_new_chat_clicked=self._on_new_chat_clicked,
            parent=self
        )
        self.history_widget.setFixedWidth(340)

        main_layout.addWidget(self.left_col, 1)
        main_layout.addWidget(self.history_widget, 0)

        self.create_header()
        self.create_quick_prompts()
        self.create_chat_area()
        self.create_input_box()

        # Cài đặt bộ lắng nghe phím Enter và tự động cuộn
        self.text_input.installEventFilter(self)
        self.chat_scroll.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)

        # Tải danh sách lịch sử các phiên chat từ MySQL DB lên
        self.load_history_from_db()

    def make_card(self):
        """Tạo khung thẻ (Card) với viền và bo góc dùng cho các phần tử trong trang chat."""
        card = QFrame()
        card.setObjectName("chat_card")
        card.setStyleSheet(STYLE_CHAT_CARD)
        return card

    @qasync.asyncSlot()
    async def load_history_from_db(self):
        """Đồng bộ lịch sử từ database thông qua HistoryPanelWidget."""
        await self.history_widget.load_history()

    def select_session_async(self, session_id):
        """Gọi xử lý bất đồng bộ khi click chọn phiên chat cũ."""
        import asyncio
        asyncio.create_task(self.select_session(session_id))

    async def select_session(self, session_id: int):
        """Tải toàn bộ tin nhắn cũ của phiên chat được chọn từ DB và vẽ lên màn hình."""
        self.current_session_id = session_id
        self.history_widget.current_session_id = session_id
        self.is_new_session = False    # Đây là cuộc hội thoại cũ đã có tin nhắn, tắt cờ mới tinh!

        # 1. Dọn sạch giao diện bong bóng chat hiện tại
        while self.chat_area_layout.count():
            child = self.chat_area_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Gọi backend tải toàn bộ tin nhắn của phiên chat từ MySQL DB
        messages = await self.ai_service.load_session_messages(session_id=session_id)

        if not messages:
            # Nếu chưa có tin nhắn nào
            self.add_ai_message(
                "Xin chào! Cuộc trò chuyện này hiện chưa có tin nhắn nào. Bạn hãy gửi câu hỏi đầu tiên nhen!",
                timestamp="Bây giờ"
            )
        else:
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                created_at = msg.get("created_at")

                # Định dạng giờ giấc hiển thị gọn gàng HH:MM
                time_str = "Bây giờ"
                if isinstance(created_at, datetime):
                    time_str = created_at.strftime("%H:%M")
                elif created_at:
                    time_str = str(created_at)[:16]

                if role == "user":
                    self.add_user_message(content, timestamp=time_str)
                else:
                    self.add_ai_message(content, timestamp=time_str)

    def _on_new_chat_clicked(self):
        """Bấm nút '+ Chat mới': Reset trạng thái màn hình và ID phiên chat về rỗng."""
        self.current_session_id = None
        self.history_widget.current_session_id = None
        self.is_new_session = True     # Đánh dấu đây là cuộc hội thoại mới tinh hoàn toàn

        # Dọn sạch bóng chat cũ
        while self.chat_area_layout.count():
            child = self.chat_area_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Lời chào mặc định
        self.add_ai_message(
            "Xin chào! Mình là StudyAI – Trợ lý học tập thông minh của bạn. "
            "Bạn có câu hỏi hoặc bài tập nào cần giải quyết không?",
            timestamp="Bây giờ"
        )

    def scroll_to_bottom(self, min_val=0, max_val=0):
        """Tự động cuộn thanh cuộn xuống dưới cùng khi có tin nhắn mới."""
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def eventFilter(self, obj, event):
        """Bắt sự kiện gõ phím Enter trên ô nhập liệu để gửi câu hỏi."""
        if obj == self.text_input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._on_send_clicked()
                    return True
        return super().eventFilter(obj, event)

    def select_quick_prompt(self, prompt_text):
        """Điền câu hỏi nhanh vào ô nhập liệu khi bấm chip gợi ý."""
        self.text_input.setPlainText(prompt_text)
        self.text_input.setFocus()

    def create_header(self):
        """Tạo phần đầu trang với tiêu đề và các nút chức năng nhanh."""
        header = QFrame()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title = QLabel("Trợ lý AI")
        title.setFont(qfont(FONTS["h1_ai"]))
        title.setStyleSheet(STYLE_LABEL_PRIMARY)

        sub = QLabel("AI có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.")
        sub.setFont(qfont(FONTS["body_ai"]))
        sub.setStyleSheet(STYLE_LABEL_SECONDARY)

        title_box.addWidget(title)
        title_box.addWidget(sub)

        h_layout.addLayout(title_box)
        h_layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn = QPushButton("+ Chat mới")
        btn.setFixedHeight(36)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFont(qfont(FONTS["body_bold_ai"]))
        btn.setStyleSheet(STYLE_BTN_PRIMARY)
        btn.clicked.connect(self._on_new_chat_clicked)
        btn_box.addWidget(btn)

        h_layout.addLayout(btn_box)
        self.left_layout.addWidget(header)

    def create_quick_prompts(self):
        """Tạo thanh chứa các câu lệnh gợi ý nhanh (Chips)."""
        card = self.make_card()
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(15, 10, 15, 10)
        c_layout.setSpacing(10)

        lbl = QLabel("Gợi ý nhanh")
        lbl.setFont(qfont(FONTS["body_bold_ai"]))
        lbl.setStyleSheet(STYLE_LABEL_PRIMARY)
        c_layout.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(45)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(STYLE_CHIPS_SCROLL)

        scroll_content = QWidget()
        scroll_content.setStyleSheet(STYLE_TRANSPARENT)
        chips_row = QHBoxLayout(scroll_content)
        chips_row.setContentsMargins(0, 0, 0, 0)
        chips_row.setSpacing(10)
        chips_row.setAlignment(Qt.AlignLeft)

        for prompt in self.QUICK_PROMPTS:
            btn = QPushButton(prompt)
            btn.setFixedHeight(32)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            btn.setFont(qfont(FONTS["small_ai"]))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(STYLE_CHIP_BTN)
            btn.clicked.connect(lambda checked=False, p=prompt: self.select_quick_prompt(p))
            chips_row.addWidget(btn)

        chips_row.addStretch()
        scroll.setWidget(scroll_content)
        c_layout.addWidget(scroll)

        self.left_layout.addWidget(card)

    def create_chat_area(self):
        """Tạo vùng hiển thị nội dung hội thoại (Scroll Area)."""
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet(STYLE_RIGHT_SCROLL)

        self.chat_content = QWidget()
        self.chat_content.setStyleSheet(STYLE_TRANSPARENT)
        self.chat_area_layout = QVBoxLayout(self.chat_content)
        self.chat_area_layout.setContentsMargins(0, 0, 10, 0)
        self.chat_area_layout.setSpacing(15)
        self.chat_area_layout.setAlignment(Qt.AlignTop)

        self.chat_scroll.setWidget(self.chat_content)
        self.left_layout.addWidget(self.chat_scroll, 1)

        # Lời chào mặc định
        self.add_ai_message(
            "Xin chào! Mình là StudyAI – Trợ lý học tập thông minh của bạn. "
            "Bạn có câu hỏi hoặc bài tập nào cần giải quyết không?",
            timestamp="Bây giờ"
        )

    def add_user_message(self, text, timestamp="", attachment=None):
        """Thêm bong bóng tin nhắn người dùng bằng cách dựng UserBubbleWidget."""
        bubble = UserBubbleWidget(text, timestamp=timestamp, attachment=attachment, parent=self)
        self.chat_area_layout.addWidget(bubble)

    def add_ai_message(self, text, timestamp=""):
        """Thêm bong bóng tin nhắn của AI bằng cách dựng AIBubbleWidget."""
        # Callback copy clipboard chuẩn hóa
        on_copy = lambda txt: self.copy_to_clipboard(txt)
        bubble = AIBubbleWidget(text, timestamp=timestamp, on_copy_callback=on_copy, parent=self)
        self.chat_area_layout.addWidget(bubble)
        
        # Trả về các phần tử text label và time label để cập nhật cho hiệu ứng typewriter/thinking
        return bubble.lbl, bubble.time_lbl, bubble.btn_copy

    def copy_to_clipboard(self, text):
        """Sao chép nội dung tin nhắn AI vào bộ nhớ tạm Clipboard."""
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtWidgets import QMessageBox
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Thông báo", "Đã sao chép nội dung vào bộ nhớ tạm!")

    def select_attachment(self):
        """Mở hộp thoại QFileDialog để người dùng tải lên hình ảnh hoặc tài liệu PDF/Word."""
        from PySide6.QtWidgets import QFileDialog
        import os
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn tệp ảnh hoặc tài liệu học tập",
            "",
            "Tài liệu (*.png *.jpg *.jpeg *.pdf *.doc *.docx)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.selected_file_name = os.path.basename(file_path)
            self.show_attachment_preview()

    def show_attachment_preview(self):
        """Hiển thị nhãn logo PDF/Word/Ảnh nhỏ và tên tệp đính kèm ngay trong khung chat input."""
        if not self.selected_file_name:
            self.attachment_preview.setVisible(False)
            return

        ext = self.selected_file_name.split(".")[-1].upper()
        if ext in ("PNG", "JPG", "JPEG"):
            logo_text = "🖼️ ẢNH"
            self.attachment_logo.setStyleSheet(STYLE_LOGO_PDF + " background-color: #e6fffa; color: #319795; border: 1px solid #b2f5ea;")
        elif ext in ("DOC", "DOCX", "WORD"):
            logo_text = "📘 WORD"
            self.attachment_logo.setStyleSheet(STYLE_LOGO_PDF + " background-color: #ebf8ff; color: #2b6cb0; border: 1px solid #bee3f8;")
        elif ext == "PDF":
            logo_text = "📕 PDF"
            self.attachment_logo.setStyleSheet(STYLE_LOGO_PDF)
        else:
            logo_text = "📁 TỆP"
            self.attachment_logo.setStyleSheet(STYLE_LOGO_PDF + " background-color: #edf2f7; color: #4a5568; border: 1px solid #e2e8f0;")

        self.attachment_logo.setText(logo_text)
        self.attachment_name.setText(self.selected_file_name)
        self.attachment_preview.setVisible(True)

    def clear_attachment(self):
        """Hủy đính kèm tệp tin và ẩn khung preview."""
        self.selected_file_path = None
        self.selected_file_name = None
        self.attachment_preview.setVisible(False)

    def create_input_box(self):
        """Tạo ô nhập câu hỏi cùng nút tải tệp (+) và gửi tin nhắn."""
        container = self.make_card()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(15, 12, 15, 12)
        c_layout.setSpacing(10)

        # 🚀 A: Khung Preview Đính Kèm Tệp Tin
        self.attachment_preview = QFrame()
        self.attachment_preview.setFixedHeight(34)
        self.attachment_preview.setStyleSheet(STYLE_PREVIEW_CONTAINER)
        
        ap_layout = QHBoxLayout(self.attachment_preview)
        ap_layout.setContentsMargins(8, 4, 8, 4)
        ap_layout.setSpacing(8)

        self.attachment_logo = QLabel("📕 PDF")
        self.attachment_logo.setFont(qfont(FONTS["small_bold_ai"]))
        self.attachment_logo.setFixedSize(56, 20)
        self.attachment_logo.setAlignment(Qt.AlignCenter)
        self.attachment_logo.setStyleSheet(STYLE_LOGO_PDF)
        ap_layout.addWidget(self.attachment_logo)

        self.attachment_name = QLabel("")
        self.attachment_name.setFont(qfont(FONTS["small_ai"]))
        self.attachment_name.setStyleSheet(STYLE_ATTACH_NAME)
        ap_layout.addWidget(self.attachment_name, 1)

        btn_cancel = QPushButton("✕")
        btn_cancel.setFixedSize(20, 20)
        btn_cancel.setFont(qfont(("Segoe UI", 9, "bold")))
        btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
        btn_cancel.setStyleSheet(STYLE_CANCEL_BTN)
        btn_cancel.clicked.connect(self.clear_attachment)
        ap_layout.addWidget(btn_cancel)

        self.attachment_preview.setVisible(False)
        c_layout.addWidget(self.attachment_preview)

        # 🚀 B: Vùng Nhập Liệu
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập câu hỏi học tập tại đây (Nhấn Shift + Enter để xuống dòng)...")
        self.text_input.setFont(qfont(FONTS["body_ai"]))
        self.text_input.setFixedHeight(70)
        self.text_input.setStyleSheet(STYLE_TEXT_INPUT)
        c_layout.addWidget(self.text_input)

        # 🚀 C: Thanh Công Cụ Phía Dưới
        tool_row = QHBoxLayout()
        tool_row.setContentsMargins(0, 0, 0, 0)
        tool_row.setSpacing(10)

        # Nút cộng (+) đính kèm tệp tài liệu
        btn_attach = QPushButton("＋")
        btn_attach.setFixedSize(38, 38)
        btn_attach.setFont(qfont(("Segoe UI", 16, "bold")))
        btn_attach.setCursor(QCursor(Qt.PointingHandCursor))
        btn_attach.setToolTip("Đính kèm ảnh, tài liệu PDF/Word...")
        btn_attach.setStyleSheet(STYLE_ATTACH_BTN)
        btn_attach.clicked.connect(self.select_attachment)
        tool_row.addWidget(btn_attach)

        tool_row.addStretch()

        # Nút Gửi câu hỏi
        btn_send = QPushButton("➔")
        btn_send.setFixedSize(38, 38)
        btn_send.setFont(qfont(("Segoe UI", 13, "bold")))
        btn_send.setCursor(QCursor(Qt.PointingHandCursor))
        btn_send.setStyleSheet(STYLE_SEND_BTN)
        btn_send.clicked.connect(self._on_send_clicked)
        tool_row.addWidget(btn_send)

        c_layout.addLayout(tool_row)
        self.left_layout.addWidget(container)

    @qasync.asyncSlot()
    async def _on_send_clicked(self):
        """Gửi tin nhắn: Xử lý lưu DB, tự tạo Session mới nếu cần và hiển thị kết quả."""
        text = self.text_input.toPlainText().strip()
        
        if not text and not self.selected_file_path:
            return

        attachment_data = None
        if self.selected_file_path:
            import os
            try:
                size_bytes = os.path.getsize(self.selected_file_path)
                if size_bytes < 1024 * 1024:
                    size_str = f"{round(size_bytes / 1024, 1)} KB"
                else:
                    size_str = f"{round(size_bytes / (1024 * 1024), 1)} MB"
            except Exception:
                size_str = "Chưa rõ"
            
            ext = self.selected_file_name.split(".")[-1].upper()
            attachment_data = {
                "name": self.selected_file_name,
                "size": size_str,
                "path": self.selected_file_path,
                "type": ext
            }

        self.text_input.clear()

        # 1. Tạo phiên hội thoại MySQL nếu đây là tin nhắn đầu tiên của phiên mới
        if self.is_new_session or self.current_session_id is None:
            session_title = text[:25] + "..." if text else (self.selected_file_name[:25] + "...")
            session_id = await self.ai_service.create_chat_session(user_id=self.user_id, title=session_title)
            if session_id:
                self.current_session_id = session_id
                self.history_widget.current_session_id = session_id
                self.is_new_session = False

        # 2. Lưu câu hỏi vào MySQL DB
        if self.current_session_id:
            db_content = text
            if attachment_data:
                db_content += f"\n[Đính kèm tệp: {attachment_data['name']} ({attachment_data['size']})]"
            await self.ai_service.save_chat_message(
                session_id=self.current_session_id,
                role="user",
                content=db_content
            )

        # Hiển thị tin nhắn của người dùng lên UI
        self.add_user_message(text, timestamp="Vừa xong", attachment=attachment_data)
        
        file_path = attachment_data["path"] if attachment_data else None
        self.clear_attachment()

        # 🚀 HIỂN THỊ BÓNG CHAT "ĐANG SUY NGHĨ..." CỦA AI TRƯỚC
        ai_bubble = AIBubbleWidget("StudyAI đang suy nghĩ...", timestamp="Bây giờ", on_copy_callback=lambda txt: self.copy_to_clipboard(txt), parent=self)
        self.chat_area_layout.addWidget(ai_bubble)
        ai_bubble.start_thinking_animation()

        # Gọi Gemini lấy câu trả lời
        try:
            if self.current_session_id:
                reply = await self.ai_service.get_chat_response_db(
                    session_id=self.current_session_id,
                    user_message=text,
                    file_path=file_path
                )
                
                ai_bubble.stop_thinking_animation()

                # Lưu câu trả lời của AI vào MySQL DB
                await self.ai_service.save_chat_message(
                    session_id=self.current_session_id,
                    role="assistant",
                    content=reply
                )
            else:
                reply = await self.ai_service.get_chat_response(message=text)
                ai_bubble.stop_thinking_animation()
        except Exception as e:
            ai_bubble.stop_thinking_animation()
            reply = f"Lỗi AI: {e}"

        # 🚀 CHẠY HIỆU ỨNG GÕ CHỮ TỪ TỪ CHO AI BUBBLE
        def on_typewriter_finished():
            ai_bubble.time_lbl.setText("Vừa xong")
            ai_bubble.update_copy_text(reply)

        ai_bubble.start_typewriter_effect(
            text=reply,
            scroll_callback=self.scroll_to_bottom,
            on_finished=on_typewriter_finished
        )

        # Cập nhật lại lịch sử bên phải
        await self.load_history_from_db()