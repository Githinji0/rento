

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        title = QLabel("Rent Management Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        stats = QLabel(
                "Welcome!\n\n"
                "• Total Properties: --\n"
                "• Occupied Units: --\n"
                "• Vacant Units: --\n"
                "• Monthly Income: --"
            )
        layout.addWidget(title)
        layout.addWidget(stats)
        self.setLayout(layout)