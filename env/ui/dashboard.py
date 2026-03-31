from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QPieSeries,
    QValueAxis,
)
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from database.db import (
    count_occupied_units,
    count_properties,
    count_units,
    count_vacant_units,
    total_arrears,
    total_income,
)
from ui.theme import (
    CARD_BORDER,
    GREEN_100,
    GREEN_200,
    GREEN_600,
    GREEN_700,
    GREEN_900,
    PRIMARY_BUTTON_STYLE,
    TEXT_MAIN,
    TEXT_MUTED,
    WHITE,
)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: {WHITE};
                color: {TEXT_MAIN};
            }}
            QLabel#title {{
                font-size: 28px;
                font-weight: 700;
                color: {GREEN_900};
                margin-bottom: 2px;
            }}
            QLabel#stats {{
                background: {GREEN_100};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
                padding: 14px;
                font-size: 14px;
                color: {TEXT_MUTED};
                line-height: 1.4;
            }}
            QPushButton {{
                min-height: 38px;
            }}
            """
        )

        title = QLabel("Rent Management Dashboard")
        title.setObjectName("title")

        self.stats = QLabel()
        self.stats.setObjectName("stats")

        self.occupancy_chart = QChartView()
        self.occupancy_chart.setRenderHint(QPainter.Antialiasing)
        self.occupancy_chart.setStyleSheet(
            f"background: {WHITE}; border: 1px solid {CARD_BORDER}; border-radius: 12px;"
        )

        self.finance_chart = QChartView()
        self.finance_chart.setRenderHint(QPainter.Antialiasing)
        self.finance_chart.setStyleSheet(
            f"background: {WHITE}; border: 1px solid {CARD_BORDER}; border-radius: 12px;"
        )

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(14)
        charts_layout.addWidget(self.occupancy_chart)
        charts_layout.addWidget(self.finance_chart)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_data)

        layout.addWidget(title)
        layout.addWidget(self.stats)
        layout.addLayout(charts_layout)
        layout.addWidget(refresh_btn)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        properties = count_properties()
        units = count_units()
        occupied = count_occupied_units()
        vacant = count_vacant_units()
        income = total_income()
        arrears = total_arrears()

        self.stats.setText(
            "\n".join(
                [
                    f"Total Properties: {properties}",
                    f"Total Units: {units}",
                    f"Occupied Units: {occupied}",
                    f"Vacant Units: {vacant}",
                    f"Total Income: KES {income:,.2f}",
                    f"Total Arrears: KES {arrears:,.2f}",
                ]
            )
        )

        occupancy_series = QPieSeries()
        if units > 0:
            occupancy_series.append("Occupied", occupied)
            occupancy_series.append("Vacant", vacant)
        else:
            occupancy_series.append("No Units", 1)

        for pie_slice in occupancy_series.slices():
            pie_slice.setLabelVisible(True)
            pie_slice.setLabelColor(QColor(TEXT_MAIN))
            pie_slice.setBorderColor(QColor(WHITE))
            pie_slice.setBorderWidth(1)

        slices = occupancy_series.slices()
        if len(slices) == 2:
            slices[0].setColor(QColor(GREEN_700))
            slices[1].setColor(QColor(GREEN_200))
        elif len(slices) == 1:
            slices[0].setColor(QColor(GREEN_200))

        occupancy_chart = QChart()
        occupancy_chart.addSeries(occupancy_series)
        occupancy_chart.setTitle("Unit Occupancy")
        occupancy_chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        occupancy_chart.setTitleBrush(QColor(GREEN_900))
        occupancy_chart.setBackgroundBrush(QColor(WHITE))
        occupancy_chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        occupancy_chart.setPlotAreaBackgroundVisible(True)
        occupancy_chart.legend().setVisible(True)
        occupancy_chart.legend().setLabelColor(QColor(TEXT_MUTED))
        occupancy_chart.legend().setFont(QFont("Segoe UI", 9))
        self.occupancy_chart.setChart(occupancy_chart)

        bar_set = QBarSet("KES")
        bar_set.append(max(income, 0))
        bar_set.append(max(arrears, 0))
        bar_set.setColor(QColor(GREEN_700))
        bar_set.setBorderColor(QColor(GREEN_900))

        bar_series = QBarSeries()
        bar_series.append(bar_set)

        finance_chart = QChart()
        finance_chart.addSeries(bar_series)
        finance_chart.setTitle("Financial Overview")
        finance_chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        finance_chart.setTitleBrush(QColor(GREEN_900))
        finance_chart.setBackgroundBrush(QColor(WHITE))
        finance_chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        finance_chart.setPlotAreaBackgroundVisible(True)
        finance_chart.legend().setVisible(False)

        categories = ["Income", "Arrears"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsColor(QColor(TEXT_MUTED))
        axis_x.setGridLineVisible(False)
        axis_x.setLinePen(QPen(QColor(GREEN_200), 1))
        finance_chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setRange(0, max(income, arrears, 1) * 1.2)
        axis_y.setLabelsColor(QColor(TEXT_MUTED))
        axis_y.setGridLineColor(QColor(GREEN_200))
        axis_y.setLinePen(QPen(QColor(GREEN_200), 1))
        finance_chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        self.finance_chart.setChart(finance_chart)