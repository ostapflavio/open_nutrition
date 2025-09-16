# pages/favorites_page.py
from typing import Iterable, Callable
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QFrame, QListWidget, QListWidgetItem
)

# Reuse your existing styles (no new colors)
from styles import GREEN_BTN_STYLE, COMPACT_GREEN_BTN_STYLE, PANEL_STYLE

class FavoritesPage(QWidget):
    """
    A simple favorites list:
      - Back button
      - Title 'Favorites'
      - Box with list of meals; each row has [ x ] [ + ] and the meal name
        x = delete favorite
        + = go to New Meal page (to use this favorite as a starting point)
    """
    def __init__(
        self,
        go_back: Callable[[], None],
        on_use_meal: Callable[[str], None],
        on_delete_meal: Callable[[str], None],
        initial_meals: Iterable[str] | None = None,
    ):
        super().__init__()
        self.setObjectName("favoritesPage")
        self.setStyleSheet(PANEL_STYLE)

        self._go_back = go_back
        self._on_use = on_use_meal
        self._on_delete = on_delete_meal

        # --- Header: back + centered title
        header = QHBoxLayout()
        self.btn_back = QPushButton("<")
        self.btn_back.setFixedWidth(48)
        self.btn_back.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_back.clicked.connect(self._go_back)

        self.title = QLabel("Favorites")
        tf = QFont(); tf.setPointSize(22); tf.setBold(True)
        self.title.setFont(tf)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(self.btn_back, 0, Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.title, 1)
        header.addItem(QSpacerItem(48, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # --- Box frame with list
        self.box = QFrame()
        self.box.setObjectName("boxFrame")
        self.box.setMinimumWidth(760)
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(12, 12, 12, 12)
        box_layout.setSpacing(8)

        self.list = QListWidget(self)
        self.list.setSpacing(6)  # little breathing room
        box_layout.addWidget(self.list)

        # --- Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(14)
        root.addLayout(header)
        root.addStretch(1)
        root.addWidget(self.box, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(2)

        # Optional initial data
        if initial_meals:
            self.set_meals(initial_meals)

    # Public API ---------------------------------------------------------------
    def set_meals(self, meals: Iterable[str]):
        """Replace list content with `meals`."""
        self.list.clear()
        for name in meals:
            self._add_row(name)

    def add_meal(self, name: str):
        """Append one meal row."""
        self._add_row(name)

    # Internals ----------------------------------------------------------------
    def _add_row(self, meal_name: str):
        item = QListWidgetItem()
        item.setSizeHint(item.sizeHint())  # allow custom widget sizing
        self.list.addItem(item)

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(6, 0, 6, 0)
        h.setSpacing(6)

        # Small buttons use LIGHT_BTN_STYLE so they stay compact
        btn_del = QPushButton("x")
        btn_del.setFixedWidth(28)
        btn_del.setStyleSheet(COMPACT_GREEN_BTN_STYLE)
        btn_del.clicked.connect(lambda _=False, n=meal_name: self._handle_delete(n))

        btn_use = QPushButton("+")
        btn_use.setFixedWidth(28)
        btn_use.setStyleSheet(COMPACT_GREEN_BTN_STYLE)
        btn_use.clicked.connect(lambda _=False, n=meal_name: self._handle_use(n))

        name_lbl = QLabel(meal_name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        h.addWidget(btn_del, 0)
        h.addWidget(btn_use, 0)
        h.addWidget(name_lbl, 1)

        self.list.setItemWidget(item, row)

    def _handle_delete(self, name: str):
        self._on_delete(name)
        # remove first matching row from UI
        for i in range(self.list.count()):
            w = self.list.itemWidget(self.list.item(i))
            if isinstance(w, QWidget):
                lbl: QLabel = w.findChild(QLabel)
                if lbl and lbl.text() == name:
                    self.list.takeItem(i)
                    break

    def _handle_use(self, name: str):
        # Navigate to New Meal page (caller decides what to prefill there)
        self._on_use(name)

    # Responsive title sizing (same as your other pages)
    def resizeEvent(self, e):
        w = self.width()
        size = max(22, w // 40)
        f = self.title.font()
        f.setPointSize(size)
        self.title.setFont(f)
        super().resizeEvent(e)
