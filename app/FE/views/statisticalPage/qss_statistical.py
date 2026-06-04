# app/FE/views/statisticalPage/qss_statistical.py
"""
QSS Stylesheet định nghĩa phong cách giao diện sang trọng, tối giản, bo góc mềm mại 14px 
và phối màu xanh dương thanh lịch cho trang Thống kê học tập của StudyAI.
"""

COLORS = {
    "primary": "#4D8CF5",       # Xanh dương chủ đạo của StudyAI
    "primary_hover": "#3B7BE3",
    "bg_page": "#FFFFFF",       # Nền trang màu trắng tinh khôi
    "bg_card": "#FFFFFF",       # Nền card màu trắng
    "border_card": "#E2E8F0",   # Viền card xám mịn tinh tế
    "text_primary": "#1E293B",   # Chữ đen sẫm
    "text_secondary": "#64748B", # Chữ xám phụ mô tả
    
    # Các màu nhấn cho Icon
    "accent_orange": "#F97316",  # Streak ngày hoạt động
    "accent_green": "#10B981",   # Tỷ lệ hoàn thành task
    "accent_purple": "#8B5CF6",  # Tài liệu
}

FONTS = {
    "title": "font-family: 'Segoe UI'; font-size: 24px; font-weight: bold;",
    "subtitle": "font-family: 'Segoe UI'; font-size: 13px; font-weight: normal;",
    "card_title": "font-family: 'Segoe UI'; font-size: 16px; font-weight: bold;",
    "kpi_value": "font-family: 'Segoe UI'; font-size: 26px; font-weight: bold;",
    "kpi_label": "font-family: 'Segoe UI'; font-size: 12px; font-weight: 500;",
    "body_text": "font-family: 'Segoe UI'; font-size: 13.5px;",
    "body_bold": "font-family: 'Segoe UI'; font-size: 13.5px; font-weight: bold;",
    "ai_title": "font-family: 'Segoe UI'; font-size: 15px; font-weight: bold;",
}

# Style cho toàn bộ trang
STYLE_PAGE = f"background-color: {COLORS['bg_page']};"

# Style cho Header
STYLE_HEADER_TITLE = f"{FONTS['title']} color: {COLORS['text_primary']}; border: none; background: transparent;"
STYLE_HEADER_SUBTITLE = f"{FONTS['subtitle']} color: {COLORS['text_secondary']}; border: none; background: transparent;"

# Style cho ComboBox khoảng thời gian
STYLE_COMBOBOX = f"""
QComboBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_card']};
    border-radius: 8px;
    padding: 6px 12px 6px 12px;
    min-width: 120px;
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI';
    font-size: 13px;
}}
QComboBox::drop-down {{
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_card']};
    selection-background-color: #E0E7FF;
    selection-color: {COLORS['text_primary']};
    color: {COLORS['text_primary']};
}}
"""

# Style cho các Card lớn
STYLE_CARD = f"""
QFrame {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_card']};
    border-radius: 14px;
}}
"""

# Style riêng biệt cho KPI Cards
STYLE_KPI_CARD = STYLE_CARD

# Style cho Icon Box tròn nhỏ trong KPI Card
def get_icon_box_style(bg_color):
    return f"""
    QLabel {{
        background-color: {bg_color};
        border-radius: 20px;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        font-size: 18px;
        border: none;
    }}
    """

# Text labels styles
STYLE_LABEL_PRIMARY = f"color: {COLORS['text_primary']}; border: none; background: transparent;"
STYLE_LABEL_SECONDARY = f"color: {COLORS['text_secondary']}; border: none; background: transparent;"

# Nút xem phân tích chi tiết AI
STYLE_BTN_ANALYTICS = f"""
QPushButton {{
    background-color: {COLORS['primary']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-family: 'Segoe UI';
    font-size: 12.5px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}
"""
