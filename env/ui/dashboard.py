from datetime import datetime

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
from PySide6.QtWidgets import (
    QBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database.db import (
    count_occupied_units,
    count_properties,
    count_units,
    count_vacant_units,
    get_current_month_key,
    get_dashboard_monthly_snapshot,
    get_monthly_income,
    total_arrears,
    total_income,
    upsert_dashboard_monthly_snapshot,
)
from ui.theme import (
    CARD_BORDER,
    GREEN_100,
    GREEN_200,
    GREEN_300,
    GREEN_700,
    GREEN_900,
    PRIMARY_BUTTON_STYLE,
    TEXT_MAIN,
    TEXT_MUTED,
    WHITE,
)


class MetricCard(QWidget):
    def __init__(self, heading):
        super().__init__()

        self.setObjectName("metricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        self.heading = QLabel(heading)
        self.heading.setObjectName("metricHeading")

        self.value = QLabel("--")
        self.value.setObjectName("metricValue")

        self.trend = QLabel("-")
        self.trend.setObjectName("metricTrend")

        layout.addWidget(self.heading)
        layout.addWidget(self.value)
        layout.addWidget(self.trend)
        layout.addStretch()

    def update(self, value_text, trend_text, trend_positive=True):
        self.value.setText(value_text)
        self.trend.setText(trend_text)
        trend_color = GREEN_700 if trend_positive else "#d32f2f"
        self.trend.setStyleSheet(f"color: {trend_color};")


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)
        root.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: {WHITE};
                color: {TEXT_MAIN};
            }}
            QLabel#title {{
                font-size: 26px;
                font-weight: 700;
                color: {GREEN_900};
                margin-bottom: 4px;
            }}
            QWidget#metricCard {{
                background: {GREEN_100};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            QLabel#metricHeading {{
                font-size: 14px;
                color: {TEXT_MUTED};
                font-weight: 600;
            }}
            QLabel#metricValue {{
                font-size: 38px;
                font-weight: 700;
                color: {TEXT_MAIN};
            }}
            QLabel#metricTrend {{
                font-size: 15px;
                font-weight: 600;
            }}
            QWidget#graphCard {{
                background: {WHITE};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            QLabel#graphTitle {{
                font-size: 20px;
                font-weight: 700;
                color: {GREEN_900};
            }}
            QLabel#graphSubtitle {{
                font-size: 14px;
                color: {TEXT_MUTED};
            }}
            QPushButton {{
                min-height: 38px;
            }}
            """
        )

        title_row = QHBoxLayout()

        title = QLabel("Dashboard")
        title.setObjectName("title")
        title_row.addWidget(title)
        title_row.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_data)
        title_row.addWidget(refresh_btn)

        self.cards = {
            "properties": MetricCard("Properties"),
            "units": MetricCard("Total Units"),
            "occupied": MetricCard("Occupied"),
            "vacant": MetricCard("Vacant"),
            "income": MetricCard("Income"),
            "arrears": MetricCard("Arrears"),
        }

        cards_grid = QGridLayout()
        cards_grid.setHorizontalSpacing(12)
        cards_grid.setVerticalSpacing(12)
        cards_grid.addWidget(self.cards["properties"], 0, 0)
        cards_grid.addWidget(self.cards["units"], 0, 1)
        cards_grid.addWidget(self.cards["occupied"], 1, 0)
        cards_grid.addWidget(self.cards["vacant"], 1, 1)
        cards_grid.addWidget(self.cards["income"], 2, 0)
        cards_grid.addWidget(self.cards["arrears"], 2, 1)

        self.occupancy_chart = QChartView()
        self.occupancy_chart.setRenderHint(QPainter.Antialiasing)
        self.occupancy_chart.setStyleSheet("border: none; background: transparent;")

        self.finance_chart = QChartView()
        self.finance_chart.setRenderHint(QPainter.Antialiasing)
        self.finance_chart.setStyleSheet("border: none; background: transparent;")

        self.occupancy_container = QWidget()
        self.occupancy_container.setObjectName("graphCard")
        self.occupancy_container.setMinimumHeight(330)
        self.occupancy_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        occupancy_layout = QVBoxLayout(self.occupancy_container)
        occupancy_layout.setContentsMargins(16, 14, 16, 10)
        occupancy_layout.setSpacing(4)

        occupancy_title = QLabel("Unit Occupancy")
        occupancy_title.setObjectName("graphTitle")
        self.occupancy_subtitle = QLabel("-")
        self.occupancy_subtitle.setObjectName("graphSubtitle")
        occupancy_layout.addWidget(occupancy_title)
        occupancy_layout.addWidget(self.occupancy_subtitle)
        self.occupancy_chart.setMinimumHeight(250)
        occupancy_layout.addWidget(self.occupancy_chart, 1)

        self.finance_container = QWidget()
        self.finance_container.setObjectName("graphCard")
        self.finance_container.setMinimumHeight(330)
        self.finance_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        finance_layout = QVBoxLayout(self.finance_container)
        finance_layout.setContentsMargins(16, 14, 16, 10)
        finance_layout.setSpacing(4)

        finance_title = QLabel("Finance Snapshot")
        finance_title.setObjectName("graphTitle")
        self.finance_subtitle = QLabel("-")
        self.finance_subtitle.setObjectName("graphSubtitle")
        finance_layout.addWidget(finance_title)
        finance_layout.addWidget(self.finance_subtitle)
        self.finance_chart.setMinimumHeight(250)
        finance_layout.addWidget(self.finance_chart, 1)

        self.charts_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.charts_layout.setSpacing(12)
        self.charts_layout.addWidget(self.occupancy_container)
        self.charts_layout.addWidget(self.finance_container)

        root.addLayout(title_row)
        root.addLayout(cards_grid)
        root.addLayout(self.charts_layout)

        self._update_responsive_layout()
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        if self.width() < 1080:
            direction = QBoxLayout.Direction.TopToBottom
        else:
            direction = QBoxLayout.Direction.LeftToRight

        if self.charts_layout.direction() != direction:
            self.charts_layout.setDirection(direction)

    @staticmethod
    def _previous_month_key(month_key):
        current = datetime.strptime(month_key + "-01", "%Y-%m-%d")
        if current.month == 1:
            return f"{current.year - 1}-12"
        return f"{current.year}-{current.month - 1:02d}"

    @staticmethod
    def _format_trend(current_value, previous_value, lower_is_better=False):
        if previous_value is None:
            return "No previous month record", True

        delta = current_value - previous_value
        if previous_value == 0:
            if current_value == 0:
                return "No change vs last month", True
            sign = "+" if delta >= 0 else ""
            is_good = delta <= 0 if lower_is_better else delta >= 0
            return f"{sign}{delta:,.0f} vs last month", is_good

        pct = (delta / previous_value) * 100
        sign = "+" if pct >= 0 else ""
        is_good = delta <= 0 if lower_is_better else delta >= 0
        return f"{sign}{pct:.1f}% vs last month", is_good

    def load_data(self):
        properties = count_properties()
        units = count_units()
        occupied = count_occupied_units()
        vacant = count_vacant_units()
        income = total_income()
        arrears = total_arrears()
        month_key = get_current_month_key()
        previous_month = self._previous_month_key(month_key)
        previous_snapshot = get_dashboard_monthly_snapshot(previous_month)

        current_month_income = get_monthly_income(month_key)
        previous_month_income = get_monthly_income(previous_month)

        upsert_dashboard_monthly_snapshot(
            month_key,
            properties,
            units,
            occupied,
            vacant,
            arrears,
        )

        occupancy_rate = (occupied / units * 100) if units else 0
        vacancy_rate = 100 - occupancy_rate if units else 0

        properties_prev = previous_snapshot["properties"] if previous_snapshot else None
        units_prev = previous_snapshot["units"] if previous_snapshot else None
        occupied_prev = previous_snapshot["occupied"] if previous_snapshot else None
        vacant_prev = previous_snapshot["vacant"] if previous_snapshot else None
        arrears_prev = previous_snapshot["arrears"] if previous_snapshot else None

        properties_trend = self._format_trend(properties, properties_prev)
        units_trend = self._format_trend(units, units_prev)
        occupied_trend = self._format_trend(occupied, occupied_prev)
        vacant_trend = self._format_trend(vacant, vacant_prev, lower_is_better=True)
        income_trend = self._format_trend(current_month_income, previous_month_income)
        arrears_trend = self._format_trend(arrears, arrears_prev, lower_is_better=True)

        self.cards["properties"].update(str(properties), properties_trend[0], properties_trend[1])
        self.cards["units"].update(str(units), units_trend[0], units_trend[1])
        self.cards["occupied"].update(str(occupied), occupied_trend[0], occupied_trend[1])
        self.cards["vacant"].update(str(vacant), vacant_trend[0], vacant_trend[1])
        self.cards["income"].update(f"KES {income:,.0f}", income_trend[0], income_trend[1])
        self.cards["arrears"].update(f"KES {arrears:,.0f}", arrears_trend[0], arrears_trend[1])

        self.occupancy_subtitle.setText(
            f"{occupied} of {units} units occupied ({occupancy_rate:.0f}%)"
        )
        self.finance_subtitle.setText(
            f"Monthly income KES {current_month_income:,.0f} | Outstanding arrears KES {arrears:,.0f}"
        )

        occupancy_series = QPieSeries()
        occupancy_series.setHoleSize(0.4)
        has_occupancy_data = units > 0

        if has_occupancy_data:
            occupancy_series.append("Occupied", occupied)
            occupancy_series.append("Vacant", vacant)
        else:
            occupancy_series.append("No Units", 1)
            self.occupancy_subtitle.setText("No unit occupancy data available yet")

        for pie_slice in occupancy_series.slices():
            pie_slice.setLabelVisible(has_occupancy_data)
            pie_slice.setLabelColor(QColor(TEXT_MAIN))
            pie_slice.setBorderColor(QColor(WHITE))
            pie_slice.setBorderWidth(1)

        slices = occupancy_series.slices()
        if len(slices) == 2:
            slices[0].setColor(QColor(GREEN_700))
            slices[1].setColor(QColor(GREEN_300))
        elif len(slices) == 1:
            slices[0].setColor(QColor(GREEN_200))

        occupancy_chart = QChart()
        occupancy_chart.addSeries(occupancy_series)
        occupancy_chart.setTitle("")
        occupancy_chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        occupancy_chart.setTitleBrush(QColor(GREEN_900))
        occupancy_chart.setBackgroundBrush(QColor(WHITE))
        occupancy_chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        occupancy_chart.setPlotAreaBackgroundVisible(True)
        occupancy_chart.legend().setVisible(has_occupancy_data)
        occupancy_chart.legend().setAlignment(Qt.AlignBottom)
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
        bar_series.setBarWidth(0.55)

        finance_chart = QChart()
        finance_chart.addSeries(bar_series)
        finance_chart.setTitle("")
        finance_chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        finance_chart.setTitleBrush(QColor(GREEN_900))
        finance_chart.setBackgroundBrush(QColor(WHITE))
        finance_chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        finance_chart.setPlotAreaBackgroundVisible(True)
        finance_chart.legend().setVisible(False)
        finance_chart.setAnimationOptions(QChart.SeriesAnimations)

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
