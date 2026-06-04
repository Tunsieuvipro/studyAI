import os
import asyncio
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QDialogButtonBox, QProgressBar, QPushButton
)

# Helper function to create fonts cleanly
def qfont(family, size, bold=False):
    f = QFont(family, size)
    f.setWeight(QFont.Bold if bold else QFont.Normal)
    return f


# ── WORKER LUỒNG NỀN ĐỘC LẬP CHO CLOUDINARY UPLOAD ───────────────────────────
class UploadWorker(QThread):
    progress = Signal(int, str)  # percent, status text
    finished_stages = Signal(str, float)  # cloud_url, size_mb
    failed = Signal(str)         # error message

    def __init__(self, local_filepath):
        super().__init__()
        self.local_filepath = local_filepath

    def run(self):
        try:
            self.progress.emit(15, "Khởi tạo kết nối đám mây Cloudinary...")
            import cloudinary
            import cloudinary.uploader
            from app.BE.core.config import settings
            
            # Cấu hình thông tin kết nối Cloudinary
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            
            self.progress.emit(40, "Đang tải tệp tin lên đám mây Cloudinary...")
            
            # Tính toán dung lượng file cục bộ
            file_size_bytes = os.path.getsize(self.local_filepath)
            size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            # Upload file lên Cloudinary đồng bộ trên luồng nền này
            upload_result = cloudinary.uploader.upload(
                self.local_filepath,
                resource_type="auto",
                folder="smartstudy/documents"
            )
            cloud_url = upload_result.get("secure_url")
            
            self.progress.emit(85, "Tải lên Cloudinary thành công!")
            self.finished_stages.emit(cloud_url, size_mb)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.failed.emit(str(e))


