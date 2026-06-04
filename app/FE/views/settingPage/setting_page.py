import os
import sys
import qasync
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QScrollArea, QFrame, QApplication, QCheckBox, QStyledItemDelegate
)
from PySide6.QtGui import QPixmap, QCursor, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QPoint

from app.FE.config import COLORS, FONTS
from app.FE.views.settingPage.qss_settingPage import *

def get_font_style(font_tuple):
    """Hàm tiện ích để tạo chuỗi style CSS cho Font dựa trên tuple cấu hình."""
    family, size, *weight = font_tuple
    w = "bold" if weight and weight[0] == "bold" else "normal"
    return f"font-family: '{family}'; font-size: {size}px; font-weight: {w};"

class ToggleSwitch(QCheckBox):
    """Nút gạt (Switch) tùy chỉnh theo phong cách iOS/Material Design."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.stateChanged.connect(self.update_state)

    def update_state(self):
        self.update()

    def hitButton(self, pos: QPoint) -> bool:
        return self.rect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Track (Nền thanh gạt)
        track_opacity = 1.0
        track_color = QColor(COLORS['primary']) if self.isChecked() else QColor(COLORS['border'])
        painter.setBrush(track_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 4, 44, 20, 10, 10)

        # Thumb (Nút tròn gạt)
        painter.setBrush(QColor("white"))
        # Vị trí nút tròn: 4 khi tắt, 24 khi bật
        x_pos = 24 if self.isChecked() else 4
        painter.drawEllipse(x_pos, 7, 14, 14)
        painter.end()

class ArrowComboBox(QComboBox):
    """QComboBox tùy chỉnh tự vẽ mũi tên xuống, không cần sử dụng file ảnh bên ngoài."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(QStyledItemDelegate())
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Sử dụng màu chữ chính để đảm bảo độ tương phản
        painter.setPen(QColor(COLORS.get('text_primary', '#111827')))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        arrow_rect = QRect(self.width() - 22, 0, 18, self.height())
        painter.drawText(arrow_rect, Qt.AlignVCenter | Qt.AlignHCenter, "▼")
        painter.end()

# ═══════════════════════════════════════════════
#  HELPER
# ═══════════════════════════════════════════════
def create_card():
    """Hàm tạo khung thẻ (Card) trắng có viền bo góc dùng cho các mục cài đặt."""
    card = QFrame()
    card.setStyleSheet(STYLE_CARD)
    return card

def create_divider():
    """Tạo đường kẻ ngang mỏng để phân tách các mục."""
    div = QFrame()
    div.setFixedHeight(1)
    div.setStyleSheet(STYLE_DIVIDER)
    return div

