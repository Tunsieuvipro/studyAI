import qasync
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QMessageBox
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

class HistoryPanelWidget(QFrame):
    """Widget quản lý thanh Lịch sử hội thoại bên phải."""
    def __init__(self, ai_service, user_id, on_session_selected, on_new_chat_clicked, parent=None):
        super().__init__(parent)
        self.ai_service = ai_service
        self.user_id = user_id
        self.on_session_selected = on_session_selected
        self.on_new_chat_clicked = on_new_chat_clicked
        self.current_session_id = None
        self.history_items = [] # Chứa các tuple (title, session_id)

        self.setStyleSheet(STYLE_TRANSPARENT)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Tạo Card Lịch sử
        hist_card = QFrame()
        hist_card.setObjectName("chat_card")
        hist_card.setStyleSheet(STYLE_CHAT_CARD)
        h_layout = QVBoxLayout(hist_card)
        h_layout.setContentsMargins(10, 10, 10, 10)
        h_layout.setSpacing(10)

        # Header Lịch sử
        hdr = QFrame()
        hdr.setStyleSheet(STYLE_HIST_HDR)
        hdr.setFixedHeight(40)
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(8, 0, 8, 0)

        hdr_title = QLabel("💬  Lịch sử hội thoại")
        hdr_title.setFont(qfont(FONTS["body_bold_ai"]))
        hdr_title.setStyleSheet("color: #2d3748; border: none;")
        hdr_layout.addWidget(hdr_title)
        hdr_layout.addStretch()

        h_layout.addWidget(hdr)

        # Vùng cuộn chứa lịch sử
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet(STYLE_RIGHT_SCROLL + " border: none;")
        
        self.history_container = QWidget()
        self.history_container.setStyleSheet(STYLE_TRANSPARENT)
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 5, 0)
        self.history_layout.setSpacing(8)
        self.history_layout.setAlignment(Qt.AlignTop)

        self.history_scroll.setWidget(self.history_container)
        h_layout.addWidget(self.history_scroll)

        layout.addWidget(hist_card, 1)

    @qasync.asyncSlot()
    async def load_history(self):
        """Tải dữ liệu lịch sử hội thoại thực từ Database MySQL."""
        sessions = await self.ai_service.load_chat_sessions(user_id=self.user_id)
        self.history_items = [(s["title"], s["id"]) for s in sessions]
        self.render_sidebar()

    def render_sidebar(self):
        """Vẽ danh sách lịch sử hội thoại động lên giao diện cột phải."""
        # Clear cũ
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.history_items:
            empty_lbl = QLabel("Chưa có lịch sử trò chuyện.")
            empty_lbl.setFont(qfont(FONTS["small_ai"]))
            empty_lbl.setStyleSheet(STYLE_HIST_ITEM_TIME + " padding: 15px;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.history_layout.addWidget(empty_lbl)
        else:
            for title, session_id in self.history_items:
                item = QFrame()
                item.setCursor(QCursor(Qt.PointingHandCursor))
                item.setStyleSheet(STYLE_HIST_ITEM)
                item.setFixedHeight(65)
                
                item_layout = QHBoxLayout(item)
                item_layout.setContentsMargins(10, 6, 10, 6)
                item_layout.setSpacing(8)

                info_widget = QWidget()
                info_widget.setStyleSheet("background: transparent; border: none;")
                info_layout = QVBoxLayout(info_widget)
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(2)

                t_lbl = QLabel(title)
                t_lbl.setFont(qfont(FONTS["small_bold_ai"]))
                t_lbl.setStyleSheet(STYLE_HIST_ITEM_TITLE)
                t_lbl.setWordWrap(True)

                time_lbl = QLabel("Hội thoại cũ")
                time_lbl.setFont(qfont(FONTS["small_ai"]))
                time_lbl.setStyleSheet(STYLE_HIST_ITEM_TIME)

                info_layout.addWidget(t_lbl)
                info_layout.addWidget(time_lbl)
                
                item_layout.addWidget(info_widget, 1)

                # Nút xóa nhanh
                btn_delete = QPushButton("🗑")
                btn_delete.setFixedSize(28, 28)
                btn_delete.setFont(qfont(("Segoe UI", 11)))
                btn_delete.setCursor(QCursor(Qt.PointingHandCursor))
                btn_delete.setToolTip("Xóa cuộc hội thoại")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        color: #a0aec0;
                        background-color: transparent;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        color: #e53e3e;
                        background-color: #fed7d7;
                    }
                """)
                btn_delete.clicked.connect(lambda checked=False, sid=session_id: self.delete_session(sid))
                item_layout.addWidget(btn_delete)

                # Sự kiện chọn hội thoại
                item.mousePressEvent = lambda event, sid=session_id: self.on_session_selected(sid)
                self.history_layout.addWidget(item)

        self.history_layout.addStretch()

    @qasync.asyncSlot()
    async def delete_session(self, session_id: int):
        """Xác nhận và xóa phiên trò chuyện khỏi DB MySQL."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Xác nhận xóa")
        msg_box.setText("Bạn có chắc chắn muốn xóa vĩnh viễn cuộc trò chuyện này cùng toàn bộ tin nhắn không?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                min-width: 650px;
            }
            QLabel#qt_msgbox_label {
                color: #1a202c;
                font-size: 13px;
                min-width: 580px;
                line-height: 18px;
            }
            QLabel {
                color: #1a202c;
                font-size: 13px;
            }
            QPushButton {
                color: #2d3748;
                background-color: #ffffff;
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding: 6px 18px;
                min-width: 70px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #edf2f7;
                border-color: #a0aec0;
                color: #1a202c;
            }
        """)
        
        reply = msg_box.exec()
        if reply == QMessageBox.No:
            return

        success = await self.ai_service.delete_chat_session(session_id=session_id, user_id=self.user_id)
        if success:
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.on_new_chat_clicked()
            await self.load_history()
