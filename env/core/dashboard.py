from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton
from database import (
    count_properties,
    count_units,
    count_occupied_units,
    count_vacant_units,
    count_tenants,
    total_income,
    total_arrears,
)


class StatCard(QLabel):
    def __init__(self, title, value):
        super().__init__()

        self.setText(f"{title}\n\n{value}")
        self.setStyleSheet("""
            background-color: #1e1e2f;
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-size: 16px;
        """)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        title = QLabel("📊 Dashboard Overview")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(title)

        # Grid Layout
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)

        # Refresh Button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_stats)
        self.layout.addWidget(refresh_btn)

        self.setLayout(self.layout)

        self.load_stats()

    def load_stats(self):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        stats = [
            ("Properties", count_properties()),
            ("Units", count_units()),
            ("Occupied", count_occupied_units()),
            ("Vacant", count_vacant_units()),
            ("Tenants", count_tenants()),
            ("Income (KES)", total_income()),
            ("Arrears (KES)", total_arrears()),
        ]

        row = 0
        col = 0

        for title, value in stats:
            card = StatCard(title, value)
            self.grid.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1