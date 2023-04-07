from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PySide6.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lib.APL_share import APL_Share
import os
import sys
from PySide6.QtGui import QIcon



class Func_PlotAPLPrecision(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        outerLayout = QHBoxLayout()
        leftlayout = QVBoxLayout()
        rightlayout = QVBoxLayout()
        self.setWindowTitle("APL Precision Plot")
        iconPath = os.path.join(os.path.dirname(sys.argv[0]), "icons", "apl.png")
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


        topleft_canvas.figure = APL_Share.SubFigList["Precision_data_fullscreen"]
        bottomleft_canvas.figure = APL_Share.SubFigList["Precision_error_fullscreen"]

        topright_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        rightlayout.addWidget(NavigationToolbar(topright_canvas, self))
        rightlayout.addWidget(topright_canvas)

        bottomright_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        rightlayout.addWidget(bottomright_canvas)
        rightlayout.addWidget(NavigationToolbar(bottomright_canvas, self))

        topright_canvas.figure = APL_Share.SubFigList["Precision_data_centre"]
        bottomright_canvas.figure = APL_Share.SubFigList["Precision_error_centre"]


        # add layout
        outerLayout.addLayout(leftlayout)
        outerLayout.addLayout(rightlayout)

        self._main.setLayout(outerLayout)