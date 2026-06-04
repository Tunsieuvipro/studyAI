from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import qasync

from app.FE.components.select_date import create_date_edit
from app.FE.components.select_hour import TimePickerDialog


PRIMARY = "#4C96F5"
PRIMARY_HOVER = "#357FE0"
BG = "#F5F7FB"
CARD = "#FFFFFF"
BORDER = "#D8E0EE"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748B"
DANGER = "#EF4444"


def make_font(size, bold=False):
    font = QFont()
    font.setPointSize(size)
    # Ép dùng Enum chuẩn thay vì truyền số nguyên int
    if bold:
        font.setWeight(QFont.Weight.Bold)
    else:
        font.setWeight(QFont.Weight.Normal)

    return font

class AddTaskDialog(QDialog):
    """Cửa sổ hội thoại (Popup) để người dùng nhập thông tin và thêm nhiệm vụ mới."""
    def __init__(self, home_service, parent=None, on_task_created=None):
        super().__init__(parent)
        self.home_service = home_service
        self.on_task_created = on_task_created
        self.setWindowTitle("Thêm nhiệm vụ")
        self.setModal(True)
        self.setFixedSize(520, 480)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(self._style_sheet())

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)

        card = QFrame()
        card.setObjectName("taskCard")
        root_layout.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Header
        layout.addWidget(self._build_header())

        # Task name
        layout.addWidget(self._build_task_name())

        # Deadline date/time
        layout.addWidget(self._build_deadline())

        # Note
        layout.addWidget(self._build_note())
        layout.addStretch()

        # Footer
        root_layout.addWidget(self._build_footer())

    def _build_header(self):
        """Xây dựng phần đầu của form gồm Icon và Tiêu đề."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(12)

        icon = QLabel("✅")
        icon.setFixedSize(42, 42)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background-color: #EAF2FF; color: {PRIMARY}; border-radius: 12px; font-size: 21px;"
        )
        layout.addWidget(icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title = QLabel("Thêm nhiệm vụ")
        title.setFont(make_font(18, True))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        title_box.addWidget(title)

        subtitle = QLabel("Tạo nhiệm vụ học tập mới")
        subtitle.setFont(make_font(11))
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY};")
        title_box.addWidget(subtitle)

        layout.addLayout(title_box, 1)

        return header

    def _build_task_name(self):
        """Tạo ô nhập tên nhiệm vụ."""
        wrapper = self._field_wrapper("Tên nhiệm vụ")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("VD: Nộp bài tập Lập trình Python")
        self.name_input.setFixedHeight(40)
        wrapper.layout().addWidget(self.name_input)
        return wrapper

    def _build_deadline(self):
        """Tạo khu vực chọn Ngày và Giờ hết hạn (Deadline)."""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        date_field = self._field_wrapper("Ngày hết hạn")
        self.deadline_date_edit = create_date_edit(self)
        self.deadline_date_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self._setup_emoji_icon(self.deadline_date_edit, "📅")
        date_field.layout().addWidget(self.deadline_date_edit)

        time_field = self._field_wrapper("Giờ hết hạn")
        self.deadline_time_input = QLineEdit("23:55")
        self.deadline_time_input.setReadOnly(True)
        self.deadline_time_input.setFixedHeight(40)
        self.deadline_time_input.setCursor(QCursor(Qt.PointingHandCursor))
        self.deadline_time_input.mousePressEvent = lambda event, w=self.deadline_time_input: self._open_time_picker(w)
        self._setup_emoji_icon(self.deadline_time_input, "🕒")
        time_field.layout().addWidget(self.deadline_time_input)

        layout.addWidget(date_field, 1)
        layout.addWidget(time_field, 1)
        return row

    def _open_time_picker(self, target_input):
        """Mở cửa sổ chọn giờ khi người dùng click vào ô nhập giờ."""
        dialog = TimePickerDialog(target_input.text(), self)
        if dialog.exec() == QDialog.Accepted:
            target_input.setText(dialog.get_time())

    def _build_note(self):
        """Tạo ô nhập ghi chú chi tiết cho nhiệm vụ."""
        wrapper = self._field_wrapper("Ghi chú")
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Nhập ghi chú nếu có...")
        self.note_input.setFixedHeight(80)
        wrapper.layout().addWidget(self.note_input)
        wrapper.layout().setContentsMargins(0, 0, 0, 10)
        return wrapper

    def _build_footer(self):
        """Tạo phần chân trang với các nút Hủy và Thêm."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.addStretch()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(96, 38)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Thêm nhiệm vụ")
        submit_btn.setObjectName("submitButton")
        submit_btn.setFixedSize(128, 38)
        submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        submit_btn.clicked.connect(self._submit)
        layout.addWidget(submit_btn)

        return footer

    def _field_wrapper(self, label_text):
        """Hàm hỗ trợ bọc một ô nhập liệu kèm theo nhãn (Label) phía trên."""
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setFont(make_font(11, True))
        label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(label)
        return wrapper

    def _setup_emoji_icon(self, widget, emoji):
        """Chèn một biểu tượng Emoji vào phía bên phải của Widget nhập liệu."""
        icon_label = QLabel(emoji, widget)
        icon_label.setStyleSheet("background: transparent; font-size: 14px; border: none;")
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(icon_label)

    @qasync.asyncSlot()
    async def _submit(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Thiếu tên", "Vui lòng nhập tên nhiệm vụ.")
            return

        # 🌟 PHẢI ĐÚNG CẤU TRÚC ĐỂ REPAINT_TASKS NHẬN ĐƯỢC
        task_data = {
            "name": name,
            "deadline": f"{self.deadline_date_edit.date().toString('dd/MM/yyyy')} {self.deadline_time_input.text()}",
            "done": False, # Thêm key này vào để Checkbox không bị lỗi
            "note": self.note_input.toPlainText().strip()
        }
        try:
            user_id = getattr(self.parent(), "user_id", 1) or 1
            success = await self.home_service.add_task(user_id=user_id, task_data=task_data)
        except Exception as e:
            print(f"add_task lỗi: {e}")
            success = False

        if success:
            if self.on_task_created:
                self.on_task_created(task_data)
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu nhiệm vụ. Vui lòng thử lại.")

    def _style_sheet(self):
        return f"""
            QDialog {{
                background-color: {BG};
            }}
            QMessageBox {{
                background-color: #FFFFFF;
            }}
            QMessageBox QLabel {{
                color: #111827;
                font-family: "Segoe UI";
                font-size: 13px;
            }}
            QMessageBox QPushButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                min-width: 70px;
                min-height: 24px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            #taskCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
            }}
            QLineEdit, QDateEdit, QTextEdit {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 0 12px;
                padding-right: 30px;
                font-family: "Segoe UI";
                font-size: 13px;
                selection-background-color: {PRIMARY};
                selection-color: #FFFFFF;
            }}
            QTextEdit {{
                padding: 9px 12px;
            }}
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {{
                border: 1px solid {PRIMARY};
            }}
            QPushButton {{
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
                border-radius: 9px;
            }}
            #submitButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: none;
            }}
            #submitButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            #cancelButton {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
            }}
            #cancelButton:hover {{
                background-color: #F8FAFC;
            }}
            #closeButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 22px;
                font-weight: 700;
            }}
            #closeButton:hover {{
                background-color: #EAF2FF;
                color: {DANGER};
            }}
        """