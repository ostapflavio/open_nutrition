# styles.py
from PyQt6.QtWidgets import QFrame

# -----------------------------------------------------------------------------
# Color palette (requested)
#   rgb(85, 107, 47)   - Dark green
#   rgb(143, 163, 30)  - Medium green  
#   rgb(198, 216, 112) - Light green
#   rgb(239, 245, 210) - Very light green
#   Text colors:       black/white/grey where needed
# -----------------------------------------------------------------------------

PALETTE = {
    "dark_green": "rgb(85, 107, 47)",
    "medium_green": "rgb(143, 163, 30)",
    "light_green": "rgb(198, 216, 112)",
    "very_light_green": "rgb(239, 245, 210)",
    "white": "#FFFFFF",
    "black": "#000000",
    "grey_border": "#cfcfcf",
    "grey_bg": "#f4f4f4",
}

# App-wide base styles (apply to QApplication via setStyleSheet)
APP_STYLE = f"""
/* Base background and text */
QWidget {{
    background: #DCCFC0;
    color: {PALETTE["black"]};
    font-size: 14px;
}}

/* Headings can be bold by widgets; labels default color */
QLabel {{ color: {PALETTE["black"]}; }}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QTableWidget, QListWidget {{
    background: {PALETTE["white"]};
    border: 1px solid {PALETTE["grey_border"]};
    border-radius: 6px;
}}

/* Ensure viewports are white inside boxes */
QListWidget::viewport, QTableView::viewport, QTableWidget::viewport {{
    background: {PALETTE["white"]};
}}

/* Splitter handle subtle */
QSplitter::handle {{ background: #e9e9e9; }}
"""

# Primary action button (uses dark green, with medium green hover/pressed)
GREEN_BTN_STYLE = f"""
QPushButton {{
    background: {PALETTE["dark_green"]};
    color: {PALETTE["white"]};
    font-size: 15px;
    font-weight: 600;
    padding: 10px 22px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{ background: {PALETTE["medium_green"]}; }}
QPushButton:pressed {{ background: {PALETTE["light_green"]}; color: {PALETTE["black"]}; }}
QPushButton:disabled {{ background: {PALETTE["light_green"]}; color: {PALETTE["black"]}; }}
"""

# Compact variant for small icon-like buttons (e.g., list rows)
COMPACT_GREEN_BTN_STYLE = f"""
QPushButton {{
    background: {PALETTE["dark_green"]};
    color: {PALETTE["white"]};
    font-size: 14px;
    font-weight: 700;
    padding: 2px 6px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{ background: {PALETTE["medium_green"]}; }}
QPushButton:pressed {{ background: {PALETTE["light_green"]}; color: {PALETTE["black"]}; }}
"""

# Secondary/light button (uses very light green with light green border)
LIGHT_BTN_STYLE = f"""
QPushButton {{
    background: {PALETTE["very_light_green"]};
    color: {PALETTE["black"]};
    border: 1px solid {PALETTE["light_green"]};
    padding: 8px 18px;
    border-radius: 6px;
}}
QPushButton:hover {{ background: {PALETTE["light_green"]}; }}
QPushButton:pressed {{ background: {PALETTE["medium_green"]}; color: {PALETTE["white"]}; }}
"""

# Destructive button variant (uses dark green for consistency)
RED_BTN_STYLE = f"""
QPushButton {{
    background: {PALETTE["dark_green"]};
    color: {PALETTE["white"]};
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{ background: {PALETTE["medium_green"]}; }}
QPushButton:pressed {{ background: {PALETTE["light_green"]}; color: {PALETTE["black"]}; }}
"""

# Framed panels and boxes
PANEL_STYLE = f"""
QFrame#statPanel, QFrame#boxFrame {{
    background: {PALETTE["white"]};
    border: 1px solid {PALETTE["light_green"]};
    border-radius: 8px;
}}
/* Force all descendants inside panels to inherit white background */
QFrame#boxFrame *, QFrame#statPanel * {{
    background: {PALETTE["white"]};
}}
"""

class StatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statPanel")
        self.setStyleSheet(PANEL_STYLE)
