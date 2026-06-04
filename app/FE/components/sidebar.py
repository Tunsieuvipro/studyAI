import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt

from app.FE.config import COLORS, FONTS

class Sidebar(QFrame):
    """Thanh menu bên trái (Sidebar) điều hướng chính cho toàn bộ ứng dụng."""
    def __init__(self, on_navigate=None, parent=None):
        super().__init__(parent)
        self.on_navigate = on_navigate

        # Cấu hình UI cơ bản cho Sidebar
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            #Sidebar {{
                background-color: {COLORS['sidebar']};
                border-right: 3px solid {COLORS['border']};
            }}
        """)
        self.setFixedWidth(300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # PHẦN TRÊN: Logo & Tiêu đề
        # ----------------------------------------------------
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(18, 35, 10, 15)
        logo_layout.setSpacing(8)

        logo_icon = QLabel("📘")
        logo_icon.setStyleSheet(f"color: {COLORS['primary']}; font-family: 'Segoe UI Emoji'; font-size: 29px;")
        logo_layout.addWidget(logo_icon)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        title_label = QLabel("StudyAI")
        title_label.setStyleSheet(f"color: {COLORS['primary']}; font-family: '{FONTS['sidebar_title'][0]}'; font-size: {FONTS['sidebar_title'][1]}px; font-weight: {FONTS['sidebar_title'][2]};")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Học tập thông minh cùng AI")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-family: '{FONTS['sidebar_desc'][0]}'; font-size: {FONTS['sidebar_desc'][1]}px;")
        title_layout.addWidget(subtitle_label)

        logo_layout.addWidget(title_container, 1) # stretch=1
        main_layout.addWidget(logo_widget)

        # Đường kẻ ngang
        divider_container = QWidget()
        divider_layout = QVBoxLayout(divider_container)
        divider_layout.setContentsMargins(25, 0, 25, 15)
        divider = QFrame()
        divider.setFixedHeight(3)
        divider.setStyleSheet(f"background-color: {COLORS['primary']}; border: none;")
        divider_layout.addWidget(divider)
        main_layout.addWidget(divider_container)

        # ----------------------------------------------------
        # PHẦN GIỮA: Menu Điều hướng
        # ----------------------------------------------------
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(15, 0, 15, 0)
        nav_layout.setSpacing(6)

        self.nav_items = [
            ("Tổng quan",        "🏠"),
            ("Tài liệu",         "📁"),
            ("Trợ lý AI",        "🤖"),
            ("Thống kê",         "📊"),
            ("Cài đặt",          "⚙️"),
        ]

        self.nav_buttons = {}
        for text, icon in self.nav_items:
            btn = QPushButton(f" {icon}  {text}")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedHeight(50)
            btn.setProperty("page_name", text)
            btn.clicked.connect(lambda checked=False, t=text: self._on_btn_click(t))
            nav_layout.addWidget(btn)
            self.nav_buttons[text] = btn

        main_layout.addWidget(nav_widget)
        main_layout.addStretch(1) # Pushes everything above up and below down

        # Mặc định chọn
        self.set_active_page("Tổng quan")

        # ----------------------------------------------------
        # PHẦN DƯỚI: Thông tin cá nhân (Profile Card)
        # ----------------------------------------------------
        profile_container = QWidget()
        profile_layout = QVBoxLayout(profile_container)
        profile_layout.setContentsMargins(20, 0, 20, 25)

        profile_frame = QFrame()
        profile_frame.setObjectName("ProfileFrame")
        profile_frame.setStyleSheet(f"""
            #ProfileFrame {{
                background-color: transparent;
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        pf_layout = QHBoxLayout(profile_frame)
        pf_layout.setContentsMargins(12, 12, 12, 12)
        pf_layout.setSpacing(15)

        # Avatar
        self.avatar = QLabel()
        self.avatar.setFixedSize(45, 45)

        base_dir = os.path.dirname(os.path.dirname(__file__))      # → app/FE
        img_dir  = os.path.join(base_dir, "assets")
        img_path = os.path.join(img_dir, "user_sidebar.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(45, 45, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.avatar.setPixmap(pixmap)
        else:
            self.avatar.setText("👤")
            self.avatar.setAlignment(Qt.AlignCenter)
            self.avatar.setStyleSheet(f"background-color: {COLORS['hover']}; border-radius: 22px; font-size: 21px;")

        pf_layout.addWidget(self.avatar)

        # Info
        pinfo_widget = QWidget()
        pinfo_layout = QVBoxLayout(pinfo_widget)
        pinfo_layout.setContentsMargins(0, 0, 0, 0)
        pinfo_layout.setSpacing(0)

        self.profile_name = QLabel("Nguyen Van A")
        self.profile_name.setStyleSheet(f"color: {COLORS['text_primary']}; font-family: '{FONTS['nav_main'][0]}'; font-size: {FONTS['nav_main'][1]}px; font-weight: {FONTS['nav_main'][2]}; border: none;")
        pinfo_layout.addWidget(self.profile_name)

        self.profile_class = QLabel("K.AI212")
        self.profile_class.setStyleSheet(f"color: {COLORS['text_secondary']}; font-family: '{FONTS['sidebar_desc'][0]}'; font-size: {FONTS['sidebar_desc'][1]}px; border: none;")
        pinfo_layout.addWidget(self.profile_class)

        pf_layout.addWidget(pinfo_widget, 1)
        profile_layout.addWidget(profile_frame)

        main_layout.addWidget(profile_container)

    def _on_btn_click(self, page_name):
        """Xử lý sự kiện khi người dùng click vào một mục trên menu."""
        self.set_active_page(page_name)
        if self.on_navigate:
            self.on_navigate(page_name)

    def set_active_page(self, page_name):
        """Cập nhật trạng thái Highlight cho nút tương ứng với trang đang hiển thị."""
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['primary']};
                        color: #FFFFFF;
                        font-family: '{FONTS['nav_main'][0]}';
                        font-size: {FONTS['nav_main'][1]}px;
                        font-weight: {FONTS['nav_main'][2]};
                        text-align: left;
                        border-radius: 10px;
                        border: none;
                        padding-left: 15px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_secondary']};
                        font-family: '{FONTS['nav_sub'][0]}';
                        font-size: {FONTS['nav_sub'][1]}px;
                        text-align: left;
                        border-radius: 10px;
                        border: 2px solid transparent;
                        padding-left: 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['hover']};
                        border: 2px solid {COLORS['primary']};
                    }}
                """)

    def update_profile_info(self, name: str, student_id: str, gender: str = "other"):
        """Cập nhật thông tin và ảnh đại diện động của người dùng ở Sidebar"""
        # Chỉ lấy tên cuối cùng để hiển thị gọn gàng trên Sidebar
        display_name = name
        if name:
            parts = name.strip().split()
            if parts:
                display_name = parts[-1]
        
        self.profile_name.setText(display_name)
        self.profile_class.setText(student_id)
        
        # Chọn ảnh đại diện phù hợp theo giới tính
        base_dir = os.path.dirname(os.path.dirname(__file__))
        img_dir  = os.path.join(base_dir, "assets")
        
        if gender == "female" or gender == "Nữ":
            img_name = "user_woman.png"
        elif gender == "male" or gender == "Nam":
            img_name = "user_man.png"
        else:
            img_name = "user_sidebar.png"
            
        img_path = os.path.join(img_dir, img_name)
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(45, 45, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.avatar.setPixmap(pixmap)