from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from app.FE.config import COLORS, FONTS
from app.FE.views.documentsPage.qss_document import *

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class ExamCardWidget(QFrame):
    """Widget đại diện cho mỗi Thẻ tài liệu/Đề thi hiển thị trên danh sách chính."""
    def __init__(self, exam, on_view_callback, on_download_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_card")
        self.setStyleSheet(STYLE_CHAT_CARD)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        is_pdf = exam.get("file_type", "PDF") == "PDF"
        icon_color    = "#E74C3C" if is_pdf else "#2980B9"
        icon_bg_color = "#FDDEDE" if is_pdf else "#D6EAFB"
        icon_text     = "PDF"     if is_pdf else "DOC"

        file_icon = QLabel(icon_text)
        file_icon.setFixedSize(65, 65)
        file_icon.setAlignment(Qt.AlignCenter)
        file_icon.setStyleSheet(f"background-color: {icon_bg_color}; color: {icon_color}; {STYLE_FILE_ICON}")
        layout.addWidget(file_icon)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        name_lbl = QLabel(exam.get("name", "Tài liệu học tập"))
        name_lbl.setFont(qfont(FONTS["body_bold_exam"]))
        name_lbl.setStyleSheet(STYLE_LABEL_PRIMARY)
        info_layout.addWidget(name_lbl)

        sub_lbl = QLabel(exam.get("sub", "Mô tả tài liệu"))
        sub_lbl.setFont(qfont(FONTS["small_exam"]))
        sub_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        info_layout.addWidget(sub_lbl)

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)

        tags = [
            (exam.get("subject", "Chưa rõ"), COLORS["primary"], "#DCF0FF")
        ]
        
        grade_val = exam.get("grade")
        if grade_val and grade_val != "Không có":
            tags.append((grade_val, COLORS["text_secondary"], "#F1F5F9"))
            
        tags.append((exam.get("type", "Tài liệu"), COLORS.get("warning", "#F59E0B"), "#FEF3C7"))

        for text, color, bg in tags:
            tag_lbl = QLabel(f" {text} ")
            tag_lbl.setFont(qfont(FONTS["small_bold_exam"]))
            tag_lbl.setStyleSheet(f"""
                background-color: {bg};
                color: {color};
                border-radius: 6px;
                padding: 2px 4px;
                border: none;
            """)
            tags_layout.addWidget(tag_lbl)
        tags_layout.addStretch()

        info_layout.addLayout(tags_layout)
        layout.addLayout(info_layout, 1)

        right_info = QVBoxLayout()
        right_info.setSpacing(6)
        right_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        date_lbl = QLabel(f"📅 {exam.get('date', '---')}")
        date_lbl.setFont(qfont(FONTS["small_exam"]))
        date_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        date_lbl.setAlignment(Qt.AlignRight)
        right_info.addWidget(date_lbl)

        meta_lbl = QLabel(f"👁️ {exam.get('views', 0)} lượt  •  ⬇️ {exam.get('downloads', 0)} lượt  •  {exam.get('size', '0 KB')}")
        meta_lbl.setFont(qfont(FONTS["small_exam"]))
        meta_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        meta_lbl.setAlignment(Qt.AlignRight)
        right_info.addWidget(meta_lbl)

        btns_layout = QHBoxLayout()
        btns_layout.setAlignment(Qt.AlignRight)
        btns_layout.setSpacing(8)

        btn_view = QPushButton("Xem")
        btn_view.setFixedSize(80, 32)
        btn_view.setFont(qfont(FONTS["small_bold_exam"]))
        btn_view.setCursor(QCursor(Qt.PointingHandCursor))
        btn_view.setStyleSheet(STYLE_BTN_VIEW)

        btn_dl = QPushButton("Tải")
        btn_dl.setFixedSize(80, 32)
        btn_dl.setFont(qfont(FONTS["small_bold_exam"]))
        btn_dl.setCursor(QCursor(Qt.PointingHandCursor))
        btn_dl.setStyleSheet(STYLE_BTN_DOWNLOAD)

        # Khởi tạo sự kiện click
        doc_id = exam.get("id")
        btn_view.clicked.connect(lambda checked=False: on_view_callback(doc_id))
        btn_dl.clicked.connect(lambda checked=False: on_download_callback(doc_id))

        btns_layout.addWidget(btn_view)
        btns_layout.addWidget(btn_dl)
        right_info.addLayout(btns_layout)

        layout.addLayout(right_info)
