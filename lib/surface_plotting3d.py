import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtDataVisualization import Q3DSurface
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton, QRadioButton,
                               QSizePolicy, QSlider, QVBoxLayout, QWidget)

from lib.surfacegraph  import SurfaceGraph

from PySide6 import QtCore, QtGui, QtWidgets
from lib.share import ShareDataManager

THEMES = ["Qt", "Primary Colors", "Digia", "Stone Moss", "Army Blue", "Retro", "Ebony", "Isabelle"]

class Func_Plot3Dsurface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)

        self.graph = Q3DSurface()
        self.container = QWidget.createWindowContainer(self.graph)

        if not self.graph.hasContext():
            msgBox = QMessageBox()
            msgBox.setText("Couldn't initialize the OpenGL context.")
            msgBox.exec()
            sys.exit(-1)

        screenSize = self.graph.screen().size()
        self.container.setMinimumSize(QSize(screenSize.width() / 2, screenSize.height() / 1.6))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)

        hLayout = QHBoxLayout(self)
        vLayout = QVBoxLayout()
        hLayout.addWidget(self.container, 1)
        hLayout.addLayout(vLayout)
        vLayout.setAlignment(Qt.AlignTop)

        self.setWindowTitle("Mutual Grid Surface Plot Viewer")

        modelGroupBox = QGroupBox("Model")

        sqrtSinModelRB = QRadioButton(self)
        sqrtSinModelRB.setText("Sqrt& Sin")
        sqrtSinModelRB.setChecked(False)

        # heightMapModelRB = QRadioButton(self)
        # heightMapModelRB.setText("Height Map")
        # heightMapModelRB.setChecked(False)

        modelVBox = QVBoxLayout()
        modelVBox.addWidget(sqrtSinModelRB)
        # modelVBox.addWidget(heightMapModelRB)
        modelGroupBox.setLayout(modelVBox)

        selectionGroupBox = QGroupBox("Selection Mode")

        modeNoneRB = QRadioButton(self)
        modeNoneRB.setText("No selection")
        modeNoneRB.setChecked(False)

        modeItemRB = QRadioButton(self)
        modeItemRB.setText("Item")
        modeItemRB.setChecked(False)

        modeSliceRowRB = QRadioButton(self)
        modeSliceRowRB.setText("Row Slice")
        modeSliceRowRB.setChecked(False)

        modeSliceColumnRB = QRadioButton(self)
        modeSliceColumnRB.setText("Column Slice")
        modeSliceColumnRB.setChecked(False)

        selectionVBox = QVBoxLayout()
        selectionVBox.addWidget(modeNoneRB)
        selectionVBox.addWidget(modeItemRB)
        selectionVBox.addWidget(modeSliceRowRB)
        selectionVBox.addWidget(modeSliceColumnRB)
        selectionGroupBox.setLayout(selectionVBox)



        axisMinSliderX = QSlider(Qt.Horizontal, self)
        axisMinSliderX.setMinimum(0)
        axisMinSliderX.setTickInterval(1)
        axisMinSliderX.setEnabled(True)
        axisMaxSliderX = QSlider(Qt.Horizontal, self)
        axisMaxSliderX.setMinimum(1)
        axisMaxSliderX.setTickInterval(1)
        axisMaxSliderX.setEnabled(True)
        axisMinSliderZ = QSlider(Qt.Horizontal, self)
        axisMinSliderZ.setMinimum(0)
        axisMinSliderZ.setTickInterval(1)
        axisMinSliderZ.setEnabled(True)
        axisMaxSliderZ = QSlider(Qt.Horizontal, self)
        axisMaxSliderZ.setMinimum(1)
        axisMaxSliderZ.setTickInterval(1)
        axisMaxSliderZ.setEnabled(True)

        self.themeList = QComboBox(self)
        self.themeList.addItems(THEMES)

        self.colorGroupBox = QGroupBox("Custom gradient")

        # todo color bar 01
        grBtoY = QLinearGradient(0, 0, 1, 100)
        grBtoY.setColorAt(1.0, Qt.black)
        grBtoY.setColorAt(0.67, Qt.blue)
        grBtoY.setColorAt(0.33, Qt.red)
        grBtoY.setColorAt(0.0, Qt.yellow)

        pm = QPixmap(15, 100)
        pmp = QPainter(pm)
        pmp.setBrush(QBrush(grBtoY))
        pmp.setPen(Qt.NoPen)
        pmp.drawRect(0, 0, 15, 100)
        pmp.end()

        gradientBtoYPB = QPushButton(self)
        gradientBtoYPB.setIcon(QIcon(pm))
        gradientBtoYPB.setIconSize(QSize(15, 100))


        # todo color bar 02
        grGtoR = QLinearGradient(0, 0, 1, 100)
        grGtoR.setColorAt(1.0, Qt.darkGreen)
        grGtoR.setColorAt(0.5, Qt.yellow)
        grGtoR.setColorAt(0.2, Qt.red)
        grGtoR.setColorAt(0.0, Qt.darkRed)
        pmp.begin(pm)
        pmp.setBrush(QBrush(grGtoR))
        pmp.drawRect(0, 0, 15, 100)
        pmp.end()

        gradientGtoRPB = QPushButton(self)
        gradientGtoRPB.setIcon(QIcon(pm))
        gradientGtoRPB.setIconSize(QSize(15, 100))

        # todo color bar 03

        grBtoR = QLinearGradient(0, 0, 1, 100)
        grBtoR.setColorAt(1.0, Qt.darkBlue)
        grBtoR.setColorAt(0.5, Qt.cyan)
        grBtoR.setColorAt(0.2, Qt.red)
        grBtoR.setColorAt(0.0, Qt.darkRed)
        pmp.begin(pm)
        pmp.setBrush(QBrush(grBtoR))
        pmp.drawRect(0, 0, 15, 100)
        pmp.end()

        gradientBtoR = QPushButton(self)
        gradientBtoR.setIcon(QIcon(pm))
        gradientBtoR.setIconSize(QSize(15, 100))

        # todo color bar 04

        grWtoB = QLinearGradient(0, 0, 1, 100)
        grWtoB.setColorAt(1.0, Qt.white)
        grWtoB.setColorAt(0.5, Qt.gray)
        grWtoB.setColorAt(0.2, Qt.darkGray)
        grWtoB.setColorAt(0.0, Qt.black)
        pmp.begin(pm)
        pmp.setBrush(QBrush(grWtoB))
        pmp.drawRect(0, 0, 15, 100)
        pmp.end()

        gradientWtoB = QPushButton(self)
        gradientWtoB.setIcon(QIcon(pm))
        gradientWtoB.setIconSize(QSize(15, 100))


        colorHBox = QHBoxLayout()
        colorHBox.addWidget(gradientBtoYPB)
        colorHBox.addWidget(gradientGtoRPB)
        colorHBox.addWidget(gradientBtoR)
        colorHBox.addWidget(gradientWtoB)
        self.colorGroupBox.setLayout(colorHBox)

        vLayout.addWidget(modelGroupBox)
        vLayout.addWidget(selectionGroupBox)
        vLayout.addWidget(QLabel("Column range"))
        vLayout.addWidget(axisMinSliderX)
        vLayout.addWidget(axisMaxSliderX)
        vLayout.addWidget(QLabel("Row range"))
        vLayout.addWidget(axisMinSliderZ)
        vLayout.addWidget(axisMaxSliderZ)
        vLayout.addWidget(QLabel("Theme"))
        vLayout.addWidget(self.themeList)
        vLayout.addWidget(self.colorGroupBox)


        self.modifier = SurfaceGraph(self.graph)

        sqrtSinModelRB.toggled.connect(self.modifier.enableSqrtSinModel)
        modeNoneRB.toggled.connect(self.modifier.toggleModeNone)
        modeItemRB.toggled.connect(self.modifier.toggleModeItem)
        modeSliceRowRB.toggled.connect(self.modifier.toggleModeSliceRow)
        modeSliceColumnRB.toggled.connect(self.modifier.toggleModeSliceColumn)
        axisMinSliderX.valueChanged.connect(self.modifier.adjustXMin)
        axisMaxSliderX.valueChanged.connect(self.modifier.adjustXMax)
        axisMinSliderZ.valueChanged.connect(self.modifier.adjustZMin)
        axisMaxSliderZ.valueChanged.connect(self.modifier.adjustZMax)
        self.themeList.currentIndexChanged[int].connect(self.modifier.changeTheme)
        gradientBtoYPB.pressed.connect(self.modifier.setBlackToYellowGradient)
        gradientGtoRPB.pressed.connect(self.modifier.setGreenToRedGradient)
        gradientBtoR.pressed.connect(self.modifier.setBlueToRedGradient)
        gradientWtoB.pressed.connect(self.modifier.setWhiteToBlackGradient)

        self.modifier.setAxisMinSliderX(axisMinSliderX)
        self.modifier.setAxisMaxSliderX(axisMaxSliderX)
        self.modifier.setAxisMinSliderZ(axisMinSliderZ)
        self.modifier.setAxisMaxSliderZ(axisMaxSliderZ)

        #
        sqrtSinModelRB.setChecked(True)
        modeItemRB.setChecked(True)
        self.themeList.setCurrentIndex(2)

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
            del ShareDataManager.subWinTable[str(Func_Plot3Dsurface)]
            event.accept()
        else:
            event.ignore()