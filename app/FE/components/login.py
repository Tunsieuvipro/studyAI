import os
import asyncio
import qasync
from pathlib import Path
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QCursor, QFont, QPixmap, QPalette, QBrush, QPainter, QPen, QColor, QIcon
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QMessageBox, QFrame, QComboBox, QDialog
)

# Import schemas và auth service của Backend
from app.BE.models.schemas import LoginIn, RegisterIn
from app.BE.services.auth_service import login, register, reset_password_via_security_question
from app.FE.config import FONTS

# Khởi tạo đường dẫn đến file ảnh nền background.png lưu trong assets
CURRENT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = CURRENT_DIR.parent / "assets"
BG_PATH = ASSETS_DIR / "background.png"

def create_eye_icon(open_eye=True):
    """Tạo QIcon con mắt động cực đẹp bằng QPainter"""
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    pen = QPen(QColor("#718096"), 1.8)
    painter.setPen(pen)
    
    # Cung mắt trên và dưới
    painter.drawArc(2, 4, 16, 12, 35 * 16, 110 * 16)
    painter.drawArc(2, 4, 16, 12, 215 * 16, 110 * 16)
    
    if open_eye:
        # Đồng tử tròn màu xanh dương
        painter.setBrush(QBrush(QColor("#3182ce")))
        painter.setPen(QPen(QColor("#3182ce"), 1))
        painter.drawEllipse(7, 7, 6, 6)
    else:
        # Đồng tử xám nhỏ + đường gạch chéo mắt đóng
        painter.setBrush(QBrush(QColor("#a0aec0")))
        painter.setPen(QPen(QColor("#a0aec0"), 1))
        painter.drawEllipse(8, 8, 4, 4)
        
        painter.setPen(QPen(QColor("#e53e3e"), 1.8))
        painter.drawLine(3, 3, 17, 17)
        
    painter.end()
    return QIcon(pixmap)

# Các bộ stylesheet thiết kế giao diện cao cấp
STYLE_CARD = """
    QFrame#card_container {
        background-color: rgba(255, 255, 255, 0.93);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
    }
    QFrame#card_container QLabel {
        color: #2d3748;
        font-size: 13px;
        background: transparent;
    }
"""

STYLE_INPUT = """
    QLineEdit {
        background-color: #ffffff;
        border: 1.5px solid #cbd5e0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #2d3748;
    }
    QLineEdit:focus {
        border: 1.5px solid #3182ce;
        background-color: #ffffff;
    }
"""

STYLE_COMBO = """
    QComboBox {
        background-color: #ffffff;
        border: 1.5px solid #cbd5e0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #2d3748;
    }
    QComboBox:focus {
        border: 1.5px solid #3182ce;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #2d3748;
        selection-background-color: #ebf8ff;
        selection-color: #2b6cb0;
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        padding: 4px;
    }
"""

STYLE_PRIMARY_BTN = """
    QPushButton {
        background-color: #3182ce;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 11px 20px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2b6cb0;
    }
    QPushButton:pressed {
        background-color: #2c5282;
    }
"""

STYLE_TEXT_BTN = """
    QPushButton {
        background-color: transparent;
        color: #3182ce;
        border: none;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        color: #2b6cb0;
        text-decoration: underline;
    }
"""

