import os
import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QHBoxLayout
from dotenv import load_dotenv
load_dotenv()

# Import nội bộ
from app.BE.database.connection import init_pool, close_pool
from app.BE.services.home_service import HomeService
from app.BE.services.exam_service import DocumentService
from app.BE.services import ai_service
from app.FE.views.homePage.home_page import HomePage
from app.FE.views.documentsPage.document_page import DocumentPage
from app.FE.views.AI_AssistantPage.AI_assistant_page import AIAssistantPage
from app.FE.views.settingPage.setting_page import SettingPage
from app.FE.views.statisticalPage.statistical_page import StatisticalPage
from app.FE.components.sidebar import Sidebar


class MainWindow(QMainWindow):
    PAGE_INDEX = {
        "Tổng quan": 0,
        "Tài liệu":  1,
        "Trợ lý AI": 2,
        "Thống kê":  3,
        "Cài đặt":   4,
    }

    def __init__(self, home_service, exam_service, ai_service_module, user_id: int = 0):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("StudyAI - Học tập thông minh")
        self.resize(1280, 800)

        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        layout = QHBoxLayout(self.main_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar       = Sidebar(on_navigate=self.handle_navigation, parent=self)
        self.content_stack = QStackedWidget()

        # Khởi tạo các page thật, mỗi page đúng 1 lần
        self.home_page     = HomePage(self, home_service, ai_service_module)
        self.document_page = DocumentPage(self, exam_service)
        self.ai_page       = AIAssistantPage(self, ai_service_module, self.user_id)
        self.stats_page    = StatisticalPage(self, self.user_id)
        self.setting_page  = SettingPage(self, self.user_id)

        self.content_stack.addWidget(self.home_page)      # 0
        self.content_stack.addWidget(self.document_page)  # 1
        self.content_stack.addWidget(self.ai_page)        # 2
        self.content_stack.addWidget(self.stats_page)     # 3
        self.content_stack.addWidget(self.setting_page)   # 4

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack, 1)

        # Khởi chạy tải thông tin cá nhân từ DB bất đồng bộ
        asyncio.create_task(self.load_user_profile())

    def handle_navigation(self, page_name: str):
        idx = self.PAGE_INDEX.get(page_name, 0)
        self.content_stack.setCurrentIndex(idx)
        
        # Tự động làm mới dữ liệu Thống kê theo thời gian thực khi người dùng chuyển sang trang Thống kê
        if page_name == "Thống kê":
            if hasattr(self.stats_page, "refresh_data"):
                self.stats_page.refresh_data()

    async def load_user_profile(self):
        """Tải dữ liệu thông tin tài khoản người dùng từ database và gán lên UI"""
        if not self.user_id:
            return
        try:
            from app.BE.services.auth_service import get_user_profile
            user = await get_user_profile(self.user_id)
            if user:
                # Cập nhật thông tin trên Sidebar
                self.sidebar.update_profile_info(user["full_name"], user["student_id"], user["gender"])
                # Cập nhật thông tin trên SettingPage
                self.setting_page.set_user_data(user)
        except Exception as e:
            print(f"Lỗi tải thông tin tài khoản người dùng: {e}")


async def _async_main(window_ready_event: asyncio.Event):
    try:
        await init_pool()
        print("Database kết nối thành công!")
    except Exception as e:
        print(f"Lỗi DB: {e}")
        # Vẫn cho UI hiện lên để còn debug được
    window_ready_event.set()


def main():
    app  = QApplication(sys.argv)
    app.setStyleSheet("""
        QMessageBox {
            background-color: #FFFFFF;
        }
        QMessageBox QLabel {
            color: #111827 !important;
            font-family: "Segoe UI";
            font-size: 13px;
        }
        QMessageBox QPushButton {
            background-color: #4C96F5;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 5px 15px;
            min-width: 70px;
            min-height: 24px;
            font-family: "Segoe UI";
            font-size: 12px;
            font-weight: 600;
        }
        QMessageBox QPushButton:hover {
            background-color: #357FE0;
        }
    """)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    home_service = HomeService()
    exam_service = DocumentService()
    
    # Khởi chạy màn hình Đăng nhập trước tiên để xác thực người dùng
    from app.FE.components.login import LoginWindow
    window = LoginWindow(home_service, exam_service, ai_service)
    window.show()

    # Khởi động init DB trên vòng lặp qasync rồi chạy vòng lặp mãi mãi.
    with loop:
        ready = asyncio.Event()
        loop.create_task(_async_main(ready))
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(close_pool())


if __name__ == "__main__":
    main()
