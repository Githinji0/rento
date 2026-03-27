import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget
)
from ui.dashboard import Dashboard
from database.db import initialize_database
from core.properties import PropertiesPage
from core.units import UnitsPage
from core.tenants import TenantsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rent Management System")
        self.resize(800, 600)


        main_widget = QWidget()
        main_layout = QHBoxLayout()

        sidebar = QVBoxLayout()


        btn_dashboard = QPushButton("Dashboard")
        btn_properties = QPushButton("Properties")
        btn_units = QPushButton("Units")
        btn_tenants = QPushButton("Tenants")
        btn_payments = QPushButton("Payments")
        btn_reports = QPushButton("Reports")


        for btn in [
             btn_dashboard,
            btn_properties,
            btn_units,
            btn_tenants,
            btn_payments,
            btn_reports,
        ]:
            btn.setFixedHeight(40)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        # ===== Content Area =====
        self.stack = QStackedWidget()

        self.dashboard_page = Dashboard()
        self.stack.addWidget(self.dashboard_page)

        # Placeholder pages
        self.stack.addWidget(PropertiesPage())
        self.stack.addWidget(UnitsPage())
        self.stack.addWidget(TenantsPage())
        self.stack.addWidget(QLabel("Payments Page"))
        self.stack.addWidget(QLabel("Reports Page"))

        # ===== Navigation Logic =====
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_properties.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_units.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_tenants.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_payments.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_reports.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        # Add layouts
        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.stack, 4)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
