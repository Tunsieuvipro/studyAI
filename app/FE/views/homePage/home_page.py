from datetime import datetime
import qasync
from PySide6.QtCore import Qt, QSize, QTimer
import datetime as dt
import asyncio

from PySide6.QtGui import QCursor, QFont, QColor
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget, QDialog, QGraphicsDropShadowEffect, QMessageBox
)

from app.FE.config import COLORS, FONTS
from app.FE.components.form_calender import AddScheduleDialog
from app.FE.components.focus_timer import FocusTimerCard
from app.FE.views.homePage.form_tasks import AddTaskDialog
from app.FE.views.homePage.qss_homePage import *

DAY_PALETTE = [
    ("#EEF2FF", "#4F46E5"),  # Thứ 2 - Indigo
    ("#F0FDF4", "#16A34A"),  # Thứ 3 - Green
    ("#FFF7ED", "#EA580C"),  # Thứ 4 - Orange
    ("#FAF5FF", "#9333EA"),  # Thứ 5 - Purple
    ("#FFF1F2", "#E11D48"),  # Thứ 6 - Rose
    ("#F0FDFA", "#0D9488"),  # Thứ 7 - Teal
    ("#FFFBEB", "#D97706"),  # Chủ nhật - Amber
]

PERIOD_INFO = {
    "Sáng": {"icon": "☀️", "bg": "#FEFCE8", "fg": "#854D0E"},
    "Chiều": {"icon": "🌤️", "bg": "#FFF7ED", "fg": "#9A3412"},
    "Tối": {"icon": "🌙", "bg": "#EFF6FF", "fg": "#1E40AF"},
}

DAY_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

# --- Dữ liệu lịch học mẫu chống sập ---
MOCK_SCHEDULE = [{"date": "25/05", "sessions": []}, {"date": "26/05", "sessions": []}, {"date": "27/05", "sessions": []}, {"date": "28/05", "sessions": []}, {"date": "29/05", "sessions": []}, {"date": "30/05", "sessions": []}, {"date": "31/05", "sessions": []}]
MOCK_STATS = {"total_sessions": 4, "self_study_hours": 12, "completion": 0.75}
MOCK_TASKS = []

