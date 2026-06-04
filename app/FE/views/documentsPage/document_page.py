import asyncio
import qasync

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QCursor, QFont, QPainter, QColor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QLayout,
    QPushButton, QScrollArea, QVBoxLayout, QWidget, QStyledItemDelegate,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QTextEdit, QFileDialog
)

from app.FE.config import FONTS
from app.FE.views.documentsPage.qss_document import *
from app.BE.services.exam_service import get_stats
from app.FE.views.documentsPage.form_upload import UploadDocDialog, UploadProgressDialog
from app.FE.views.documentsPage.stats_card import StatsRowWidget
from app.FE.views.documentsPage.exam_card import ExamCardWidget

# ── DỮ LIỆU GIẢ LẬP CHUẨN CẤU TRÚC CHỐNG SẬP ──
MOCK_STATS = {
    "total": 0,
    "pdf_count": 0,
    "word_count": 0,
    "recent_downloads": 0
}

MOCK_EXAMS = []
MOCK_POPULAR = []

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class ArrowComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(QStyledItemDelegate())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#64748B"))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        arrow_rect = QRect(self.width() - 22, 0, 18, self.height())
        painter.drawText(arrow_rect, Qt.AlignVCenter | Qt.AlignHCenter, "▼")
        painter.end()



# ── TRANG TÀI LIỆU CHÍNH ──────────────────────────────────────────────────────
class DocumentPage(QFrame):
    def __init__(self, master, exam_service=None):
        super().__init__(master)
        self.exam_service = exam_service
        self._stats = MOCK_STATS
        self._exams = MOCK_EXAMS
        self._popular = MOCK_POPULAR

        self.setStyleSheet(STYLE_PAGE)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # Cột trái (Chiếm phần lớn diện tích)
        self.left_col = QFrame()
        self.left_col.setStyleSheet(STYLE_TRANSPARENT)
        self.left_layout = QVBoxLayout(self.left_col)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(12)

        # Cột phải (Sử dụng tỉ lệ phần trăm co giãn tự động thay cho kích thước cố định)
        self.right_col = QFrame()
        self.right_col.setStyleSheet(STYLE_TRANSPARENT)
        self.right_layout = QVBoxLayout(self.right_col)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(12)
        self.right_layout.setAlignment(Qt.AlignTop)

        # Phân chia tỉ lệ động: Cột trái chiếm 72%, Cột phải chiếm 28%
        main_layout.addWidget(self.left_col, 72)
        main_layout.addWidget(self.right_col, 28)

        # 1. Header (Hệ thống đề thi)
        self.create_header()

        # 2. Bộ tìm kiếm (QLineEdit + Button Tìm kiếm, không có Combobox) - ĐƯA LÊN TRÊN ĐẦU
        self.create_filters()

        # 3. Khu vực thống kê chỉ số - ĐƯA XUỐNG DƯỚI THANH TÌM KIẾM
        self.stats_layout = QVBoxLayout()
        self.left_layout.addLayout(self.stats_layout)

        # 4. Vùng cuộn chứa danh sách đề thi (Tắt thanh cuộn ngang tuyệt đối)
        self.exam_scroll = QScrollArea()
        self.exam_scroll.setWidgetResizable(True)
        self.exam_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.exam_scroll.setStyleSheet(STYLE_RIGHT_SCROLL)
        self.exam_content = QWidget()
        self.exam_content.setStyleSheet(STYLE_TRANSPARENT)
        self.exam_list_layout = QVBoxLayout(self.exam_content)
        self.exam_list_layout.setContentsMargins(0, 0, 5, 0)
        self.exam_list_layout.setSpacing(10)
        self.exam_list_layout.setAlignment(Qt.AlignTop)
        self.exam_scroll.setWidget(self.exam_content)
        self.left_layout.addWidget(self.exam_scroll, 1)

        # Cột phải danh mục phổ biến
        self.cat_container = QWidget()
        self.cat_container.setStyleSheet(STYLE_TRANSPARENT)
        self.cat_list_layout = QVBoxLayout(self.cat_container)
        self.cat_list_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_list_layout.setSpacing(12)
        self.create_right_panel()

        # Tắt chính sách thanh cuộn ngang của Widget tổng
        self.setAttribute(Qt.WA_MacShowFocusRect, False)

        # Thực thi tải dữ liệu từ database thông qua Service thật
        self.trigger_async_load()

    def make_card(self):
        card = QFrame()
        card.setObjectName("chat_card")
        card.setStyleSheet(STYLE_CHAT_CARD)
        return card

    def trigger_async_load(self):
        """Khởi tạo và chạy Task bất đồng bộ tải dữ liệu từ DB MySQL cực kỳ an toàn."""
        import asyncio
        asyncio.create_task(self._load())

    async def _load(self, filters=None):
        """Hàm load dữ liệu từ Database thông qua exam_service."""
        try:
            # 1. Gọi backend lấy các chỉ số thống kê thật từ MySQL
            self._stats = await get_stats()
            self._render_stats()

            # 2. Gọi backend tìm kiếm và hiển thị danh sách đề thi
            if filters:
                self._exams = await self.exam_service.get_exams_with_filters(filters)
            else:
                self._exams = await self.exam_service.get_exams()
            self._render_exams()

            # 3. Lấy danh mục môn học phổ biến nhất
            self._popular = await self.exam_service.get_popular_subjects()
            self._render_popular_categories()

            # 4. Lấy tất cả môn học có sẵn để phục vụ form đăng tải
            self._all_subjects = await self.exam_service.get_subjects()

        except Exception as e:
            print(f"[ERROR] DocumentPage load thất bại: {e}")

    def create_header(self):
        """Tạo phần đầu trang với Tiêu đề 'Hệ thống đề thi' và các nút bấm."""
        header = QFrame()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title = QLabel("Hệ thống đề thi")
        title.setFont(qfont(FONTS["h1_exam"]))
        title.setStyleSheet(STYLE_LABEL_PRIMARY)

        sub = QLabel("Quản lý, tìm kiếm và tải xuống tài liệu ôn tập")
        sub.setFont(qfont(FONTS["body_exam"]))
        sub.setStyleSheet(STYLE_LABEL_SECONDARY)

        title_box.addWidget(title)
        title_box.addWidget(sub)
        h_layout.addLayout(title_box)
        h_layout.addStretch()

        # Nút Đăng tải tài liệu (+ Upload đề thi)
        btn_upload = QPushButton("+ Upload đề thi")
        btn_upload.setFixedHeight(36)
        btn_upload.setCursor(QCursor(Qt.PointingHandCursor))
        btn_upload.setFont(qfont(FONTS["body_bold_exam"]))
        btn_upload.setStyleSheet(STYLE_BTN_UPLOAD_TOP)
        btn_upload.clicked.connect(self.open_upload_dialog)
        h_layout.addWidget(btn_upload)

        # Nút Làm mới (styled with STYLE_BTN_REFRESH)
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        btn_refresh.setFont(qfont(FONTS["body_bold_exam"]))
        btn_refresh.setStyleSheet(STYLE_BTN_REFRESH)
        btn_refresh.clicked.connect(lambda: self.trigger_async_load())
        h_layout.addWidget(btn_refresh)

        self.left_layout.addWidget(header)

    def create_filters(self):
        """Tạo thanh tìm kiếm nằm trên cùng, chiếm trọn chiều ngang, không còn combobox."""
        bar = self.make_card()
        b_layout = QHBoxLayout(bar)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(10)

        # Hộp tìm kiếm full ngang
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Tìm kiếm đề thi, môn học, lớp học...")
        self.search_entry.setFixedHeight(40)
        self.search_entry.setFont(qfont(FONTS["small_exam"]))
        self.search_entry.setStyleSheet(STYLE_SEARCH_ENTRY)
        self.search_entry.returnPressed.connect(self._on_search_clicked)
        b_layout.addWidget(self.search_entry, 1)

        # Nút Tìm kiếm
        btn_search = QPushButton("Tìm kiếm")
        btn_search.setFixedHeight(40)
        btn_search.setFixedWidth(100)
        btn_search.setFont(qfont(FONTS["body_bold_exam"]))
        btn_search.setCursor(QCursor(Qt.PointingHandCursor))
        btn_search.setStyleSheet(STYLE_BTN_SEARCH)
        btn_search.clicked.connect(self._on_search_clicked)
        b_layout.addWidget(btn_search)

        self.left_layout.addWidget(bar)

    def _render_stats(self):
        # Dọn dẹp stats_layout cũ
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Dựng Widget hàng 4 thẻ thống kê mới
        stats_widget = StatsRowWidget(self._stats, parent=self)
        self.stats_layout.addWidget(stats_widget)

    def _render_exams(self):
        # Dọn dẹp exam_list_layout cũ
        while self.exam_list_layout.count():
            item = self.exam_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        exams = self._exams

        hdr = QFrame()
        h_layout = QHBoxLayout(hdr)
        h_layout.setContentsMargins(0, 5, 0, 5)

        title = QLabel("Danh sách đề thi")
        title.setFont(qfont(FONTS["h3_exam"]))
        title.setStyleSheet(STYLE_LABEL_PRIMARY)
        h_layout.addWidget(title)
        h_layout.addStretch()

        count_lbl = QLabel(f"Hiển thị {len(exams)} / {len(exams)} đề thi")
        count_lbl.setFont(qfont(FONTS["small_exam"]))
        count_lbl.setStyleSheet(STYLE_LABEL_SECONDARY)
        h_layout.addWidget(count_lbl)

        self.exam_list_layout.addWidget(hdr)

        # Vẽ từng Card đề thi/tài liệu bằng ExamCardWidget cực mượt
        for exam in exams:
            card = ExamCardWidget(
                exam=exam,
                on_view_callback=self.open_viewer_dialog,
                on_download_callback=self.download_document,
                parent=self
            )
            self.exam_list_layout.addWidget(card)

    def create_right_panel(self):
        cat_card = self.make_card()
        self.cat_card_layout = QVBoxLayout(cat_card)
        self.cat_card_layout.setContentsMargins(15, 15, 15, 15)
        self.cat_card_layout.setSpacing(10)
        self.cat_card_layout.setSizeConstraint(QLayout.SetMinimumSize)  # Ép thẻ card luôn tự co dãn để ôm khít chiều cao các danh mục bên trong

        cat_hdr = QFrame()
        cat_hdr.setStyleSheet(STYLE_CAT_HDR)
        cat_hdr.setFixedHeight(40)  # Cố định chiều cao tiêu đề màu xanh để không bao giờ bị dãn
        cat_h_layout = QHBoxLayout(cat_hdr)
        cat_h_layout.setContentsMargins(10, 8, 10, 8)
        cat_title = QLabel("Danh mục phổ biến")
        cat_title.setFont(qfont(FONTS["h3_exam"]))
        cat_title.setStyleSheet(STYLE_CAT_TITLE)
        cat_h_layout.addWidget(cat_title)
        cat_h_layout.addStretch()
        self.cat_card_layout.addWidget(cat_hdr)

        # Tạo vùng cuộn cho danh sách danh mục phổ biến
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cat_scroll.setStyleSheet(STYLE_RIGHT_SCROLL)
        self.cat_scroll.setWidget(self.cat_container)
        self.cat_scroll.setMinimumHeight(150)  # Khóa chiều cao tối thiểu để không bị sập về 0px
        self.cat_scroll.setMaximumHeight(250)  # Giới hạn chiều cao tối đa để kích hoạt thanh cuộn dọc

        self.cat_card_layout.addWidget(self.cat_scroll)

        self.right_layout.addWidget(cat_card)
        self.right_layout.addStretch(1)  # Đẩy toàn bộ thẻ card danh mục lên sát trên cùng và giữ cố định ở đó

    def _render_popular_categories(self):
        while self.cat_list_layout.count():
            item = self.cat_list_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
            elif item.widget():
                item.widget().deleteLater()

        popular_subjects = self._popular
        for subj, count in popular_subjects:
            row = QHBoxLayout()
            row.setContentsMargins(5, 4, 5, 4)

            # Icon nhỏ tượng trưng giống ảnh
            icon_lbl = QLabel("📚")
            icon_lbl.setFont(qfont(("Segoe UI", 10)))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            row.addWidget(icon_lbl)

            s_lbl = QLabel(subj)
            s_lbl.setFont(qfont(FONTS["body_exam"]))
            s_lbl.setStyleSheet(STYLE_LABEL_PRIMARY)
            s_lbl.setWordWrap(True) # Tự động xuống dòng khi tên môn dài
            row.addWidget(s_lbl, 1) # Cho phép chiếm dụng linh hoạt và co giãn theo tỉ lệ

            row.addStretch()

            c_lbl = QLabel(str(count))
            c_lbl.setFont(qfont(FONTS["small_bold_exam"]))
            c_lbl.setAlignment(Qt.AlignCenter)
            c_lbl.setFixedSize(22, 22)
            c_lbl.setStyleSheet(STYLE_POP_COUNT)
            row.addWidget(c_lbl)

            self.cat_list_layout.addLayout(row)

    def open_upload_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn tài liệu học tập/Đề thi", "",
            "Tài liệu (*.pdf *.docx)"
        )
        if not file_path:
            return
            
        subjects = getattr(self, "_all_subjects", [])
        dialog = UploadDocDialog(self, file_path, subjects)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self._execute_upload(file_path, data)

    def _execute_upload(self, filepath, data):
        try:
            user_id = 2
            if self.parent() and hasattr(self.parent(), "user_id"):
                user_id = self.parent().user_id
                
            progress_dialog = UploadProgressDialog(self, self.exam_service, data, filepath, user_id)
            if progress_dialog.exec() == QDialog.Accepted:
                asyncio.create_task(self._load())
        except Exception as e:
            QMessageBox.critical(self, "Lỗi đăng tải", f"Tải tệp lên Cloudinary thất bại: {e}")

    def _on_filter_changed(self, text):
        self._on_search_clicked()

    def _on_search_clicked(self):
        q = self.search_entry.text().strip()
        if not q:
            q = None
            
        filters = {
            "subject": None,
            "exam_type": None,
            "query": q
        }
        
        import asyncio
        asyncio.create_task(self._load(filters))

    @qasync.asyncSlot()
    async def open_viewer_dialog(self, doc_id: int):
        """Mở trực tiếp tài liệu trong Trình duyệt mặc định và tăng lượt Xem lên DB."""
        try:
            doc_details = await self.exam_service.get_exam_detail(doc_id)
            if not doc_details:
                QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy thông tin chi tiết của tài liệu này.")
                return
                
            url = doc_details.get("file_url")
            if not url:
                QMessageBox.warning(self, "Lỗi liên kết", "Tài liệu này chưa có liên kết trực tuyến để xem.")
                return
                
            # Mở trực tiếp bằng Trình duyệt mặc định của hệ điều hành
            import webbrowser
            webbrowser.open(url)
            
            # Tải lại giao diện để hiển thị số lượt xem cập nhật tức thì
            await self._load()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể mở tài liệu trực tuyến: {e}")

    @qasync.asyncSlot()
    async def download_document(self, doc_id: int):
        """Mở hộp thoại chọn nơi lưu tệp tin và tải ngầm từ Cloudinary về máy tính của người dùng."""
        try:
            # 1. Lấy thông tin tài liệu trước
            doc_details = await self.exam_service.get_exam_detail(doc_id)
            url = doc_details.get("file_url")
            title = doc_details.get("title", "tai_lieu")
            file_type = doc_details.get("file_type", "pdf").lower()
            
            if not url:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy liên kết tải tài liệu.")
                return
                
            # 2. Định vị thư mục Downloads mặc định trên Windows của User làm thư mục gợi ý đầu tiên
            import os
            from pathlib import Path
            downloads_path = str(Path.home() / "Downloads")
            
            # Làm sạch tên file gợi ý để tránh ký tự đặc biệt gây lỗi hệ thống file Windows
            import unicodedata
            import re
            
            clean_title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('utf-8')
            clean_title = re.sub(r'[^a-zA-Z0-9\s_-]', '', clean_title).strip()
            clean_title = clean_title.replace(" ", "_")
            if not clean_title:
                clean_title = "tai_lieu"
                
            default_filename = f"{clean_title}.{file_type}"
            default_save_path = os.path.join(downloads_path, default_filename)
            
            # 3. Mở Hộp thoại Save File Dialog mặc định của hệ điều hành
            file_filter = f"Tài liệu (*.{file_type})"
            dest_filepath, _ = QFileDialog.getSaveFileName(
                self, 
                "Chọn nơi lưu tài liệu học tập", 
                default_save_path, 
                file_filter
            )
            
            # Nếu người dùng bấm "Cancel" hủy chọn nơi lưu
            if not dest_filepath:
                return
                
            # 4. Gọi backend tăng lượt tải lên DB
            await self.exam_service.increment_download(doc_id)
            
            # 5. Thực hiện tải ngầm bất đồng bộ (tránh đơ UI)
            import urllib.request
            
            def _download_file():
                urllib.request.urlretrieve(url, dest_filepath)
                
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _download_file)
            
            # 6. Làm mới giao diện và hiển thị thông báo thành công rực rỡ
            await self._load()
            QMessageBox.information(
                self, 
                "Tải xuống thành công", 
                f"🎉 Tài liệu học tập đã được lưu thành công!\n\nĐường dẫn: {dest_filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi tải xuống", f"Không thể tải tệp tin về máy: {e}")