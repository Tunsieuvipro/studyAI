from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
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

from app.FE.components.select_hour import TimePickerDialog
from app.FE.components.select_date import StyledCalendar

PRIMARY = "#4C96F5"
PRIMARY_HOVER = "#357FE0"
BG = "#F5F7FB"
CARD = "#FFFFFF"
BORDER = "#D8E0EE"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748B"


def make_font(size, bold=False):
    """Tạo đối tượng QFont với font Segoe UI và định dạng in đậm tùy chọn."""
    font = QFont("Segoe UI", size)
    font.setWeight(QFont.Bold if bold else QFont.Normal)
    return font

class AddScheduleDialog(QDialog):
    """Cửa sổ hội thoại để thêm một tiết học/lịch học mới vào thời khóa biểu."""
    def __init__(self, home_service, parent=None):
        super().__init__(parent)
        self.home_service = home_service
        self.setWindowTitle("Thêm lịch học")
        self.setModal(True)
        self.setFixedSize(720, 720) # Giảm chiều cao xuống 720px gọn gàng
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(self._style_sheet())
        self._center_on_screen() # Tự động căn giữa màn hình khi mở form

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. Header tiêu đề
        main_layout.addWidget(self._build_header())

        # 2. Vùng chọn thời gian (Ngày & Giờ bắt đầu/kết thúc)
        main_layout.addWidget(self._build_time_section())

        # 3. Vùng nhập thông tin học phần (Môn học, phòng, loại hình)
        main_layout.addWidget(self._build_course_section())

        # 4. Vùng ghi chú thêm
        main_layout.addWidget(self._build_note_section())

        # 5. Thanh nút bấm Footer (Hủy / Thêm lịch)
        main_layout.addWidget(self._build_footer())

    def showEvent(self, event):
        """Đảm bảo định vị cửa sổ nằm chính xác giữa màn hình khi hiển thị."""
        super().showEvent(event)
        self._center_on_screen()

    def _center_on_screen(self):
        """Căn giữa cửa sổ dialog hoàn hảo cả trục ngang và trục dọc trên màn hình chính."""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            # Lấy vùng không gian hiển thị khả dụng (đã trừ đi thanh Taskbar của Windows)
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            # Di chuyển cửa sổ đến vị trí trung tâm tuyệt đối của màn hình chính
            self.move(screen_geo.x() + x, screen_geo.y() + y)

    def _build_header(self):
        """Xây dựng phần đầu của form gồm biểu tượng lịch và tiêu đề."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 2)
        layout.setSpacing(12)

        icon = QLabel("📅")
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background-color: #EAF2FF; color: {PRIMARY}; border-radius: 14px; font-size: 24px;"
        )
        layout.addWidget(icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        title = QLabel("Thêm lịch học")
        title.setFont(make_font(18, True))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        title_box.addWidget(title)

        subtitle = QLabel("Nhập thông tin để thêm lịch học mới")
        subtitle.setFont(make_font(11))
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY};")
        title_box.addWidget(subtitle)

        layout.addLayout(title_box, 1)
        return header

    def _build_time_section(self):
        """Tạo phần chọn thời gian cho lịch học."""
        card, layout = self._create_card("Thời gian")
        card.setMinimumHeight(210)

        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_time_edit = self._create_time_input(QTime.currentTime().toString("HH:mm"))
        self.end_time_edit = self._create_time_input(QTime.currentTime().addSecs(90 * 60).toString("HH:mm"))

        for date_edit in (self.start_date_edit, self.end_date_edit):
            date_edit.setCalendarPopup(True)
            date_edit.setCalendarWidget(StyledCalendar(date_edit))
            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setFixedHeight(36)
            date_edit.setCursor(QCursor(Qt.PointingHandCursor))
            self._setup_emoji_icon(date_edit, "📅")

        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # Chia đều grid thành 4 cột
        for i in range(4):
            grid.setColumnStretch(i, 1)

        self._add_field(grid, "Ngày bắt đầu", self.start_date_edit, 0, 0, 1, 2)
        self._add_field(grid, "Ngày kết thúc", self.end_date_edit, 0, 2, 1, 2)
        self._add_field(grid, "Giờ bắt đầu", self.start_time_edit, 1, 0, 1, 2)
        self._add_field(grid, "Giờ kết thúc", self.end_time_edit, 1, 2, 1, 2)
        layout.addLayout(grid)

        return card

    def _create_time_input(self, value):
        """Tạo ô nhập liệu thời gian và cấu hình click mở TimePicker."""
        time_input = QLineEdit(value)
        time_input.setReadOnly(True)
        time_input.setFixedHeight(36)
        time_input.setCursor(QCursor(Qt.PointingHandCursor))
        self._setup_emoji_icon(time_input, "🕒")
        time_input.mousePressEvent = lambda event, widget=time_input: self._open_time_picker(widget)
        return time_input

    def _open_time_picker(self, target_input):
        """Mở cửa sổ chọn giờ chi tiết."""
        dialog = TimePickerDialog(target_input.text(), self)
        if dialog.exec() == QDialog.Accepted:
            target_input.setText(dialog.get_time())

    def _build_course_section(self):
        """Tạo phần nhập thông tin học phần."""
        card, layout = self._create_card("Thông tin học phần")
        card.setMinimumHeight(210)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nhập tên môn học hoặc tiêu đề...")
        self.title_input.setFixedHeight(36)

        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("VD: A205, B101...")
        self.room_input.setFixedHeight(36)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lý thuyết", "Thực hành", "Thể dục"])
        self.type_combo.setFixedHeight(36)
        self.type_combo.setCursor(QCursor(Qt.PointingHandCursor))

        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(18)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self._add_field(grid, "Tiêu đề", self.title_input, 0, 0, 1, 2)
        self._add_field(grid, "Phòng học", self.room_input, 1, 0)
        self._add_field(grid, "Loại buổi học", self.type_combo, 1, 1)
        layout.addLayout(grid)

        return card

    def _build_note_section(self):
        """Tạo phần ghi chú cho lịch học với layout an toàn."""
        card, layout = self._create_card("Ghi chú")
        card.setFixedHeight(105)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Nhập ghi chú nếu có...")
        self.note_input.setFixedHeight(50)

        layout.setContentsMargins(15, 10, 15, 10)
        layout.addWidget(self.note_input)

        return card

    def _build_footer(self):
        """Tạo phần chân trang với các nút chức năng."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.addStretch()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Thêm lịch học")
        submit_btn.setObjectName("submitButton")
        submit_btn.setFixedSize(140, 36)
        submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        submit_btn.clicked.connect(self._submit)
        layout.addWidget(submit_btn)

        return footer

    def _create_card(self, title_text):
        """Tạo khung bọc thẻ bo góc đặc trưng."""
        card = QFrame()
        card.setObjectName("sectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setFont(make_font(13, True))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        return card, layout

    def _add_field(self, grid, label_text, widget, row, col, row_span=1, col_span=1):
        """Bọc widget vào một layout có label tiêu đề phía trên."""
        wrapper = QWidget()
        wrapper.setMinimumHeight(65)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 3)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setFont(make_font(11, True))
        label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(label)
        layout.addWidget(widget)

        grid.addWidget(wrapper, row, col, row_span, col_span)

    def _setup_emoji_icon(self, widget, emoji):
        """Thêm biểu tượng Emoji làm vật trang trí bên trong ô nhập liệu."""
        icon_label = QLabel(emoji, widget)
        icon_label.setStyleSheet("background: transparent; font-size: 14px; border: none;")
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(icon_label)

    @qasync.asyncSlot()
    async def _submit(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu tiêu đề", "Vui lòng nhập tiêu đề lịch học.")
            self.title_input.setFocus()
            return

        same_day     = self.start_date_edit.date() == self.end_date_edit.date()
        invalid_time = self.end_time_edit.text() <= self.start_time_edit.text()
        if same_day and invalid_time:
            QMessageBox.warning(
                self, "Thời gian không hợp lệ",
                "Giờ kết thúc phải lớn hơn giờ bắt đầu trong cùng một ngày.",
            )
            return

        # Tự động tính Thứ trong tuần dựa trên Ngày bắt đầu học sinh chọn
        qdate = self.start_date_edit.date()
        # QDate dayOfWeek(): 1 = Thứ 2, ..., 7 = Chủ nhật
        weekday_val = qdate.dayOfWeek()
        
        weekday_names = {
            1: "Thứ 2",
            2: "Thứ 3",
            3: "Thứ 4",
            4: "Thứ 5",
            5: "Thứ 6",
            6: "Thứ 7",
            7: "Chủ nhật"
        }
        weekday_text = weekday_names.get(weekday_val, "Thứ 2")

        data = {
            "start_date": self.start_date_edit.date().toString("dd/MM/yyyy"),
            "end_date":   self.end_date_edit.date().toString("dd/MM/yyyy"),
            "start_time": self.start_time_edit.text(),
            "end_time":   self.end_time_edit.text(),
            "weekday":    weekday_val,
            "weekday_text": weekday_text,
            "title":      title,
            "room":       self.room_input.text().strip(),
            "type":       self.type_combo.currentText(),
            "note":       self.note_input.toPlainText().strip(),
        }

        try:
            # 1. Gọi backend thực hiện in log / lưu vào mảng mock
            await self.home_service.add_schedule(user_id=1, schedule_data=data)
            self.accept()
            return

        except Exception as e:
            print(f"add_schedule lỗi: {e}")
            # Nếu lỗi thật sự thì vẫn cho qua để ra ngoài ép giao diện tự vẽ bằng dữ liệu mock
            self.accept()

    def _style_sheet(self):
        return f"""
            QDialog {{
                background-color: {BG};
            }}
            #sectionCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
            }}
            QLineEdit, QDateEdit, QComboBox, QTextEdit {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 11px;
                font-family: "Segoe UI";
                font-size: 12px;
                selection-background-color: {PRIMARY};
            }}
            QTextEdit {{
                padding: 9px 11px;
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {PRIMARY};
            }}
            QComboBox::drop-down, QDateEdit::drop-down {{
                border: none;
                width: 32px;
            }}
            QDateEdit {{
                padding-right: 30px;
            }}
            QComboBox::down-arrow {{
                image: url(image/down_arrow.png);
                width: 14px;
                height: 14px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                selection-background-color: #EAF2FF;
                selection-color: {TEXT_PRIMARY};
                outline: none;
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
        """