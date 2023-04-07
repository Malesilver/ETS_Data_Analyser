import os.path
import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PySide6.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lib.APL_share import APL_Share
from PySide6.QtGui import QIcon

# class MyFigureCanvas(FigureCanvas):
#     def __init__(self):
#         fig = Figure()
#         FigureCanvas.__init__(self, fig)
#         self.axes = fig.add_subplot(111)
#         accuracy_error = APL_Share.align_error_df
#         centre_error = 0.6
#         edge_error = 1.2
#         max_error = math.ceil(abs(accuracy_error.max().max()))
#         # self.axes.set_aspect(1)
#         self.axes.plot(accuracy_error['X_delta'], accuracy_error['Y_delta'], 'o', color='r')
#         # accuracy_error.plot(x=0, y=1, kind='scatter', color='r')
#         theta = np.linspace(0, 2 * np.pi, 100)
#         for i in np.arange(centre_error, max_error + 0.5, 0.5):
#             # x1 = i * np.cos(theta)
#             # x2 = i * np.sin(theta)
#             # plt.plot(x1, x2, color='k')
#             Drawing_uncolored_circle = plt.Circle((0, 0), i, fill=False, color='k')
#             self.axes.add_patch(Drawing_uncolored_circle)
#         self.axes.axhline(y=0, color='k')
#         self.axes.axvline(x=0, color='k')
#         self.axes.set_xlim([-edge_error - 0.5, edge_error + 0.5])
#         self.axes.set_ylim([-edge_error - 0.5, edge_error + 0.5])
#         graph_title_with_size = "test"
#         self.axes.set_title(graph_title_with_size)
#         self.axes.set_xlabel('Accuracy Error X (mm)')
#         self.axes.set_ylabel('Accuracy Error Y (mm)')
#         self.draw()
#
#
#
# class Func_PlotAPLCalib(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.plot = MyFigureCanvas()
#         self.buttonClose = QPushButton('Press to close this window')
#         self.buttonClose.clicked.connect(self.close)
#         layout = QVBoxLayout()
#         layout.addWidget(self.plot)
#         layout.addWidget(self.buttonClose)
#         self.setLayout(layout)
#         self.show()


class Func_PlotAPLCalib(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        outerLayout = QHBoxLayout()
        leftlayout = QVBoxLayout()
        rightlayout = QVBoxLayout()

        self.setWindowTitle("APL Calibration Plot")
        iconPath = os.path.join(os.path.dirname(sys.argv[0]),"icons","apl.png")
        self.setWindowIcon(QIcon(iconPath))


        topleft_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        leftlayout.addWidget(NavigationToolbar(topleft_canvas, self))
        leftlayout.addWidget(topleft_canvas)

        bottomleft_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        leftlayout.addWidget(bottomleft_canvas)
        leftlayout.addWidget(NavigationToolbar(bottomleft_canvas, self))


        topleft_canvas.figure = APL_Share.SubFigList["Calibration_rawdata_before"]
        bottomleft_canvas.figure = APL_Share.SubFigList["Calibration_error_before"]

        topright_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        rightlayout.addWidget(NavigationToolbar(topright_canvas, self))
        rightlayout.addWidget(topright_canvas)

        bottomright_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        rightlayout.addWidget(bottomright_canvas)
        rightlayout.addWidget(NavigationToolbar(bottomright_canvas, self))

        topright_canvas.figure = APL_Share.SubFigList["Calibration_rawdata_after"]
        bottomright_canvas.figure = APL_Share.SubFigList["Calibration_error_after"]


        # add layout
        outerLayout.addLayout(leftlayout)
        outerLayout.addLayout(rightlayout)

        self._main.setLayout(outerLayout)

