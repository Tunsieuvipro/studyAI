from app.FE.config import COLORS

STYLE_PAGE = f"background-color: {COLORS['bg']};"

STYLE_SCROLL = "QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }"
STYLE_RIGHT_SCROLL = STYLE_SCROLL

STYLE_TRANSPARENT = "background: transparent;"

STYLE_EXAM_CARD = f"""
    #chat_card {{
        background-color: {COLORS['card']};
        border: 2px solid {COLORS['border']};
        border-radius: 12px;
    }}
"""
STYLE_CHAT_CARD = STYLE_EXAM_CARD

STYLE_LABEL_PRIMARY = f"color: {COLORS['text_primary']}; border: none;"
STYLE_LABEL_SECONDARY = f"color: {COLORS['text_secondary']}; border: none;"

STYLE_BTN_UPLOAD = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0 15px;
    }}
    QPushButton:hover {{
        background-color: #357FE0;
    }}
"""
STYLE_BTN_UPLOAD_TOP = STYLE_BTN_UPLOAD

STYLE_BTN_REFRESH = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 0 15px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_SEARCH_ENTRY = f"""
    QLineEdit {{
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 0 10px;
        background-color: {COLORS['bg']};
        color: {COLORS['text_primary']};
    }}
"""

STYLE_COMBO = f"""
    QComboBox {{
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 0 32px 0 10px;
        background-color: white;
        color: {COLORS['text_primary']};
    }}
    QComboBox::drop-down {{ width: 0px; border: none; }}
    QComboBox::down-arrow {{ image: none; }}
    QComboBox QAbstractItemView {{
        background-color: white;
        color: #111827;
        selection-background-color: #F5F7FB;
        selection-color: #111827;
        border: 1px solid #BFCAD9;
    }}
"""
STYLE_COMBOBOX = STYLE_COMBO

STYLE_BTN_SEARCH = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: #357FE0;
    }}
"""

STYLE_ICON_BOX = "border-radius: 12px; font-size: 19px; border: none;"

STYLE_FILE_ICON = "border-radius: 12px; font-size: 15px; font-weight: bold; border: none;"

STYLE_TAG = "border-radius: 6px; padding: 2px 4px; border: none;"

STYLE_BTN_VIEW = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: #DCF0FF;
    }}
"""

STYLE_BTN_DOWNLOAD = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: #357FE0;
    }}
"""

STYLE_UP_HDR = f"background-color: {COLORS['primary']}; border-radius: 8px; border: none;"
STYLE_UP_TITLE = "color: white; border: none; background: transparent;"

STYLE_DROP_ZONE = f"""
    QFrame {{
        background-color: {COLORS['hover']};
        border: 2px dashed #A8CFFA;
        border-radius: 10px;
    }}
"""

STYLE_DROP_ICON_TXT = "border: none; background: transparent;"

STYLE_BTN_CHOOSE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: #357FE0;
    }}
"""

STYLE_CAT_HDR = f"background-color: {COLORS['primary']}; border-radius: 8px; border: none;"
STYLE_CAT_TITLE = "color: white; border: none; background: transparent;"

STYLE_POP_COUNT = f"""
    background-color: #E2F0FD;
    color: {COLORS['primary']};
    border-radius: 11px;
    border: none;
"""

STYLE_XEM_THEM = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['primary']};
        border: none;
        text-align: center;
    }}
    QPushButton:hover {{
        color: #357FE0;
    }}
"""