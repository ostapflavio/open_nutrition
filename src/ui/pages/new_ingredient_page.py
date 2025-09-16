# pages/new_ingredient_page.py
from __future__ import annotations
from typing import Callable, Optional, TypedDict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QFrame, QGridLayout, QLineEdit, QDoubleSpinBox, QMessageBox
)

from styles import LIGHT_BTN_STYLE, GREEN_BTN_STYLE, PANEL_STYLE


class IngredientPayload(TypedDict):
    name: str
    proteins_per_100g: float
    fats_per_100g: float
    carbs_per_100g: float
    kcal_per_100g: float


class NewIngredientPage(QWidget):
    """
    Page to create a new ingredient:
      - '<' back button
      - Title 'New Ingredient'
      - Form with name + macros + kcal (per 100g)
      - 'Create' button -> on_create(payload)
    """
    def __init__(self, go_back: Callable[[], None], on_create: Callable[[IngredientPayload], None]):
        super().__init__()
        self.setObjectName("newIngredientPage")
        self.setStyleSheet(PANEL_STYLE)

        self._go_back = go_back
        self._on_create = on_create

        # ----- Header -----
        header = QHBoxLayout()
        back = QPushButton("<")
        back.setFixedWidth(48)
        back.setStyleSheet(GREEN_BTN_STYLE)
        back.clicked.connect(self._go_back)

        self.title = QLabel("New Ingredient")
        f = QFont(); f.setPointSize(22); f.setBold(True)
        self.title.setFont(f)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.title, 1)
        header.addItem(QSpacerItem(48, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # ----- Form box -----
        box = QFrame()
        box.setObjectName("boxFrame")
        form = QGridLayout(box)
        form.setContentsMargins(18, 18, 18, 18)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        # Name
        form.addWidget(QLabel("Name"), 0, 0)
        self.ed_name = QLineEdit()
        self.ed_name.setMinimumWidth(360)
        form.addWidget(self.ed_name, 0, 1, 1, 2)

        # Helpers to make spinboxes
        def spin(minv=0.0, maxv=5000.0, step=0.1) -> QDoubleSpinBox:
            s = QDoubleSpinBox()
            s.setRange(minv, maxv)
            s.setDecimals(2)
            s.setSingleStep(step)
            s.setAlignment(Qt.AlignmentFlag.AlignRight)
            s.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            s.setFixedWidth(120)
            return s

        # Proteins
        form.addWidget(QLabel("Proteins"), 1, 0)
        self.sp_prot = spin()
        form.addWidget(self.sp_prot, 1, 1)
        form.addWidget(QLabel("g per 100g"), 1, 2)

        # Fats
        form.addWidget(QLabel("Fats"), 2, 0)
        self.sp_fats = spin()
        form.addWidget(self.sp_fats, 2, 1)
        form.addWidget(QLabel("g per 100g"), 2, 2)

        # Carbohydrates
        form.addWidget(QLabel("Carbohydrates"), 3, 0)
        self.sp_carbs = spin()
        form.addWidget(self.sp_carbs, 3, 1)
        form.addWidget(QLabel("g per 100g"), 3, 2)

        # Kcal
        form.addWidget(QLabel("Kcal"), 4, 0)
        self.sp_kcal = spin(maxv=10000.0, step=1.0)
        form.addWidget(self.sp_kcal, 4, 1)
        form.addWidget(QLabel("per 100g"), 4, 2)

        # ----- Footer -----
        footer = QHBoxLayout()
        footer.addStretch(1)
        btn_create = QPushButton("Create")
        btn_create.setStyleSheet(GREEN_BTN_STYLE)
        btn_create.clicked.connect(self._submit)
        footer.addWidget(btn_create)

        # ----- Root layout -----
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 18, 26, 18)
        root.setSpacing(18)
        root.addLayout(header)
        root.addStretch(1)
        root.addWidget(box, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(2)
        root.addLayout(footer)

    # Public helpers -----------------------------------------------------------
    def clear_form(self):
        self.ed_name.clear()
        self.sp_prot.setValue(0.0)
        self.sp_fats.setValue(0.0)
        self.sp_carbs.setValue(0.0)
        self.sp_kcal.setValue(0.0)

    def prefill(self, name: str, proteins: float, fats: float, carbs: float, kcal: float):
        """Optional: reuse page for 'edit ingredient' later."""
        self.ed_name.setText(name)
        self.sp_prot.setValue(float(proteins))
        self.sp_fats.setValue(float(fats))
        self.sp_carbs.setValue(float(carbs))
        self.sp_kcal.setValue(float(kcal))

    # Internals ---------------------------------------------------------------
    def _submit(self):
        name = self.ed_name.text().strip()

        # Basic validation
        if not name:
            QMessageBox.warning(self, "Validation", "Please enter the ingredient name.")
            return

        payload: IngredientPayload = {
            "name": name,
            "proteins_per_100g": float(self.sp_prot.value()),
            "fats_per_100g": float(self.sp_fats.value()),
            "carbs_per_100g": float(self.sp_carbs.value()),
            "kcal_per_100g": float(self.sp_kcal.value()),
        }

        # Optional sanity check: macros shouldn't be absurdly high
        total_macros = payload["proteins_per_100g"] + payload["fats_per_100g"] + payload["carbs_per_100g"]
        if total_macros > 200:
            if QMessageBox.question(
                self, "Confirm",
                f"Total macros = {total_macros:.1f} g/100g. Continue?"
            ) != QMessageBox.StandardButton.Yes:
                return

        self._on_create(payload)

    # Responsive title like other pages
    def resizeEvent(self, e):
        w = self.width()
        size = max(22, w // 40)
        f = self.title.font()
        f.setPointSize(size)
        self.title.setFont(f)
        super().resizeEvent(e)
