import sys

from PySide6.QtCore import QDate, QRectF, Qt
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPen, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QDateEdit,
    QGraphicsDropShadowEffect,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


PRIMARY = "#4C96F5"
PRIMARY_HOVER = "#357FE0"
PRIMARY_LIGHT = "#EAF2FF"
PRIMARY_SOFT = "#DBEAFE"
BG = "#FFFFFF"
BORDER = "#D8E0EE"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748B"
TEXT_MUTED = "#CBD5E1"
SUNDAY = "#EF4444"
HEADER_BG = "#F8FAFC"


class StyledCalendar(QCalendarWidget):
    """Bảng lịch (Calendar) được tùy chỉnh giao diện hiện đại, sạch sẽ."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.setNavigationBarVisible(True)
        self.setFirstDayOfWeek(Qt.Monday)
        self.setFixedSize(370, 340)
        self.setFont(QFont("Segoe UI", 10))
        self.setMouseTracking(True)
        self.setStyleSheet(self._style_sheet())
        self._apply_header_formats()
        self._style_navigation_buttons()
        self._apply_shadow()

    def paintCell(self, painter, rect, date):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        cell_rect = QRectF(rect).adjusted(5, 4, -5, -4)
        is_selected = date == self.selectedDate()
        is_today = date == QDate.currentDate()
        is_outside_month = date.month() != self.monthShown()
        is_saturday = date.dayOfWeek() == 6
        is_sunday = date.dayOfWeek() == 7
        is_hovered = cell_rect.contains(self.mapFromGlobal(QCursor.pos()))

        if is_selected:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(PRIMARY))
            painter.drawRoundedRect(cell_rect, 8, 8)
        elif is_today:
            painter.setPen(QPen(QColor(PRIMARY), 1.2))
            painter.setBrush(QColor(PRIMARY_LIGHT))
            painter.drawRoundedRect(cell_rect, 8, 8)
        elif is_hovered and not is_outside_month:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(PRIMARY_LIGHT))
            painter.drawRoundedRect(cell_rect, 8, 8)

        if is_selected:
            text_color = QColor("#FFFFFF")
        elif is_outside_month:
            text_color = QColor(TEXT_MUTED)
        elif is_sunday:
            text_color = QColor(SUNDAY)
        elif is_saturday:
            text_color = QColor(PRIMARY)
        else:
            text_color = QColor(TEXT_PRIMARY)

        font = QFont("Segoe UI", 10)
        if is_selected or is_today:
            font.setWeight(QFont.Bold)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(cell_rect, Qt.AlignCenter, str(date.day()))
        painter.restore()

    def mouseMoveEvent(self, event):
        self.updateCells()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.updateCells()
        super().leaveEvent(event)

    def _apply_header_formats(self):
        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(TEXT_SECONDARY))
        weekday_format.setBackground(QColor(HEADER_BG))
        weekday_format.setFont(QFont("Segoe UI", 9, QFont.DemiBold))

        saturday_format = QTextCharFormat(weekday_format)
        saturday_format.setForeground(QColor(PRIMARY))

        sunday_format = QTextCharFormat(weekday_format)
        sunday_format.setForeground(QColor(SUNDAY))

        for day in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday):
            self.setWeekdayTextFormat(day, weekday_format)
        self.setWeekdayTextFormat(Qt.Saturday, saturday_format)
        self.setWeekdayTextFormat(Qt.Sunday, sunday_format)

    def _style_navigation_buttons(self):
        prev_button = self.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.findChild(QToolButton, "qt_calendar_nextmonth")

        if prev_button:
            prev_button.setText("<")
            prev_button.setCursor(Qt.PointingHandCursor)
            prev_button.setStyleSheet(self._arrow_button_style())
        if next_button:
            next_button.setText(">")
            next_button.setCursor(Qt.PointingHandCursor)
            next_button.setStyleSheet(self._arrow_button_style())

    def _arrow_button_style(self):
        """Định nghĩa style CSS cho các nút mũi tên chuyển tháng trên lịch."""
        return f"""
            QToolButton {{
                qproperty-icon: none;
                color: #111827;
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-family: "Segoe UI";
                font-size: 16px;
                font-weight: 800;
            }}
            QToolButton:hover {{
                color: #111827;
                background-color: {PRIMARY_SOFT};
                border-color: {PRIMARY};
            }}
            QToolButton:pressed {{
                color: #111827;
                background-color: {PRIMARY_LIGHT};
                border-color: {PRIMARY};
            }}
        """

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(17, 24, 39, 34))
        self.setGraphicsEffect(shadow)

    def _style_sheet(self):
        return f"""
            QCalendarWidget {{
                background-color: {BG};
                border: 1px solid {BORDER};
                border-radius: 12px;
                color: {TEXT_PRIMARY};
                font-family: "Segoe UI";
            }}

            QCalendarWidget QWidget {{
                background-color: {BG};
                alternate-background-color: {HEADER_BG};
                color: {TEXT_PRIMARY};
                font-family: "Segoe UI";
                selection-background-color: {PRIMARY};
                selection-color: #FFFFFF;
            }}

            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {PRIMARY_LIGHT};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid {BORDER};
                padding: 4px;
            }}

            QCalendarWidget QToolButton {{
                height: 32px;
                min-width: 34px;
                margin: 6px 4px;
                padding: 0 8px;
                color: {PRIMARY};
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-family: "Segoe UI";
                font-size: 14px;
                font-weight: 700;
            }}

            QCalendarWidget QToolButton:hover {{
                background-color: {PRIMARY_SOFT};
                color: {PRIMARY_HOVER};
                border-color: {PRIMARY};
            }}

            QCalendarWidget QToolButton:pressed {{
                background-color: {PRIMARY};
                color: #FFFFFF;
            }}

            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {{
                min-width: 94px;
                color: {TEXT_PRIMARY};
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-weight: 700;
            }}

            QCalendarWidget QToolButton#qt_calendar_monthbutton:hover,
            QCalendarWidget QToolButton#qt_calendar_yearbutton:hover {{
                background-color: #FFFFFF;
                color: {PRIMARY_HOVER};
                border: 1px solid {BORDER};
            }}

            QCalendarWidget QMenu {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 6px;
            }}

            QCalendarWidget QMenu::item {{
                padding: 7px 18px;
                border-radius: 6px;
            }}

            QCalendarWidget QMenu::item:selected {{
                background-color: {PRIMARY_LIGHT};
                color: {TEXT_PRIMARY};
            }}

            QCalendarWidget QSpinBox {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY};
                selection-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 4px 8px;
                min-width: 72px;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: 700;
            }}

            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button {{
                width: 0px;
                border: none;
            }}

            QCalendarWidget QAbstractItemView {{
                background-color: #FFFFFF;
                alternate-background-color: {HEADER_BG};
                color: {TEXT_PRIMARY};
                border: none;
                outline: 0;
                padding: 8px;
                font-family: "Segoe UI";
                font-size: 13px;
                selection-background-color: transparent;
                selection-color: {TEXT_PRIMARY};
            }}

            QCalendarWidget QAbstractItemView:enabled {{
                color: {TEXT_PRIMARY};
                selection-background-color: transparent;
                selection-color: {TEXT_PRIMARY};
            }}

            QCalendarWidget QAbstractItemView:focus {{
                outline: 0;
                border: none;
            }}

            QCalendarWidget QAbstractItemView:disabled {{
                color: {TEXT_MUTED};
                background-color: #FFFFFF;
                selection-background-color: #FFFFFF;
                selection-color: {TEXT_MUTED};
            }}
        """


def create_date_edit(parent=None):
    """Hàm tiện ích tạo ra một ô nhập ngày (QDateEdit) đã được gắn bảng lịch StyledCalendar."""
    date_edit = QDateEdit(parent)
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat("dd/MM/yyyy")
    date_edit.setFixedHeight(40)
    # Gắn bảng lịch đã tùy chỉnh vào ô nhập
    date_edit.setCalendarWidget(StyledCalendar(date_edit))
    date_edit.setDate(QDate.currentDate())
    
    # Lấy đường dẫn tuyệt đối đến icon lịch
    import os
    base_dir = os.path.dirname(os.path.dirname(__file__)) # → app/FE
    icon_path = os.path.join(base_dir, "assets", "calendar_black.png").replace("\\", "/")

    date_edit.setStyleSheet(f"""
        QDateEdit {{
            background-color: #FFFFFF;
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 0 12px;
            padding-right: 34px;
            font-family: "Segoe UI";
            font-size: 13px;
            selection-background-color: {PRIMARY};
            selection-color: #FFFFFF;
        }}
        QDateEdit:focus {{
            border: 1px solid {PRIMARY};
        }}
        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left-style: none;
        }}
        QDateEdit::down-arrow {{
            image: url({icon_path});
            width: 16px;
            height: 16px;
        }}
    """)
    return date_edit


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Styled Calendar Test")
    window.resize(460, 160)
    window.setStyleSheet("QWidget { background-color: #F5F7FB; }")

    layout = QVBoxLayout(window)
    layout.setContentsMargins(32, 32, 32, 32)
    layout.addWidget(create_date_edit(window))
    layout.addStretch()

    window.show()
    sys.exit(app.exec())