# ═══════════════════════════════════════════════
#  MAIN PAGE
# ═══════════════════════════════════════════════
class SettingPage(QWidget):
    """Trang cài đặt hệ thống: Thông tin tài khoản, Giao diện, Thông báo và Bảo mật."""
    def __init__(self, parent=None, user_id: int = 0):
        super().__init__(parent)
        self.user_id = user_id
        self.inputs = {}
        self.is_editing = False

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLE_PAGE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(STYLE_SCROLL_AREA)

        # Scroll Content
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(STYLE_SCROLL_CONTENT)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(14)

        # Variables
        self.selected_theme = "Sáng"
        self.gender_val = "Nam"

        # Build UI
        self.create_header()
        self.create_account_info_card()
        self.create_password_card()
        self.create_appearance_card()
        self.create_account_action_card()

        # Ban đầu khóa các trường để chỉ hiển thị
        self.set_fields_enabled(False)

        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    # ──────────────────────────────────────────
    #  1. HEADER
    # ──────────────────────────────────────────
    def create_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 18)
        layout.setSpacing(2)

        title = QLabel("Cài đặt")
        title.setStyleSheet(f"{get_font_style(FONTS['h1_set'])} color: {COLORS['text_primary']};")
        layout.addWidget(title)

        subtitle = QLabel("Tùy chỉnh tài khoản và ứng dụng của bạn")
        subtitle.setStyleSheet(f"{get_font_style(FONTS['body_set'])} color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle)

        self.scroll_layout.addWidget(header)

    # ──────────────────────────────────────────
    #  2. CARD: THÔNG TIN TÀI KHOẢN
    # ──────────────────────────────────────────
    def create_account_info_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        # Header
        hdr = QWidget()
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 14)

        title = QLabel("👤  Thông tin tài khoản")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        hdr_layout.addWidget(title)

        hdr_layout.addStretch()

        self.btn_edit = QPushButton("Chỉnh sửa")
        self.btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_edit.setFixedSize(90, 30)
        self.btn_edit.setStyleSheet(STYLE_BTN_EDIT(get_font_style(FONTS['small_bold_set'])))
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        hdr_layout.addWidget(self.btn_edit)
        layout.addWidget(hdr)

        # Body
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)

        # Avatar
        avatar_col = QWidget()
        avatar_col.setFixedWidth(120)
        avatar_layout = QVBoxLayout(avatar_col)
        avatar_layout.setContentsMargins(0, 0, 20, 0)
        avatar_layout.setAlignment(Qt.AlignTop)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        img_dir = os.path.join(base_dir, "assets")

        self.man_pixmap = QPixmap(os.path.join(img_dir, "user_man.png")).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.woman_pixmap = QPixmap(os.path.join(img_dir, "user_woman.png")).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        self.update_avatar()
        avatar_layout.addWidget(self.avatar_label)
        body_layout.addWidget(avatar_col)

        # Form
        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)

        fields = [
            ("Họ và tên",           "Nguyen Van A",              0, 0, False),
            ("Email",               "nguyenvana@student.edu.vn", 0, 1, False),
            ("Giới tính",           "Nam",                       1, 0, True),
            ("Ngày tháng năm sinh", "01/01/2000",                1, 1, False),
            ("Mã sinh viên",        "K.AI212",                   2, 0, False),
            ("Số điện thoại",       "0912345678",                2, 1, False),
            ("Trường",              "Đại học Công nghệ",         3, 0, False),
            ("Ngành học",           "Công nghệ thông tin",       3, 1, False),
        ]

        for label_text, value, row, col, is_combo in fields:
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(6)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
            cell_layout.addWidget(lbl)

            if is_combo:
                cb = ArrowComboBox()
                cb.setFixedHeight(36)
                cb.setStyleSheet(STYLE_COMBO(get_font_style(FONTS['body_set'])))
                if label_text == "Giới tính":
                    cb.addItems(["Nam", "Nữ"])
                    cb.setCurrentText(value)
                    cb.currentTextChanged.connect(self.on_gender_change)
                else:
                    cb.addItems([value, "Khác"])
                cell_layout.addWidget(cb)
                self.inputs[label_text] = cb
            elif label_text == "Ngày tháng năm sinh":
                from app.FE.components.select_date import create_date_edit
                de = create_date_edit(self)
                de.setFixedHeight(36)
                de.setStyleSheet(de.styleSheet() + "\nQDateEdit { height: 36px; font-size: 13px; }")
                cell_layout.addWidget(de)
                self.inputs[label_text] = de
            else:
                ent = QLineEdit()
                ent.setFixedHeight(36)
                ent.setText(value)
                ent.setStyleSheet(STYLE_LINE_EDIT(get_font_style(FONTS['body_set'])))
                cell_layout.addWidget(ent)
                self.inputs[label_text] = ent

            form_layout.addWidget(cell, row, col)

        body_layout.addWidget(form, 1)
        layout.addWidget(body)
        self.scroll_layout.addWidget(card)

    def update_avatar(self):
        if self.gender_val == "Nam":
            self.avatar_label.setPixmap(self.man_pixmap)
        else:
            self.avatar_label.setPixmap(self.woman_pixmap)

    def on_gender_change(self, text):
        self.gender_val = text
        self.update_avatar()

    # ──────────────────────────────────────────
    #  3. CARD: ĐỔI MẬT KHẨU
    # ──────────────────────────────────────────
    def create_eye_icon(self, open_eye=True):
        """Tạo QIcon con mắt động cực đẹp bằng QPainter (giống màn hình đăng nhập)"""
        from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QIcon, QPixmap
        from PySide6.QtCore import Qt
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

    def create_password_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        # Hàng tiêu đề có tích hợp nút xem mật khẩu ở bên phải cùng dòng
        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Đổi mật khẩu")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        title_row_layout.addWidget(title)

        title_row_layout.addStretch()

        # Nút con mắt xem chung dùng QIcon động
        self.eye_open_icon = self.create_eye_icon(True)
        self.eye_close_icon = self.create_eye_icon(False)

        self.btn_eye_all = QPushButton()
        self.btn_eye_all.setIcon(self.eye_close_icon)
        self.btn_eye_all.setFixedSize(28, 28)
        self.btn_eye_all.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_eye_all.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-radius: 6px;
            }
        """)
        self.btn_eye_all.clicked.connect(self.toggle_all_passwords)
        title_row_layout.addWidget(self.btn_eye_all)

        layout.addWidget(title_row)

        pw_form = QWidget()
        pw_layout = QHBoxLayout(pw_form)
        pw_layout.setContentsMargins(0, 12, 0, 0)
        pw_layout.setSpacing(16)

        pw_fields = [
            ("Mật khẩu hiện tại", "Nhập mật khẩu hiện tại"),
            ("Mật khẩu mới", "Nhập mật khẩu mới"),
            ("Xác nhận mật khẩu mới", "Nhập lại mật khẩu mới")
        ]

        self.pw_inputs = {}
        for label_text, placeholder in pw_fields:
            col_frame = QWidget()
            col_layout = QVBoxLayout(col_frame)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(6)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
            col_layout.addWidget(lbl)

            ent = QLineEdit()
            ent.setPlaceholderText(placeholder)
            ent.setEchoMode(QLineEdit.Password)
            ent.setFixedHeight(36)
            ent.setStyleSheet(STYLE_LINE_EDIT(get_font_style(FONTS['body_set'])))
            col_layout.addWidget(ent)
            self.pw_inputs[label_text] = ent
            pw_layout.addWidget(col_frame, 1)

        btn_update = QPushButton("Cập nhật mật khẩu")
        btn_update.setFixedHeight(36)
        btn_update.setCursor(QCursor(Qt.PointingHandCursor))
        btn_update.setStyleSheet(STYLE_BTN_UPDATE(get_font_style(FONTS['body_bold_set'])))
        btn_update.clicked.connect(self.on_change_password_clicked)

        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignBottom)
        btn_layout.addWidget(btn_update)

        pw_layout.addWidget(btn_container)
        layout.addWidget(pw_form)
        self.scroll_layout.addWidget(card)

    def toggle_all_passwords(self):
        """Đồng bộ ẩn/hiện mật khẩu cho cả 3 ô nhập cùng lúc"""
        if not self.pw_inputs:
            return
        # Lấy trạng thái của ô đầu tiên để làm mốc đổi ngược lại
        first_input = list(self.pw_inputs.values())[0]
        is_hidden = first_input.echoMode() == QLineEdit.Password

        new_mode = QLineEdit.Normal if is_hidden else QLineEdit.Password
        new_icon = self.eye_open_icon if is_hidden else self.eye_close_icon

        for ent in self.pw_inputs.values():
            ent.setEchoMode(new_mode)

        self.btn_eye_all.setIcon(new_icon)

    # ──────────────────────────────────────────
    #  4. CARD: GIAO DIỆN
    # ──────────────────────────────────────────
    def create_appearance_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        title = QLabel("🎨  Giao diện")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)

        row_frame = QWidget()
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(0, 14, 0, 0)

        desc = QWidget()
        desc_layout = QVBoxLayout(desc)
        desc_layout.setContentsMargins(0, 0, 0, 0)

        l1 = QLabel("Chế độ giao diện")
        l1.setStyleSheet(f"{get_font_style(FONTS['body_bold_set'])} color: {COLORS['text_primary']}; border: none;")
        desc_layout.addWidget(l1)

        l2 = QLabel("Chọn chế độ hiển thị phù hợp với bạn")
        l2.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
        desc_layout.addWidget(l2)

        row_layout.addWidget(desc)
        row_layout.addStretch()

        options_row = QWidget()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(10)

        themes = [("☀️", "Sáng"), ("🌙", "Tối")]
        self.theme_btns = {}

        for icon, name in themes:
            btn = QPushButton(f"{icon}  {name}")
            btn.setFixedSize(110, 38)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.theme_btns[name] = btn
            btn.clicked.connect(lambda checked=False, n=name: self.select_theme(n))
            options_layout.addWidget(btn)

        self.select_theme("Sáng")
        row_layout.addWidget(options_row)

        layout.addWidget(row_frame)
        self.scroll_layout.addWidget(card)

    def apply_theme_ui(self, name):
        """Chỉ cập nhật trạng thái hiển thị của các nút giao diện (Sáng/Tối) mà không ghi đè DB"""
        ui_name = "Sáng"
        if name in ["light", "Sáng"]:
            ui_name = "Sáng"
        elif name in ["dark", "Tối"]:
            ui_name = "Tối"

        self.selected_theme = ui_name
        for n, btn in self.theme_btns.items():
            if n == ui_name:
                btn.setStyleSheet(STYLE_THEME_BTN_ACTIVE(get_font_style(FONTS['body_bold_set'])))
            else:
                btn.setStyleSheet(STYLE_THEME_BTN_INACTIVE(get_font_style(FONTS['body_bold_set'])))

    @qasync.asyncSlot()
    async def select_theme(self, name):
        self.apply_theme_ui(name)
        db_theme = "light" if self.selected_theme == "Sáng" else "dark"

        if self.user_id:
            try:
                from app.BE.services.auth_service import update_user_settings
                notify_before = 30
                notify_enabled = True
                if hasattr(self, "user_data") and self.user_data:
                    notify_before = self.user_data.get("notify_before_min", 30) or 30
                    notify_enabled = bool(self.user_data.get("notify_enabled", True))
                await update_user_settings(self.user_id, theme=db_theme)
                if hasattr(self, "user_data") and self.user_data:
                    self.user_data["theme"] = db_theme
            except Exception as e:
                print(f"Lỗi lưu theme vào database: {e}")



    # ──────────────────────────────────────────
    #  6. CARD: TÀI KHOẢN
    # ──────────────────────────────────────────
    def create_account_action_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        title = QLabel("👤  Tài khoản")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)

        self.create_action_row(layout, "🚪", "#FEE2E2", "Đăng xuất", "Đăng xuất khỏi StudyAI trên thiết bị này", "Đăng xuất", self.on_logout_clicked)
        layout.addWidget(create_divider())
        self.create_action_row(layout, "🗑", "#FEE2E2", "Xóa tài khoản", "Xóa vĩnh viễn tài khoản và toàn bộ dữ liệu của bạn", "Xóa tài khoản", self.on_delete_account_clicked)

        warn = QLabel("⚠️   Lưu ý: Hành động này không thể hoàn tác. Vui lòng cân nhắc kỹ trước khi xóa tài khoản.")
        warn.setWordWrap(True)
        warn.setStyleSheet(STYLE_WARN(get_font_style(FONTS['small_set'])))
        layout.addWidget(warn)
        self.scroll_layout.addWidget(card)

    def create_action_row(self, parent_layout, icon, icon_bg, title, subtitle, btn_text, cmd):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 8, 0, 8)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"background-color: {icon_bg}; border-radius: 10px; font-size: 15px; border: none;")
        row_layout.addWidget(icon_lbl)

        txt = QWidget()
        txt_layout = QVBoxLayout(txt)
        txt_layout.setContentsMargins(12, 0, 0, 0)

        l1 = QLabel(title)
        l1.setStyleSheet(f"{get_font_style(FONTS['body_bold_set'])} color: {COLORS['text_primary']}; border: none;")
        txt_layout.addWidget(l1)

        l2 = QLabel(subtitle)
        l2.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
        txt_layout.addWidget(l2)

        row_layout.addWidget(txt, 1)

        btn = QPushButton(btn_text)
        btn.setFixedSize(120, 34)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet(STYLE_BTN_DANGER(get_font_style(FONTS['small_bold_set'])))
        btn.clicked.connect(cmd)
        row_layout.addWidget(btn)

        parent_layout.addWidget(row)

    def set_fields_enabled(self, enabled: bool):
        """Bật/tắt trạng thái chỉnh sửa của các trường (trừ Email và MSSV)"""
        from PySide6.QtWidgets import QDateEdit
        for name, widget in self.inputs.items():
            if name in ["Email", "Mã sinh viên"]:
                widget.setReadOnly(True)
                widget.setEnabled(False)
                continue
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(not enabled)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(enabled)
            elif isinstance(widget, QDateEdit):
                widget.setEnabled(enabled)

    def set_user_data(self, user: dict):
        """Đổ dữ liệu người dùng từ database lên giao diện"""
        self.user_data = user
        if "full_name" in user and "Họ và tên" in self.inputs:
            self.inputs["Họ và tên"].setText(user["full_name"] or "")
        if "email" in user and "Email" in self.inputs:
            self.inputs["Email"].setText(user["email"] or "")
            self.inputs["Email"].setReadOnly(True)
            self.inputs["Email"].setEnabled(False)
        if "gender" in user and "Giới tính" in self.inputs:
            gender_str = "Nam" if user["gender"] in ["male", "Nam"] else "Nữ"
            self.inputs["Giới tính"].setCurrentText(gender_str)
            self.gender_val = gender_str
            self.update_avatar()
        if "birth_date" in user and "Ngày tháng năm sinh" in self.inputs:
            bdate = user["birth_date"]
            from PySide6.QtCore import QDate
            from PySide6.QtWidgets import QDateEdit
            widget = self.inputs["Ngày tháng năm sinh"]
            if isinstance(widget, QDateEdit):
                if bdate:
                    if hasattr(bdate, "year"):
                        widget.setDate(QDate(bdate.year, bdate.month, bdate.day))
                    else:
                        qd = QDate.fromString(str(bdate), "yyyy-MM-dd")
                        if not qd.isValid():
                            qd = QDate.fromString(str(bdate), "dd/MM/yyyy")
                        if qd.isValid():
                            widget.setDate(qd)
                else:
                    widget.setDate(QDate.currentDate())
            else:
                bdate_str = bdate.strftime("%d/%m/%Y") if hasattr(bdate, "strftime") else str(bdate or "")
                widget.setText(bdate_str)
        if "student_id" in user and "Mã sinh viên" in self.inputs:
            self.inputs["Mã sinh viên"].setText(user["student_id"] or "")
            self.inputs["Mã sinh viên"].setReadOnly(True)
            self.inputs["Mã sinh viên"].setEnabled(False)
        if "phone" in user and "Số điện thoại" in self.inputs:
            self.inputs["Số điện thoại"].setText(user["phone"] or "")
        if "university" in user and "Trường" in self.inputs:
            self.inputs["Trường"].setText(user["university"] or "")
        if "major" in user and "Ngành học" in self.inputs:
            self.inputs["Ngành học"].setText(user["major"] or "")
            
        # Tải theme hiển thị
        if "theme" in user and user["theme"]:
            self.apply_theme_ui(user["theme"])



    @qasync.asyncSlot()
    async def on_edit_clicked(self):
        """Xử lý nút bấm Chỉnh sửa / Lưu thay đổi"""
        import qasync
        from PySide6.QtWidgets import QMessageBox
        
        if not self.is_editing:
            # Chuyển sang chế độ chỉnh sửa
            self.is_editing = True
            self.btn_edit.setText("Lưu thay đổi")
            self.btn_edit.setStyleSheet(STYLE_BTN_SAVE(get_font_style(FONTS['small_bold_set'])))
            self.set_fields_enabled(True)
        else:
            # Lưu thay đổi vào DB
            self.setCursor(Qt.WaitCursor)
            try:
                full_name = self.inputs["Họ và tên"].text().strip()
                gender_text = self.inputs["Giới tính"].currentText()
                gender = "male" if gender_text == "Nam" else "female"
                birth_date_widget = self.inputs["Ngày tháng năm sinh"]
                phone = self.inputs["Số điện thoại"].text().strip()
                university = self.inputs["Trường"].text().strip()
                major = self.inputs["Ngành học"].text().strip()

                from PySide6.QtWidgets import QDateEdit
                if isinstance(birth_date_widget, QDateEdit):
                    birth_date = birth_date_widget.date().toString("yyyy-MM-dd")
                else:
                    birth_date_str = birth_date_widget.text().strip()
                    birth_date = None
                    if birth_date_str:
                        try:
                            parts = birth_date_str.split('/')
                            if len(parts) == 3:
                                birth_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                            else:
                                birth_date = birth_date_str
                        except Exception:
                            birth_date = None

                from app.BE.services.auth_service import update_user_profile
                await update_user_profile(
                    self.user_id,
                    full_name=full_name,
                    gender=gender,
                    birth_date=birth_date,
                    phone=phone,
                    university=university,
                    major=major
                )
                
                # Đồng bộ lại Avatar và Sidebar
                if self.parent():
                    main_win = self.window()
                    if hasattr(main_win, "sidebar"):
                        main_win.sidebar.update_profile_info(full_name, self.inputs["Mã sinh viên"].text(), gender_text)
                
                self.unsetCursor()
                self.show_message("Thành công", "🎉 Cập nhật thông tin cá nhân thành công!", QMessageBox.Information)
                
                # Quay lại trạng thái chỉ đọc
                self.is_editing = False
                self.btn_edit.setText("Chỉnh sửa")
                self.btn_edit.setStyleSheet(STYLE_BTN_EDIT(get_font_style(FONTS['small_bold_set'])))
                self.set_fields_enabled(False)
            except Exception as e:
                self.unsetCursor()
                self.show_message("Lỗi", f"❌ Không thể lưu thông tin: {e}", QMessageBox.Critical)

    def show_message(self, title, text, icon_type):
        """Hộp thông báo hiện đại đồng điệu giao diện"""
        from PySide6.QtWidgets import QMessageBox
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(icon_type)
        box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                min-width: 350px;
            }}
            QLabel {{
                color: #2d3748;
                font-size: 13px;
            }}
            QPushButton {{
                color: #2d3748;
                font-weight: bold;
                background-color: #edf2f7;
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 5px 15px;
            }}
        """)
        box.exec()

    @qasync.asyncSlot()
    async def on_change_password_clicked(self):
        """Đổi mật khẩu tài khoản người dùng"""
        current_pw = self.pw_inputs["Mật khẩu hiện tại"].text()
        new_pw = self.pw_inputs["Mật khẩu mới"].text()
        confirm_pw = self.pw_inputs["Xác nhận mật khẩu mới"].text()
        
        from PySide6.QtWidgets import QMessageBox
        if not current_pw or not new_pw or not confirm_pw:
            self.show_message("Cảnh báo", "Vui lòng nhập đầy đủ thông tin mật khẩu!", QMessageBox.Warning)
            return
            
        if len(new_pw) < 6:
            self.show_message("Cảnh báo", "Mật khẩu mới phải có tối thiểu 6 ký tự!", QMessageBox.Warning)
            return
            
        if new_pw != confirm_pw:
            self.show_message("Cảnh báo", "Mật khẩu xác nhận không khớp!", QMessageBox.Warning)
            return
            
        self.setCursor(Qt.WaitCursor)
        try:
            from app.BE.services.auth_service import change_password
            await change_password(self.user_id, current_pw, new_pw, confirm_pw)
            self.unsetCursor()
            self.show_message("Thành công", "🎉 Đổi mật khẩu thành công!", QMessageBox.Information)
            
            self.pw_inputs["Mật khẩu hiện tại"].clear()
            self.pw_inputs["Mật khẩu mới"].clear()
            self.pw_inputs["Xác nhận mật khẩu mới"].clear()
        except Exception as e:
            self.unsetCursor()
            err_msg = str(e)
            if hasattr(e, "detail"):
                err_msg = e.detail
            self.show_message("Lỗi", f"❌ Không thể đổi mật khẩu: {err_msg}", QMessageBox.Critical)



    def confirm_dialog(self, title, text):
        """Hộp thoại xác nhận hành động nguy hiểm"""
        from PySide6.QtWidgets import QMessageBox
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Question)
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.No)
        box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                min-width: 380px;
            }}
            QLabel {{
                color: #2d3748;
                font-size: 13px;
            }}
            QPushButton {{
                color: #2d3748;
                font-weight: bold;
                background-color: #edf2f7;
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 5px 15px;
            }}
        """)
        return box.exec() == QMessageBox.Yes

    @qasync.asyncSlot()
    async def on_logout_clicked(self):
        """Đăng xuất tài khoản người dùng"""
        if not self.confirm_dialog("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất khỏi ứng dụng?"):
            return
            
        self.setCursor(Qt.WaitCursor)
        try:
            from app.BE.services.auth_service import logout
            await logout(self.user_id)
            self.unsetCursor()
            
            # Close MainWindow and Relaunch LoginWindow
            main_win = self.window()
            main_win.close()
            
            # Khởi chạy lại màn hình Login
            from app.FE.components.login import LoginWindow
            from app.BE.services.home_service import HomeService
            from app.BE.services.exam_service import DocumentService
            from app.BE.services import ai_service
            
            self.login_window = LoginWindow(HomeService(), DocumentService(), ai_service)
            self.login_window.show()
        except Exception as e:
            self.unsetCursor()
            from PySide6.QtWidgets import QMessageBox
            self.show_message("Lỗi", f"❌ Không thể đăng xuất: {e}", QMessageBox.Critical)

    @qasync.asyncSlot()
    async def on_delete_account_clicked(self):
        """Xóa vĩnh viễn tài khoản người dùng"""
        if not self.confirm_dialog("CẢNH BÁO", "⚠️ Hành động này sẽ XÓA VĨNH VIỄN tài khoản của bạn và không thể hoàn tác.\nBạn có thực sự chắc chắn muốn tiếp tục?"):
            return
            
        self.setCursor(Qt.WaitCursor)
        try:
            from app.BE.services.auth_service import delete_user_account
            await delete_user_account(self.user_id)
            self.unsetCursor()
            from PySide6.QtWidgets import QMessageBox
            self.show_message("Thành công", "🎉 Tài khoản của bạn đã được xóa thành công. Ứng dụng sẽ quay trở lại màn hình đăng nhập.", QMessageBox.Information)
            
            # Close MainWindow and Relaunch LoginWindow
            main_win = self.window()
            main_win.close()
            
            from app.FE.components.login import LoginWindow
            from app.BE.services.home_service import HomeService
            from app.BE.services.exam_service import DocumentService
            from app.BE.services import ai_service
            
            self.login_window = LoginWindow(HomeService(), DocumentService(), ai_service)
            self.login_window.show()
        except Exception as e:
            self.unsetCursor()
            from PySide6.QtWidgets import QMessageBox
            self.show_message("Lỗi", f"❌ Không thể xóa tài khoản: {e}", QMessageBox.Critical)

# ═══════════════════════════════════════════════
#  CHẠY THỬ ĐỘC LẬP
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingPage()
    window.resize(1100, 760)
    window.show()
    sys.exit(app.exec())