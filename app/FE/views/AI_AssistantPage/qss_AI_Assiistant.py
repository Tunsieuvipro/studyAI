from app.FE.config import COLORS

STYLE_PAGE = f"background-color: {COLORS['bg']};"

STYLE_RIGHT_SCROLL = "QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }"

STYLE_TRANSPARENT = "background: transparent;"

STYLE_CHAT_CARD = f"""
    #chat_card {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
    }}
"""

STYLE_LABEL_PRIMARY = f"color: {COLORS['text_primary']}; border: none;"
STYLE_LABEL_SECONDARY = f"color: {COLORS['text_secondary']}; border: none;"

STYLE_BTN_PRIMARY = f"""
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

STYLE_BTN_SECONDARY = f"""
    QPushButton {{
        background-color: {COLORS['card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 0 15px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_CHIPS_SCROLL = "QScrollArea { border: none; background: transparent; }"

STYLE_CHIP_BTN = f"""
    QPushButton {{
        background-color: {COLORS['card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 0 15px;
    }}
    QPushButton:hover {{
        background-color: #DBEAFE;
        border: 1px solid {COLORS['primary']};
    }}
"""

STYLE_USER_BUBBLE = f"""
    QFrame {{
        background-color: {COLORS.get('chat_user', '#EAF2FF')};
        border-radius: 14px;
    }}
"""

STYLE_USER_BUBBLE_LBL = f"color: {COLORS['text_primary']}; border: none; background: transparent;"

STYLE_ATTACHMENT_CARD = f"""
    QFrame {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    }}
"""

STYLE_ATTACHMENT_ICON = "background-color: #FDDEDE; color: #E74C3C; border-radius: 8px; font-weight: bold; border: none;"

STYLE_ATTACHMENT_TXT = f"color: {COLORS['text_primary']}; border: none; background: transparent;"
STYLE_ATTACHMENT_SIZE = f"color: {COLORS['text_secondary']}; border: none; background: transparent;"

STYLE_AI_BUBBLE = f"""
    QFrame {{
        background-color: {COLORS.get('chat_ai', '#FFFFFF')};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
    }}
"""

STYLE_AVATAR = "background-color: #DBEAFE; border-radius: 19px; font-size: 17px;"

STYLE_CHAT_ACTION_BTN = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        padding: 0 5px;
    }}
    QPushButton:hover {{
        color: {COLORS['primary']};
        background-color: {COLORS['hover']};
        border-radius: 4px;
    }}
"""

# Text input styling
STYLE_INPUT_CARD = f"""
    #input_card {{
        background-color: {COLORS['card']};
        border: 2px solid {COLORS['primary']};
        border-radius: 12px;
    }}
"""

STYLE_INPUT_TEXT = f"""
    QTextEdit {{
        border: none;
        background: transparent;
        color: {COLORS['text_primary']};
    }}
"""

STYLE_INPUT_TOOL_BTN = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 0 12px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_MIC_BTN = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 18px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_SEND_BTN = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 19px;
    }}
    QPushButton:hover {{
        background-color: #357FE0;
    }}
"""

# History & suggestions styling
STYLE_HIST_HDR = f"background-color: {COLORS['primary']}; border-radius: 8px;"
STYLE_HIST_HDR_LBL = "color: white; background: transparent; border: none;"

STYLE_HIST_ITEM = f"""
    QFrame:hover {{
        background-color: {COLORS['hover']};
        border-radius: 6px;
    }}
"""

STYLE_HIST_ITEM_TITLE = f"color: {COLORS['text_primary']}; background: transparent; border: none;"
STYLE_HIST_ITEM_TIME = f"color: {COLORS['text_secondary']}; background: transparent; border: none;"

STYLE_MORE_BTN = f"""
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

STYLE_SUG_HDR = f"background-color: {COLORS['primary']}; border-radius: 8px;"
STYLE_SUG_HDR_LBL = "color: white; background: transparent; border: none;"
STYLE_SUG_DOT = f"color: {COLORS['primary']}; background: transparent; border: none;"
STYLE_SUG_TXT = f"color: {COLORS['text_primary']}; background: transparent; border: none;"

# --- CÁC STYLE BỔ SUNG CHO KHUNG ĐÍNH KÈM & Ô NHẬP LIỆU ---
STYLE_PREVIEW_CONTAINER = f"""
    QFrame {{
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }}
"""

STYLE_LOGO_PDF = """
    background-color: #FEE2E2;
    color: #EF4444;
    border-radius: 4px;
    font-weight: bold;
    border: none;
"""

STYLE_ATTACH_NAME = f"color: {COLORS['text_primary']}; border: none; background: transparent;"

STYLE_CANCEL_BTN = """
    QPushButton {
        background-color: transparent;
        color: #94A3B8;
        border: none;
    }
    QPushButton:hover {
        color: #EF4444;
    }
"""

STYLE_TEXT_INPUT = f"""
    QTextEdit {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: white;
        color: {COLORS['text_primary']};
        padding: 5px;
    }}
    QTextEdit:focus {{
        border-color: {COLORS['primary']};
    }}
"""

STYLE_ATTACH_BTN = f"""
    QPushButton {{
        background-color: {COLORS['hover']};
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: #E2E8F0;
        color: {COLORS['primary']};
    }}
"""

def STYLE_TOOL_BTN(bg_color):
    return f"""
        QPushButton {{
            background-color: {bg_color};
            border-radius: 8px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #E2E8F0;
        }}
    """