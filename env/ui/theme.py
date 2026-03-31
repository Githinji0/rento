WHITE = "#ffffff"
GREEN_900 = "#0f3d1e"
GREEN_700 = "#1f7a3a"
GREEN_600 = "#2e8b57"
GREEN_300 = "#a5d6a7"
GREEN_200 = "#c8e6c9"
GREEN_100 = "#e8f5e9"
TEXT_MAIN = "#17351f"
TEXT_MUTED = "#2f5a3d"
CARD_BORDER = "#d7ead9"

PAGE_STYLESHEET = f"""
QWidget {{
    background: {WHITE};
    color: {TEXT_MAIN};
    font-size: 13px;
}}
QLabel#pageTitle {{
    font-size: 24px;
    font-weight: 700;
    color: {GREEN_900};
    padding-bottom: 4px;
}}
QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {TEXT_MUTED};
}}
QTableWidget {{
    background: {WHITE};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    gridline-color: {GREEN_100};
    selection-background-color: {GREEN_200};
    selection-color: {GREEN_900};
}}
QHeaderView::section {{
    background: {GREEN_100};
    color: {GREEN_900};
    border: none;
    border-bottom: 1px solid {CARD_BORDER};
    padding: 8px;
    font-weight: 600;
}}
QLineEdit, QTextEdit, QComboBox, QDateEdit {{
    background: {WHITE};
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 8px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 1px solid {GREEN_600};
}}
QAbstractSpinBox {{
    background: {WHITE};
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 6px;
}}
"""

PRIMARY_BUTTON_STYLE = f"""
QPushButton {{
    background: {GREEN_700};
    color: {WHITE};
    border: none;
    border-radius: 9px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {GREEN_600};
}}
QPushButton:pressed {{
    background: {GREEN_900};
}}
"""

DANGER_BUTTON_STYLE = f"""
QPushButton {{
    background: {GREEN_900};
    color: {WHITE};
    border: none;
    border-radius: 9px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {GREEN_700};
}}
QPushButton:pressed {{
    background: {TEXT_MAIN};
}}
"""

SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background: {GREEN_100};
    color: {GREEN_900};
    border: 1px solid {GREEN_300};
    border-radius: 9px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {GREEN_200};
}}
QPushButton:pressed {{
    background: {GREEN_300};
}}
"""

NAV_BUTTON_STYLE = f"""
QPushButton {{
    background: transparent;
    color: {GREEN_100};
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 10px 12px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: rgba(232, 245, 233, 0.18);
}}
QPushButton:checked {{
    background: {GREEN_200};
    color: {GREEN_900};
}}
"""

MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background: {WHITE};
}}
QWidget#sidebar {{
    background: {GREEN_900};
    border-radius: 12px;
}}
QLabel#sidebarTitle {{
    color: {GREEN_100};
    font-size: 18px;
    font-weight: 700;
    padding: 4px 2px 10px 2px;
}}
"""
