from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox,
    QComboBox, QDateEdit
)
from PySide6.QtCore import QDate

from database.db import (
    get_payments,
    add_payment,
    delete_payment,
    get_tenant_list,
    get_tenant_rent,
    get_total_paid,
)
from ui.theme import (
    DANGER_BUTTON_STYLE,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class PaymentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(PAGE_STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ===== Title =====
        title = QLabel(" Payments Management")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tenant", "Amount", "Date", "Month"]
        )
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self.load_selected)

        # ===== Form =====
        form_layout = QVBoxLayout()

        self.tenant_combo = QComboBox()
        self.load_tenants()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.month_input = QLineEdit()
        self.month_input.setPlaceholderText("Month (e.g. 2026-03)")

        # Arrears label
        self.arrears_label = QLabel("Arrears: KES 0")

        tenant_label = QLabel("Tenant")
        tenant_label.setObjectName("fieldLabel")
        form_layout.addWidget(tenant_label)
        form_layout.addWidget(self.tenant_combo)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.date_input)
        form_layout.addWidget(self.month_input)
        form_layout.addWidget(self.arrears_label)

        self.arrears_label.setObjectName("fieldLabel")

        layout.addLayout(form_layout)

        # ===== Buttons =====
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton(" Add Payment")
        self.delete_btn = QPushButton(" Delete")
        self.refresh_btn = QPushButton(" Refresh")

        self.add_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.delete_btn.setStyleSheet(DANGER_BUTTON_STYLE)
        self.refresh_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ===== Events =====
        self.add_btn.clicked.connect(self.add_payment)
        self.delete_btn.clicked.connect(self.delete_payment)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.tenant_combo.currentIndexChanged.connect(self.update_arrears)

        self.selected_id = None

        self.load_data()
        self.update_arrears()

    # =============================
    # Load Tenants
    # =============================
    def load_tenants(self):
        self.tenant_combo.clear()
        self.tenants = get_tenant_list()

        for tenant_id, name in self.tenants:
            self.tenant_combo.addItem(name, tenant_id)

    # =============================
    # Load Payments
    # =============================
    def load_data(self):
        data = get_payments()
        self.table.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

    # =============================
    # Update Arrears
    # =============================
    def update_arrears(self):
        tenant_id = self.tenant_combo.currentData()

        if tenant_id:
            rent = get_tenant_rent(tenant_id)
            paid = get_total_paid(tenant_id)

            arrears = rent - paid
            self.arrears_label.setText(f"Arrears: KES {arrears:.2f}")

    # =============================
    # Add Payment
    # =============================
    def add_payment(self):
        tenant_id = self.tenant_combo.currentData()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")
        month = self.month_input.text()

        if not amount or not month:
            QMessageBox.warning(self, "Error", "Fill all fields")
            return

        add_payment(tenant_id, float(amount), date, month)
        self.load_data()
        self.update_arrears()
        self.amount_input.clear()
        self.month_input.clear()

    # =============================
    # Delete Payment
    # =============================
    def delete_payment(self):
        selected = self.table.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Error", "Select a payment")
            return

        payment_id = int(self.table.item(selected, 0).text())

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Delete this payment?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            delete_payment(payment_id)
            self.load_data()
            self.update_arrears()

    # =============================
    # Refresh
    # =============================
    def refresh_data(self):
        self.load_data()
        self.update_arrears()

    def load_selected(self):
        pass