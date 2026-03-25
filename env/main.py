import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget
)
from env.ui.dashboard import Dashboard
from env.database.db import initialize_database

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
