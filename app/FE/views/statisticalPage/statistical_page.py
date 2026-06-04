# app/FE/views/statisticalPage/statistical_page.py
import asyncio
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QPushButton, QScrollArea
)

from app.FE.config import FONTS
from app.FE.views.statisticalPage.qss_statistical import *

class StatisticalPage(QWidget):
    def __init__(self, parent, user_id: int = 2):
        super().__init__(parent)
        self.user_id = user_id
        
        # Bắt buộc Qt phải vẽ màu nền stylesheet cho QWidget tùy biến (Tránh lỗi nền đen mặc định của Qt)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Áp dụng stylesheet trang màu trắng tinh khôi
        self.setStyleSheet(STYLE_PAGE)
        
        # Layout chính của trang
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)
        
        # Dựng vùng cuộn ScrollArea cho trang với nền trắng và ẩn hoàn toàn thanh cuộn bên phải
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: #FFFFFF; border: none;")
        
        scroll_content = QWidget()
        scroll_content.setAttribute(Qt.WA_StyledBackground, True)
        scroll_content.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        # 1. Khởi tạo Header
        self.init_header()
        
        # 2. Khởi tạo hàng 4 KPI Cards (Khởi tạo bằng 0/giá trị rỗng, không chứa dữ liệu ảo)
        self.init_kpi_cards()
        
        # 3. Khởi tạo Grid 2x2 chứa 4 Card lớn
        self.init_grid_details()
        
        scroll.setWidget(scroll_content)
        self.main_layout.addWidget(scroll)
        
        # Load dữ liệu thống kê thực tế từ database
        asyncio.create_task(self.load_statistics_data())

    def init_header(self):
        """Khởi tạo thanh tiêu đề lớn"""
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tiêu đề + Mô tả ngắn
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.lbl_title = QLabel("Thống kê học tập")
        self.lbl_title.setStyleSheet(STYLE_HEADER_TITLE)
        
        self.lbl_subtitle = QLabel("Theo dõi hiệu suất học tập và tiến độ của bạn")
        self.lbl_subtitle.setStyleSheet(STYLE_HEADER_SUBTITLE)
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_subtitle)
        h_layout.addLayout(text_layout)
        
        h_layout.addStretch()
        self.content_layout.addWidget(header_widget)

    def init_kpi_cards(self):
        """Dựng dải 4 KPI Cards thống kê ngang nhau khởi tạo bằng 0"""
        kpi_widget = QWidget()
        kpi_widget.setStyleSheet("background: transparent;")
        kpi_layout = QHBoxLayout(kpi_widget)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(15)
        
        # Card 1: Tổng thời gian tập trung - Viền Xanh dương
        self.card_focus = self.create_kpi_card("🕒", "#E0E7FF", "0h 0m", "Tổng thời gian tập trung", "#3B82F6")
        kpi_layout.addWidget(self.card_focus, 1)
        
        # Card 2: Chuỗi hoạt động liên tiếp - Viền Cam đỏ
        self.card_streak = self.create_kpi_card("🔥", "#FFEFEB", "0 ngày", "Chuỗi hoạt động liên tiếp", "#EF4444")
        kpi_layout.addWidget(self.card_streak, 1)
        
        # Card 3: Tỷ lệ hoàn thành nhiệm vụ - Viền Xanh lá
        self.card_tasks = self.create_kpi_card("✅", "#E6F4EA", "0%", "Tỷ lệ hoàn thành nhiệm vụ", "#10B981")
        kpi_layout.addWidget(self.card_tasks, 1)
        
        # Card 4: Tài liệu đã tải lên - Viền Vàng
        self.card_docs = self.create_kpi_card("📂", "#F3E8FF", "0", "Tài liệu đã tải lên", "#F59E0B")
        kpi_layout.addWidget(self.card_docs, 1)
        
        self.content_layout.addWidget(kpi_widget)

    def create_kpi_card(self, icon, icon_bg, value, label, border_color) -> QFrame:
        """Helper tạo 1 thẻ KPI Card bo góc với viền màu sắc rực rỡ đặc trưng"""
        card = QFrame()
        card.setObjectName("KpiCard")
        card.setStyleSheet(f"""
            QFrame#KpiCard {{
                background-color: #FFFFFF;
                border: 1.5px solid {border_color};
                border-radius: 14px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)
        
        # Icon tròn nền màu dịu mát
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet(get_icon_box_style(icon_bg))
        layout.addWidget(lbl_icon)
        
        # Label và Value
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"{FONTS['kpi_value']} {STYLE_LABEL_PRIMARY}")
        
        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"{FONTS['kpi_label']} {STYLE_LABEL_SECONDARY}")
        
        text_layout.addWidget(lbl_val)
        text_layout.addWidget(lbl_label)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        return card

    def init_grid_details(self):
        """Khởi tạo lưới 2x2 chứa 4 Card lớn chi tiết"""
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(15)
        
        # 1. Card Hiệu suất học tập
        self.card_1 = self.create_card_1()
        grid_layout.addWidget(self.card_1, 0, 0)
        
        # 2. Card Nhiệm vụ học tập
        self.card_2 = self.create_card_2()
        grid_layout.addWidget(self.card_2, 0, 1)
        
        # 3. Card Tài liệu & Đề thi
        self.card_3 = self.create_card_3()
        grid_layout.addWidget(self.card_3, 1, 0)
        
        # 4. Card AI Gợi ý cho bạn
        self.card_4 = self.create_card_4()
        grid_layout.addWidget(self.card_4, 1, 1)
        
        self.content_layout.addWidget(grid_widget)

    def create_card_1(self) -> QFrame:
        """Card 1: Hiệu suất học tập (Khởi tạo bằng 0)"""
        card = QFrame()
        card.setObjectName("DetailCard")
        card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: #FFFFFF;
                border: 1.5px solid #94A3B8;
                border-radius: 14px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Hiệu suất học tập")
        title.setStyleSheet(f"{FONTS['card_title']} {STYLE_LABEL_PRIMARY}")
        layout.addWidget(title)
        
        # Đường line màu xanh dương dày 2px
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #3B82F6; max-height: 2px; border: none;")
        layout.addWidget(divider)
        
        # Danh sách chi tiết
        self.perf_list = QVBoxLayout()
        self.perf_list.setSpacing(10)
        
        self.lbl_perf_1 = self.create_list_item("Học nhiều nhất", "--", bullet_color="#3B82F6")
        self.lbl_perf_2 = self.create_list_item("Thời gian trung bình mỗi ngày", "0m", bullet_color="#3B82F6")
        self.lbl_perf_3 = self.create_list_item("Phiên học dài nhất", "0m", bullet_color="#3B82F6")
        self.lbl_perf_4 = self.create_list_item("Chuỗi hoạt động hiện tại", "0 ngày", bullet_color="#3B82F6")
        self.lbl_perf_5 = self.create_list_item("Tổng số giờ học tháng này", "0h 0m", bullet_color="#3B82F6")
        
        self.perf_list.addWidget(self.lbl_perf_1)
        self.perf_list.addWidget(self.lbl_perf_2)
        self.perf_list.addWidget(self.lbl_perf_3)
        self.perf_list.addWidget(self.lbl_perf_4)
        self.perf_list.addWidget(self.lbl_perf_5)
        
        layout.addLayout(self.perf_list)
        layout.addStretch()
        return card

    def create_card_2(self) -> QFrame:
        """Card 2: Nhiệm vụ học tập (Khởi tạo bằng 0)"""
        card = QFrame()
        card.setObjectName("DetailCard")
        card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: #FFFFFF;
                border: 1.5px solid #94A3B8;
                border-radius: 14px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Nhiệm vụ học tập")
        title.setStyleSheet(f"{FONTS['card_title']} {STYLE_LABEL_PRIMARY}")
        layout.addWidget(title)
        
        # Đường line màu xanh lá dày 2px
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #10B981; max-height: 2px; border: none;")
        layout.addWidget(divider)
        
        self.tasks_list = QVBoxLayout()
        self.tasks_list.setSpacing(10)
        
        self.lbl_task_done  = self.create_list_item("Đã hoàn thành", "0", bullet="•", bullet_color="#10B981")
        self.lbl_task_doing = self.create_list_item("Đang thực hiện", "0", bullet="•", bullet_color="#4D8CF5")
        self.lbl_task_delay = self.create_list_item("Trễ hạn", "0", bullet="•", bullet_color="#EF4444")
        self.lbl_task_todo  = self.create_list_item("Chưa làm", "0", bullet="•", bullet_color="#64748B")
        
        self.tasks_list.addWidget(self.lbl_task_done)
        self.tasks_list.addWidget(self.lbl_task_doing)
        self.tasks_list.addWidget(self.lbl_task_delay)
        self.tasks_list.addWidget(self.lbl_task_todo)
        
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setStyleSheet("background-color: #E2E8F0; max-height: 1px; border: none;")
        self.tasks_list.addWidget(divider2)
        
        self.lbl_task_ontime = self.create_list_item("Tỷ lệ hoàn thành đúng hạn", "0%", bullet="")
        self.tasks_list.addWidget(self.lbl_task_ontime)
        
        layout.addLayout(self.tasks_list)
        layout.addStretch()
        return card

    def create_card_3(self) -> QFrame:
        """Card 3: Tài liệu & Đề thi (Khởi tạo bằng 0, Danh sách Top tài liệu động)"""
        card = QFrame()
        card.setObjectName("DetailCard")
        card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: #FFFFFF;
                border: 1.5px solid #94A3B8;
                border-radius: 14px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Tài liệu & Đề thi")
        title.setStyleSheet(f"{FONTS['card_title']} {STYLE_LABEL_PRIMARY}")
        layout.addWidget(title)
        
        # Đường line màu vàng dày 2px
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #F59E0B; max-height: 2px; border: none;")
        layout.addWidget(divider)
        
        self.docs_list = QVBoxLayout()
        self.docs_list.setSpacing(8)
        
        self.lbl_doc_total = self.create_list_item("Tổng tài liệu", "0", bullet="•", bullet_color="#F59E0B")
        self.lbl_doc_views = self.create_list_item("Tổng lượt xem", "0", bullet="•", bullet_color="#4D8CF5")
        self.lbl_doc_dls   = self.create_list_item("Tổng lượt tải", "0", bullet="•", bullet_color="#10B981")
        
        self.docs_list.addWidget(self.lbl_doc_total)
        self.docs_list.addWidget(self.lbl_doc_views)
        self.docs_list.addWidget(self.lbl_doc_dls)
        
        # Phần Top tài liệu phổ biến
        self.top_lbl = QLabel("Top tài liệu phổ biến:")
        self.top_lbl.setStyleSheet(f"{FONTS['body_bold']} color: {COLORS['text_primary']}; margin-top: 5px;")
        self.docs_list.addWidget(self.top_lbl)
        
        # Container cho Top tài liệu (để xóa đi vẽ lại động từ DB)
        self.top_docs_container = QWidget()
        self.top_docs_container.setStyleSheet("background: transparent; border: none;")
        self.top_docs_layout = QVBoxLayout(self.top_docs_container)
        self.top_docs_layout.setContentsMargins(0, 0, 0, 0)
        self.top_docs_layout.setSpacing(6)
        
        # Nhãn mặc định khi chưa có dữ liệu
        self.lbl_no_docs = QLabel("Chưa có tài liệu nào được xem")
        self.lbl_no_docs.setStyleSheet(f"{FONTS['body_text']} color: {COLORS['text_secondary']}; italic;")
        self.top_docs_layout.addWidget(self.lbl_no_docs)
        
        self.docs_list.addWidget(self.top_docs_container)
        
        layout.addLayout(self.docs_list)
        layout.addStretch()
        return card

    def create_card_4(self) -> QFrame:
        """Card 4: AI gợi ý cho bạn (Khởi tạo thông tin gợi ý mặc định)"""
        card = QFrame()
        card.setObjectName("DetailCard")
        card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: #FFFFFF;
                border: 1.5px solid #94A3B8;
                border-radius: 14px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("AI gợi ý cho bạn")
        title.setStyleSheet(f"{FONTS['card_title']} {STYLE_LABEL_PRIMARY}")
        layout.addWidget(title)
        
        # Đường line màu cam đỏ dày 2px
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #EF4444; max-height: 2px; border: none;")
        layout.addWidget(divider)
        
        self.ai_list = QVBoxLayout()
        self.ai_list.setSpacing(10)
        
        self.lbl_ai_1 = QLabel("• Chưa tích lũy đủ dữ liệu hoạt động học tập.")
        self.lbl_ai_2 = QLabel("• Hãy bắt đầu thêm phiên tập trung để AI phân tích hiệu suất của bạn.")
        self.lbl_ai_3 = QLabel("• Tải lên tài liệu học tập để lưu trữ và chia sẻ cùng mọi người.")
        self.lbl_ai_4 = QLabel("• Tạo thêm các nhiệm vụ học tập mới để lập kế hoạch ôn thi hiệu quả.")
        self.lbl_ai_5 = QLabel("• StudyAI Bot sẽ đồng hành cùng bạn trên con đường học tập!")
        
        for lbl in [self.lbl_ai_1, self.lbl_ai_2, self.lbl_ai_3, self.lbl_ai_4, self.lbl_ai_5]:
            lbl.setStyleSheet(f"{FONTS['body_text']} {STYLE_LABEL_SECONDARY}")
            lbl.setWordWrap(True)
            self.ai_list.addWidget(lbl)
            
        layout.addLayout(self.ai_list)
        layout.addStretch()
        return card

    def create_list_item(self, label, value, bullet="•", bullet_color="#4D8CF5") -> QWidget:
        """Helper tạo 1 dòng văn bản thông tin căn chỉnh đều 2 bên"""
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout = QHBoxLayout()
        left_layout.setSpacing(6)
        
        if bullet:
            lbl_bullet = QLabel(bullet)
            lbl_bullet.setStyleSheet(f"color: {bullet_color}; font-weight: bold; font-size: 15px; border: none; background: transparent;")
            left_layout.addWidget(lbl_bullet)
            
        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"{FONTS['body_text']} {STYLE_LABEL_SECONDARY}")
        left_layout.addWidget(lbl_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"{FONTS['body_bold']} {STYLE_LABEL_PRIMARY}")
        layout.addWidget(lbl_val)
        
        return w

    def create_popular_doc_item(self, filename, views) -> QWidget:
        """Helper tạo dòng tài liệu phổ biến"""
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(8, 2, 0, 2)
        
        lbl_file = QLabel(filename)
        lbl_file.setStyleSheet(f"{FONTS['body_text']} {STYLE_LABEL_SECONDARY}")
        layout.addWidget(lbl_file)
        
        layout.addStretch()
        
        lbl_views = QLabel(views)
        lbl_views.setStyleSheet(f"{FONTS['body_text']} color: {COLORS['text_secondary']}; font-size: 11.5px;")
        layout.addWidget(lbl_views)
        
        return w

    def on_btn_analytics_clicked(self):
        """Xử lý sự kiện xem phân tích chi tiết từ AI"""
        print("[AI Analytics] Đang phân tích chi tiết dữ liệu học tập...")

    def refresh_data(self):
        """Phương thức công khai để MainWindow yêu cầu làm mới dữ liệu từ Database"""
        import asyncio
        asyncio.create_task(self.load_statistics_data())

    async def load_statistics_data(self):
        """Truy vấn dữ liệu học tập thực tế từ Database MySQL và cập nhật lên Dashboard"""
        try:
            from app.BE.database.connection import fetchrow, fetch
            from app.BE.database.repositories.document_repo import DocumentRepository
            
            # --- 1. TRUY VẤN TÀI LIỆU & ĐỀ THI ---
            doc_stats = await DocumentRepository.get_summary_stats()
            t_total_docs = doc_stats.get("total", 0)
            t_total_views = doc_stats.get("view_count", 0)
            t_total_downloads = doc_stats.get("recent", 0)
            
            # Cập nhật KPI Card tài liệu
            for child in self.card_docs.findChildren(QLabel):
                if child.text().isdigit() or child.text() == "0":
                    child.setText(str(t_total_docs))
            
            # Cập nhật chi tiết Card Tài liệu
            self.lbl_doc_total.layout().itemAt(2).widget().setText(str(t_total_docs))
            self.lbl_doc_views.layout().itemAt(2).widget().setText(f"{t_total_views:,}")
            self.lbl_doc_dls.layout().itemAt(2).widget().setText(str(t_total_downloads))
            
            # Tải Top 3 tài liệu phổ biến thực tế từ Database
            popular_docs = await fetch("""
                SELECT title, view_count 
                FROM documents 
                WHERE is_approved=TRUE 
                ORDER BY view_count DESC 
                LIMIT 3
            """)
            
            # Xóa các phần tử cũ trong Top tài liệu
            for i in reversed(range(self.top_docs_layout.count())):
                widget = self.top_docs_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            if popular_docs:
                for doc in popular_docs:
                    title_short = doc["title"]
                    if len(title_short) > 30:
                        title_short = title_short[:28] + "..."
                    doc_item = self.create_popular_doc_item(f"📄 {title_short}", f"{doc['view_count']} lượt xem")
                    self.top_docs_layout.addWidget(doc_item)
            else:
                lbl_empty = QLabel("Chưa có tài liệu nào được xem")
                lbl_empty.setStyleSheet(f"{FONTS['body_text']} color: {COLORS['text_secondary']}; italic; border: none;")
                self.top_docs_layout.addWidget(lbl_empty)
            
            # --- 2. TRUY VẤN NHIỆM VỤ HỌC TẬP (Tasks) ---
            task_stats = await fetchrow("""
                SELECT 
                    COUNT(*) AS total,
                    SUM(IF(status='done', 1, 0)) AS done,
                    SUM(IF(status='pending', 1, 0)) AS pending,
                    SUM(IF(status='overdue', 1, 0)) AS overdue
                FROM tasks
                WHERE user_id = %s
            """, self.user_id)
            
            t_total = 0
            t_done = 0
            t_doing = 0
            t_todo = 0
            t_delay = 0
            t_pct = 0
            
            if task_stats and task_stats["total"] > 0:
                t_total = task_stats["total"]
                t_done  = task_stats["done"] or 0
                t_todo  = task_stats["pending"] or 0
                t_doing = 0  # Bảng database chỉ có trạng thái 'pending' hoặc 'done'
                t_delay = task_stats["overdue"] or 0
                t_pct   = int((t_done / t_total) * 100)
                
            # Cập nhật KPI Card Tỷ lệ hoàn thành nhiệm vụ
            for child in self.card_tasks.findChildren(QLabel):
                if "%" in child.text() or child.text() == "0%":
                    child.setText(f"{t_pct}%")
            
            # Cập nhật chi tiết Card Nhiệm vụ
            self.lbl_task_done.layout().itemAt(2).widget().setText(str(t_done))
            self.lbl_task_doing.layout().itemAt(2).widget().setText(str(t_doing))
            self.lbl_task_delay.layout().itemAt(2).widget().setText(str(t_delay))
            self.lbl_task_todo.layout().itemAt(2).widget().setText(str(t_todo))
            self.lbl_task_ontime.layout().itemAt(2).widget().setText(f"{t_pct}%")
            
            # --- 3. TRUY VẤN PHIÊN HỌC TẬP (Study Sessions) ---
            study_stats = await fetchrow("""
                SELECT 
                    COALESCE(SUM(duration_min), 0) AS total_mins,
                    COUNT(DISTINCT scheduled_date) AS active_days,
                    COALESCE(MAX(duration_min), 0) AS max_duration
                FROM study_sessions
                WHERE user_id = %s AND status = 'done'
            """, self.user_id)
            
            total_mins = 0
            active_days = 0
            max_duration = 0
            time_str = "0h 0m"
            
            if study_stats:
                total_mins = study_stats["total_mins"] or 0
                active_days = study_stats["active_days"] or 0
                max_duration = study_stats["max_duration"] or 0
                hrs = total_mins // 60
                mins = total_mins % 60
                time_str = f"{hrs}h {mins}m"
                
            # Cập nhật KPI Card Tổng thời gian tập trung
            for child in self.card_focus.findChildren(QLabel):
                if "h" in child.text() or child.text() == "0h 0m":
                    child.setText(time_str)
            
            # Cập nhật KPI Card Chuỗi hoạt động liên tiếp
            for child in self.card_streak.findChildren(QLabel):
                if "ngày" in child.text() or child.text() == "0 ngày":
                    child.setText(f"{active_days} ngày")
            
            # Cập nhật chi tiết Card Hiệu suất học tập
            self.lbl_perf_4.layout().itemAt(2).widget().setText(f"{active_days} ngày")
            self.lbl_perf_5.layout().itemAt(2).widget().setText(time_str)
            self.lbl_perf_3.layout().itemAt(2).widget().setText(f"{max_duration // 60}h {max_duration % 60}m")
            
            # Truy vấn ngày học nhiều nhất trong tuần
            max_day_data = await fetchrow("""
                SELECT DAYNAME(scheduled_date) AS day_name, SUM(duration_min) AS total_mins
                FROM study_sessions
                WHERE user_id = %s AND status = 'done'
                GROUP BY scheduled_date
                ORDER BY total_mins DESC
                LIMIT 1
            """, self.user_id)
            
            days_vi = {
                "Monday": "Thứ Hai",
                "Tuesday": "Thứ Ba",
                "Wednesday": "Thứ Tư",
                "Thursday": "Thứ Năm",
                "Friday": "Thứ Sáu",
                "Saturday": "Thứ Bảy",
                "Sunday": "Chủ Nhật"
            }
            max_day_name = "--"
            if max_day_data and max_day_data["day_name"]:
                max_day_name = days_vi.get(max_day_data["day_name"], "--")
            self.lbl_perf_1.layout().itemAt(2).widget().setText(max_day_name)
            
            # Truy vấn thời gian trung bình mỗi ngày
            avg_day_data = await fetchrow("""
                SELECT COALESCE(AVG(day_mins), 0) AS avg_mins FROM (
                    SELECT SUM(duration_min) AS day_mins
                    FROM study_sessions
                    WHERE user_id = %s AND status = 'done'
                    GROUP BY scheduled_date
                ) t
            """, self.user_id)
            
            avg_mins = int(avg_day_data["avg_mins"]) if avg_day_data else 0
            self.lbl_perf_2.layout().itemAt(2).widget().setText(f"{avg_mins // 60}h {avg_mins % 60}m")
            
            # --- 4. CẬP NHẬT GỢI Ý HỌC TẬP TỰ ĐỘNG TỪ AI (Tránh dữ liệu ảo) ---
            if total_mins > 0 or t_total > 0 or t_total_docs > 0:
                self.lbl_ai_1.setText(f"• Bạn đang duy trì chuỗi học tập {active_days} ngày hoạt động. Hãy tiếp tục giữ vững phong độ!")
                if max_day_name != "--":
                    self.lbl_ai_2.setText(f"• Hiệu suất học tập của bạn cao nhất vào {max_day_name} với các phiên học tập trung.")
                else:
                    self.lbl_ai_2.setText("• Hãy lên lịch biểu đều đặn hơn để AI phân tích ngày tập trung hiệu quả nhất.")
                
                self.lbl_ai_3.setText(f"• Bạn đã tải lên {t_total_docs} tài liệu học tập. Tài liệu của bạn đã tích lũy {t_total_views} lượt xem từ hệ thống.")
                self.lbl_ai_4.setText(f"• Đã hoàn thành {t_done} trên tổng số {t_total} nhiệm vụ học tập đề ra.")
                
                if t_pct >= 80:
                    self.lbl_ai_5.setText(f"• Tuyệt vời! Tỷ lệ hoàn thành nhiệm vụ đạt {t_pct}%. Bạn đang quản lý thời gian học tập rất tốt!")
                else:
                    self.lbl_ai_5.setText(f"• Tỷ lệ hoàn thành nhiệm vụ hiện đạt {t_pct}%. Hãy cố gắng giải quyết các task trễ hạn nhé!")
            else:
                self.lbl_ai_1.setText("• Chưa tích lũy đủ dữ liệu hoạt động học tập.")
                self.lbl_ai_2.setText("• Hãy bắt đầu thêm phiên tập trung để AI phân tích hiệu suất của bạn.")
                self.lbl_ai_3.setText("• Tải lên tài liệu học tập để lưu trữ và chia sẻ cùng mọi người.")
                self.lbl_ai_4.setText("• Tạo thêm các nhiệm vụ học tập mới để lập kế hoạch ôn thi hiệu quả.")
                self.lbl_ai_5.setText("• StudyAI Bot sẽ đồng hành cùng bạn trên con đường học tập!")
                
        except Exception as e:
            print(f"[Error loading statistics] {e}")