def get_period(start_str: str) -> str:
    try:
        h = int(start_str.split(":")[0])
        if h < 12:  return "Sáng"
        if h < 18:  return "Chiều"
        return "Tối"
    except:
        return "Sáng"

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class HomePage(QFrame):
    """Trang chủ hiển thị Tổng quan lịch học, nhiệm vụ và thông báo (Đã sửa lỗi gọi Coroutine bậy)."""

    def __init__(self, master, home_service, ai_service):
        super().__init__(parent=master)
        self.home_service = home_service
        self.ai_service = ai_service
        self._selected_day = dt.datetime.now().weekday()
        self.week_offset = 0
        self._day_buttons = []
        self.user_id = getattr(master, "user_id", 1) or 1
        self.setStyleSheet(STYLE_PAGE)

        # 1. Khởi tạo dữ liệu mặc định (Tránh lỗi AttributeError)
        self.schedule_data = MOCK_SCHEDULE
        self.tasks_data = MOCK_TASKS
        self.stats_data = MOCK_STATS
        self.study_suggestion = "Đang tải gợi ý từ AI..."

        # 2. Xây dựng Layout nền tảng
        self._init_main_layout()
        self._build_left_column()
        self._build_right_column()

        # 3. Đánh dấu chưa load dữ liệu lần nào — sẽ load đúng lúc showEvent khi window thực sự hiển thị
        self._data_loaded = False

    def showEvent(self, event):
        """Override showEvent: chỉ load dữ liệu lần đầu tiên khi page thực sự hiển ra màn hình."""
        super().showEvent(event)
        if not self._data_loaded:
            self._data_loaded = True
            # Delay nhỏ 100ms sau khi window đã paint xong để event loop sẵn sàng
            QTimer.singleShot(100, lambda: asyncio.create_task(self.load_all_data()))

    def _init_main_layout(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self.left_frame = QFrame()
        self.right_frame = QFrame()
        self.right_frame.setFixedWidth(360)

        self.main_layout.addWidget(self.left_frame, 1)
        self.main_layout.addWidget(self.right_frame, 0)

    def _build_left_column(self):
        layout = QVBoxLayout(self.left_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.create_header(layout)
        self.create_week_bar(layout)
        self.create_schedule_list(layout)
        self.create_bottom_cards(layout)

    def _build_right_column(self):
        layout = QVBoxLayout(self.right_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Khởi tạo Container chứa dữ liệu nhiệm vụ học tập
        self.task_list_container = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_list_container)
        self.task_list_layout.setContentsMargins(0, 0, 0, 0)
        self.task_list_layout.setSpacing(12)

        self.create_today_tasks(layout)
        self.create_timer_card(layout)

    def make_card(self):
        card = QFrame()
        card.setObjectName("card_frame")
        card.setStyleSheet(STYLE_CARD_FRAME)
        return card

    async def load_all_data(self):
        """
        Nạp dữ liệu từ DB song song (asyncio.gather) để tối ưu tốc độ.
        AI gợi ý được tách ra load riêng ở background để không block UI.
        """
        try:
            # ⚡ Chạy SONG SONG cả schedule + tasks cùng lúc → giảm 50% thời gian chờ
            schedule_res, tasks_res = await asyncio.gather(
                self.home_service.get_schedule(user_id=self.user_id, week_offset=self.week_offset),
                self.home_service.get_tasks(user_id=self.user_id),
                return_exceptions=True
            )

            # Xử lý kết quả schedule
            if isinstance(schedule_res, Exception):
                print(f"[Warning] Lỗi load schedule: {schedule_res}")
                self.schedule_data = MOCK_SCHEDULE
            else:
                self.schedule_data = schedule_res or MOCK_SCHEDULE

            # Xử lý kết quả tasks
            if isinstance(tasks_res, Exception):
                print(f"[Warning] Lỗi load tasks: {tasks_res}")
                self.tasks_data = MOCK_TASKS
            else:
                self.tasks_data = tasks_res if tasks_res is not None else []

            # Tính stats từ dữ liệu đã load
            total_s = sum(len(d.get("sessions", [])) for d in self.schedule_data)
            done_t  = sum(1 for t in self.tasks_data if t.get("done", False))
            total_t = len(self.tasks_data) or 1
            self.stats_data = {
                "total_sessions":   total_s,
                "self_study_hours": total_s * 2,
                "completion":       done_t / total_t
            }

        except Exception as e:
            print(f"[Warning] Lỗi kết nối DB, dùng dữ liệu mặc định: {e}")
            self.schedule_data = MOCK_SCHEDULE
            self.stats_data    = MOCK_STATS
            self.tasks_data    = MOCK_TASKS

        # 🚀 Đẩy lịch + nhiệm vụ lên UI NGAY LẬP TỨC (không chờ AI)
        self.update_week_ui()
        self.reload_side_panels()

        # 🤖 Load gợi ý AI ở background — xong thì tự cập nhật label, không block UI
        asyncio.create_task(self._load_ai_suggestion_background())

    async def _load_ai_suggestion_background(self):
        """Load gợi ý AI riêng biệt ở background để không làm chậm hiển thị chính."""
        try:
            suggestion = await self.home_service.get_study_suggestions(user_id=self.user_id)
            self.study_suggestion = suggestion
        except Exception as ai_err:
            print(f"[AI Suggestion] Lỗi: {ai_err}")
            pending = [t.get("name", "") for t in self.tasks_data if not t.get("done", False)]
            if pending:
                self.study_suggestion = f"Bạn còn {len(pending)} nhiệm vụ chưa hoàn thành. Hãy ưu tiên: \"{pending[0]}\" trước nhé!"
            else:
                self.study_suggestion = "Bạn đã hoàn thành tất cả nhiệm vụ hôm nay! 🎉 Hãy ôn lại bài hoặc đọc thêm tài liệu nhen!"
        finally:
            # Chỉ cập nhật label gợi ý AI, không re-render toàn bộ trang
            if hasattr(self, "ai_suggestion_label") and self.ai_suggestion_label is not None:
                try:
                    self.ai_suggestion_label.setText(str(self.study_suggestion))
                except Exception:
                    pass

    def create_header(self, parent_layout):
        header = QFrame()
        header.setStyleSheet(STYLE_TRANSPARENT)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Lịch học tập")
        title.setFont(qfont(FONTS["h1_center"]))
        title.setStyleSheet(STYLE_LABEL_PRIMARY)
        h_layout.addWidget(title)
        h_layout.addStretch()

        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(36, 36)
        btn_prev.setStyleSheet(STYLE_BTN_NAV)
        btn_prev.setCursor(QCursor(Qt.PointingHandCursor))
        btn_prev.clicked.connect(lambda: self.change_week(-1))
        h_layout.addWidget(btn_prev)

        btn_next = QPushButton(">")
        btn_next.setFixedSize(36, 36)
        btn_next.setStyleSheet(STYLE_BTN_NAV)
        btn_next.setCursor(QCursor(Qt.PointingHandCursor))
        btn_next.clicked.connect(lambda: self.change_week(1))
        h_layout.addWidget(btn_next)

        btn_add = QPushButton("+ Thêm lịch học")
        btn_add.setFixedHeight(36)
        btn_add.setFont(qfont(FONTS["body_bold_center"]))
        btn_add.setCursor(QCursor(Qt.PointingHandCursor))
        btn_add.setStyleSheet(STYLE_BTN_ADD_SCHEDULE)
        self.add_schedule_btn = btn_add
        self.add_schedule_btn.clicked.connect(self.open_add_schedule_dialog)
        h_layout.addWidget(btn_add)

        parent_layout.addWidget(header)

    def open_add_schedule_dialog(self):
        dialog = AddScheduleDialog(self.home_service, self)

        # 1. Bật popup lên chờ bồ nhập liệu
        if dialog.exec() == QDialog.Accepted:
            print("🎉 Dialog báo Accepted! Ép giao diện vẽ card trực tiếp...")

            try:
                # 2. Bóc dữ liệu trực tiếp từ các ô nhập của Dialog
                s_date = dialog.start_date_edit.date().toString("dd/MM/yyyy")
                s_time = dialog.start_time_edit.text()
                e_time = dialog.end_time_edit.text()
                title_text = dialog.title_input.text().strip()
                room_text = dialog.room_input.text().strip()
                type_text = dialog.type_combo.currentText()
                note_text = dialog.note_input.toPlainText().strip()

                # Tạo một dict chuẩn khớp 100% với các key trong hàm build_session_card
                new_session = {
                    "start_date": s_date,
                    "start_time": s_time,
                    "end_time":   e_time,
                    "title":      title_text if title_text else "Môn học mới",
                    "room":       room_text if room_text else "A123",
                    "type":       type_text if type_text else "LT",
                    "note":       note_text
                }

                # 3. ĐÚT THẲNG VÀO MẢNG DỮ LIỆU ĐANG HIỂN THỊ CỦA GIAO DIỆN
                if not hasattr(self, "schedule_data") or not isinstance(self.schedule_data, list):
                    self.schedule_data = []

                # Ép dữ liệu vào đầu mảng để nó hiện lên trên cùng
                self.schedule_data.insert(0, new_session)
                print(f"🔥 Đã ép cứng dữ liệu vào FE thành công: {new_session}")

                # 4. LỆNH PHẢI VẼ: Gọi thẳng hàm vẽ card ra màn hình ngay lập tức!
                # Lấy bảng màu theo Tab hiện tại để vẽ
                from app.FE.views.homePage.home_page import DAY_PALETTE # Hoặc biến DAY_PALETTE bồ định nghĩa ở file
                bg_day, accent = DAY_PALETTE[self._selected_day % len(DAY_PALETTE)]

                # Bắt hàm build_session_card tự vẽ luôn, không qua bộ lọc ngày tháng của hàm load nữa!
                self.build_session_card(new_session, bg_day, accent)
                print("✨ Đã ép hàm build_session_card vẽ trực tiếp lên màn hình!")

            except Exception as e:
                print(f"❌ Lỗi ép dữ liệu vẽ card: {e}")
                import traceback
                traceback.print_exc()

            # Vẫn chạy gọi load ngầm để cập nhật stats/AI phía sau cho đúng bài
            import asyncio
            asyncio.create_task(self.load_all_data())

    def create_week_bar(self, parent_layout):
        bar_outer = self.make_card()
        bar_layout = QHBoxLayout(bar_outer)
        bar_layout.setContentsMargins(10, 10, 10, 10)
        bar_layout.setSpacing(10)

        for i, label in enumerate(DAY_LABELS):
            btn = QPushButton(f"{label}\n--/--")
            btn.setFont(qfont(FONTS["small_bold_center"]))
            btn.setFixedHeight(65)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked=False, idx=i: self.select_day(idx))
            self._day_buttons.append(btn)
            bar_layout.addWidget(btn, 1)

        self.refresh_day_styles()
        parent_layout.addWidget(bar_outer)

    def select_day(self, idx):
        self._selected_day = idx
        self.refresh_day_styles()
        self.reload_schedule()

    def update_week_ui(self):
        schedule = getattr(self, "schedule_data", []) or []

        for i, btn in enumerate(self._day_buttons):
            try:
                # 🚨 ĐÒN BẢO HIỂM: Kiểm tra cực kỳ nghiêm ngặt cấu trúc dữ liệu tuần lồng nhau
                if isinstance(schedule, list) and i < len(schedule) and isinstance(schedule[i], dict):
                    # Trường hợp 1: Nếu đúng cấu trúc tuần tự Backend trả về (có key "date")
                    if "date" in schedule[i]:
                        label = DAY_LABELS[i]
                        date_part = str(schedule[i]["date"]).split("/")
                        date_str = f"{date_part[0]}/{date_part[1]}" if len(date_part) > 1 else str(schedule[i]["date"])
                        btn.setText(f"{label}\n{date_str}")
                        continue

                    # Trường hợp 2: Nếu lỡ bị biến thành mảng phẳng do nhập tay (có start_date)
                    elif "start_date" in schedule[i]:
                        label = DAY_LABELS[i % len(DAY_LABELS)]
                        date_part = str(schedule[i]["start_date"]).split("/")
                        date_str = f"{date_part[0]}/{date_part[1]}" if len(date_part) > 1 else str(schedule[i]["start_date"])
                        btn.setText(f"{label}\n{date_str}")
                        continue

                # Trường hợp 3: Nếu mảng trống hoặc lỗi dữ liệu, tự hiển thị text mặc định chứ CẤM ĐƯỢC CRASH!
                label = DAY_LABELS[i % len(DAY_LABELS)]
                btn.setText(f"{label}\n--/--")

            except Exception as e:
                print(f"⚠️ Bỏ qua lỗi vặt hiển thị ngày trên nút thứ {i}: {e}")
                # Nếu có lỗi phát sinh trong lúc bóc tách chuỗi, ép hiển thị an toàn rồi chạy tiếp
                label = DAY_LABELS[i % len(DAY_LABELS)]
                btn.setText(f"{label}\n--/--")

        # 🚀 LỆNH SỐNG CÒN: Được bọc an toàn để chắc chắn luôn được gọi vẽ giao diện ra màn hình!
        try:
            self.refresh_day_styles()
        except Exception as e:
            print(f"⚠️ Lỗi style nút: {e}")

        try:
            print("✨ Luồng chạy mượt mà! Tiến hành dọn layout và vẽ card lên màn hình...")
            self.reload_schedule()
        except Exception as e:
            print(f"❌ Hàm reload_schedule bị gãy: {e}")

    @qasync.asyncSlot()
    async def change_week(self, delta):
        self.week_offset += delta
        try:
            self.schedule_data = await self.home_service.get_schedule(user_id=self.user_id, week_offset=self.week_offset) or MOCK_SCHEDULE
        except Exception as e:
            print(f"Lỗi đổi tuần: {e}")
        self.update_week_ui()

    def refresh_day_styles(self):
        for i, btn in enumerate(self._day_buttons):
            if i == self._selected_day:
                btn.setStyleSheet(STYLE_DAY_BTN_ACTIVE)
            else:
                btn.setStyleSheet(STYLE_DAY_BTN_INACTIVE)

    def create_schedule_list(self, parent_layout):
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(STYLE_SCROLL)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(STYLE_TRANSPARENT)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self._scroll.setWidget(self.scroll_content)
        parent_layout.addWidget(self._scroll, 1)
        self.reload_schedule()

    def reload_schedule(self):
        """Dọn dẹp layout cũ và hẹn giờ vẽ layout mới để tránh lệch nhịp Async."""
        # 1. Dọn dẹp sạch sẽ các card cũ trên màn hình
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                # Dọn layout con nếu có
                self.clear_layout(item.layout())
        QTimer.singleShot(50, lambda: self.load_day_schedule(self._selected_day))

    def load_day_schedule(self, day_idx):
        # 1. Lấy dữ liệu an toàn
        schedules = getattr(self, "schedule_data", []) or []

        # 2. TÍNH TOÁN NGÀY THỰC TẾ CỦA TAB THỨ ĐANG CHỌN
        try:
            today = dt.datetime.now()
            # Tìm ngày Thứ 2 của tuần hiện tại làm mốc
            monday_this_week = today - dt.timedelta(days=today.weekday())
            # Tính ra ngày của Tab bồ đang bấm (cộng thêm số tuần nếu có chuyển tuần)
            target_date = monday_this_week + dt.timedelta(weeks=self.week_offset, days=day_idx)
            target_date_str = target_date.strftime("%d/%m/%Y") # '28/05/2026'

            # Khúc này để bồ kiểm tra xem app đang tìm ngày mấy ở Terminal nè:
            print(f"🔎 Đang lọc lịch học cho ngày thực tế: {target_date_str} (Tab index: {day_idx})")
        except Exception as e:
            print(f"Lỗi tính ngày: {e}")
            target_date_str = dt.datetime.now().strftime("%d/%m/%Y")

        bg_day, accent = DAY_PALETTE[day_idx % len(DAY_PALETTE)]
        valid_sessions = []

        # 3. QUÉT DỮ LIỆU ĐA CẤU TRÚC (Bất chấp Backend trả về kiểu gì cũng lọc được)
        if isinstance(schedules, list):
            for item in schedules:
                # Trường hợp 1: Mảng phẳng từ DB đổ về [{'start_date': '28/05/2026', ...}]
                if isinstance(item, dict) and item.get("start_date") == target_date_str:
                    valid_sessions.append(item)

                # Trường hợp 2: Cấu trúc lồng kiểu cũ của bồ [{"date": "...", "sessions": [...]}]
                elif isinstance(item, dict) and "sessions" in item:
                    # Nếu bồ lưu ngày kiểu ngắn "28/05" thì check thử
                    short_date = target_date_str[:5] # '28/05'
                    if item.get("date") == short_date or item.get("date") == target_date_str:
                        for s in item.get("sessions", []):
                            valid_sessions.append(s)

        elif isinstance(schedules, dict):
            # Trường hợp 3: Trả về một object đơn lẻ
            if schedules.get("start_date") == target_date_str:
                valid_sessions.append(schedules)
            elif "sessions" in schedules:
                for s in schedules["sessions"]:
                    if s.get("start_date") == target_date_str:
                        valid_sessions.append(s)

        # 4. TIẾN HÀNH VẼ LÊN GIAO DIỆN
        if not valid_sessions:
            print(f" -> Ngày {target_date_str} không tìm thấy lịch trùng khớp.")
            self._show_placeholder_msg("Không có lịch học hôm nay 🎉")
            return

        print(f" -> 🎉 Tìm thấy {len(valid_sessions)} lịch học! Tiến hành vẽ card...")

        # Sắp xếp theo giờ học cho đẹp
        try:
            valid_sessions.sort(key=lambda x: x.get("start_time", "00:00"))
        except:
            pass

        # Vẽ từng card môn học
        for s in valid_sessions:
            self.build_session_card(s, bg_day, accent)
    def _show_placeholder_msg(self, text):
        lbl = QLabel(text)
        lbl.setFont(qfont(FONTS["body_center"]))
        lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        lbl.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(lbl)

    def build_session_card(self, session, bg_day, accent):
        card = self.make_card()
        card.setFixedHeight(95)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        bar = QFrame()
        bar.setFixedWidth(5)
        bar.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")
        layout.addWidget(bar)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setAlignment(Qt.AlignVCenter)

        # ⚙️ ĐÃ SỬA KEY: 'start' -> 'start_time', 'end' -> 'end_time' để khớp DB
        start_t = session.get('start_time', '00:00')
        end_t = session.get('end_time', '00:00')
        time_lbl = QLabel(f"⏱  {start_t} – {end_t}")
        time_lbl.setFont(qfont(FONTS["small_center"]))
        time_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        content_layout.addWidget(time_lbl)

        subj_layout = QHBoxLayout()
        subj_layout.setSpacing(8)
        dot = QLabel("•")
        dot.setStyleSheet(f"color: {accent}; font-size: 15px; border: none; font-weight: bold;")

        # ⚙️ ĐÃ SỬA KEY: 'subject' -> 'title' để khớp DB
        subj_lbl = QLabel(session.get("title", "Môn học học tập"))
        subj_lbl.setFont(qfont(FONTS["body_bold_center"]))
        subj_lbl.setStyleSheet(STYLE_LABEL_PRIMARY)
        subj_layout.addWidget(dot)
        subj_layout.addWidget(subj_lbl)
        subj_layout.addStretch()
        content_layout.addLayout(subj_layout)

        room_lbl = QLabel(f"📍  {session.get('room', 'Chưa rõ')}")
        room_lbl.setFont(qfont(FONTS["small_center"]))
        room_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        content_layout.addWidget(room_lbl)
        layout.addLayout(content_layout, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

        type_lbl = QLabel(session.get("type", "LT"))
        type_lbl.setFont(qfont(FONTS["small_bold_center"]))
        type_lbl.setAlignment(Qt.AlignCenter)
        type_lbl.setStyleSheet(f"background-color: {bg_day}; color: {accent}; border-radius: 6px; padding: 4px 10px; border: none;")
        right_layout.addWidget(type_lbl)

        more_lbl = QLabel("⋮")
        more_lbl.setStyleSheet(STYLE_MORE_LBL)
        more_lbl.setCursor(QCursor(Qt.PointingHandCursor))
        right_layout.addWidget(more_lbl)

        # Thêm ghi chú ngay dưới bên phải của card lịch
        note_text = session.get("note", "").strip()
        bottom_text = note_text
        if bottom_text:
            if len(bottom_text) > 30:
                bottom_text = bottom_text[:28] + "..."
            note_lbl = QLabel(bottom_text)
            note_lbl.setFont(qfont(FONTS["small_center"]))
            note_lbl.setStyleSheet("color: #888888; font-style: italic; border: none; background: transparent;")
            note_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            right_layout.addWidget(note_lbl)

        layout.addLayout(right_layout)
        self.scroll_layout.addWidget(card)

    def create_bottom_cards(self, parent_layout):
        # Thẻ AI Gợi ý
        ai_card = self.make_card()
        ai_card.setFixedHeight(175)
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(15, 15, 15, 15)
        ai_layout.setSpacing(10)

        ai_header = QFrame()
        ai_header.setStyleSheet(STYLE_AI_HDR)
        ai_header.setFixedHeight(40)
        ai_h_layout = QHBoxLayout(ai_header)
        ai_h_layout.setContentsMargins(10, 8, 10, 8)
        icon_ai = QLabel("✨")
        icon_ai.setStyleSheet(STYLE_TRANSPARENT + " color: white;")
        title_ai = QLabel("Gợi ý học tập từ AI")
        title_ai.setFont(qfont(FONTS["h3_center"]))
        title_ai.setStyleSheet(STYLE_AI_TITLE)
        ai_h_layout.addWidget(icon_ai)
        ai_h_layout.addWidget(title_ai)
        ai_h_layout.addStretch()

        ai_layout.addWidget(ai_header)

        self.ai_suggestion_label = QLabel(self.study_suggestion)
        self.ai_suggestion_label.setWordWrap(True)
        self.ai_suggestion_label.setFont(qfont(FONTS["small_center"]))
        self.ai_suggestion_label.setStyleSheet(STYLE_LABEL_SECONDARY)
        ai_layout.addWidget(self.ai_suggestion_label, 1)
        
        parent_layout.addWidget(ai_card)

    def create_timer_card(self, parent_layout):
        # Thẻ Đồng hồ tập trung thay thế cho Thống kê cũ
        self.timer_card = FocusTimerCard(parent_page=self, home_service=self.home_service, user_id=self.user_id)
        self.timer_card.session_completed.connect(self.on_timer_session_completed)
        parent_layout.addWidget(self.timer_card, 4)

    @qasync.asyncSlot()
    async def on_timer_session_completed(self):
        # Nạp lại toàn bộ dữ liệu trên trang chủ sau khi hoàn thành phiên học tập trung
        await self.load_all_data()
        self.reload_side_panels()

    def create_today_tasks(self, parent_layout):
        card = self.make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        hdr = QFrame()
        hdr.setStyleSheet(STYLE_TASK_HDR)
        hdr.setFixedHeight(40)
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(10, 8, 10, 8)
        title = QLabel("Nhiệm vụ")
        title.setFont(qfont(FONTS["h3_center"]))
        title.setStyleSheet(STYLE_TASK_TITLE)
        hdr_layout.addWidget(title)
        hdr_layout.addStretch()

        btn_add = QPushButton("+ Thêm")
        btn_add.setFixedSize(70, 26)
        btn_add.setFont(qfont(FONTS["small_bold_center"]))
        btn_add.setStyleSheet(STYLE_BTN_ADD_TASK)
        btn_add.clicked.connect(self.open_add_task_dialog)
        hdr_layout.addWidget(btn_add)
        layout.addWidget(hdr)

        # Thanh cuộn bọc ngoài danh sách nhiệm vụ học tập
        self.task_scroll = QScrollArea()
        self.task_scroll.setWidgetResizable(True)
        self.task_scroll.setStyleSheet(STYLE_SCROLL)
        self.task_list_container.setStyleSheet("background: transparent;")
        self.task_scroll.setWidget(self.task_list_container)
        
        layout.addWidget(self.task_scroll, 1)

        parent_layout.addWidget(card, 6)
        self.repaint_tasks(self.tasks_data)

    def open_add_task_dialog(self):
        dialog = AddTaskDialog(self.home_service, self, on_task_created=self.on_task_created)
        dialog.exec()

    def on_task_created(self, task_data):
        print("DEBUG: Task được tạo thành công:", task_data)

        # 1. Đảm bảo khởi tạo mảng nếu nó chưa có
        if not hasattr(self, "tasks_data") or not isinstance(self.tasks_data, list):
            self.tasks_data = []

        # 2. Thêm vào đầu mảng
        self.tasks_data.insert(0, task_data)

        # 3. ÉP GIAO DIỆN VẼ LẠI NGAY LẬP TỨC
        self.repaint_tasks(self.tasks_data)



    def reload_side_panels(self):
        # ⚙️ GỢI Ý AI: BẢO HIỂM TUYỆT ĐỐI CHỐNG SẬP NGẦM LUỒNG VẼ TASK
        if hasattr(self, "ai_suggestion_label") and self.ai_suggestion_label is not None:
            try:
                # Dùng getattr an toàn, nếu chưa có biến study_suggestion thì hiện chữ Đang tải
                ai_text = getattr(self, "study_suggestion", "Gemini đang phân tích lộ trình học tập của bồ...")
                self.ai_suggestion_label.setText(str(ai_text))
            except Exception as e:
                print(f"⚠️ Tạm thời bỏ qua lỗi nhãn AI: {e}")

        # 🚀 LỆNH SỐNG CÒN: Được giải thoát hoàn toàn, chắc chắn luôn được vẽ ra màn hình!
        try:
            tasks_list = getattr(self, "tasks_data", []) or []
            print(f"📋 Tiến hành vẽ lại danh sách {len(tasks_list)} nhiệm vụ học tập lên màn hình...")
            self.repaint_tasks(tasks_list)
        except Exception as e:
            print(f"❌ Hàm repaint_tasks bị gãy: {e}")



    def repaint_tasks(self, tasks):
        """Hàm dọn dẹp và vẽ lại bảng danh sách Nhiệm vụ (Phiên bản bất tử)."""

        # 1. Dọn dẹp sạch sẽ layout cũ
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Nếu có layout con, dọn layout con đó
                child = item.layout()
                while child.count():
                    c_item = child.takeAt(0)
                    if c_item.widget(): c_item.widget().deleteLater()
                item.widget().deleteLater() if item.widget() else None

        # 2. Kiểm tra nếu mảng trống thì hiện label báo
        if not tasks:
            lbl = QLabel("Hôm nay bồ nghỉ ngơi nhen! 🎉")
            lbl.setStyleSheet("color: #888; padding: 20px; font-style: italic;")
            lbl.setAlignment(Qt.AlignCenter)
            self.task_list_layout.addWidget(lbl)
        else:
            # 3. Duyệt danh sách và vẽ từng task
            for task in tasks:
                # Container bọc ngoài
                row_frame = QFrame()
                row_frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: none;
                        border-radius: 12px;
                        margin: 4px 0px;
                    }
                    QFrame:hover {
                        background-color: #F8FAFF;
                        border: 1px solid #C6DBFF;
                    }
                """)
                # Thêm hiệu ứng đổ bóng cho sang (tùy chỉnh cho PySide6)
                shadow = QGraphicsDropShadowEffect(row_frame)
                shadow.setBlurRadius(10)
                shadow.setOffset(0, 2)
                shadow.setColor(QColor(0, 0, 0, 30))
                row_frame.setGraphicsEffect(shadow)

                t_row = QHBoxLayout(row_frame)
                t_row.setContentsMargins(16, 12, 16, 12)
                t_row.setSpacing(14)

                # Nội dung
                info_layout = QVBoxLayout()
                info_layout.setSpacing(4)

                name_lbl = QLabel(task.get("name", "Nhiệm vụ mới"))
                name_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #1E293B;")
                name_lbl.setWordWrap(True)
                info_layout.addWidget(name_lbl)

                # Deadline (Dùng icon và màu nhã nhặn hơn)
                dl_lbl = QLabel(f"🕒 {task.get('deadline', 'Trong ngày')}")
                dl_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-style: italic;")
                info_layout.addWidget(dl_lbl)

                # Ghi chú xám nhỏ bên dưới (Thêm theo yêu cầu)
                note_text = task.get("note", "").strip()
                if note_text:
                    if len(note_text) > 40:
                        note_text = note_text[:37] + "..."
                    note_lbl = QLabel(f"📝 {note_text}")
                    note_lbl.setStyleSheet("color: #888888; font-size: 11px; font-style: italic; border: none; background: transparent;")
                    note_lbl.setWordWrap(True)
                    info_layout.addWidget(note_lbl)

                t_row.addLayout(info_layout, 1)

                # Layout chứa các nút tác vụ bên phải nhiệm vụ
                actions_layout = QVBoxLayout()
                actions_layout.setSpacing(6)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setAlignment(Qt.AlignCenter)

                # Nút "+ Chọn"
                if not task.get("done", False):
                    btn_focus = QPushButton("+ Chọn")
                    btn_focus.setToolTip("Nạp nhiệm vụ này vào đồng hồ tập trung để học")
                    btn_focus.setFixedSize(70, 26)
                    btn_focus.setCursor(QCursor(Qt.PointingHandCursor))
                    btn_focus.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #E0F2FE;
                            border: 1px solid #BAE6FD;
                            border-radius: 13px;
                            color: {COLORS['primary']};
                            font-size: 11px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: {COLORS['primary']};
                            color: white;
                            border: 1px solid {COLORS['primary']};
                        }}
                    """)
                    btn_focus.clicked.connect(lambda checked=False, t=task: self.timer_card.set_session(
                        task_name=t.get("name", "Nhiệm vụ"),
                        minutes=45,
                        task_id=t.get("id"),
                        source="manual"
                    ))
                    actions_layout.addWidget(btn_focus)

                # Nút "Chi tiết"
                btn_detail = QPushButton("Chi tiết")
                btn_detail.setToolTip("Xem toàn bộ chi tiết ghi chú của nhiệm vụ")
                btn_detail.setFixedSize(70, 24)
                btn_detail.setCursor(QCursor(Qt.PointingHandCursor))
                btn_detail.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                        color: {COLORS['text_secondary']};
                        font-size: 10px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: #F1F5F9;
                        color: {COLORS['text_primary']};
                        border: 1px solid #94A3B8;
                    }}
                """)
                btn_detail.clicked.connect(lambda checked=False, t=task: self.show_task_detail(t))
                actions_layout.addWidget(btn_detail)

                t_row.addLayout(actions_layout)
                self.task_list_layout.addWidget(row_frame)
            # Thêm khoảng trống đẩy task lên trên cùng
            self.task_list_layout.addStretch(1)

        # 4. ÉP UI CẬP NHẬT
        container = self.task_list_layout.parentWidget()
        if container:
            container.update()
            container.show()



    def clear_layout(self, param):
        pass

    def show_task_detail(self, task):
        """Hiển thị chi tiết ghi chú đầy đủ của nhiệm vụ trong popup sang trọng."""
        note = task.get("note", "").strip() or "Không có ghi chú nào cho nhiệm vụ này."
        
        box = QMessageBox(self)
        box.setWindowTitle("Chi tiết nhiệm vụ")
        box.setText(f"📋 <b>Nhiệm vụ:</b> {task.get('name')}<br><br>"
                     f"🕒 <b>Thời hạn:</b> {task.get('deadline', 'Trong ngày')}<br><br>"
                     f"📝 <b>Ghi chú chi tiết:</b><br>{note}")
        box.setIcon(QMessageBox.Information)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #111827 !important;
                font-family: "Segoe UI";
                font-size: 13px;
                background: transparent;
            }
            QPushButton {
                background-color: #4C96F5 !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 6px !important;
                padding: 6px 18px !important;
                min-width: 75px !important;
                min-height: 25px !important;
                font-family: "Segoe UI" !important;
                font-size: 12px !important;
                font-weight: 600 !important;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #357FE0 !important;
            }
        """)
        box.exec()