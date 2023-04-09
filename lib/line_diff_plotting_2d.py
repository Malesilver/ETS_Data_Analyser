import sys
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication,QSizePolicy,QVBoxLayout,QWidget
from PySide6.QtCharts import (QBarCategoryAxis, QBarSet, QChart, QChartView,
                              QStackedBarSeries, QValueAxis)
from PySide6 import QtWidgets
from lib.share import ShareDataManager

class Func_Plot2DStackBar(QWidget):
    def __init__(self):
        super().__init__()

        vLayout = QVBoxLayout(self)
        screenSize = self.screen().size()
        self.setMinimumSize(QSize(screenSize.width() / 4, screenSize.height() / 3.2))
        self.setMaximumSize(screenSize)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)
        self.resize(QSize(screenSize.width() / 1.8, screenSize.height() / 2))
        self.setWindowTitle("Self Cap Diff. Data Viewer")

        # *************** Rx ****************

        self.rx_Low = QBarSet("Min")
        self.rx_High = QBarSet("Max")
        Rx_low_data = ShareDataManager.current_row_data_min.flatten()
        Rx_high_data = ShareDataManager.current_row_data_max.flatten()

        self.rx_Low.append(list(Rx_low_data))
        self.rx_High.append(list(Rx_high_data))


        self.series_Rx = QStackedBarSeries()
        self.series_Rx.append(self.rx_Low)
        self.series_Rx.append(self.rx_High)

        self.chart_Rx = QChart()
        self.chart_Rx.addSeries(self.series_Rx)
        self.chart_Rx.setTitle("Self Cap. Rx Peak-Peak max/min")
        self.chart_Rx.setAnimationOptions(QChart.SeriesAnimations)

        self.axis_x = QBarCategoryAxis()
        self.chart_Rx.addAxis(self.axis_x, Qt.AlignBottom)
        self.series_Rx.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%d")
        self.chart_Rx.addAxis(self.axis_y, Qt.AlignLeft)
        self.series_Rx.attachAxis(self.axis_y)


        self.chart_Rx.legend().setVisible(True)
        self.chart_Rx.legend().setAlignment(Qt.AlignBottom)

        self.chart_view_Rx = QChartView(self.chart_Rx)
        self.chart_view_Rx.setRenderHint(QPainter.Antialiasing)

        # *************** Tx ****************

        self.tx_Low = QBarSet("Min")
        self.tx_High = QBarSet("Max")
        tx_low_data = ShareDataManager.current_col_data_min.flatten()
        tx_high_data = ShareDataManager.current_col_data_max.flatten()

        self.tx_Low.append(list(tx_low_data))
        self.tx_High.append(list(tx_high_data))

        self.series_Tx = QStackedBarSeries()
        self.series_Tx.append(self.tx_Low)
        self.series_Tx.append(self.tx_High)

        self.chart_Tx = QChart()
        self.chart_Tx.addSeries(self.series_Tx)
        self.chart_Tx.setTitle("Self Cap. Tx Peak-Peak max/min")
        self.chart_Tx.setAnimationOptions(QChart.SeriesAnimations)

        self.axis_x = QBarCategoryAxis()
        self.chart_Tx.addAxis(self.axis_x, Qt.AlignBottom)
        self.series_Tx.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%d")
        self.chart_Tx.addAxis(self.axis_y, Qt.AlignLeft)
        self.series_Tx.attachAxis(self.axis_y)

        self.chart_Tx.legend().setVisible(True)
        self.chart_Tx.legend().setAlignment(Qt.AlignBottom)

        self.chart_view_Tx = QChartView(self.chart_Tx)
        self.chart_view_Tx.setRenderHint(QPainter.Antialiasing)



        vLayout.addWidget(self.chart_view_Rx)
        vLayout.addWidget(self.chart_view_Tx)

    def closeEvent(self, event):
        # message为窗口标题
        # Are you sure to quit?窗口显示内容
        # QtWidgets.QMessageBox.Yes | QtGui.QMessageBox.No窗口按钮部件
        # QtWidgets.QMessageBox.No默认焦点停留在NO上
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               "Are you sure to quit?",
                                               QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        # 判断返回结果处理相应事项
        if reply == QtWidgets.QMessageBox.Yes:
            del ShareDataManager.subWinTable[str(Func_Plot2DStackBar)]
            event.accept()
        else:
            event.ignore()