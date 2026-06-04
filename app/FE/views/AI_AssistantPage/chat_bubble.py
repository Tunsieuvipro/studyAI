from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget
)
from app.FE.config import COLORS, FONTS
from app.FE.views.AI_AssistantPage.qss_AI_Assiistant import *

def qfont(font_tuple):
    """Hàm tiện ích để tạo QFont từ tuple cấu hình trong file config."""
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class UserBubbleWidget(QFrame):
    """Widget hiển thị bong bóng tin nhắn của người dùng."""
    def __init__(self, text, timestamp="", attachment=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        w_layout = QHBoxLayout(self)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.addStretch() # Đẩy bong bóng về bên phải

        bubble_wrap = QVBoxLayout()
        bubble_wrap.setAlignment(Qt.AlignRight)

        bubble = QFrame()
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        bubble.setStyleSheet(STYLE_USER_BUBBLE)
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(8)

        lbl = QLabel(text)
        lbl.setFont(qfont(FONTS["body_ai"]))
        lbl.setStyleSheet(STYLE_USER_BUBBLE_LBL)
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(450)
        b_layout.addWidget(lbl)

        # Nếu có đính kèm tệp tin
        if attachment:
            att_card = QFrame()
            att_card.setStyleSheet(STYLE_ATTACHMENT_CARD)
            a_layout = QHBoxLayout(att_card)
            a_layout.setContentsMargins(10, 10, 10, 10)
            a_layout.setSpacing(10)

            file_ext = attachment.get("type", "PDF")
            pdf_icon = QLabel(file_ext)
            pdf_icon.setFixedSize(40, 40)
            pdf_icon.setAlignment(Qt.AlignCenter)
            if file_ext in ("PNG", "JPG", "JPEG"):
                pdf_icon.setStyleSheet(STYLE_ATTACHMENT_ICON + " background-color: #e6fffa; color: #319795;")
            elif file_ext in ("DOC", "DOCX", "WORD"):
                pdf_icon.setStyleSheet(STYLE_ATTACHMENT_ICON + " background-color: #ebf8ff; color: #2b6cb0;")
            else:
                pdf_icon.setStyleSheet(STYLE_ATTACHMENT_ICON)
            a_layout.addWidget(pdf_icon)

            info = QVBoxLayout()
            name_lbl = QLabel(attachment["name"])
            name_lbl.setFont(qfont(FONTS["small_bold_ai"]))
            name_lbl.setStyleSheet(STYLE_ATTACHMENT_TXT)
            info.addWidget(name_lbl)

            size_lbl = QLabel(attachment["size"])
            size_lbl.setFont(qfont(FONTS["small_ai"]))
            size_lbl.setStyleSheet(STYLE_ATTACHMENT_SIZE)
            info.addWidget(size_lbl)
            a_layout.addLayout(info, 1)

            eye_icon = QLabel("👁")
            eye_icon.setStyleSheet(STYLE_TRANSPARENT + " font-size: 15px; border: none;")
            a_layout.addWidget(eye_icon)

            b_layout.addWidget(att_card)

        time_lbl = QLabel(timestamp)
        time_lbl.setFont(qfont(FONTS["small_ai"]))
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        time_lbl.setAlignment(Qt.AlignRight)

        bubble_wrap.addWidget(bubble)
        bubble_wrap.addWidget(time_lbl)

        w_layout.addLayout(bubble_wrap)


class AIBubbleWidget(QFrame):
    """Widget hiển thị bong bóng tin nhắn của Trợ lý StudyAI kèm các hiệu ứng gõ chữ và copy."""
    def __init__(self, text, timestamp="", on_copy_callback=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.on_copy_callback = on_copy_callback
        self.text_content = text

        w_layout = QHBoxLayout(self)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        avatar = QLabel("🤖")
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(STYLE_AVATAR)

        av_layout = QVBoxLayout()
        av_layout.addWidget(avatar)
        av_layout.addStretch()
        w_layout.addLayout(av_layout)

        bubble_wrap = QVBoxLayout()

        bubble = QFrame()
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        bubble.setStyleSheet(STYLE_AI_BUBBLE)
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(8)

        self.lbl = QLabel(text)
        self.lbl.setFont(qfont(FONTS["body_ai"]))
        self.lbl.setStyleSheet(STYLE_USER_BUBBLE_LBL)
        self.lbl.setWordWrap(True)
        self.lbl.setMaximumWidth(500)
        b_layout.addWidget(self.lbl)

        bottom = QHBoxLayout()
        self.time_lbl = QLabel(timestamp)
        self.time_lbl.setFont(qfont(FONTS["small_ai"]))
        self.time_lbl.setStyleSheet(STYLE_ATTACHMENT_SIZE)
        bottom.addWidget(self.time_lbl)
        bottom.addStretch()

        self.btn_copy = QPushButton("📋 Copy")
        self.btn_copy.setFixedHeight(26)
        self.btn_copy.setFont(qfont(FONTS["small_ai"]))
        self.btn_copy.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_copy.setStyleSheet(STYLE_CHAT_ACTION_BTN)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        bottom.addWidget(self.btn_copy)

        b_layout.addLayout(bottom)
        bubble_wrap.addWidget(bubble)

        w_layout.addLayout(bubble_wrap)
        w_layout.addStretch() # Đẩy bong bóng về bên trái

    def _on_copy_clicked(self):
        """Khi bấm nút copy."""
        if self.on_copy_callback:
            self.on_copy_callback(self.text_content)

    def update_copy_text(self, text):
        """Cập nhật văn bản mới cho nút copy khi đổi nội dung sau gõ xong."""
        self.text_content = text
        try:
            self.btn_copy.clicked.disconnect()
        except Exception:
            pass
        self.btn_copy.clicked.connect(self._on_copy_clicked)

    def start_thinking_animation(self):
        """Tạo hiệu ứng động 3 chấm chạy chạy (...) trong lúc đợi AI phản hồi."""
        from PySide6.QtCore import QTimer
        state = {"dots": 1}
        timer = QTimer(self.lbl)
        
        def update_dots():
            dots_str = "." * state["dots"]
            self.lbl.setText(f"StudyAI đang suy nghĩ{dots_str}")
            state["dots"] = (state["dots"] % 3) + 1
            
        timer.timeout.connect(update_dots)
        timer.start(400) # Lặp lại mỗi 400ms
        self.lbl.setProperty("thinking_timer", timer)

    def stop_thinking_animation(self):
        """Dừng hiệu ứng suy nghĩ và xóa timer."""
        timer = self.lbl.property("thinking_timer")
        if timer:
            timer.stop()
            timer.deleteLater()
            self.lbl.setProperty("thinking_timer", None)

    def start_typewriter_effect(self, text, scroll_callback=None, on_finished=None):
        """Tạo hiệu ứng máy đánh chữ chạy chữ từ từ mượt mà cực xịn."""
        from PySide6.QtCore import QTimer
        state = {"idx": 0}
        timer = QTimer(self.lbl)
        
        def update_text():
            if state["idx"] < len(text):
                step = 4 if len(text) > 400 else (2 if len(text) > 150 else 1)
                state["idx"] += step
                self.lbl.setText(text[:state["idx"]])
                if scroll_callback:
                    scroll_callback()
            else:
                timer.stop()
                timer.deleteLater()
                if on_finished:
                    on_finished()
                    
        timer.timeout.connect(update_text)
        timer.start(8)
