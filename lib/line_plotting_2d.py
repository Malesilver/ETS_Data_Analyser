import sys

from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                              QChartView, QValueAxis)
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QMainWindow,QWidget,QSizePolicy
from PySide6 import QtWidgets
from PySide6 import QtGui
from lib.share import sdm
class Func_Plot2DLine(QWidget):
    def __init__(self):
        super().__init__()
        vLayout = QtWidgets.QVBoxLayout(self)


        screenSize = self.screen().size()
        self.setMinimumSize(QSize(screenSize.width() / 4, screenSize.height() / 3.2))
        self.setMaximumSize(screenSize)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)
        self.resize(QSize(screenSize.width() / 1.8, screenSize.height() / 1.6))
        self.setWindowTitle("Self Cap Plot Viewer")
        # *************************Rx**********************
        self.set_Rx = QBarSet("Self Cap. Rx")

        Rx_data = sdm.current_sct_row.flatten()


        self.set_Rx.append(list(Rx_data))


        self.series_Rx = QBarSeries()
        self.series_Rx.setBarWidth(0.9)
        self.series_Rx.append(self.set_Rx)


        self.chart_Rx = QChart()
        self.chart_Rx.addSeries(self.series_Rx)
        self.chart_Rx.setTitle("Self Cap. Rx")
        self.chart_Rx.setAnimationOptions(QChart.SeriesAnimations)
        self.chart_Rx.setTheme(QChart.ChartThemeBlueIcy)

        self.axis_x = QBarCategoryAxis()
        self.chart_Rx.addAxis(self.axis_x, Qt.AlignBottom)
        self.series_Rx.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%d")
        # self.axis_y.setRange(-50, 50)
        self.chart_Rx.addAxis(self.axis_y, Qt.AlignLeft)
        self.series_Rx.attachAxis(self.axis_y)

        self.chart_Rx.legend().setVisible(True)
        self.chart_Rx.legend().setAlignment(Qt.AlignBottom)

        self._chart_view_Rx = QChartView(self.chart_Rx)
        self._chart_view_Rx.setRenderHint(QPainter.Antialiasing)

        # *************************Tx**********************
        self.set_Tx = QBarSet("Self Cap. Tx")
        Tx_data = sdm.current_sct_col.flatten()
        self.set_Tx.append(list(Tx_data))

        self.series_Tx = QBarSeries()
        self.series_Tx.setBarWidth(0.9)
        self.series_Tx.append(self.set_Tx)

        self.chart_Tx = QChart()
        self.chart_Tx.addSeries(self.series_Tx)
        self.chart_Tx.setTitle("Self Cap. Tx")
        self.chart_Tx.setAnimationOptions(QChart.SeriesAnimations)
        self.chart_Tx.setTheme(QChart.ChartThemeBlueIcy)

        self.axis_x = QBarCategoryAxis()
        self.chart_Tx.addAxis(self.axis_x, Qt.AlignBottom)
        self.series_Tx.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%d")
        # self.axis_y.setRange(-50, 50)
        self.chart_Tx.addAxis(self.axis_y, Qt.AlignLeft)
        self.series_Tx.attachAxis(self.axis_y)

        self.chart_Tx.legend().setVisible(True)
        self.chart_Tx.legend().setAlignment(Qt.AlignBottom)

        self._chart_view_Tx = QChartView(self.chart_Tx)
        self._chart_view_Tx.setRenderHint(QPainter.Antialiasing)




        vLayout.addWidget(self._chart_view_Rx)
        vLayout.addWidget(self._chart_view_Tx)

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
            del sdm.subWinTable[str(Func_Plot2DLine)]
            event.accept()
        else:
            event.ignore()