class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Khôi phục mật khẩu - StudyAI")
        self.resize(430, 540)
        self.setMinimumSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2d3748;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #2d3748;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #3182ce;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        
        title = QLabel("Khôi phục mật khẩu")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a202c;")
        layout.addWidget(title)
        
        desc = QLabel("Vui lòng điền đúng thông tin tài khoản và câu hỏi bảo mật để thiết lập mật khẩu mới.")
        desc.setStyleSheet("color: #718096; font-size: 12px; font-weight: normal; line-height: 18px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addSpacing(5)
        
        # Form inputs
        layout.addWidget(QLabel("Email cá nhân"))
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("name@example.com")
        layout.addWidget(self.input_email)
        
        layout.addWidget(QLabel("Mã sinh viên"))
        self.input_sid = QLineEdit()
        self.input_sid.setPlaceholderText("Ví dụ: 25IT001")
        layout.addWidget(self.input_sid)
        
        layout.addWidget(QLabel("Câu hỏi bảo mật đã đăng ký"))
        self.input_question = QComboBox()
        self.input_question.addItems([
            "Tên trường tiểu học đầu tiên của bạn?",
            "Tên thú cưng đầu tiên của bạn?",
            "Thành phố nơi bạn được sinh ra?",
            "Món ăn yêu thích nhất của bạn?",
            "Tên người bạn thân nhất của bạn?"
        ])
        self.input_question.setStyleSheet(STYLE_COMBO)
        layout.addWidget(self.input_question)
        
        layout.addWidget(QLabel("Câu trả lời bảo mật"))
        self.input_answer = QLineEdit()
        self.input_answer.setPlaceholderText("Nhập câu trả lời của bạn")
        layout.addWidget(self.input_answer)
        
        layout.addWidget(QLabel("Mật khẩu mới"))
        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("Tối thiểu 6 ký tự")
        self.input_pw.setEchoMode(QLineEdit.Password)
        self.input_pw.setStyleSheet(STYLE_INPUT)
        
        # Action for eye
        self.eye_open_icon = create_eye_icon(True)
        self.eye_close_icon = create_eye_icon(False)
        self.action_pw = self.input_pw.addAction(self.eye_close_icon, QLineEdit.TrailingPosition)
        self.action_pw.triggered.connect(self._toggle_pw)
        layout.addWidget(self.input_pw)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_box = QHBoxLayout()
        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #edf2f7;
                color: #4a5568;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_submit = QPushButton("Đổi mật khẩu")
        self.btn_submit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_submit.setStyleSheet(STYLE_PRIMARY_BTN)
        self.btn_submit.clicked.connect(self.on_submit_clicked)
        
        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_submit)
        layout.addLayout(btn_box)
        
    def _toggle_pw(self):
        if self.input_pw.echoMode() == QLineEdit.Password:
            self.input_pw.setEchoMode(QLineEdit.Normal)
            self.action_pw.setIcon(self.eye_open_icon)
        else:
            self.input_pw.setEchoMode(QLineEdit.Password)
            self.action_pw.setIcon(self.eye_close_icon)
            
    def on_submit_clicked(self):
        # Validate input values are not empty
        if not self.input_email.text().strip() or not self.input_sid.text().strip() or not self.input_answer.text().strip() or not self.input_pw.text().strip():
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ tất cả các trường!")
            return
        if len(self.input_pw.text()) < 6:
            QMessageBox.warning(self, "Thông báo", "Mật khẩu mới phải từ 6 ký tự trở lên!")
            return
        self.accept()

    def get_data(self):
        return {
            "email": self.input_email.text().strip(),
            "student_id": self.input_sid.text().strip(),
            "question": self.input_question.currentText().strip(),
            "answer": self.input_answer.text().strip(),
            "new_password": self.input_pw.text()
        }

