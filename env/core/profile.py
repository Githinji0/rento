from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.db import (
    add_user_profile,
    delete_user_profile,
    get_auth_user_by_id,
    get_user_profiles,
    set_active_user_profile,
    update_auth_user_self,
    update_user_profile,
)
from ui.theme import (
    DANGER_BUTTON_STYLE,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class ProfilePage(QWidget):
    profile_changed = Signal()

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.is_admin = bool(
            current_user and current_user.get("role", "").lower() == "admin"
        )
        self.setStyleSheet(PAGE_STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        title = QLabel("User Profiles")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Role", "Active"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.load_selected)
        root.addWidget(self.table)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Role")

        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Bio")
        self.bio_input.setFixedHeight(80)

        self.active_check = QCheckBox("Set as active profile")

        form = QVBoxLayout()
        form.setSpacing(8)
        form.addWidget(self.name_input)
        form.addWidget(self.email_input)
        form.addWidget(self.phone_input)
        form.addWidget(self.role_input)
        form.addWidget(self.bio_input)
        form.addWidget(self.active_check)
        root.addLayout(form)

        buttons = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.update_btn = QPushButton("Update")
        self.update_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.activate_btn = QPushButton("Set Active")
        self.activate_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(DANGER_BUTTON_STYLE)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)

        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.update_btn)
        buttons.addWidget(self.activate_btn)
        buttons.addWidget(self.delete_btn)
        buttons.addWidget(self.clear_btn)

        root.addLayout(buttons)

        self.add_btn.clicked.connect(self.add_profile)
        self.update_btn.clicked.connect(self.update_profile)
        self.activate_btn.clicked.connect(self.activate_profile)
        self.delete_btn.clicked.connect(self.delete_profile)
        self.clear_btn.clicked.connect(self.clear_form)

        self.selected_id = None
        self._profiles_by_id = {}

        if self.is_admin:
            self.load_data()
        else:
            self._configure_non_admin_view()
            self._load_current_user_details()

    def _configure_non_admin_view(self):
        self.table.hide()
        self.add_btn.hide()
        self.delete_btn.hide()
        self.activate_btn.hide()
        self.clear_btn.hide()
        self.active_check.hide()

        self.update_btn.setText("Save My Details")
        self.phone_input.setReadOnly(True)
        self.bio_input.setReadOnly(True)
        self.role_input.setReadOnly(True)

        self.phone_input.setPlaceholderText("Username")
        self.bio_input.setPlaceholderText("Account status")

    def _load_current_user_details(self):
        if not self.current_user:
            return

        row = get_auth_user_by_id(self.current_user.get("id"))
        if not row:
            return

        user_id, full_name, username, email, role, is_enabled = row
        self.selected_id = user_id
        self.name_input.setText(full_name or "")
        self.email_input.setText(email or "")
        self.phone_input.setText(username or "")
        self.role_input.setText(role or "")
        self.bio_input.setText("Enabled" if is_enabled else "Disabled")

    def load_data(self):
        rows = get_user_profiles()
        self._profiles_by_id = {row[0]: row for row in rows}

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            profile_id, full_name, email, _, role, _, is_active = row
            values = [
                str(profile_id),
                full_name,
                email or "",
                role or "",
                "Yes" if is_active else "No",
            ]
            for c, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

    def load_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        profile_id = int(self.table.item(selected, 0).text())
        profile = self._profiles_by_id.get(profile_id)
        if not profile:
            return

        _, full_name, email, phone, role, bio, is_active = profile
        self.selected_id = profile_id
        self.name_input.setText(full_name or "")
        self.email_input.setText(email or "")
        self.phone_input.setText(phone or "")
        self.role_input.setText(role or "")
        self.bio_input.setText(bio or "")
        self.active_check.setChecked(bool(is_active))

    def _validate(self):
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        role = self.role_input.text().strip()
        bio = self.bio_input.toPlainText().strip()
        is_active = self.active_check.isChecked()

        if not full_name:
            QMessageBox.warning(self, "Validation", "Full Name is required")
            return None

        return full_name, email, phone, role, bio, is_active

    def add_profile(self):
        data = self._validate()
        if not data:
            return

        try:
            add_user_profile(*data)
            self.load_data()
            self.clear_form()
            self.profile_changed.emit()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not add profile:\n{error}")

    def update_profile(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Validation", "Select a profile first")
            return

        if not self.is_admin:
            full_name = self.name_input.text().strip()
            email = self.email_input.text().strip()

            if not full_name or not email:
                QMessageBox.warning(
                    self,
                    "Validation",
                    "Name and email are required",
                )
                return

            try:
                update_auth_user_self(self.selected_id, full_name, email)
                self.profile_changed.emit()
                QMessageBox.information(
                    self,
                    "Profile",
                    "Your details were updated successfully",
                )
            except Exception as error:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not update profile:\n{error}",
                )
            return

        data = self._validate()
        if not data:
            return

        try:
            update_user_profile(self.selected_id, *data)
            self.load_data()
            self.profile_changed.emit()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not update profile:\n{error}")

    def activate_profile(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Validation", "Select a profile first")
            return

        set_active_user_profile(self.selected_id)
        self.load_data()
        self.active_check.setChecked(True)
        self.profile_changed.emit()

    def delete_profile(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Validation", "Select a profile first")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "Delete this profile?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            delete_user_profile(self.selected_id)
            self.load_data()
            self.clear_form()
            self.profile_changed.emit()

    def clear_form(self):
        self.selected_id = None
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.role_input.clear()
        self.bio_input.clear()
        self.active_check.setChecked(False)
        self.table.clearSelection()
