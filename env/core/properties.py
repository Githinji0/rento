from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QTextEdit, QLabel, QMessageBox
)

from database.db import (
    get_properties,
    add_property,
    update_property,
    delete_property,
)
from ui.theme import (
    DANGER_BUTTON_STYLE,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class PropertiesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(PAGE_STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ===== Title =====
        title = QLabel("🏢 Properties Management")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Address", "Description"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self.load_selected)

        # ===== Form =====
        form_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Property Name")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.desc_input)

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

        # ===== Button Events =====
        self.add_btn.clicked.connect(self.add_property)
        self.update_btn.clicked.connect(self.update_property)
        self.delete_btn.clicked.connect(self.delete_property)
        self.clear_btn.clicked.connect(self.clear_form)

        self.selected_id = None

        self.load_data()

    # =============================
    # Load Table Data
    # =============================
    def load_data(self):
        data = get_properties()
        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(value))
                )

    # =============================
    # Load Selected Row
    # =============================
    def load_selected(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.selected_id = int(self.table.item(selected, 0).text())
            self.name_input.setText(self.table.item(selected, 1).text())
            self.address_input.setText(self.table.item(selected, 2).text())
            self.desc_input.setText(self.table.item(selected, 3).text())

    # =============================
    # Add Property
    # =============================
    def add_property(self):
        name = self.name_input.text()
        address = self.address_input.text()
        desc = self.desc_input.toPlainText()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required")
            return

        add_property(name, address, desc)
        self.load_data()
        self.clear_form()

    # =============================
    # Update Property
    # =============================
    def update_property(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a property first")
            return

        name = self.name_input.text()
        address = self.address_input.text()
        desc = self.desc_input.toPlainText()

        update_property(self.selected_id, name, address, desc)
        self.load_data()

    # =============================
    # Delete Property
    # =============================
    def delete_property(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a property first")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Delete this property?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            delete_property(self.selected_id)
            self.load_data()
            self.clear_form()

    # =============================
    # Clear Form
    # =============================
    def clear_form(self):
        self.selected_id = None
        self.name_input.clear()
        self.address_input.clear()
        self.desc_input.clear()