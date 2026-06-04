from app.FE.config import COLORS

STYLE_PAGE = f"background-color: {COLORS['bg']};"

STYLE_SCROLL_AREA = "QScrollArea { border: none; background-color: transparent; }"

STYLE_SCROLL_CONTENT = "background-color: transparent;"

STYLE_DIVIDER = f"background-color: {COLORS['border']}; border: none;"

STYLE_CARD = f"""
    QFrame {{
        background-color: {COLORS['card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}
"""

def STYLE_BTN_EDIT(font_style):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            border-radius: 8px;
            {font_style}
        }}
        QPushButton:hover {{
            background-color: {COLORS['hover']};
        }}
    """

def STYLE_BTN_SAVE(font_style):
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: #FFFFFF;
            border-radius: 8px;
            border: none;
            {font_style}
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
    """

def STYLE_COMBO(font_style):
    return f"""
        QComboBox {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: transparent;
            color: {COLORS['text_primary']};
            padding: 4px 8px;
            padding-right: 26px;
            {font_style}
        }}
        QComboBox::drop-down {{
            width: 0px;
            border: none;
        }}
        QComboBox::down-arrow {{
            image: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: white;
            color: {COLORS['text_primary']};
            selection-background-color: {COLORS['hover']};
        }}
    """

def STYLE_LINE_EDIT(font_style):
    return f"""
        QLineEdit {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: transparent;
            color: {COLORS['text_primary']};
            padding: 4px 8px;
            {font_style}
        }}
    """

def STYLE_PW_LINE_EDIT(font_style):
    return STYLE_LINE_EDIT(font_style)

def STYLE_BTN_UPDATE(font_style):
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: #FFFFFF;
            border-radius: 8px;
            border: none;
            padding: 0 15px;
            {font_style}
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
    """

def STYLE_THEME_BTN_ACTIVE(font_style):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            border-radius: 8px;
            {font_style}
        }}
    """

def STYLE_THEME_BTN_INACTIVE(font_style):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            {font_style}
        }}
        QPushButton:hover {{ background-color: {COLORS['hover']}; }}
    """

def STYLE_NOTE(font_style):
    return f"""
        QLabel {{
            background-color: {COLORS['blue_light']};
            color: {COLORS['text_secondary']};
            border-radius: 8px;
            padding: 10px 12px;
            border: none;
            {font_style}
        }}
    """

def STYLE_NOTIF_ROW_COMBO(font_style):
    return f"""
        QComboBox {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: transparent;
            color: {COLORS['text_primary']};
            padding: 4px 26px 4px 8px;
            {font_style}
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

def STYLE_WARN(font_style):
    return f"""
        QLabel {{
            background-color: {COLORS['danger_bg']};
            color: {COLORS['danger']};
            border-radius: 8px;
            padding: 10px 12px;
            border: none;
            {font_style}
        }}
    """

def STYLE_BTN_DANGER(font_style):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['danger']};
            border: 2px solid {COLORS['danger']};
            border-radius: 8px;
            {font_style}
        }}
        QPushButton:hover {{
            background-color: {COLORS['danger_bg']};
        }}
    """