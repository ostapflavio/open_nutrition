# pages/history_page.py
from __future__ import annotations
from typing import Iterable, Sequence, Callable, TypedDict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QFrame, QListWidget, QListWidgetItem
)

# If styles.py is at project root and this file is in pages/, use relative import:
from styles import GREEN_BTN_STYLE, COMPACT_GREEN_BTN_STYLE, PANEL_STYLE

# ------------ Types for data you pass in ------------
class MealRow(TypedDict):
    name: str
    favorite: bool  # True if it's already in favorites (controls star state)

# One day = (date_label, [meals...])
HistoryDay = tuple[str, Sequence[MealRow]]


class HistoryPage(QWidget):
    """
    History list grouped by day.
    For each meal row:
        [ x ]  [ ⋮ ]  [ ★/☆ ]  MealName
         del   modify  fav
    Head of page has a '<' back button to Home.
    """
    def __init__(
        self,
        go_back: Callable[[], None],
        on_modify: Callable[[str], None],            # open New Meal page with this meal
        on_delete: Callable[[str, str], None],       # delete (date, meal_name)
        on_toggle_fav: Callable[[str, bool], None],  # (meal_name, new_state)
        initial_history: Iterable[HistoryDay] | None = None,
    ):
        super().__init__()
        self.setObjectName("historyPage")
        self.setStyleSheet(PANEL_STYLE)

        self._go_back = go_back
        self._on_modify = on_modify
        self._on_delete = on_delete
        self._on_toggle_fav = on_toggle_fav

        # ----- Header: back + centered title
        header = QHBoxLayout()
        back = QPushButton("<")
        back.setFixedWidth(48)
        back.setStyleSheet(GREEN_BTN_STYLE)
        back.clicked.connect(self._go_back)

        title = QLabel("History")
        f = QFont(); f.setPointSize(22); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        header.addWidget(title, 1)
        header.addItem(QSpacerItem(48, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # ----- Main box with the grouped days
        self.box = QFrame()
        self.box.setObjectName("boxFrame")
        self.box.setMinimumWidth(760)
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(12, 12, 12, 12)
        box_layout.setSpacing(10)

        # We’ll use a list widget to hold each Day section (custom widgets)
        self.day_list = QListWidget(self)
        self.day_list.setSpacing(10)
        box_layout.addWidget(self.day_list)

        # ----- Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(14)
        root.addLayout(header)
        root.addStretch(1)
        root.addWidget(self.box, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(2)

        if initial_history:
            self.set_history(initial_history)

        # keep reference to title for responsive font
        self._title = title

    # ------------------ Public API ------------------
    def set_history(self, days: Iterable[HistoryDay]):
        """Replace the whole list with `days`."""
        self.day_list.clear()
        for date_str, meals in days:
            self._add_day(date_str, meals)

    # ------------------ Internals -------------------
    def _add_day(self, date_str: str, meals: Sequence[MealRow]):
        """Add one 'day' section widget to the list."""
        item = QListWidgetItem()
        self.day_list.addItem(item)

        section = QFrame()
        section.setObjectName("boxFrame")  # reuse same framed look
        lay = QVBoxLayout(section)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        # Date header (underlined, centered)
        lbl = QLabel(date_str)
        df = QFont(); df.setBold(True)
        lbl.setFont(df)
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        lbl.setStyleSheet("QLabel { text-decoration: underline; }")
        lay.addWidget(lbl)

        # A thin separator line under the date
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        lay.addWidget(sep)

        # Rows
        for m in meals:
            lay.addWidget(self._meal_row(date_str, m["name"], m.get("favorite", False)))

        # Final spacer to mimic your mockup
        spacer = QSpacerItem(0, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        lay.addItem(spacer)

        # Size hint so the section shows fully
        item.setSizeHint(section.sizeHint())
        self.day_list.setItemWidget(item, section)

    def _meal_row(self, date_str: str, meal_name: str, favorite: bool):
        row_widget = QWidget()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(4, 0, 4, 0)
        row.setSpacing(6)

        # x = delete (left)
        btn_del = QPushButton("x")
        btn_del.setFixedWidth(28)
        btn_del.setStyleSheet(COMPACT_GREEN_BTN_STYLE)

        def handle_delete():
            self._on_delete(date_str, meal_name)
            row_widget.setParent(None)
            row_widget.deleteLater()

        btn_del.clicked.connect(handle_delete)

        # + = create/use (center)
        btn_use = QPushButton("+")
        btn_use.setFixedWidth(28)
        btn_use.setStyleSheet(COMPACT_GREEN_BTN_STYLE)
        btn_use.clicked.connect(lambda _=False, n=meal_name: self._on_modify(n))

        # ★ / ☆ = favorite toggle (right)
        star_char = "★" if favorite else "☆"
        btn_star = QPushButton(star_char)
        btn_star.setFixedWidth(28)
        btn_star.setStyleSheet(COMPACT_GREEN_BTN_STYLE)
        btn_star.setCheckable(True)
        btn_star.setChecked(favorite)

        def toggle_star(checked: bool):
            btn_star.setText("★" if checked else "☆")
            self._on_toggle_fav(meal_name, checked)

        btn_star.toggled.connect(toggle_star)

        name_lbl = QLabel(meal_name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        row.addWidget(btn_del, 0)
        row.addWidget(btn_use, 0)
        row.addWidget(btn_star, 0)
        row.addWidget(name_lbl, 1)

        return row_widget

    # Responsive title like your other pages
    def resizeEvent(self, e):
        w = self.width()
        size = max(22, w // 40)
        f = self._title.font()
        f.setPointSize(size)
        self._title.setFont(f)
        super().resizeEvent(e)
