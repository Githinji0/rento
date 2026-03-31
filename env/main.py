import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QButtonGroup
)
from ui.dashboard import Dashboard
from ui.theme import MAIN_WINDOW_STYLE, NAV_BUTTON_STYLE
from database.db import initialize_database
from core.properties import PropertiesPage
from core.units import UnitsPage
from core.tenants import TenantsPage
from core.payments import PaymentsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        sidebar_title = QLabel("Rento")
        sidebar_title.setObjectName("sidebarTitle")
        sidebar.addWidget(sidebar_title)


        btn_dashboard = QPushButton("Dashboard")
        btn_properties = QPushButton("Properties")
        btn_units = QPushButton("Units")
        btn_tenants = QPushButton("Tenants")
        btn_payments = QPushButton("Payments")
        btn_reports = QPushButton("Reports")

        self.nav_buttons = [
            btn_dashboard,
            btn_properties,
            btn_units,
            btn_tenants,
            btn_payments,
            btn_reports,
        ]

        btn_group = QButtonGroup(self)
        btn_group.setExclusive(True)

        for btn in self.nav_buttons:
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_BUTTON_STYLE)
            btn.setFixedHeight(40)
            btn_group.addButton(btn)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        btn_dashboard.setChecked(True)

        # ===== Content Area =====
        self.stack = QStackedWidget()

        self.dashboard_page = Dashboard()
        self.stack.addWidget(self.dashboard_page)

        # Placeholder pages
        self.stack.addWidget(PropertiesPage())
        self.stack.addWidget(UnitsPage())
        self.stack.addWidget(TenantsPage())
        self.stack.addWidget(PaymentsPage())
        self.stack.addWidget(QLabel("Reports Page"))

        # ===== Navigation Logic =====
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_properties.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_units.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tenants.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_payments.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_reports.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        # Add layouts
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stack, 4)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
