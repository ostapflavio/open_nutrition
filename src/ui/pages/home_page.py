# pages/home_page.py
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QSplitter, QSizePolicy, QSpacerItem
)

from styles import GREEN_BTN_STYLE, PANEL_STYLE, StatPanel

class HomePage(QWidget):
    def __init__(self, goto_new_meal, goto_favorites, goto_history, goto_new_ingredient):
        super().__init__()
        self.setWindowTitle("HomePage")
        self.resize(980, 650)

        self.title = QLabel("HomePage")
        f = QFont(); f.setPointSize(22); f.setBold(True)
        self.title.setFont(f)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        left_panel = StatPanel()
        right_panel = StatPanel()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setHandleWidth(2)
        splitter.setSizes([400, 400])

        btn_new = QPushButton("NewMeal")
        btn_fav = QPushButton("Favorite")
        btn_hist = QPushButton("History")
        btn_ing = QPushButton("Ingredients")
        for b in (btn_new, btn_fav, btn_hist, btn_ing):
            b.setStyleSheet(GREEN_BTN_STYLE)

        btn_new.clicked.connect(goto_new_meal)
        btn_fav.clicked.connect(goto_favorites)
        btn_hist.clicked.connect(goto_history)
        btn_ing.clicked.connect(goto_new_ingredient)
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(14)
        buttons_row.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        buttons_row.addWidget(btn_new)
        buttons_row.addWidget(btn_fav)
        buttons_row.addWidget(btn_hist)
        buttons_row.addWidget(btn_ing)
        buttons_row.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 22)
        root.setSpacing(18)
        root.addWidget(self.title)
        root.addWidget(splitter, 2)
        root.addLayout(buttons_row)

    def resizeEvent(self, e):
        w = self.width()
        new_size = max(22, w // 40)
        f = self.title.font()
        f.setPointSize(new_size)
        self.title.setFont(f)
        super().resizeEvent(e)