class LoginWindow(QMainWindow):
    def __init__(self, home_service, exam_service, ai_service):
        super().__init__()
        self.home_service = home_service
        self.exam_service = exam_service
        self.ai_service = ai_service
        
        # Khởi tạo các icon mắt động cho ô mật khẩu
        self.eye_open_icon = create_eye_icon(True)
        self.eye_close_icon = create_eye_icon(False)
        
        self.setWindowTitle("Đăng nhập - StudyAI")
        self.resize(1100, 750)
        self.setMinimumSize(950, 710)
        
        # 1. Vẽ hình nền bao phủ toàn bộ màn hình
        self.bg_label = QLabel(self)
        if BG_PATH.exists():
            self.bg_label.setPixmap(QPixmap(str(BG_PATH)))
        else:
            self.bg_label.setStyleSheet("background-color: #1a202c;")
        self.bg_label.setScaledContents(True)
        
        # 2. Container trung tâm chứa giao diện chính
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(60, 25, 60, 25)
        main_layout.setSpacing(40)
        
        # 3. Phía trái: Đoạn giới thiệu text ấn tượng
        self.left_pane = QWidget()
        self.left_pane.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(self.left_pane)
        left_layout.setContentsMargins(45, 15, 45, 0)
        left_layout.setSpacing(15)
        
        logo_lbl = QLabel("StudyAI")
        logo_lbl.setStyleSheet("color: #1a202c; font-size: 42px; font-weight: 800; letter-spacing: 1px;")
        logo_lbl.setAlignment(Qt.AlignLeft)
        
        slogan_lbl = QLabel("Học thông minh hơn cùng trợ lý AI")
        slogan_lbl.setStyleSheet("color: #2d3748; font-size: 24px; font-weight: 600;")
        slogan_lbl.setWordWrap(True)
        slogan_lbl.setAlignment(Qt.AlignLeft)
        
        desc_lbl = QLabel("Hệ thống hỗ trợ học tập thông minh tích hợp trí tuệ nhân tạo.           Quản lý tài liệu, lập lịch học tự động, tóm tắt bài giảng & giải bài tập nhanh chóng cùng trợ lý thông minh AI.")
        desc_lbl.setStyleSheet("color: #4a5568; font-size: 14px; line-height: 22px;")
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignLeft)
        
        left_layout.addWidget(logo_lbl)
        left_layout.addWidget(slogan_lbl)
        left_layout.addWidget(desc_lbl)
        
        # Đẩy toàn bộ khối chữ lên phía trên cao (vùng trời xanh trống) bằng Stretch ở dưới cùng
        left_layout.addStretch()
        
        # 4. Phía phải: Form Đăng nhập / Đăng ký Glassmorphism
        self.card_frame = QFrame()
        self.card_frame.setObjectName("card_container")
        self.card_frame.setStyleSheet(STYLE_CARD)
        self.card_frame.setFixedWidth(400)
        
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(30, 20, 30, 20)
        card_layout.setSpacing(10)
        
        self.stack = QStackedWidget()
        card_layout.addWidget(self.stack)
        
        # Tạo hai trang form
        self.init_login_page()
        self.init_register_page()
        
        main_layout.addWidget(self.card_frame, 0)
        main_layout.addWidget(self.left_pane, 1)

    def resizeEvent(self, event):
        # Đảm bảo hình nền luôn kéo dãn vừa khít cửa sổ khi thu phóng kích thước
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_centered"):
            self._centered = True
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._center_on_screen)

    def _center_on_screen(self):
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.left() + (screen.width()  - self.frameGeometry().width())  // 2
        y = screen.top()  + (screen.height() - self.frameGeometry().height()) // 2
        self.move(x, y)

    def init_login_page(self):
        """Khởi tạo giao diện Form Đăng Nhập"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignVCenter)
        
        title = QLabel("Chào mừng trở lại!")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a202c;")
        
        sub = QLabel("Đăng nhập để tiếp tục học tập cùng AI")
        sub.setStyleSheet("font-size: 13px; color: #718096;")
        
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(10)
        
        # Email Input
        layout.addWidget(QLabel("Email cá nhân"))
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("name@example.com")
        self.login_email.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.login_email)
        
        # Password Input Header Row
        pw_header = QWidget()
        pw_header.setStyleSheet("background: transparent;")
        pw_header_layout = QHBoxLayout(pw_header)
        pw_header_layout.setContentsMargins(0, 0, 0, 0)
        
        pw_lbl = QLabel("Mật khẩu")
        pw_header_layout.addWidget(pw_lbl)
        
        pw_header_layout.addStretch()
        
        btn_forgot = QPushButton("Quên mật khẩu?")
        btn_forgot.setStyleSheet(STYLE_TEXT_BTN)
        btn_forgot.setCursor(QCursor(Qt.PointingHandCursor))
        btn_forgot.clicked.connect(self._on_forgot_password_clicked)
        pw_header_layout.addWidget(btn_forgot)
        
        layout.addWidget(pw_header)

        self.login_pw = QLineEdit()
        self.login_pw.setPlaceholderText("••••••••")
        self.login_pw.setEchoMode(QLineEdit.Password)
        self.login_pw.setStyleSheet(STYLE_INPUT)
        
        # Thêm Action mắt xem mật khẩu
        self.toggle_login_pw_action = self.login_pw.addAction(
            self.eye_close_icon, QLineEdit.TrailingPosition
        )
        self.toggle_login_pw_action.triggered.connect(self._toggle_login_pw_visibility)
        
        layout.addWidget(self.login_pw)
        
        layout.addSpacing(10)
        
        # Nút Đăng nhập
        btn_login = QPushButton("Đăng nhập")
        btn_login.setStyleSheet(STYLE_PRIMARY_BTN)
        btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        btn_login.clicked.connect(self._on_login_clicked)
        layout.addWidget(btn_login)

        # Nhấn Enter ở ô email → nhảy sang ô mật khẩu
        self.login_email.returnPressed.connect(self.login_pw.setFocus)
        # Nhấn Enter ở ô mật khẩu → tự động đăng nhập luôn
        self.login_pw.returnPressed.connect(btn_login.click)
        
        # Nút chuyển sang Đăng ký
        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignCenter)
        
        lbl_switch = QLabel("Chưa có tài khoản?")
        lbl_switch.setStyleSheet("color: #2d3748; font-size: 13px; background: transparent;")
        
        btn_switch = QPushButton("Đăng ký ngay")
        btn_switch.setStyleSheet(STYLE_TEXT_BTN)
        btn_switch.setCursor(QCursor(Qt.PointingHandCursor))
        btn_switch.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        switch_layout.addWidget(lbl_switch)
        switch_layout.addWidget(btn_switch)
        
        layout.addLayout(switch_layout)
        self.stack.addWidget(page)

    def init_register_page(self):
        """Khởi tạo giao diện Form Đăng Ký"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignVCenter)
        
        title = QLabel("Tạo tài khoản mới")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a202c;")
        
        layout.addWidget(title)
        layout.addSpacing(3)
        
        # Mã sinh viên Input
        layout.addWidget(QLabel("Mã sinh viên"))
        self.reg_sid = QLineEdit()
        self.reg_sid.setPlaceholderText("Ví dụ: 25IT001")
        self.reg_sid.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.reg_sid)
        
        # Họ và tên Input
        layout.addWidget(QLabel("Họ và tên"))
        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Ví dụ: Nguyen Van A")
        self.reg_name.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.reg_name)
        
        # Giới tính ComboBox
        layout.addWidget(QLabel("Giới tính"))
        self.reg_gender = QComboBox()
        self.reg_gender.addItem("Nam", "male")
        self.reg_gender.addItem("Nữ", "female")
        self.reg_gender.addItem("Khác", "other")
        self.reg_gender.setStyleSheet(STYLE_COMBO)
        layout.addWidget(self.reg_gender)
        
        # Email Input
        layout.addWidget(QLabel("Email đăng ký"))
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("name@example.com")
        self.reg_email.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.reg_email)
        
        # Mật khẩu Input
        layout.addWidget(QLabel("Mật khẩu"))
        self.reg_pw = QLineEdit()
        self.reg_pw.setPlaceholderText("•••••••• (Tối thiểu 6 ký tự)")
        self.reg_pw.setEchoMode(QLineEdit.Password)
        self.reg_pw.setStyleSheet(STYLE_INPUT)
        
        # Thêm Action mắt xem mật khẩu
        self.toggle_reg_pw_action = self.reg_pw.addAction(
            self.eye_close_icon, QLineEdit.TrailingPosition
        )
        self.toggle_reg_pw_action.triggered.connect(self._toggle_reg_pw_visibility)
        
        layout.addWidget(self.reg_pw)

        # Câu hỏi bảo mật ComboBox
        layout.addWidget(QLabel("Câu hỏi bảo mật"))
        self.reg_question = QComboBox()
        self.reg_question.addItems([
            "Tên trường tiểu học đầu tiên của bạn?",
            "Tên thú cưng đầu tiên của bạn?",
            "Thành phố nơi bạn được sinh ra?",
            "Món ăn yêu thích nhất của bạn?",
            "Tên người bạn thân nhất của bạn?"
        ])
        self.reg_question.setStyleSheet(STYLE_COMBO)
        layout.addWidget(self.reg_question)
        
        # Câu trả lời bảo mật Input
        layout.addWidget(QLabel("Câu trả lời bảo mật"))
        self.reg_answer = QLineEdit()
        self.reg_answer.setPlaceholderText("Nhập câu trả lời của bạn")
        self.reg_answer.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.reg_answer)
        
        layout.addSpacing(3)
        
        # Nút Đăng ký
        btn_reg = QPushButton("Đăng ký tài khoản")
        btn_reg.setStyleSheet(STYLE_PRIMARY_BTN)
        btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        btn_reg.clicked.connect(self._on_register_clicked)
        layout.addWidget(btn_reg)
        
        # Nút chuyển sang Đăng nhập
        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignCenter)
        
        lbl_switch = QLabel("Đã có tài khoản?")
        lbl_switch.setStyleSheet("color: #2d3748; font-size: 13px; background: transparent;")
        
        btn_switch = QPushButton("Đăng nhập")
        btn_switch.setStyleSheet(STYLE_TEXT_BTN)
        btn_switch.setCursor(QCursor(Qt.PointingHandCursor))
        btn_switch.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        switch_layout.addWidget(lbl_switch)
        switch_layout.addWidget(btn_switch)
        
        layout.addLayout(switch_layout)
        self.stack.addWidget(page)

    @qasync.asyncSlot()
    async def _on_login_clicked(self):
        """Xử lý sự kiện đăng nhập khi bấm nút"""
        email = self.login_email.text().strip()
        password = self.login_pw.text()
        
        if not email or not password:
            self.show_message("Thông báo", "Vui lòng điền đầy đủ Email và Mật khẩu!", QMessageBox.Warning)
            return
            
        self.setCursor(Qt.WaitCursor)
        try:
            # Khởi tạo Pydantic Schema của Backend
            payload = LoginIn(email=email, password=password)
            
            # Gọi trực tiếp hàm login bất đồng bộ từ BE auth_service
            tokens = await login(payload)
            self.unsetCursor()
            
            # Giải mã access token để lấy sub (user_id)
            from app.BE.core.security import decode_token
            payload_data = decode_token(tokens.access_token)
            user_id = int(payload_data["sub"]) if payload_data else 0
            
            # Đăng nhập thành công -> Thông báo và khởi chạy MainWindow chính
            self.show_message("Thành công", "🎉 Đăng nhập thành công!", QMessageBox.Information)
            self.accept_login(user_id)
        except Exception as e:
            self.unsetCursor()
            # Bắt lỗi chuẩn xác từ FastAPI/MySQL (ví dụ: mật khẩu sai hoặc tài khoản không tồn tại)
            err_msg = str(e)
            if hasattr(e, "detail"):
                err_msg = e.detail
            self.show_message("Đăng nhập thất bại", f"❌ {err_msg}", QMessageBox.Critical)

    @qasync.asyncSlot()
    async def _on_register_clicked(self):
        """Xử lý sự kiện đăng ký tài khoản mới khi bấm nút"""
        sid = self.reg_sid.text().strip()
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        pw = self.reg_pw.text()
        question = self.reg_question.currentText().strip()
        answer = self.reg_answer.text().strip()
        
        if not sid or not name or not email or not pw or not answer:
            self.show_message("Thông báo", "Vui lòng điền đầy đủ tất cả thông tin bao gồm câu trả lời bảo mật!", QMessageBox.Warning)
            return
            
        if len(pw) < 6:
            self.show_message("Thông báo", "Mật khẩu phải chứa tối thiểu 6 ký tự!", QMessageBox.Warning)
            return
            
        self.setCursor(Qt.WaitCursor)
        try:
            gender = self.reg_gender.currentData()
            
            # Khởi tạo Pydantic Schema của Backend
            payload = RegisterIn(
                student_id=sid,
                full_name=name,
                email=email,
                password=pw,
                gender=gender,
                security_question=question,
                security_answer=answer
            )
            
            # Gọi trực tiếp hàm register bất đồng bộ từ BE auth_service
            result = await register(payload)
            self.unsetCursor()
            
            self.show_message("Đăng ký thành công", "🎉 Tạo tài khoản thành công! Bây giờ bạn có thể đăng nhập.", QMessageBox.Information)
            
            # Đăng ký thành công tự động chuyển về form Đăng nhập
            self.login_email.setText(email)
            self.login_pw.setText(pw)
            self.stack.setCurrentIndex(0)
            
        except Exception as e:
            self.unsetCursor()
            err_msg = str(e)
            if hasattr(e, "detail"):
                err_msg = e.detail
            self.show_message("Đăng ký thất bại", f"❌ {err_msg}", QMessageBox.Critical)

    def accept_login(self, user_id: int):
        """Chuyển tiếp sang màn hình chính của ứng dụng"""
        self.close()
        
        # Import MainWindow tại đây để tránh import vòng lặp (circular import)
        from app.main import MainWindow
        self.main_window = MainWindow(self.home_service, self.exam_service, self.ai_service, user_id)
        self.main_window.showMaximized()

    def show_message(self, title, text, icon_type):
        """Hộp thoại thông báo thiết kế chữ đen cao cấp, căn lề trái cực đẹp"""
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(icon_type)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                min-width: 400px;
            }
            QLabel {
                color: #2d3748;
                font-size: 13px;
            }
            QPushButton {
                color: #2d3748;
                font-weight: bold;
                background-color: #edf2f7;
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 5px 15px;
            }
        """)
        box.exec()

    def _toggle_login_pw_visibility(self):
        """Bật tắt ẩn hiện mật khẩu đăng nhập"""
        if self.login_pw.echoMode() == QLineEdit.Password:
            self.login_pw.setEchoMode(QLineEdit.Normal)
            self.toggle_login_pw_action.setIcon(self.eye_open_icon)
        else:
            self.login_pw.setEchoMode(QLineEdit.Password)
            self.toggle_login_pw_action.setIcon(self.eye_close_icon)

    def _toggle_reg_pw_visibility(self):
        """Bật tắt ẩn hiện mật khẩu đăng ký"""
        if self.reg_pw.echoMode() == QLineEdit.Password:
            self.reg_pw.setEchoMode(QLineEdit.Normal)
            self.toggle_reg_pw_action.setIcon(self.eye_open_icon)
        else:
            self.reg_pw.setEchoMode(QLineEdit.Password)
            self.toggle_reg_pw_action.setIcon(self.eye_close_icon)

    @qasync.asyncSlot()
    async def _on_forgot_password_clicked(self):
        """Mở hộp thoại quên mật khẩu và xử lý khôi phục mật khẩu"""
        dialog = ForgotPasswordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.setCursor(Qt.WaitCursor)
            try:
                # Gọi hàm khôi phục mật khẩu bất đồng bộ của Backend
                await reset_password_via_security_question(
                    email=data["email"],
                    student_id=data["student_id"],
                    question=data["question"],
                    answer=data["answer"],
                    new_password=data["new_password"]
                )
                self.unsetCursor()
                self.show_message(
                    "Thành công",
                    "🎉 Khôi phục và đổi mật khẩu thành công! Bây giờ bạn có thể đăng nhập bằng mật khẩu mới.",
                    QMessageBox.Information
                )
                # Tự động điền email mới vào ô đăng nhập
                self.login_email.setText(data["email"])
                self.login_pw.clear()
            except Exception as e:
                self.unsetCursor()
                err_msg = str(e)
                if hasattr(e, "detail"):
                    err_msg = e.detail
                self.show_message(
                    "Khôi phục thất bại",
                    f"❌ {err_msg}",
                    QMessageBox.Critical
                )
