import math

from PySide6.QtCore import QObject, Qt, Slot,QStringListModel
from PySide6.QtDataVisualization import (Q3DTheme, QAbstract3DGraph,
                                         QHeightMapSurfaceDataProxy,
                                         QSurface3DSeries, QSurfaceDataItem,
                                         QSurfaceDataProxy, QValue3DAxis)
from PySide6.QtGui import QImage, QLinearGradient, QVector3D,QColor
from PySide6.QtWidgets import QSlider, QMessageBox
import numpy as np
from lib.share import sdm




class SurfaceGraph(QObject):
    def __init__(self, surface, parent=None):
        QObject.__init__(self, parent)

        self.m_graph = surface
        self.m_graph.setAxisX(QValue3DAxis())
        self.m_graph.setAxisY(QValue3DAxis())
        self.m_graph.setAxisZ(QValue3DAxis())

        self.m_sqrtSinProxy = QSurfaceDataProxy()
        self.m_sqrtSinSeries = QSurface3DSeries(self.m_sqrtSinProxy)
        if sdm.current_mct_grid is not None:

            self.fillSqrtSinProxy(sdm.current_mct_grid)
        else:
            self.fillSqrtSinProxy(np.zeros((20,40)))

        # heightMapImage = QImage("mountain.png")
        # self.m_heightMapProxy = QHeightMapSurfaceDataProxy(heightMapImage)
        # self.m_heightMapSeries = QSurface3DSeries(self.m_heightMapProxy)
        # self.m_heightMapSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        # self.m_heightMapProxy.setValueRanges(34.0, 40.0, 18.0, 24.0)
        #
        # self.m_heightMapWidth = heightMapImage.width()
        # self.m_heightMapHeight = heightMapImage.height()

        self.m_axisMinSliderX = QSlider()
        self.m_axisMaxSliderX = QSlider()
        self.m_axisMinSliderZ = QSlider()
        self.m_axisMaxSliderZ = QSlider()
        self.m_rangeMinX = 0.0
        self.m_rangeMinZ = 0.0
        self.m_stepX = 0.0
        self.m_stepZ = 0.0

    def fillSqrtSinProxy(self,rawdata):

        dataArray = []
        # rawdata = np.random.randint(0, 10, (40, 20))
        sampleZ ,sampleX = rawdata.shape
        for i in range(sampleZ):
            newRow = []

            for j in range(sampleX):
                value = rawdata[i][j]
                newRow.append(QSurfaceDataItem(QVector3D(j, value, i)))
            dataArray.append(newRow)



        self.m_sqrtSinProxy.resetArray(dataArray)

    def enableSqrtSinModel(self, enable):
        if enable:
            sampleCountX = sdm.colum_num
            sampleCountZ = sdm.row_num
            self.m_sqrtSinSeries.setDrawMode(QSurface3DSeries.DrawSurfaceAndWireframe)
            self.m_sqrtSinSeries.setFlatShadingEnabled(True)
            self.m_sqrtSinSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")


            self.m_graph.axisX().setLabelFormat("Tx %d")
            self.m_graph.axisZ().setLabelFormat("Rx %d")
            self.m_graph.axisX().setRange(0, sdm.colum_num)
            # self.m_graph.axisY().setRange(0.0, 100.0)
            self.m_graph.axisZ().setRange(0, sdm.row_num)
            self.m_graph.axisX().setLabelAutoRotation(30)
            self.m_graph.axisY().setLabelAutoRotation(90)
            self.m_graph.axisZ().setLabelAutoRotation(30)

            # self.m_graph.removeSeries(self.m_heightMapSeries)
            self.m_graph.addSeries(self.m_sqrtSinSeries)

            # Reset range sliders for Sqrt&Sin

            self.m_axisMinSliderX.setMaximum(sampleCountX-1)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(sampleCountX -1)
            self.m_axisMaxSliderX.setValue(sampleCountX-1 )
            self.m_axisMinSliderZ.setMaximum(sampleCountZ-1)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(sampleCountZ-1)
            self.m_axisMaxSliderZ.setValue(sampleCountZ-1)
            self.setGreenToRedGradient()



    def adjustXMin(self, minimum):

        maximum = self.m_axisMaxSliderX.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderX.setValue(maximum)


        self.setAxisXRange(minimum, maximum)

    def adjustXMax(self, maximum):


        minimum = self.m_axisMinSliderX.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderX.setValue(minimum)

        self.setAxisXRange(minimum, maximum)

    def adjustZMin(self, minimum):

        maximum = self.m_axisMaxSliderZ.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderZ.setValue(maximum)

        self.setAxisZRange(minimum, maximum)

    def adjustZMax(self, maximum):

        minimum = self.m_axisMinSliderZ.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderZ.setValue(minimum)

        self.setAxisZRange(minimum, maximum)

    def setAxisXRange(self, minimum, maximum):
        self.m_graph.axisX().setRange(minimum, maximum)

    def setAxisZRange(self, minimum, maximum):
        self.m_graph.axisZ().setRange(minimum, maximum)

    @Slot()
    def changeTheme(self, theme):
        self.m_graph.activeTheme().setType(Q3DTheme.Theme(theme))

    def setBlackToYellowGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkBlue)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        self.m_graph.seriesList()[0].setBaseGradient(gr)
        self.m_graph.seriesList()[0].setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    def setGreenToRedGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(1.0, QColor(165, 0, 38))
        gr.setColorAt(0.6, QColor(215, 48, 39))
        gr.setColorAt(0.5, QColor(244, 109, 67))
        gr.setColorAt(0.4, QColor(253, 174, 97))
        gr.setColorAt(0.3, QColor(166, 217, 106))
        gr.setColorAt(0.2, QColor(102, 189, 99))
        gr.setColorAt(0.1, QColor(26, 152, 80))
        gr.setColorAt(0.0, QColor(0, 104, 55))

        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    def setBlueToRedGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(1.0, QColor(165, 0, 38))
        gr.setColorAt(0.6, QColor(215, 48, 39))
        gr.setColorAt(0.5, QColor(244, 109, 67))
        gr.setColorAt(0.4, QColor(253, 174, 97))
        gr.setColorAt(0.3, QColor(255, 255, 191))
        gr.setColorAt(0.2, QColor(171, 217, 233))
        gr.setColorAt(0.1, QColor(116, 173, 209))
        gr.setColorAt(0.0, QColor(49, 54, 149))


        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)
    def setWhiteToBlackGradient(self):

        gr = QLinearGradient()
        gr.setColorAt(1.0, QColor(37,37,37))
        gr.setColorAt(0.7, QColor(82, 82, 82))
        gr.setColorAt(0.5, QColor(115, 115, 115))
        gr.setColorAt(0.3, QColor(150, 150, 150))
        gr.setColorAt(0.2, QColor(189, 189, 189))
        gr.setColorAt(0.1, QColor(217, 217, 217))
        gr.setColorAt(0.0, QColor(240, 240, 240))




        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)


    def toggleModeNone(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    def toggleModeItem(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    def toggleModeSliceRow(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndRow | QAbstract3DGraph.SelectionSlice
        )

    def toggleModeSliceColumn(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndColumn | QAbstract3DGraph.SelectionSlice
        )

    def setAxisMinSliderX(self, slider):
        self.m_axisMinSliderX = slider

    def setAxisMaxSliderX(self, slider):
        self.m_axisMaxSliderX = slider

    def setAxisMinSliderZ(self, slider):
        self.m_axisMinSliderZ = slider

    def setAxisMaxSliderZ(self, slider):
        self.m_axisMaxSliderZ = slider