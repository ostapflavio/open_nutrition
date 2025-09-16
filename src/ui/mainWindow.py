from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QFrame, QSizePolicy, QSpacerItem
)
import sys


class StatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statPanel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
            QFrame#statPanel {
                background: white;
                border: 1px solid #cfcfcf;
                border-radius: 6px;
            }
        """)


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HomePage")
        self.resize(900, 600)

        # ---- Titlu
        self.title = QLabel("HomePage")
        f = QFont()
        f.setPointSize(22)
        f.setBold(True)
        self.title.setFont(f)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # ---- Zona statistică
        left_panel = StatPanel()
        right_panel = StatPanel()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 300])
        splitter.setHandleWidth(2)

        # ---- Butoane
        button_style = """
            QPushButton {
                background: #4CAF50;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 28px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #45a049; }
            QPushButton:pressed { background: #3d8b40; }
        """

        btn_new = QPushButton("NewMeal")
        btn_fav = QPushButton("Favorite")
        btn_hist = QPushButton("History")
        btn_ing = QPushButton("Ingredients")

        for btn in (btn_new, btn_fav, btn_hist, btn_ing):
            btn.setStyleSheet(button_style)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(18)
        buttons_row.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        buttons_row.addWidget(btn_new)
        buttons_row.addWidget(btn_fav)
        buttons_row.addWidget(btn_hist)
        buttons_row.addWidget(btn_ing)
        buttons_row.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # ---- Layout principal
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(16)
        root.addWidget(self.title)
        root.addWidget(splitter, 2)
        root.addLayout(buttons_row)

        left_panel.setMinimumHeight(180)
        right_panel.setMinimumHeight(180)

    def resizeEvent(self, event):
        """Crește font-size la titlu în funcție de lățime."""
        width = self.width()
        new_size = max(22, width // 40)   # 22 minim, crește la ~ width/40
        f = self.title.font()
        f.setPointSize(new_size)
        self.title.setFont(f)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = HomePage()
    w.show()
    sys.exit(app.exec())
