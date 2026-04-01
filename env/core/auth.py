import sqlite3

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from database.db import create_auth_user, get_auth_user_by_identifier
from ui.theme import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from utils.security import hash_password, verify_password


class AuthWindow(QWidget):
    authenticated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rento Login")
        self.resize(460, 420)

        self.setStyleSheet(
            """
            QWidget { background: #ffffff; color: #17351f; font-size: 13px; }
            QLabel#title { font-size: 24px; font-weight: 700; color: #0f3d1e; }
            QLabel#subtitle { color: #2f5a3d; }
            QLineEdit, QComboBox {
                border: 1px solid #d7ead9;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #2e8b57; }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        self.stack = QStackedWidget()
        self.login_page = self._build_login_page()
        self.register_page = self._build_register_page()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)

        root.addWidget(self.stack)

    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Welcome Back")
        title.setObjectName("title")
        subtitle = QLabel("Sign in to continue")
        subtitle.setObjectName("subtitle")

        self.login_identifier = QLineEdit()
        self.login_identifier.setPlaceholderText("Username or email")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        login_btn.clicked.connect(self.handle_login)

        switch_btn = QPushButton("Create account")
        switch_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        switch_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.login_identifier)
        layout.addWidget(self.login_password)
        layout.addSpacing(8)
        layout.addWidget(login_btn)
        layout.addWidget(switch_btn)
        layout.addStretch()

        return page

    def _build_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Create Account")
        title.setObjectName("title")
        subtitle = QLabel("Register a new user profile")
        subtitle.setObjectName("subtitle")

        self.reg_full_name = QLineEdit()
        self.reg_username = QLineEdit()
        self.reg_email = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_confirm = QLineEdit()
        self.reg_role = QComboBox()

        self.reg_full_name.setPlaceholderText("Full name")
        self.reg_username.setPlaceholderText("Username")
        self.reg_email.setPlaceholderText("Email")
        self.reg_password.setPlaceholderText("Password")
        self.reg_confirm.setPlaceholderText("Confirm password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_role.addItems(["admin", "manager", "viewer"])

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Full name", self.reg_full_name)
        form.addRow("Username", self.reg_username)
        form.addRow("Email", self.reg_email)
        form.addRow("Password", self.reg_password)
        form.addRow("Confirm", self.reg_confirm)
        form.addRow("Role", self.reg_role)

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        register_btn.clicked.connect(self.handle_register)

        back_btn = QPushButton("Back to login")
        back_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addWidget(register_btn)
        actions.addWidget(back_btn)
        layout.addLayout(actions)
        layout.addStretch()

        return page

    def handle_login(self):
        identifier = self.login_identifier.text().strip()
        password = self.login_password.text()

        if not identifier or not password:
            QMessageBox.warning(self, "Validation", "Enter username/email and password")
            return

        user = get_auth_user_by_identifier(identifier)
        if not user:
            QMessageBox.warning(self, "Login", "Invalid credentials")
            return

        user_id, full_name, username, email, pwd_hash, pwd_salt, role, is_enabled = user
        if not is_enabled:
            QMessageBox.warning(self, "Login", "This account is disabled")
            return

        if not verify_password(password, pwd_hash, pwd_salt):
            QMessageBox.warning(self, "Login", "Invalid credentials")
            return

        self.authenticated.emit(
            {
                "id": user_id,
                "full_name": full_name,
                "username": username,
                "email": email,
                "role": role,
            }
        )

    def handle_register(self):
        full_name = self.reg_full_name.text().strip()
        username = self.reg_username.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        role = self.reg_role.currentText()

        if not full_name or not username or not email or not password:
            QMessageBox.warning(self, "Validation", "All fields are required")
            return

        if password != confirm:
            QMessageBox.warning(self, "Validation", "Passwords do not match")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Validation", "Password must be at least 8 characters")
            return

        pwd_hash, pwd_salt = hash_password(password)

        try:
            create_auth_user(full_name, username, email, pwd_hash, pwd_salt, role)
            QMessageBox.information(self, "Registration", "Account created successfully")
            self.reg_full_name.clear()
            self.reg_username.clear()
            self.reg_email.clear()
            self.reg_password.clear()
            self.reg_confirm.clear()
            self.reg_role.setCurrentIndex(1)
            self.stack.setCurrentIndex(0)
            self.login_identifier.setText(username)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Registration",
                "Username or email already exists",
            )
