from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


PRIMARY = "#4C96F5"
PRIMARY_HOVER = "#357FE0"
BG = "#F5F7FB"
CARD = "#FFFFFF"
BORDER = "#D8E0EE"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748B"


def make_font(size, bold=False):
    font = QFont("Segoe UI", size)
    font.setWeight(QFont.Bold if bold else QFont.Normal)
    return font


class TimePickerDialog(QDialog):
    """Cửa sổ hội thoại cho phép chọn Giờ và Phút bằng cách cuộn danh sách (List Selection)."""
    def __init__(self, current_time="07:00", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chọn giờ")
        self.setModal(True)
        self.setFixedSize(360, 460)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(self._style_sheet())
        self.selected_time = current_time

        hour, minute = self._parse_time(current_time)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(14)

        title = QLabel("Chọn giờ")
        title.setFont(make_font(20, True))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        main_layout.addWidget(title)

        picker_card = QFrame()
        picker_card.setObjectName("pickerCard")
        picker_layout = QHBoxLayout(picker_card)
        picker_layout.setContentsMargins(14, 14, 14, 14)
        picker_layout.setSpacing(12)

        self.hour_list = self._create_time_list(24)
        self.minute_list = self._create_time_list(60)
        self.hour_list.setCurrentRow(hour)
        self.minute_list.setCurrentRow(minute)

        picker_layout.addWidget(self._wrap_column("Giờ", self.hour_list))
        picker_layout.addWidget(self._wrap_column("Phút", self.minute_list))
        main_layout.addWidget(picker_card, 1)

        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(96, 38)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        confirm_btn = QPushButton("Xác nhận")
        confirm_btn.setObjectName("submitButton")
        confirm_btn.setFixedSize(112, 38)
        confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        confirm_btn.clicked.connect(self._confirm)
        footer.addWidget(confirm_btn)
        main_layout.addLayout(footer)

        self.hour_list.scrollToItem(self.hour_list.currentItem())
        self.minute_list.scrollToItem(self.minute_list.currentItem())

    def get_time(self):
        """Trả về chuỗi thời gian đã chọn theo định dạng HH:mm."""
        return self.selected_time

    def _confirm(self):
        hour = self.hour_list.currentItem().text()
        minute = self.minute_list.currentItem().text()
        self.selected_time = f"{hour}:{minute}"
        self.accept()

    def _create_time_list(self, count):
        list_widget = QListWidget()
        list_widget.setObjectName("timeList")
        list_widget.setFixedWidth(140)
        list_widget.setSpacing(4)
        for value in range(count):
            item = QListWidgetItem(f"{value:02d}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setSizeHint(QSize(1, 34))
            list_widget.addItem(item)
        return list_widget

    def _wrap_column(self, title_text, list_widget):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(title_text)
        label.setFont(make_font(12, True))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(label)
        layout.addWidget(list_widget)
        return wrapper

    def _parse_time(self, value):
        try:
            hour_text, minute_text = value.split(":")
            hour = max(0, min(23, int(hour_text)))
            minute = max(0, min(59, int(minute_text)))
            return hour, minute
        except (ValueError, AttributeError):
            return 0, 0

    def _style_sheet(self):
        return f"""
            QDialog {{ background-color: {BG}; }}
            #pickerCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; }}
            #timeList {{
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 6px;
                outline: none;
                color: {TEXT_PRIMARY};
                font-family: "Segoe UI";
                font-size: 15px;
            }}
            #timeList::item {{
                border-radius: 8px;
                padding: 7px 0;
            }}
            #timeList::item:hover {{ background-color: #EAF2FF; }}
            #timeList::item:selected {{
                background-color: #EAF2FF;
                color: {PRIMARY};
                font-weight: 700;
            }}
            QPushButton {{
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: 600;
                border-radius: 9px;
            }}
            #submitButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: none;
            }}
            #submitButton:hover {{ background-color: {PRIMARY_HOVER}; }}
            #cancelButton {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
            }}
            #cancelButton:hover {{ background-color: #F8FAFC; }}
        """