# ── FORM ĐIỀN THÔNG TIN ĐĂNG TẢI TÀI LIỆU ─────────────────────────────────────
class UploadDocDialog(QDialog):
    def __init__(self, parent, file_path, subjects):
        super().__init__(parent)
        self.setWindowTitle("Đăng tải Tài liệu lên Đám mây Cloudinary")
        self.resize(520, 420)
        self.file_path = file_path
        self.subjects = subjects 
        
        # Kiểu dáng giao diện sang trọng, chữ đen sắc nét trên nền sáng dễ đọc!
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel {
                color: #334155;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding: 8px;
                color: #1e293b;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #3b82f6;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1e293b;
                selection-background-color: #edf2f7;
                selection-color: #1e293b;
                border: 1px solid #cbd5e0;
            }
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header = QLabel("ĐĂNG TẢI TÀI LIỆU MỚI")
        header.setFont(qfont("Segoe UI", 13, True))
        header.setStyleSheet("color: #1e3a8a;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Lấy tên file gốc làm tiêu đề gợi ý
        filename = os.path.basename(file_path)
        title_val = os.path.splitext(filename)[0]
        
        self.txt_title = QLineEdit(title_val)
        form_layout.addRow("Tiêu đề:", self.txt_title)
        
        # ComboBox Môn học (chọn môn đã có hoặc gõ để tự thêm mới)
        self.cb_subject = QComboBox()
        self.cb_subject.setEditable(True)
        self.cb_subject.setInsertPolicy(QComboBox.NoInsert)
        self.cb_subject.lineEdit().setPlaceholderText("Chọn hoặc tự nhập môn học mới (ví dụ: Toán, Python...)")
        
        # Thêm các môn học hiện có vào ComboBox
        if self.subjects:
            subj_names = sorted(list(set([s.get("name") for s in self.subjects if s.get("name")])))
            self.cb_subject.addItems(subj_names)
        self.cb_subject.setCurrentText("")
        form_layout.addRow("Môn học:", self.cb_subject)
        
        # ComboBox Thể loại tài liệu
        self.cb_category = QComboBox()
        self.cb_category.addItems(["Đề thi", "Đề cương", "Bài tập", "Tài liệu"])
        form_layout.addRow("Thể loại:", self.cb_category)
        
        # ComboBox Phân khúc kỳ thi
        self.cb_exam = QComboBox()
        self.cb_exam.addItems(["Không có", "Giữa kỳ", "Cuối kỳ", "15 phút", "1 tiết"])
        form_layout.addRow("Dành cho kỳ thi:", self.cb_exam)
        
        # Mô tả ngắn
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Nhập mô tả tóm tắt của đề thi/tài liệu này...")
        self.txt_desc.setFixedHeight(80)
        form_layout.addRow("Mô tả ngắn:", self.txt_desc)
        
        layout.addLayout(form_layout)
        
        # Nút bấm hành động
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.button_box.button(QDialogButtonBox.Ok).setText("Tiếp tục 🚀")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Hủy bỏ")
        layout.addWidget(self.button_box)
        
    def get_data(self):
        subj_name = self.cb_subject.currentText().strip()
        exam = self.cb_exam.currentText()
        if exam == "Không có":
            exam = None
            
        cat_mapping = {
            "Đề thi": "exam",
            "Đề cương": "summary",
            "Bài tập": "exercise",
            "Tài liệu": "other"
        }
        category_vietnamese = self.cb_category.currentText()
        category_english = cat_mapping.get(category_vietnamese, "other")
            
        return {
            "title": self.txt_title.text().strip(),
            "subject_name": subj_name if subj_name else None,
            "grade_level": None,
            "doc_category": category_english,
            "exam_type": exam,
            "description": self.txt_desc.toPlainText().strip()
        }


# ── HỘP THOẠI THANH TIẾN TRÌNH ĐỒNG BỘ ĐÁM MÂY & MYSQL ────────────────────────
class UploadProgressDialog(QDialog):
    def __init__(self, parent, service, upload_data, filepath, user_id=1):
        super().__init__(parent)
        self.setWindowTitle("Đồng bộ Đám mây & MySQL")
        self.setFixedSize(480, 220)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.service = service
        self.upload_data = upload_data
        self.filepath = filepath
        self.user_id = user_id
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2d3748;
                font-family: "Segoe UI";
            }
            QProgressBar {
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                text-align: center;
                background-color: #f7fafc;
                color: #1e293b;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #10b981);
                border-radius: 7px;
            }
            QPushButton {
                background-color: #e2e8f0;
                color: #4a5568;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #cbd5e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Tiêu đề tiến độ
        self.lbl_title = QLabel("Đang tải tài liệu lên đám mây...")
        self.lbl_title.setFont(qfont("Segoe UI", 12, True))
        self.lbl_title.setStyleSheet("color: #1e3a8a;")
        layout.addWidget(self.lbl_title)
        
        # Trạng thái mô tả chi tiết
        self.lbl_status = QLabel("Đang chuẩn bị kết nối dữ liệu...")
        self.lbl_status.setFont(qfont("Segoe UI", 10))
        self.lbl_status.setStyleSheet("color: #4a5568;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)
        
        # Thanh ProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Nút đóng
        self.btn_close = QPushButton("Đang xử lý...")
        self.btn_close.setEnabled(False)
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close, 0, Qt.AlignRight)
        
        # Chạy tác vụ tải lên Cloudinary trên QThread luồng nền tách biệt
        self.worker = UploadWorker(local_filepath=self.filepath)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_stages.connect(self.on_finished_stages)
        self.worker.failed.connect(self.on_failed)
        
        self.worker.start()
        
    def on_progress(self, percent, text):
        self.progress_bar.setValue(percent)
        self.lbl_status.setText(text)
        
    def on_finished_stages(self, cloud_url, size_mb):
        self.lbl_status.setText("Đang ghi nhận bản ghi và đồng bộ cơ sở dữ liệu MySQL...")
        self.progress_bar.setValue(90)
        # Chạy tác vụ MySQL nhẹ nhàng trực tiếp trên main loop (An toàn tuyệt đối)
        asyncio.create_task(self.save_to_mysql_async(cloud_url, size_mb))
        
    async def save_to_mysql_async(self, cloud_url, size_mb):
        try:
            from app.BE.database.connection import fetchrow, execute
            from app.BE.database.repositories.document_repo import DocumentRepository
            
            # 1. Tìm hoặc tạo môn học tự động
            subject_id = None
            subject_name = self.upload_data.get("subject_name")
            if subject_name:
                subject_name = " ".join(subject_name.split()).upper()
                if subject_name:
                    row = await fetchrow("SELECT id FROM subjects WHERE name = %s", subject_name)
                    if row:
                        subject_id = row["id"]
                    else:
                        import re
                        import unicodedata
                        
                        # Chuyển đổi tên môn học sang dạng không dấu, viết hoa không khoảng trắng
                        clean_name = unicodedata.normalize('NFKD', subject_name).encode('ASCII', 'ignore').decode('utf-8')
                        base_code = re.sub(r'[^a-zA-Z0-9]', '', clean_name).upper()
                        if not base_code:
                            base_code = "SUBJ"
                            
                        # Đảm bảo duy nhất (Unique) bằng cách dò khóa trong MySQL
                        code = base_code[:10]
                        exists = True
                        counter = 1
                        while exists:
                            dup_row = await fetchrow("SELECT id FROM subjects WHERE code = %s", code)
                            if not dup_row:
                                exists = False
                            else:
                                suffix = str(counter)
                                max_len = 10 - len(suffix)
                                code = f"{base_code[:max_len]}{suffix}"
                                counter += 1
                                
                        await execute("INSERT INTO subjects (name, code) VALUES (%s, %s)", subject_name, code)
                        new_row = await fetchrow("SELECT id FROM subjects WHERE code = %s", code)
                        if new_row:
                            subject_id = new_row["id"]
                            
            # 2. Lưu vào MySQL
            ext = os.path.splitext(self.filepath)[1].lower().replace(".", "")
            await DocumentRepository.create(
                subject_id=subject_id,
                uploader_id=self.user_id,
                title=self.upload_data["title"],
                description=self.upload_data["description"],
                file_url=cloud_url,
                file_type=ext,
                file_size_mb=size_mb,
                grade_level=None,
                doc_category=self.upload_data["doc_category"],
                exam_type=self.upload_data["exam_type"]
            )
            
            # 3. Trình bày kết quả thành công
            self.lbl_title.setText("🎉 Tải lên thành công!")
            self.lbl_status.setText("Tài liệu đã được tải lên đám mây Cloudinary và đồng bộ MySQL thành công rực rỡ.")
            self.progress_bar.setValue(100)
            self.btn_close.setText("Hoàn thành ✨")
            self.btn_close.setEnabled(True)
            self.btn_close.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.on_failed(str(e))
        
    def on_failed(self, error_msg):
        self.lbl_title.setText("❌ Lỗi đồng bộ")
        self.lbl_title.setStyleSheet("color: #ef4444;")
        self.lbl_status.setText(f"Quá trình tải lên gặp lỗi: {error_msg}")
        self.progress_bar.setValue(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #ef4444;
            }
        """)
        self.btn_close.setText("Đóng")
        self.btn_close.setEnabled(True)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
