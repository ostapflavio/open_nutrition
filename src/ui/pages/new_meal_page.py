# pages/new_meal_page.py
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QLineEdit, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QSpinBox, QAbstractItemView, QFrame
)

from styles import GREEN_BTN_STYLE, LIGHT_BTN_STYLE, PANEL_STYLE

class NewMealPage(QWidget):
    """
    - Căutare ingrediente (mock) + buton cu icon
    - Listă rezultate (click -> adaugă în tabel)
    - Tabel: Nume | Grame | X
    - Butoane: < (back), Create
    """
    def __init__(self, go_back, on_create):
        super().__init__()
        self.setObjectName("newMealPage")
        self.setStyleSheet(PANEL_STYLE)
        self.resize(980, 650)

        self.db_ingredients = [
            "Chicken breast", "Salmon", "Egg", "Milk", "Rice", "Oats",
            "Almonds", "Olive oil", "Tomato", "Cucumber", "Avocado",
            "Banana", "Apple", "Broccoli", "Spinach", "Cheese", "Yogurt",
            "Beef", "Pork", "Potato", "Sweet potato", "Carrot", "Onion",
            "Garlic", "Pasta", "Quinoa", "Peanut butter", "Cottage cheese"
        ]

        # Header
        header_row = QHBoxLayout()
        self.btn_back = QPushButton("<")
        self.btn_back.setFixedWidth(48)
        self.btn_back.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_back.clicked.connect(go_back)

        self.title = QLabel("New Meal")
        tf = QFont(); tf.setPointSize(22); tf.setBold(True)
        self.title.setFont(tf)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        header_row.addWidget(self.btn_back, 0, Qt.AlignmentFlag.AlignLeft)
        header_row.addWidget(self.title, 1)
        header_row.addItem(QSpacerItem(48, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # Search
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type ingredient name...")
        self.search_edit.setMinimumWidth(320)
        self.search_edit.returnPressed.connect(self.perform_search)
        self.search_edit.textChanged.connect(self.live_filter)

        self.btn_search = QPushButton()
        self.btn_search.setToolTip("Search")
        self.btn_search.setIcon(QIcon("searchIcon.png"))  # pune fișierul lângă app.py
        self.btn_search.setIconSize(QSize(18, 18))
        self.btn_search.setFixedSize(38, 34)
        self.btn_search.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_search.clicked.connect(self.perform_search)

        search_row.addStretch(1)
        search_row.addWidget(self.search_edit)
        search_row.addWidget(self.btn_search)
        search_row.addStretch(1)

        # Results list
        self.results = QListWidget()
        self.results.setVisible(False)
        self.results.itemClicked.connect(self.add_result_to_table)
        self.results.setMaximumHeight(180)
        self.results.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Selected box
        self.box = QFrame()
        self.box.setObjectName("boxFrame")
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(12, 12, 12, 12)
        box_layout.setSpacing(8)

        box_label = QLabel("Selected ingredients")
        blf = QFont(); blf.setBold(True)
        box_label.setFont(blf)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ingredient name", "Grams", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setDefaultSectionSize(220)
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.setColumnWidth(0, 360)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 60)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        box_layout.addWidget(box_label)
        box_layout.addWidget(self.table)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.btn_create = QPushButton("Create")
        self.btn_create.setStyleSheet(GREEN_BTN_STYLE)
        self.btn_create.clicked.connect(lambda: on_create(self.collect_payload()))
        footer.addWidget(self.btn_create)

        # Root
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(14)
        root.addLayout(header_row)
        root.addLayout(search_row)
        root.addWidget(self.results)
        root.addWidget(self.box, 1)
        root.addLayout(footer)

    # --- logic ---
    def perform_search(self):
        text = self.search_edit.text().strip().lower()
        self.populate_results([x for x in self.db_ingredients if text in x.lower()])

    def live_filter(self, text):
        text = text.strip().lower()
        if not text:
            self.results.clear()
            self.results.setVisible(False)
            return
        matches = [x for x in self.db_ingredients if text in x.lower()]
        self.populate_results(matches)

    def populate_results(self, items):
        self.results.clear()
        for it in items:
            self.results.addItem(QListWidgetItem(it))
        self.results.setVisible(bool(items))

    def add_result_to_table(self, item: QListWidgetItem):
        name = item.text()
        self.results.setVisible(False)
        self.search_edit.clear()
        self.add_row(name)

    def add_row(self, name: str, grams: int = 0):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(name))

        spin = QSpinBox()
        spin.setRange(0, 10000)
        spin.setSingleStep(5)
        spin.setValue(grams)
        spin.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # Hide arrows so they don't overlap the number in tight cells
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        spin.setFixedHeight(26)
        spin.setStyleSheet("""
            QSpinBox {
                background: white;
                border: 1px solid #cfcfcf;
                border-radius: 6px;
                padding-right: 6px; /* breathing room for the text */
                padding-left: 6px;
            }
        """)
        self.table.setCellWidget(row, 1, spin)

        btn = QPushButton("x")
        btn.setFixedWidth(36)
        btn.setStyleSheet(GREEN_BTN_STYLE)
        btn.clicked.connect(lambda: self.remove_row(btn))
        self.table.setCellWidget(row, 2, btn)

    def remove_row(self, btn: QPushButton):
        for r in range(self.table.rowCount()):
            if self.table.cellWidget(r, 2) is btn:
                self.table.removeRow(r)
                break

    def collect_payload(self):
        data = []
        for r in range(self.table.rowCount()):
            name = self.table.item(r, 0).text()
            spin = self.table.cellWidget(r, 1)
            grams = int(spin.value()) if isinstance(spin, QSpinBox) else 0
            data.append({"name": name, "grams": grams})
        return data

    def resizeEvent(self, e):
        w = self.width()
        size = max(22, w // 40)
        f = self.title.font()
        f.setPointSize(size)
        self.title.setFont(f)
        super().resizeEvent(e)
