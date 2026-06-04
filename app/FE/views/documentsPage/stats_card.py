from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from app.FE.config import COLORS, FONTS
from app.FE.views.documentsPage.qss_document import *

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class StatsRowWidget(QFrame):
    """Widget hiển thị hàng 4 thẻ chỉ số thống kê tài liệu học tập trên đầu trang."""
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_TRANSPARENT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10) # Giảm spacing xuống 10 để tiết kiệm không gian ngang

        def safe_get(key):
            val = stats.get(key)
            return val if val is not None else 0

        stats_data = [
            ("📋", str(safe_get("total")), "Tổng tài liệu", COLORS["primary"], "#DCF0FF"),
            ("📄", str(safe_get("pdf_count")), "PDF", "#E74C3C", "#FDDEDE"),
            ("📝", str(safe_get("word_count")), "Word", "#2980B9", "#D6EAFB"),
            ("⬇️", str(safe_get("recent_downloads")), "Lượt tải về", COLORS.get("success", "#10B981"), "#D4EDDA"),
        ]

        for icon, number, label, color, bg_color in stats_data:
            # Tạo khung thẻ con
            card = QFrame()
            card.setObjectName("chat_card")
            card.setStyleSheet(STYLE_CHAT_CARD)
            
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(10, 10, 10, 10) # Giảm padding cực mạnh từ 20 xuống 10
            c_layout.setSpacing(8) # Giảm spacing từ 12 xuống 8

            icon_box = QLabel(icon)
            icon_box.setFixedSize(36, 36) # Thu gọn icon từ 45x45 xuống 36x36
            icon_box.setAlignment(Qt.AlignCenter)
            icon_box.setStyleSheet(f"background-color: {bg_color}; {STYLE_ICON_BOX}")
            c_layout.addWidget(icon_box)

            text_box = QVBoxLayout()
            text_box.setSpacing(1)
            num_lbl = QLabel(number)
            num_lbl.setFont(qfont((FONTS["h3_exam"][0], FONTS["h3_exam"][1] - 2, "bold"))) # Giảm 2 size cho số đếm
            num_lbl.setStyleSheet(STYLE_LABEL_PRIMARY)

            desc_lbl = QLabel(label)
            desc_lbl.setFont(qfont((FONTS["small_exam"][0], FONTS["small_exam"][1] - 1))) # Giảm 1 size cho mô tả
            desc_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)

            text_box.addWidget(num_lbl)
            text_box.addWidget(desc_lbl)
            c_layout.addLayout(text_box)
            c_layout.addStretch()

            layout.addWidget(card, 1)
