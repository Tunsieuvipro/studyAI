CREATE DATABASE smartstudyai_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
USE smartstudyai_db;


-- 1. USERS  (Cài đặt → Thông tin tài khoản)
CREATE TABLE IF NOT EXISTS users (
    id                 INT AUTO_INCREMENT PRIMARY KEY, -- Sửa SERIAL thành INT AUTO_INCREMENT
    student_id         VARCHAR(20)  UNIQUE NOT NULL,   -- K.AI212
    full_name          VARCHAR(100) NOT NULL,
    email              VARCHAR(150) UNIQUE NOT NULL,
    password_hash      VARCHAR(255) NOT NULL,
    gender             VARCHAR(10)  DEFAULT 'other',   -- Nam | Nữ | other
    birth_date         DATE,
    phone              VARCHAR(15),
    university         VARCHAR(150),
    major              VARCHAR(150),
    avatar_url         TEXT,
    theme              VARCHAR(10)  DEFAULT 'light',   -- light | dark | auto
    security_question  VARCHAR(255) NULL,
    security_answer    VARCHAR(255) NULL,
    notify_before_min  INT          DEFAULT 30,        -- nhắc trước X phút
    notify_enabled     BOOLEAN      DEFAULT TRUE,
    is_active          BOOLEAN      DEFAULT TRUE,
    created_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP, -- Sửa NOW() thành CURRENT_TIMESTAMP
    updated_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_theme CHECK (theme IN ('light','dark','auto')) -- Tách constraint riêng cho chuẩn MySQL
);

-- 2. REFRESH TOKENS
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    token      TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. SUBJECTS  (danh mục môn học)
CREATE TABLE IF NOT EXISTS subjects (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    code       VARCHAR(20)  UNIQUE NOT NULL,    -- K.A312
    name       VARCHAR(150) NOT NULL,
    category   VARCHAR(50)  NOT NULL DEFAULT 'Other',
    difficulty SMALLINT     DEFAULT 3,
    credits    SMALLINT     DEFAULT 3,
    color      VARCHAR(7)   DEFAULT '#3b82f6',  -- hex hiển thị lịch
    CONSTRAINT chk_difficulty CHECK (difficulty BETWEEN 1 AND 5)
);

-- 4. TIMETABLE  (TKB cố định → Tổng quan / Lịch học tập)
CREATE TABLE IF NOT EXISTS timetable_entries (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    subject_id INT NOT NULL,
    weekday    SMALLINT NOT NULL,  -- 1=T2 … 7=CN
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    room       VARCHAR(30),
    entry_type VARCHAR(10) DEFAULT 'LT',   -- LT | BT | TH (loại tiết)
    semester   VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT chk_weekday CHECK (weekday BETWEEN 1 AND 7),
    CONSTRAINT chk_entry_type CHECK (entry_type IN ('LT','BT','TH'))
);

-- 5. ENROLLMENTS  (user đăng ký môn, có ngày thi + độ khó riêng)
CREATE TABLE IF NOT EXISTS enrollments (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    subject_id     INT NOT NULL,
    difficulty     SMALLINT,
    exam_date      DATE,
    priority_score DECIMAL(5,2) DEFAULT 0.00, -- Đổi NUMERIC sang DECIMAL
    semester       VARCHAR(20),
    UNIQUE (user_id, subject_id, semester),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT chk_enroll_difficulty CHECK (difficulty BETWEEN 1 AND 5)
);

-- 6. STUDY SESSIONS  (output AI scheduler → Lịch học tập)
CREATE TABLE IF NOT EXISTS study_sessions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    subject_id     INT NOT NULL,
    scheduled_date DATE NOT NULL,
    start_time     TIME NOT NULL,
    end_time       TIME NOT NULL,
    duration_min   SMALLINT NOT NULL,
    status         VARCHAR(20) DEFAULT 'planned',
    generated_by   VARCHAR(10) DEFAULT 'ai',
    note           TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT chk_session_status CHECK (status IN ('planned','done','missed','rescheduled')),
    CONSTRAINT chk_generated_by CHECK (generated_by IN ('ai','manual'))
);

