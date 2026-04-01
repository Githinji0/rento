import csv

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.db import (
    get_monthly_income_report,
    get_property_occupancy_report,
    get_tenant_arrears_report,
    total_arrears,
    total_income,
)
from ui.theme import (
    CARD_BORDER,
    GREEN_100,
    GREEN_200,
    GREEN_700,
    GREEN_900,
    PAGE_STYLESHEET,
    PRIMARY_BUTTON_STYLE,
    TEXT_MAIN,
    TEXT_MUTED,
    WHITE,
)


class ReportCard(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("reportCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        heading = QLabel(title)
        heading.setObjectName("reportCardTitle")
        self.value = QLabel("--")
        self.value.setObjectName("reportCardValue")

        layout.addWidget(heading)
        layout.addWidget(self.value)


class ReportsPage(QWidget):
    def __init__(self, can_export=True):
        super().__init__()
        self.can_export = can_export
        self.setStyleSheet(
            PAGE_STYLESHEET
            + f"""
            QWidget#reportCard {{
                background: {GREEN_100};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            QLabel#reportTitle {{
                font-size: 24px;
                font-weight: 700;
                color: {GREEN_900};
            }}
            QLabel#reportCardTitle {{
                font-size: 13px;
                font-weight: 600;
                color: {TEXT_MUTED};
            }}
            QLabel#reportCardValue {{
                font-size: 30px;
                font-weight: 700;
                color: {TEXT_MAIN};
            }}
            QWidget#chartCard {{
                background: {WHITE};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            QLabel#chartCardTitle {{
                font-size: 17px;
                font-weight: 700;
                color: {GREEN_900};
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Reports")
        title.setObjectName("reportTitle")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_data)
        header.addWidget(refresh_btn)

        export_btn = QPushButton("Export Arrears CSV")
        export_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        export_btn.clicked.connect(self.export_arrears_csv)
        export_btn.setEnabled(self.can_export)
        if not self.can_export:
            export_btn.setToolTip("Your role cannot export reports")
        header.addWidget(export_btn)

        self.income_card = ReportCard("Total Income")
        self.arrears_card = ReportCard("Total Arrears")
        self.active_tenants_card = ReportCard("Tenants In Arrears")

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(10)
        metrics.setVerticalSpacing(10)
        metrics.addWidget(self.income_card, 0, 0)
        metrics.addWidget(self.arrears_card, 0, 1)
        metrics.addWidget(self.active_tenants_card, 0, 2)

        self.income_chart_view = QChartView()
        self.income_chart_view.setRenderHint(QPainter.Antialiasing)
        self.income_chart_view.setMinimumHeight(260)
        self.income_chart_view.setStyleSheet("border:none; background: transparent;")

        self.occupancy_chart_view = QChartView()
        self.occupancy_chart_view.setRenderHint(QPainter.Antialiasing)
        self.occupancy_chart_view.setMinimumHeight(260)
        self.occupancy_chart_view.setStyleSheet("border:none; background: transparent;")

        income_card = QWidget()
        income_card.setObjectName("chartCard")
        income_card_layout = QVBoxLayout(income_card)
        income_card_layout.setContentsMargins(14, 12, 14, 10)
        income_card_layout.setSpacing(6)
        income_card_layout.addWidget(self._chart_title("Monthly Income (Last 6 Months)"))
        income_card_layout.addWidget(self.income_chart_view)

        occupancy_card = QWidget()
        occupancy_card.setObjectName("chartCard")
        occupancy_card_layout = QVBoxLayout(occupancy_card)
        occupancy_card_layout.setContentsMargins(14, 12, 14, 10)
        occupancy_card_layout.setSpacing(6)
        occupancy_card_layout.addWidget(self._chart_title("Occupancy By Property"))
        occupancy_card_layout.addWidget(self.occupancy_chart_view)

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)
        charts_layout.addWidget(income_card)
        charts_layout.addWidget(occupancy_card)

        self.arrears_table = QTableWidget()
        self.arrears_table.setColumnCount(5)
        self.arrears_table.setHorizontalHeaderLabels(
            ["Tenant", "Unit", "Rent", "Paid", "Arrears"]
        )
        self.arrears_table.horizontalHeader().setStretchLastSection(True)

        root.addLayout(header)
        root.addLayout(metrics)
        root.addLayout(charts_layout)
        root.addWidget(self._chart_title("Top Tenant Arrears"))
        root.addWidget(self.arrears_table)

        self.load_data()

    def _chart_title(self, text):
        title = QLabel(text)
        title.setObjectName("chartCardTitle")
        return title

    def load_data(self):
        monthly = get_monthly_income_report(6)
        occupancy = get_property_occupancy_report()
        arrears_rows = get_tenant_arrears_report(12)
        self.arrears_rows = arrears_rows

        total_income_value = total_income()
        total_arrears_value = total_arrears()
        tenants_in_arrears = sum(1 for row in arrears_rows if row[4] > 0)

        self.income_card.value.setText(f"KES {total_income_value:,.0f}")
        self.arrears_card.value.setText(f"KES {total_arrears_value:,.0f}")
        self.active_tenants_card.value.setText(str(tenants_in_arrears))

        self._populate_income_chart(monthly)
        self._populate_occupancy_chart(occupancy)
        self._populate_arrears_table(arrears_rows)

    def export_arrears_csv(self):
        if not self.can_export:
            QMessageBox.warning(self, "Access Denied", "You cannot export reports")
            return

        if not hasattr(self, "arrears_rows"):
            self.arrears_rows = get_tenant_arrears_report(12)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Arrears Report",
            "arrears_report.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Tenant", "Unit", "Rent", "Paid", "Arrears"])
                for tenant, unit, rent_amount, paid_amount, arrears in self.arrears_rows:
                    writer.writerow(
                        [
                            tenant,
                            unit,
                            f"{rent_amount:.2f}",
                            f"{paid_amount:.2f}",
                            f"{arrears:.2f}",
                        ]
                    )

            QMessageBox.information(self, "Export Complete", f"Saved CSV to:\n{file_path}")
        except OSError as error:
            QMessageBox.critical(self, "Export Failed", f"Could not save file:\n{error}")

    def _populate_income_chart(self, rows):
        labels = [month for month, _ in rows]
        values = [float(total) for _, total in rows]

        if not labels:
            labels = ["No Data"]
            values = [0]

        income_set = QBarSet("Income")
        for value in values:
            income_set.append(max(value, 0))
        income_set.setColor(QColor(GREEN_700))

        series = QBarSeries()
        series.append(income_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundBrush(QColor(WHITE))
        chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        chart.setPlotAreaBackgroundVisible(True)
        chart.legend().setVisible(False)

        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        axis_x.setLabelsColor(QColor(TEXT_MUTED))
        axis_x.setLinePen(QPen(QColor(GREEN_200), 1))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) * 1.2 if max(values) > 0 else 1)
        axis_y.setLabelFormat("%.0f")
        axis_y.setLabelsColor(QColor(TEXT_MUTED))
        axis_y.setGridLineColor(QColor(GREEN_200))
        axis_y.setLinePen(QPen(QColor(GREEN_200), 1))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.income_chart_view.setChart(chart)

    def _populate_occupancy_chart(self, rows):
        names = [name for name, _, _, total in rows if total > 0]
        occupied_values = [float(occupied) for _, occupied, _, total in rows if total > 0]
        vacant_values = [float(vacant) for _, _, vacant, total in rows if total > 0]

        if not names:
            names = ["No Properties"]
            occupied_values = [0]
            vacant_values = [0]

        occupied_set = QBarSet("Occupied")
        occupied_set.setColor(QColor(GREEN_700))
        for value in occupied_values:
            occupied_set.append(value)

        vacant_set = QBarSet("Vacant")
        vacant_set.setColor(QColor(GREEN_200))
        for value in vacant_values:
            vacant_set.append(value)

        series = QBarSeries()
        series.append(occupied_set)
        series.append(vacant_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundBrush(QColor(WHITE))
        chart.setPlotAreaBackgroundBrush(QColor(WHITE))
        chart.setPlotAreaBackgroundVisible(True)
        chart.legend().setVisible(True)
        chart.legend().setLabelColor(QColor(TEXT_MUTED))
        chart.legend().setFont(QFont("Segoe UI", 9))

        axis_x = QBarCategoryAxis()
        axis_x.append(names)
        axis_x.setLabelsColor(QColor(TEXT_MUTED))
        axis_x.setLinePen(QPen(QColor(GREEN_200), 1))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        max_y = max([o + v for o, v in zip(occupied_values, vacant_values)] + [1])
        axis_y = QValueAxis()
        axis_y.setRange(0, max_y * 1.2)
        axis_y.setLabelFormat("%.0f")
        axis_y.setLabelsColor(QColor(TEXT_MUTED))
        axis_y.setGridLineColor(QColor(GREEN_200))
        axis_y.setLinePen(QPen(QColor(GREEN_200), 1))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.occupancy_chart_view.setChart(chart)

    def _populate_arrears_table(self, rows):
        self.arrears_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            tenant, unit, rent_amount, paid_amount, arrears = row
            values = [
                tenant,
                unit,
                f"KES {rent_amount:,.0f}",
                f"KES {paid_amount:,.0f}",
                f"KES {arrears:,.0f}",
            ]
            for col_idx, value in enumerate(values):
                self.arrears_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
