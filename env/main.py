import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QButtonGroup
)
from ui.dashboard import Dashboard
from ui.theme import MAIN_WINDOW_STYLE, NAV_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from database.db import get_active_user_profile, get_auth_user_by_id, initialize_database
from core.auth import AuthWindow
from core.properties import PropertiesPage
from core.units import UnitsPage
from core.tenants import TenantsPage
from core.payments import PaymentsPage
from core.reports import ReportsPage
from core.profile import ProfilePage
from utils.permissions import can_access_page, get_permissions_for_role, normalize_role
from utils.session import SessionManager

class MainWindow(QMainWindow):
    def __init__(self, session_manager, on_logout=None):
        super().__init__()
        self.session_manager = session_manager
        self.on_logout = on_logout
        self._logout_in_progress = False
        self.current_role = normalize_role(self.session_manager.current_user.get("role"))
        self.permissions = get_permissions_for_role(self.current_role)
        self.setWindowTitle("Rent Management System")
        self.resize(1180, 760)
        self.setStyleSheet(MAIN_WINDOW_STYLE)


        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(12, 12, 12, 12)
        sidebar.setSpacing(8)

        self.sidebar_title = QLabel("Rento")
        self.sidebar_title.setObjectName("sidebarTitle")
        sidebar.addWidget(self.sidebar_title)

        self.sidebar_subtitle = QLabel("System")
        self.sidebar_subtitle.setObjectName("sidebarSubtitle")
        sidebar.addWidget(self.sidebar_subtitle)

        self.role_badge = QLabel("Current role: Viewer")
        self.role_badge.setObjectName("roleBadge")
        sidebar.addWidget(self.role_badge)


        btn_dashboard = QPushButton("Dashboard")
        btn_properties = QPushButton("Properties")
        btn_units = QPushButton("Units")
        btn_tenants = QPushButton("Tenants")
        btn_payments = QPushButton("Payments")
        btn_reports = QPushButton("Reports")
        btn_profile = QPushButton("Profile")

        self.nav_buttons = [
            btn_dashboard,
            btn_properties,
            btn_units,
            btn_tenants,
            btn_payments,
            btn_reports,
            btn_profile,
        ]
        self.nav_by_page = {
            "dashboard": btn_dashboard,
            "properties": btn_properties,
            "units": btn_units,
            "tenants": btn_tenants,
            "payments": btn_payments,
            "reports": btn_reports,
            "profile": btn_profile,
        }

        btn_group = QButtonGroup(self)
        btn_group.setExclusive(True)

        for btn in self.nav_buttons:
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setFixedHeight(40)
            btn_group.addButton(btn)
            sidebar.addWidget(btn)

        sidebar.addStretch()

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.logout_btn.setFixedHeight(38)
        self.logout_btn.clicked.connect(self.handle_logout)
        sidebar.addWidget(self.logout_btn)

        btn_dashboard.setChecked(True)

        # ===== Content Area =====
        self.stack = QStackedWidget()

        self.dashboard_page = Dashboard()
        self.stack.addWidget(self.dashboard_page)

        self.stack.addWidget(
            PropertiesPage(can_edit=self.permissions["edit_properties"])
        )
        self.stack.addWidget(UnitsPage(can_edit=self.permissions["edit_units"]))
        self.stack.addWidget(TenantsPage(can_edit=self.permissions["edit_tenants"]))
        self.stack.addWidget(PaymentsPage(can_edit=self.permissions["edit_payments"]))
        self.stack.addWidget(ReportsPage(can_export=self.permissions["export_reports"]))
        self.profile_page = ProfilePage(self.session_manager.current_user)
        self.stack.addWidget(self.profile_page)
        self.profile_page.profile_changed.connect(self.update_sidebar_profile_header)

        # ===== Navigation Logic =====
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_properties.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_units.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tenants.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_payments.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_reports.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        btn_profile.clicked.connect(lambda: self.stack.setCurrentIndex(6))

        self.apply_navigation_permissions()

        self.update_sidebar_profile_header()

        # Add layouts
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stack, 4)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def update_sidebar_profile_header(self):
        if self.session_manager.is_authenticated():
            user = self.session_manager.current_user
            row = get_auth_user_by_id(user.get("id"))
            if row:
                _, full_name, username, email, role, _ = row
                self.session_manager.current_user.update(
                    {
                        "full_name": full_name,
                        "username": username,
                        "email": email,
                        "role": role,
                    }
                )
                self.sidebar_title.setText(full_name or "Rento")
                self.sidebar_subtitle.setText(role or "Authenticated")
                self.role_badge.setText(
                    f"Current role: {normalize_role(role).capitalize()}"
                )
                return

            self.sidebar_title.setText(user.get("full_name") or "Rento")
            self.sidebar_subtitle.setText(user.get("role") or "Authenticated")
            self.role_badge.setText(
                f"Current role: {normalize_role(user.get('role')).capitalize()}"
            )
            return

        profile = get_active_user_profile()
        if not profile:
            self.sidebar_title.setText("Rento")
            self.sidebar_subtitle.setText("No active profile")
            self.role_badge.setText("Current role: Viewer")
            return

        _, full_name, _, _, role, _ = profile
        self.sidebar_title.setText(full_name or "Rento")
        self.sidebar_subtitle.setText(role or "Active user")
        self.role_badge.setText(f"Current role: {normalize_role(role).capitalize()}")

    def closeEvent(self, event):
        if not self._logout_in_progress:
            self.session_manager.logout()
        super().closeEvent(event)

    def handle_logout(self):
        self._logout_in_progress = True
        self.session_manager.logout()
        self.close()

        if self.on_logout:
            self.on_logout()

    def apply_navigation_permissions(self):
        for page_key, button in self.nav_by_page.items():
            allowed = can_access_page(self.current_role, page_key)
            button.setEnabled(allowed)
            if not allowed:
                button.setToolTip("Your role does not have access to this page")

        if not can_access_page(self.current_role, "dashboard"):
            for page_key, button in self.nav_by_page.items():
                if button.isEnabled():
                    button.click()
                    break


if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)
    session_manager = SessionManager()
    auth_window = AuthWindow()
    auth_window.setWindowFlag(Qt.WindowMinMaxButtonsHint, False)
    auth_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    state = {"main_window": None}

    def show_auth_window():
        auth_window.login_password.clear()
        auth_window.show()
        auth_window.raise_()
        auth_window.activateWindow()

    def on_authenticated(user_data):
        session_manager.login(user_data)
        auth_window.hide()
        main_window = MainWindow(session_manager, on_logout=show_auth_window)
        state["main_window"] = main_window
        main_window.show()

    auth_window.authenticated.connect(on_authenticated)
    auth_window.show()

    sys.exit(app.exec())