-- 7. TASKS  (Nhiệm vụ hôm nay – sidebar Tổng quan)
CREATE TABLE IF NOT EXISTS tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    subject_id  INT,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    due_date    TIMESTAMP NULL DEFAULT NULL, -- Chỉnh lại định dạng thời hạn
    status      VARCHAR(20) DEFAULT 'pending',
    priority    SMALLINT    DEFAULT 2,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT chk_task_status CHECK (status IN ('pending','done','overdue')),
    CONSTRAINT chk_task_priority CHECK (priority BETWEEN 1 AND 3)
);

-- 8. DOCUMENTS  (Hệ thống đề thi – Tài liệu)
CREATE TABLE IF NOT EXISTS documents (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    subject_id     INT,
    uploader_id    INT,
    title          VARCHAR(255) NOT NULL,
    description    TEXT,
    file_url       TEXT NOT NULL,
    file_type      VARCHAR(10)  DEFAULT 'pdf',   -- pdf | docx
    file_size_mb   DECIMAL(6,2),
    grade_level    VARCHAR(10),                  -- Lớp 12 | ĐH …
    doc_category   VARCHAR(30)  DEFAULT 'exam',  -- exam | summary | exercise
    exam_type      VARCHAR(20),                  -- Cuối kỳ | Giữa kỳ | Thi thử
    tags           TEXT,                         -- 🛠️ SỬA CHÍ MẠNG: MySQL không có TEXT[], đổi sang TEXT thường (lưu chuỗi JSON string)
    ai_summary     TEXT,                         -- cache tóm tắt AI
    download_count INT          DEFAULT 0,
    view_count     INT          DEFAULT 0,
    is_approved    BOOLEAN      DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (uploader_id) REFERENCES users(id),
    CONSTRAINT chk_file_type CHECK (file_type IN ('pdf','docx')),
    CONSTRAINT chk_doc_category CHECK (doc_category IN ('exam','summary','exercise','other'))
);

-- 9. CHAT SESSIONS  (Trợ lý AI → Lịch sử hội thoại)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    title      VARCHAR(255) NOT NULL DEFAULT 'Hội thoại mới',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. CHAT MESSAGES  (Trợ lý AI → nội dung từng tin)
CREATE TABLE IF NOT EXISTS chat_messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      INT NOT NULL,
    role            VARCHAR(15) NOT NULL,
    content         TEXT NOT NULL,
    attachment_url  TEXT,                        -- file đính kèm (PDF, ảnh)
    attachment_name VARCHAR(255),
    liked           BOOLEAN DEFAULT NULL,        -- Like / Dislike phản hồi AI
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    CONSTRAINT chk_chat_role CHECK (role IN ('user','assistant'))
);

-- 11. NOTIFICATIONS  (Thông báo – sidebar Tổng quan)
CREATE TABLE IF NOT EXISTS notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    title      VARCHAR(255) NOT NULL,
    body       TEXT,
    type       VARCHAR(30)  DEFAULT 'info',
    is_read    BOOLEAN      DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_noti_type CHECK (type IN ('info','warning','deadline','schedule_update'))
);

-- 12. WEEKLY STATS  (Thống kê hàng tuần – Tổng quan)
CREATE TABLE IF NOT EXISTS weekly_stats (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    week_start     DATE NOT NULL,
    total_sessions SMALLINT DEFAULT 0,
    done_sessions  SMALLINT DEFAULT 0,
    self_study_hrs DECIMAL(5,2) DEFAULT 0.00,
    completion_pct DECIMAL(5,2) DEFAULT 0.00,
    UNIQUE (user_id, week_start),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 📌 INDEXES (Giữ nguyên cấu trúc tăng tốc độ truy vấn cho MySQL) ────────────────
CREATE INDEX idx_timetable_user        ON timetable_entries(user_id, weekday);
CREATE INDEX idx_sessions_user_date    ON study_sessions(user_id, scheduled_date);
CREATE INDEX idx_tasks_user_due        ON tasks(user_id, due_date);
CREATE INDEX idx_docs_subject          ON documents(subject_id);
CREATE INDEX idx_docs_category         ON documents(doc_category, file_type);
CREATE INDEX idx_chat_sessions_user    ON chat_sessions(user_id, updated_at DESC);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);
CREATE INDEX idx_notifications_unread  ON notifications(user_id, is_read);
CREATE INDEX idx_enrollments_user      ON enrollments(user_id);