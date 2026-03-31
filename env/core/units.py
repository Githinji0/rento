from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QComboBox
)

from database.db import (
    get_units,
    add_unit,
    update_unit,
    delete_unit,
    get_property_list,
)
from ui.theme import (
    DANGER_BUTTON_STYLE,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class UnitsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(PAGE_STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ===== Title =====
        title = QLabel(" Units Management")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Unit No.", "Rent", "Status"]
        )
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self.load_selected)

        # ===== Form =====
        form_layout = QVBoxLayout()

        self.property_combo = QComboBox()
        self.load_properties()

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Unit Number")

        self.rent_input = QLineEdit()
        self.rent_input.setPlaceholderText("Rent Amount")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Vacant", "Occupied"])

        property_label = QLabel("Property")
        property_label.setObjectName("fieldLabel")
        form_layout.addWidget(property_label)
        form_layout.addWidget(self.property_combo)
        form_layout.addWidget(self.unit_input)
        form_layout.addWidget(self.rent_input)
        form_layout.addWidget(self.status_combo)

        layout.addLayout(form_layout)

        # ===== Buttons =====
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")

        self.add_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.update_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.delete_btn.setStyleSheet(DANGER_BUTTON_STYLE)
        self.clear_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ===== Events =====
        self.add_btn.clicked.connect(self.add_unit)
        self.update_btn.clicked.connect(self.update_unit)
        self.delete_btn.clicked.connect(self.delete_unit)
        self.clear_btn.clicked.connect(self.clear_form)

        self.selected_id = None

        self.load_data()

    # =============================
    # Load Properties into Combo
    # =============================
    def load_properties(self):
        self.property_combo.clear()
        self.properties = get_property_list()

        for prop_id, name in self.properties:
            self.property_combo.addItem(name, prop_id)

    # =============================
    # Load Units Table
    # =============================
    def load_data(self):
        data = get_units()
        self.table.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

    # =============================
    # Load Selected Row
    # =============================
    def load_selected(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.selected_id = int(self.table.item(selected, 0).text())

            property_name = self.table.item(selected, 1).text()
            unit_no = self.table.item(selected, 2).text()
            rent = self.table.item(selected, 3).text()
            status = self.table.item(selected, 4).text()

            self.unit_input.setText(unit_no)
            self.rent_input.setText(rent)
            self.status_combo.setCurrentText(status)

            index = self.property_combo.findText(property_name)
            if index >= 0:
                self.property_combo.setCurrentIndex(index)

    # =============================
    # Add Unit
    # =============================
    def add_unit(self):
        property_id = self.property_combo.currentData()
        unit_no = self.unit_input.text()
        rent = self.rent_input.text()
        status = self.status_combo.currentText()

        if not unit_no or not rent:
            QMessageBox.warning(self, "Error", "Fill all fields")
            return

        add_unit(property_id, unit_no, float(rent), status)
        self.load_data()
        self.clear_form()

    # =============================
    # Update Unit
    # =============================
    def update_unit(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a unit first")
            return

        property_id = self.property_combo.currentData()
        unit_no = self.unit_input.text()
        rent = self.rent_input.text()
        status = self.status_combo.currentText()

        update_unit(
            self.selected_id,
            property_id,
            unit_no,
            float(rent),
            status,
        )

        self.load_data()

    # =============================
    # Delete Unit
    # =============================
    def delete_unit(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a unit first")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Delete this unit?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            delete_unit(self.selected_id)
            self.load_data()
            self.clear_form()

    # =============================
    # Clear Form
    # =============================
    def clear_form(self):
        self.selected_id = None
        self.unit_input.clear()
        self.rent_input.clear()
        self.status_combo.setCurrentIndex(0)