from app.FE.config import COLORS

STYLE_PAGE = f"background-color: {COLORS['bg']};"

STYLE_CARD_FRAME = f"""
    #card_frame {{
        background-color: {COLORS['card']};
        border: 2px solid {COLORS['border']};
        border-radius: 12px;
    }}
"""

STYLE_TRANSPARENT = "background: transparent;"

STYLE_LABEL_PRIMARY = f"color: {COLORS['text_primary']}; border: none;"
STYLE_LABEL_SECONDARY = f"color: {COLORS['text_secondary']}; border: none;"

STYLE_BTN_NAV = f"""
    QPushButton {{
        background-color: {COLORS['card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_BTN_ADD_SCHEDULE = f"""
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

STYLE_DAY_BTN_ACTIVE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 10px;
        text-align: center;
    }}
"""

STYLE_DAY_BTN_INACTIVE = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        border-radius: 10px;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_SCROLL = "QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }"

STYLE_MORE_LBL = f"color: {COLORS['text_secondary']}; font-size: 17px; border: none; font-weight: bold;"

STYLE_AI_HDR = f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;"
STYLE_AI_TITLE = "color: white; border: none; background: transparent;"

STYLE_BTN_AI = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['primary']};
        border: 1px solid {COLORS['primary']};
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

STYLE_STAT_HDR = f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;"
STYLE_STAT_TITLE = "color: white; border: none; background: transparent;"

STYLE_PROGRESS = f"""
    QProgressBar {{
        background-color: {COLORS['hover']};
        border: none;
        border-radius: 4px;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
        border-radius: 4px;
    }}
"""

STYLE_TASK_HDR = f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;"
STYLE_TASK_TITLE = "color: white; border: none; background: transparent;"

STYLE_BTN_ADD_TASK = """
    QPushButton {
        background-color: white;
        color: #111827;
        border-radius: 6px;
        border: none;
    }
    QPushButton:hover {
        background-color: #F3F4F6;
    }
"""

STYLE_CHECKBOX = f"""
    QCheckBox::indicator {{
        width: 15px;
        height: 15px;
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
    }}
"""

STYLE_BTN_ALL = f"""
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

STYLE_NOTIF_HDR = f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;"
STYLE_NOTIF_TITLE = "color: white; border: none; background: transparent;"

STYLE_BADGE = f"""
    background-color: {COLORS['danger']};
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    border: none;
"""