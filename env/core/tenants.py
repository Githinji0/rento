from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox,
    QComboBox, QDateEdit
)
from PySide6.QtCore import QDate

from database.db import (
    get_tenants,
    add_tenant,
    update_tenant,
    delete_tenant,
    get_unit_list,
)
from ui.theme import (
    DANGER_BUTTON_STYLE,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class TenantsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(PAGE_STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ===== Title =====
        title = QLabel("Tenants Management")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone",
            "Email", "Unit", "Move-In", "Deposit"
        ])
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self.load_selected)

        # ===== Form =====
        form_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.unit_combo = QComboBox()
        self.load_units()

        self.move_in_input = QDateEdit()
        self.move_in_input.setCalendarPopup(True)
        self.move_in_input.setDate(QDate.currentDate())

        self.deposit_input = QLineEdit()
        self.deposit_input.setPlaceholderText("Deposit Amount")

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.email_input)
        assigned_unit_label = QLabel("Assigned Unit")
        assigned_unit_label.setObjectName("fieldLabel")
        form_layout.addWidget(assigned_unit_label)
        form_layout.addWidget(self.unit_combo)
        move_in_label = QLabel("Move-In Date")
        move_in_label.setObjectName("fieldLabel")
        form_layout.addWidget(move_in_label)
        form_layout.addWidget(self.move_in_input)
        form_layout.addWidget(self.deposit_input)

        layout.addLayout(form_layout)

        # ===== Buttons =====
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add")
        self.update_btn = QPushButton("✏️ Update")
        self.delete_btn = QPushButton("🗑️ Delete")
        self.clear_btn = QPushButton("🔄 Clear")

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
        self.add_btn.clicked.connect(self.add_tenant)
        self.update_btn.clicked.connect(self.update_tenant)
        self.delete_btn.clicked.connect(self.delete_tenant)
        self.clear_btn.clicked.connect(self.clear_form)

        self.selected_id = None

        self.load_data()

    # =============================
    # Load Units into Combo
    # =============================
    def load_units(self):
        self.unit_combo.clear()
        self.units = get_unit_list()

        for unit_id, unit_no in self.units:
            self.unit_combo.addItem(unit_no, unit_id)

    # =============================
    # Load Table Data
    # =============================
    def load_data(self):
        data = get_tenants()
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

            self.name_input.setText(self.table.item(selected, 1).text())
            self.phone_input.setText(self.table.item(selected, 2).text())
            self.email_input.setText(self.table.item(selected, 3).text())
            self.deposit_input.setText(self.table.item(selected, 6).text())

            unit_name = self.table.item(selected, 4).text()
            index = self.unit_combo.findText(unit_name)
            if index >= 0:
                self.unit_combo.setCurrentIndex(index)

    # =============================
    # Add Tenant
    # =============================
    def add_tenant(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        unit_id = self.unit_combo.currentData()
        move_in = self.move_in_input.date().toString("yyyy-MM-dd")
        deposit = self.deposit_input.text()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required")
            return

        add_tenant(name, phone, email, unit_id, move_in, float(deposit or 0))
        self.load_data()
        self.clear_form()

    # =============================
    # Update Tenant
    # =============================
    def update_tenant(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a tenant first")
            return

        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        unit_id = self.unit_combo.currentData()
        move_in = self.move_in_input.date().toString("yyyy-MM-dd")
        deposit = self.deposit_input.text()

        update_tenant(
            self.selected_id,
            name, phone, email,
            unit_id, move_in,
            float(deposit or 0)
        )

        self.load_data()

    # =============================
    # Delete Tenant
    # =============================
    def delete_tenant(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Error", "Select a tenant first")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Delete this tenant?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            delete_tenant(self.selected_id)
            self.load_data()
            self.clear_form()

    # =============================
    # Clear Form
    # =============================
    def clear_form(self):
        self.selected_id = None
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.deposit_input.clear()
        self.move_in_input.setDate(QDate.currentDate())