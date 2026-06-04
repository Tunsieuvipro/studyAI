import os
import asyncio
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCursor, QFont

from app.FE.config import COLORS, FONTS

# Hàm chuyển đổi font từ tuple cấu hình sang QFont
def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class FocusTimerCard(QFrame):
    """
    Thẻ đồng hồ đếm ngược tập trung (Pomodoro / Focus Timer) thông minh.
    - Cho phép nạp mục tiêu học tập tự động từ gợi ý AI hoặc danh sách Task.
    - Đếm ngược thời gian thực và cho phép Tạm dừng / Bỏ cuộc.
    - Tự động lưu dữ liệu học tập vào DB khi hoàn thành để phục vụ thống kê.
    - Tự động cập nhật trạng thái nhiệm vụ liên kết thành Hoàn thành.
    """
    
    # Định nghĩa các tín hiệu Signal để báo cho HomePage reload dữ liệu khi hoàn thành phiên
    session_completed = Signal()

    def __init__(self, parent_page, home_service, user_id: int = 1, parent=None):
        super().__init__(parent)
        self.parent_page = parent_page
        self.home_service = home_service
        self.user_id = user_id
        
        # Biến quản lý trạng thái đồng hồ
        self.total_seconds = 45 * 60       # Thời gian mặc định là 45 phút
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.is_paused = False
        self.current_task_name = ""        # Tên nhiệm vụ đang liên kết học
        self.current_task_id = None        # ID nhiệm vụ liên kết trong DB (nếu có)
        self.generated_by = "manual"       # Nguồn gợi ý: 'ai' hoặc 'manual'
        
        # ⏱️ Bộ đếm thời gian thực QTimer của PySide6
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        
        # Cấu hình UI cho Card Frame
        self.setObjectName("card_frame")
        self.setStyleSheet(f"""
            #card_frame {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Khởi tạo toàn bộ giao diện
        self._init_ui()
        
    def _init_ui(self):
        """Khởi tạo cấu trúc layout và các Widget của Đồng hồ"""
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(12)
        
        # ──────────────────────────────────────────────────────────
        # 1. HEADER màu xanh đồng bộ với các thẻ khác trên HomePage
        # ──────────────────────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;")
        header_frame.setFixedHeight(40)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)
        
        header_title = QLabel("Phiên tập trung")
        header_title.setFont(qfont(FONTS["h3_center"]))
        header_title.setStyleSheet("color: white; border: none; background: transparent;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        card_layout.addWidget(header_frame)
        
        # ──────────────────────────────────────────────────────────
        # 2. KHU VỰC HIỂN THỊ TIÊU ĐỀ HOẠT ĐỘNG ĐANG CHỌN
        # ──────────────────────────────────────────────────────────
        self.lbl_activity = QLabel("Hãy chọn một nhiệm vụ để bắt đầu học nhé 🚀")
        self.lbl_activity.setFont(qfont(FONTS["small_center"]))
        self.lbl_activity.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        self.lbl_activity.setWordWrap(True)
        self.lbl_activity.setAlignment(Qt.AlignCenter)
        self.lbl_activity.setMinimumHeight(40)
        card_layout.addWidget(self.lbl_activity)
        
        # ──────────────────────────────────────────────────────────
        # 3. MÀN HÌNH ĐỒNG HỒ SỐ LỚN SIÊU ĐẸP
        # ──────────────────────────────────────────────────────────
        self.lbl_time = QLabel("45:00")
        self.lbl_time.setFont(QFont("Segoe UI", 42, QFont.Bold))
        self.lbl_time.setStyleSheet(f"color: {COLORS['primary']}; border: none; background: transparent; font-weight: bold;")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_time)
        
        # ──────────────────────────────────────────────────────────
        # 4. THANH ĐIỀU KHIỂN NÚT BẤM (START, PAUSE, CANCEL)
        # ──────────────────────────────────────────────────────────
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setAlignment(Qt.AlignCenter)
        
        # Nút Bắt đầu (Start)
        self.btn_start = QPushButton("Bắt đầu học")
        self.btn_start.setFixedSize(140, 34)
        self.btn_start.setFont(qfont(FONTS["body_bold_center"]))
        self.btn_start.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_start.setEnabled(False) # Ban đầu chưa chọn Task sẽ bị mờ
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #357FE0;
            }}
            QPushButton:disabled {{
                background-color: #CBD5E1;
                color: #94A3B8;
            }}
        """)
        self.btn_start.clicked.connect(self.start_session)
        controls_layout.addWidget(self.btn_start)
        
        # Nút Tạm dừng (Pause) / Tiếp tục (Resume)
        self.btn_pause = QPushButton("Tạm dừng")
        self.btn_pause.setFixedSize(100, 34)
        self.btn_pause.setFont(qfont(FONTS["body_bold_center"]))
        self.btn_pause.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['primary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        self.btn_pause.clicked.connect(self.pause_session)
        self.btn_pause.hide() # Ban đầu ẩn đi
        controls_layout.addWidget(self.btn_pause)
        
        # Nút Bỏ cuộc (Give Up)
        self.btn_cancel = QPushButton("Bỏ cuộc")
        self.btn_cancel.setFixedSize(100, 34)
        self.btn_cancel.setFont(qfont(FONTS["body_bold_center"]))
        self.btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                color: #EF4444;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FCA5A5;
            }
        """)
        self.btn_cancel.clicked.connect(self.cancel_session)
        self.btn_cancel.hide() # Ban đầu ẩn đi
        controls_layout.addWidget(self.btn_cancel)
        
        card_layout.addLayout(controls_layout)
        
    def set_session(self, task_name: str, minutes: int = 45, task_id: int = None, source: str = "manual"):
        """
        Nạp dữ liệu phiên học tập từ gợi ý AI hoặc từ danh sách nhiệm vụ hôm nay.
        """
        if self.is_running:
            # Nếu đang có phiên học chạy, chặn không cho chuyển mục tiêu đột ngột
            self._show_message("Thông báo", "Bạn đang trong phiên học tập trung. Vui lòng hoàn thành hoặc bấm Bỏ cuộc trước khi chọn hoạt động mới!", QMessageBox.Warning)
            return
            
        self.current_task_name = task_name
        self.current_task_id = task_id
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.generated_by = source
        
        # Cập nhật hiển thị lên UI
        self.lbl_activity.setText(f"🎯 Mục tiêu: {task_name}")
        self.lbl_activity.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold; background: transparent;")
        self._update_time_display()
        
        # Kích hoạt nút Bắt đầu
        self.btn_start.setEnabled(True)
        self.btn_start.setText("Bắt đầu học")
        
    def start_session(self):
        """Bắt đầu chạy đồng hồ tập trung"""
        if not self.current_task_name:
            return
            
        self.is_running = True
        self.is_paused = False
        self.timer.start(1000) # Cứ 1 giây (1000ms) tick 1 lần
        
        # Chuyển đổi trạng thái hiển thị các nút điều khiển
        self.btn_start.hide()
        self.btn_pause.setText("Tạm dừng")
        self.btn_pause.show()
        self.btn_cancel.show()
        
        # Đổi màu hiển thị thời gian sang trạng thái tập trung cao độ
        self.lbl_time.setStyleSheet(f"color: {COLORS['primary']}; border: none; background: transparent; font-weight: bold;")
        
    def pause_session(self):
        """Tạm dừng hoặc tiếp tục chạy đồng hồ"""
        if not self.is_running:
            return
            
        if not self.is_paused:
            # Thực hiện Tạm dừng
            self.is_paused = True
            self.timer.stop()
            self.btn_pause.setText("Tiếp tục")
            self.lbl_time.setStyleSheet("color: #94A3B8; border: none; background: transparent; font-weight: bold;") # Làm mờ chữ số đếm
        else:
            # Tiếp tục học
            self.is_paused = False
            self.timer.start(1000)
            self.btn_pause.setText("Tạm dừng")
            self.lbl_time.setStyleSheet(f"color: {COLORS['primary']}; border: none; background: transparent; font-weight: bold;")
            
    def cancel_session(self):
        """Hủy bỏ phiên học hiện tại"""
        reply = self._show_message(
            "Xác nhận bỏ cuộc", 
            "Bạn có chắc chắn muốn BỎ CUỘC phiên học tập trung này không?\n(Dữ liệu sẽ không được lưu vào hệ thống)",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._reset_timer()
            
    def _reset_timer(self):
        """Đưa đồng hồ đếm ngược về trạng thái sẵn sàng ban đầu"""
        self.timer.stop()
        self.is_running = False
        self.is_paused = False
        self.remaining_seconds = self.total_seconds
        self._update_time_display()
        
        # Reset nút điều khiển
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_cancel.hide()
        
        self.lbl_time.setStyleSheet(f"color: {COLORS['primary']}; border: none; background: transparent; font-weight: bold;")
        
    def _update_time_display(self):
        """Tính toán phút:giây và gán định dạng lên nhãn hiển thị"""
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        self.lbl_time.setText(f"{mins:02d}:{secs:02d}")
        
    def _on_timer_tick(self):
        """Hành động diễn ra sau mỗi 1 giây trôi qua"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_time_display()
        else:
            # Hết giờ! Hoàn thành phiên học tập trung xuất sắc!
            self.timer.stop()
            self._on_session_completed()
            
    def _on_session_completed(self):
        """Xử lý nghiệp vụ khi phiên đếm ngược hoàn thành"""
        self.is_running = False
        
        # Reset hiển thị các nút điều khiển về ban đầu
        self.btn_start.show()
        self.btn_start.setEnabled(False) # Cần nạp Task mới để học tiếp
        self.btn_pause.hide()
        self.btn_cancel.hide()
        
        self.lbl_activity.setText("Chúc mừng bạn đã hoàn thành phiên học! 🎉")
        self.lbl_activity.setStyleSheet(f"color: {COLORS['success']}; border: none; font-weight: bold; background: transparent;")
        
        # 🎙️ Hiển thị hộp thoại chúc mừng cao cấp
        self._show_message(
            "Tuyệt vời!", 
            f"🎉 Chúc mừng bạn đã hoàn thành xuất sắc phiên học tập trung kéo dài {self.total_seconds // 60} phút cho mục tiêu:\n\"{self.current_task_name}\"\n\nHệ thống đã lưu lại kết quả tự học này vào bảng Thống kê của bạn!",
            QMessageBox.Information
        )
        
        # Chạy tác vụ ngầm ghi nhận dữ liệu vào DB (bất đồng bộ)
        asyncio.create_task(self._save_session_to_database())

    async def _save_session_to_database(self):
        """Tác vụ ngầm ghi dữ liệu tự học vào DB MySQL và tích hoàn thành Task"""
        try:
            # 1. Tính toán thời gian thực tế đã học
            duration_min = self.total_seconds // 60
            
            # Ghi nhận vào bảng study_sessions của DB thật
            from app.BE.database.repositories.session_repo import SessionRepository
            from datetime import datetime
            
            now = datetime.now()
            today_date = now.date()
            start_time = (now - asyncio.subprocess.sys.modules['datetime'].timedelta(minutes=duration_min)).time()
            end_time = now.time()
            
            # Đưa bản ghi vào DB bằng bulk_insert của SessionRepository
            row_data = (
                self.user_id,
                None,             # subject_id = None (hoặc map theo môn học nếu muốn)
                today_date,
                start_time,
                end_time,
                duration_min,
                "done",           # status = 'done'
                self.generated_by # Nguồn tạo: 'ai' hoặc 'manual'
            )
            await SessionRepository.bulk_insert([row_data])
            print("🚀 Đã ghi nhận số phút tự học thực tế vào Database study_sessions thành công!")
            
            # 2. Nếu phiên đếm ngược này liên kết với một Task cụ thể, tự động tích hoàn thành Task đó
            if self.current_task_id:
                from app.BE.database.repositories.task_repo import TaskRepository
                await TaskRepository.set_status(self.current_task_id, self.user_id, "done")
                print(f"🚀 Tự động tích xanh hoàn thành Task ID {self.current_task_id} thành công!")
            
            # 3. Kích hoạt phát tín hiệu để HomePage reload lại danh sách Task và biểu đồ thống kê
            self.session_completed.emit()
            
        except Exception as e:
            print(f"⚠️ Lỗi lưu dữ liệu tự học đếm ngược vào Database: {e}")

    def _show_message(self, title: str, text: str, icon=QMessageBox.Information, buttons=QMessageBox.Ok, default_button=QMessageBox.Ok):
        """Hiển thị QMessageBox được tùy biến CSS cao cấp để tránh lỗi kế thừa màu chữ trắng từ HomePage."""
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(icon)
        box.setStandardButtons(buttons)
        box.setDefaultButton(default_button)
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
            }
            QPushButton:hover {
                background-color: #357FE0 !important;
            }
        """)
        return box.exec()
