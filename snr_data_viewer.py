from PySide6.QtWidgets import QMessageBox, QInputDialog,QFileSystemModel, QTreeView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6 import QtCore, QtGui, QtWidgets
import pandas as pd
import numpy as np
from lib.PandasModel import PandasModel
from lib.EtsDataframe import EtsDataframe
from lib.share import ShareDataManager
from lib.surface_plotting3d import Func_Plot3Dsurface
from lib.line_plotting_2d import Func_Plot2DLine
from lib.line_diff_plotting_2d import Func_Plot2DStackBar
from PySide6.QtCharts import (QBarSet)
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from lib.share import SI
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv
import os,sys
from threading import Thread
class Win_SNRDataViewer(QtCore.QObject):

    def __init__(self):
        super(Win_SNRDataViewer, self).__init__()
        self.ui = QUiLoader().load('snr_data_viewer.ui')

        # initial split size

        self.ui.splitterBottom.setSizes([1000, 100])

        # initial split size
        # self.ui.splitterTop.setStretchFactor(0, 1)
        # self.ui.splitterTop.setStretchFactor(1, 20)
        self.ui.splitterTop.setSizes([1000, 100])

        self.ui.splitterMain.setSizes([1000, 100])

        # 翻页和3d绘图功能 disable
        # self.ui.btn_selectFile.clicked.connect(self.selectFile)
        self.ui.btn_inverse.clicked.connect(self.change_inverse_flag)
        self.ui.btnPlot3D.clicked.connect(self._open3DPlotWidget)
        self.ui.btnPlotLine.clicked.connect(self._open2DPlotWidget)
        self.ui.btnPlotSctDiff.clicked.connect(self._open2DStackBarWidget)

        # reset 页面
        self.ui.btn_resetPage.clicked.connect(self.resetPage)


        self.ui.btn_inverse.setEnabled(False)
        self.ui.btnPlot3D.setEnabled(False)
        self.ui.btnPlotLine.setEnabled(False)
        self.ui.btnPlotSctDiff.setEnabled(False)

        # 翻页按键
        self.ui.btn_next.clicked.connect(self.next_page)
        self.ui.btn_previous.clicked.connect(self.previous_page)
        self.ui.btn_next.setEnabled(False)
        self.ui.btn_previous.setEnabled(False)

        # reset 页面
        self.ui.btn_resetPage.setEnabled(False)
        self.ui.edit_maxPage.setEnabled(False)
        self.ui.edit_minPage.setEnabled(False)

        # 手动输入页码
        self.ui.edit_pageNumber.returnPressed.connect(self.editPagePressed)

        # 滑块换页
        self.ui.slider_pageNumber.sliderMoved.connect(self.change_slider_value)
        self.ui.slider_pageNumber.actionTriggered.connect(self.change_slider_value)
        self.ui.slider_pageNumber.setEnabled(False)

        # 选择显示数据类型
        self.ui.comboBox.activated.connect(self.select_dataName)

        # 字体大小 5-20
        # 只能通过按键调节
        self.ui.edit_fontSize.setReadOnly(True)
        self.ui.btn_zoomin.clicked.connect(self.zoom_In)
        self.ui.btn_zoomout.clicked.connect(self.zoom_Out)

        self.ui.installEventFilter(self)

        # exit event

        self.rawDataFrame = None
        self.DataAnalyse = None
        self.inverse = False
        self.FontSize = 10


        # Qfile

        # 这里得到目录结构
        self.model = QFileSystemModel()
        self.model.setRootPath(SI.cfg["Dataset Path"])
        # 这里过滤，只显示 py 文件
        mf = self.model.setNameFilters(["*.txt", "*.png", "*.jpg","*.csv"])
        self.model.setNameFilterDisables(False)
        # 这里做展示
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setRootIndex(self.model.index(SI.cfg["Dataset Path"]))
        self.ui.treeView.doubleClicked.connect(self.tree_double_cilcked)
        # self.tree.clicked.connect(self.tree_cilcked)
        # 这里隐藏了目录信息展示
        for i in [1, 2, 3]:
            self.ui.treeView.setColumnHidden(i, True)

    def eventFilter(self, obj, event):
        if obj is self.ui and event.type() == QtCore.QEvent.Close:
            reply = QtWidgets.QMessageBox.question(self.ui, 'Message',
                                                   "Are you sure to quit?",
                                                   QtWidgets.QMessageBox.Yes |
                                                   QtWidgets.QMessageBox.No
                                                   )

            # 判断返回结果处理相应事项
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
                self.ui.removeEventFilter(self)
            else:
                event.ignore()
            return True
        return super(Win_SNRDataViewer, self).eventFilter(obj, event)

    def tree_double_cilcked(self, Qmodelidx):
        def threadFun():
            os.system(file_path)


        file_path = self.model.filePath(Qmodelidx)
        # print(file_path)

        if os.path.isfile(file_path):
            file_ext = os.path.basename(file_path).split(".")[-1]
            if file_ext!= "csv":
                Thread(target=threadFun).start()
            else:
                filename = os.path.basename(file_path)
                prefix_notouch = SI.cfg['notouch file prefix']
                prefix_touch = SI.cfg['touch file prefix']
                if filename[:len(prefix_notouch)] == prefix_notouch or filename[:len(prefix_touch)] == prefix_touch:
                    if filename[:len(prefix_notouch)] == prefix_notouch:
                        self.loadFile(fileName=file_path,min_idx=int(SI.cfg['start idx notouch']),max_idx=int(SI.cfg['end idx notouch']))
                    else:
                        self.loadFile(fileName=file_path, min_idx=int(SI.cfg['start idx touch']),
                                      max_idx=int(SI.cfg['end idx touch']))
                    parent_path = os.path.dirname(file_path)  # 获得d所在的目录,即d的父级目录
                    self.ui.edit_path.setText(file_path)
                    self.ui.edit_path.setEnabled(False)


                    pattern = os.path.basename(parent_path)

                    if os.path.exists(os.path.join(SI.cfg['Dataset Path'], pattern,
                                                   "{}.edl.csv".format(prefix_notouch))):
                        notouch_data_path = os.path.join(SI.cfg['Dataset Path'], pattern,
                                                         "{}.edl.csv".format(prefix_notouch))
                        touch_path = os.path.join(SI.cfg['Dataset Path'], pattern,
                                                  prefix_touch + "{}.edl.csv")
                    else:
                        notouch_data_path = os.path.join(SI.cfg['Dataset Path'], pattern,
                                                         "{}.csv".format(prefix_notouch))
                        touch_path = os.path.join(SI.cfg['Dataset Path'], pattern,
                                                  prefix_touch + "{}.csv")

                    touch_list = get_touched_num(os.path.join(SI.cfg['Dataset Path'], pattern),
                                                 prefix_touch)

                    # match touch raw data file
                    touch_data_path_list = [touch_path.format(i) for i in touch_list]
                    if len(touch_list)>0:
                        self.DataAnalyse = AnalyseData(no_touch_file_path=notouch_data_path,
                                                  touch_file_paths=touch_data_path_list,
                                                  notouch_range=(
                                                      int(SI.cfg['start idx notouch']),
                                                      int(SI.cfg['end idx notouch'])),
                                                  touch_range=(int(SI.cfg['start idx touch']),
                                                               int(SI.cfg['end idx touch'])))

                else:
                    Thread(target=threadFun).start()



    def select_dataName(self, index):
        #         self.ui.comboBox.addItem("Mutual Raw Data")
        #         self.ui.comboBox.addItem("Peak-Peak Noise")
        #         self.ui.comboBox.addItem("RMS Noise")
        #         self.ui.comboBox.addItem("Max Mct Peak-Peak Position")
        #         self.ui.comboBox.addItem("Min Mct Peak-Peak Position")
        #         self.ui.comboBox.addItem("Max Sct Row Peak-Peak Position")
        #         self.ui.comboBox.addItem("Min Sct Row Position")
        #         self.ui.comboBox.addItem("Max Sct Col Peak-Peak Position")
        #         self.ui.comboBox.addItem("Min Sct Col Position")
        #       Mutual Raw Data
        if index == 0:
            page = int(self.ui.edit_pageNumber.text())
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)


        # Peak-Peak Noise
        elif index == 1:
            if self.rawDataFrame.mct_grid is not None:
                ShareDataManager.current_grid_data = self.rawDataFrame.mct_grid_p2p.astype(int)
            if self.rawDataFrame.sct_row is not None:
                ShareDataManager.current_row_data = self.rawDataFrame.sct_row_p2p.astype(int)
            if self.rawDataFrame.sct_col is not None:
                ShareDataManager.current_col_data = self.rawDataFrame.sct_col_p2p.astype(int)


            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)


        # RMS Noise
        elif index == 2:

            if self.rawDataFrame.mct_grid is not None:
                ShareDataManager.current_grid_data = np.round(self.rawDataFrame.mct_grid_rms, 2)
            if self.rawDataFrame.sct_row is not None:
                ShareDataManager.current_row_data = np.round(self.rawDataFrame.sct_row_rms, 2)
            if self.rawDataFrame.sct_col is not None:
                ShareDataManager.current_col_data = np.round(self.rawDataFrame.sct_col_rms, 2)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # Max Mct Pk-Pk Position
        elif index == 3:
            if self.rawDataFrame.mct_grid is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find Mutual data, please select file with MCT Data!')

                return

            position = self.rawDataFrame.mct_grid_p2p_position
            page = position[1] +1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))

        # min Mct Pk-Pk Position
        elif index == 4:
            if self.rawDataFrame.mct_grid is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find Mutual data, please select file with MCT Data!')
                return
            position = self.rawDataFrame.mct_grid_p2p_position
            page = position[0] + 1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))

        # Max Sct Row Peak-Peak Position
        elif index == 5:
            if self.rawDataFrame.sct_row is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find SCT Row data, please select file with SCT Data!')
                return
            position = self.rawDataFrame.sct_row_p2p_position
            page = position[1] + 1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))

        # min Sct Row Peak-Peak Position
        elif index == 6:
            if self.rawDataFrame.sct_row is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find SCT Row data, please select file with SCT Data!')
                return
            position = self.rawDataFrame.sct_row_p2p_position
            page = position[0] + 1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))


        # Max Sct Col Peak-Peak Position
        elif index == 7:
            if self.rawDataFrame.sct_col is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find SCT Col data, please select file with SCT Data!')
                return
            position = self.rawDataFrame.sct_col_p2p_position
            page = position[1] + 1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))

        # min Sct Col Peak-Peak Position
        elif index == 8:
            if self.rawDataFrame.sct_col is None:
                QMessageBox.warning(
                    self.ui,
                    'Data Error',
                    'Could not find SCT Col data, please select file with SCT Data!')
                return
            position = self.rawDataFrame.sct_col_p2p_position
            page = position[0] + 1
            self._setDataFrame(page, self.inverse)
            self.ui.btn_previous.setEnabled(True)
            self.ui.btn_next.setEnabled(True)
            self.ui.edit_pageNumber.setEnabled(True)
            self.ui.slider_pageNumber.setEnabled(True)

            self.ui.slider_pageNumber.setValue(page)
            self.ui.edit_pageNumber.setText(str(page))

        # mean value
        elif index == 9:
            if self.rawDataFrame.mct_grid is not None:
                ShareDataManager.current_grid_data = np.round(self.rawDataFrame.mct_grid.mean(axis = 0), 1)
            if self.rawDataFrame.sct_row is not None:
                ShareDataManager.current_row_data = np.round(self.rawDataFrame.sct_row.mean(axis = 0), 1)
            if self.rawDataFrame.sct_col is not None:
                ShareDataManager.current_col_data = np.round(self.rawDataFrame.sct_col.mean(axis = 0), 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # Smean Nrms R
        elif index == 10:
            if self.rawDataFrame.mct_grid is not None:
                ShareDataManager.current_grid_data = np.round(self.rawDataFrame.mct_signal_max / self.rawDataFrame.mct_grid_rms, 1)
            if self.rawDataFrame.sct_row is not None:
                ShareDataManager.current_row_data = np.round(self.rawDataFrame.sct_row_signal_max / self.rawDataFrame.sct_row_rms, 1)
            if self.rawDataFrame.sct_col is not None:
                ShareDataManager.current_col_data = np.round(self.rawDataFrame.sct_col_signal_max / self.rawDataFrame.sct_col_rms, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SNppR Custom
        elif index == 11:


            if self.rawDataFrame.mct_grid is not None:
                mct_signal,status = QInputDialog.getInt(self.ui, "MCT Signal Input", "Input tips\nplease enter number (-10000~+10000):")
                ShareDataManager.current_grid_data = np.round(mct_signal / self.rawDataFrame.mct_grid_p2p, 1)
            if self.rawDataFrame.sct_row is not None:
                sct_row_signal,status = QInputDialog.getInt(self.ui, "SCT Row Signal Input", "Input tips\nplease enter number (-10000~+10000):")
                ShareDataManager.current_row_data = np.round(sct_row_signal / self.rawDataFrame.sct_row_p2p, 1)
            if self.rawDataFrame.sct_col is not None:
                sct_col_signal,status = QInputDialog.getInt(self.ui, "SCT Col Signal Input", "Input tips\nplease enter number (-10000~+10000):")
                ShareDataManager.current_col_data = np.round(sct_col_signal / self.rawDataFrame.sct_col_p2p, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # Signal overview - summerize mean signals for fullscreen
        elif index == 12:

            if self.rawDataFrame.mct_grid is not None:
                touch_data = []

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.mct_signal_max
                    touch_grid = TouchFrame.mct_grid_mean
                    _, ynode, xnode = TouchFrame.mct_signal_position
                    touch_grid[ynode][xnode] = signal
                    touch_data.append(touch_grid)

                touch_data = np.array(touch_data)
                grid_Data = touch_data.max(axis=0)
                ShareDataManager.current_grid_data = np.round(grid_Data, 1)
            if self.rawDataFrame.sct_row is not None:
                touch_data_row = []
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    touch_row = TouchFrame.sct_row_mean
                    touch_data_row.append(touch_row)
                touch_data_row = np.array(touch_data_row).astype(int)
                touch_data_row = touch_data_row.max(axis=0)
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)
            if self.rawDataFrame.sct_col is not None:
                touch_data_col = []
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    touch_col = TouchFrame.sct_col_mean
                    touch_data_col.append(touch_col)
                touch_data_col = np.array(touch_data_col).astype(int)
                touch_data_col = touch_data_col.max(axis=0)
                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SmaxNppfullscreeR -
        elif index == 13:
            if self.rawDataFrame.mct_grid is not None:
                snr_grid_list = []
                p2p_noise_grid = self.DataAnalyse.mct_noise_p2p_grid

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.mct_signal_max
                    snr_grid = signal/p2p_noise_grid
                    snr_grid_list.append(snr_grid)

                snr_grid_list = np.array(snr_grid_list)
                grid_Data = snr_grid_list.min(axis=0)
                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:
                snr_row_list = []
                p2p_noise_row = self.DataAnalyse.sct_row_noise_p2p_line
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_max
                    snr_row = signal / p2p_noise_row
                    snr_row_list.append(snr_row)
                snr_row_list = np.array(snr_row_list)
                touch_data_row = snr_row_list.min(axis=0)
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:
                snr_col_list = []
                p2p_noise_col = self.DataAnalyse.sct_col_noise_p2p_line
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_max
                    snr_col= signal / p2p_noise_col
                    snr_col_list.append(snr_col)
                snr_col_list = np.array(snr_col_list)
                touch_data_col = snr_col_list.min(axis=0)
                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SmaxNppfullscreeR - dB
        elif index == 14:
            if self.rawDataFrame.mct_grid is not None:
                snr_grid_list = []
                p2p_noise_grid = self.DataAnalyse.mct_noise_p2p_grid

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.mct_signal_max
                    snr_grid = signal / p2p_noise_grid
                    snr_grid_list.append(snr_grid)

                snr_grid_list = np.array(snr_grid_list)
                grid_Data = snr_grid_list.min(axis=0)
                grid_Data = 20 * np.log10(grid_Data)
                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:
                snr_row_list = []
                p2p_noise_row = self.DataAnalyse.sct_row_noise_p2p_line
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_max
                    snr_row = signal / p2p_noise_row
                    snr_row_list.append(snr_row)
                snr_row_list = np.array(snr_row_list)
                touch_data_row = snr_row_list.min(axis=0)
                touch_data_row = 20 * np.log10(touch_data_row)
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:
                snr_col_list = []
                p2p_noise_col = self.DataAnalyse.sct_col_noise_p2p_line
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_max
                    snr_col = signal / p2p_noise_col
                    snr_col_list.append(snr_col)
                snr_col_list = np.array(snr_col_list)
                touch_data_col = snr_col_list.min(axis=0)
                touch_data_col = 20 * np.log10(touch_data_col)
                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SminNppnotouchnodeR for Huawei
        elif index == 15:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_min
                    grid_Data[y_node][x_node] = signal / self.DataAnalyse.NoTouchFrame.mct_grid_p2p[y_node][x_node]


                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_min
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = signal / self.DataAnalyse.NoTouchFrame.sct_row_p2p[x_node]
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_min
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = signal / self.DataAnalyse.NoTouchFrame.sct_col_p2p[y_node]
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node,touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SminNppnotouchnodeR - dB for Huawei
        elif index == 16:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_min
                    snr_mct_node = signal / self.DataAnalyse.NoTouchFrame.mct_grid_p2p[y_node][x_node]
                    snr_mct_node = 20 * np.log10(snr_mct_node)
                    grid_Data[y_node][x_node] = snr_mct_node

                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_min
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = 20 * np.log10(signal / self.DataAnalyse.NoTouchFrame.sct_row_p2p[x_node])
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_min
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = 20* np.log10(signal / self.DataAnalyse.NoTouchFrame.sct_col_p2p[y_node])
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node, touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SmeanNrmsR
        elif index == 17:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_mean
                    snr_mct_node = signal / TouchFrame.mct_grid_rms[y_node][x_node]
                    grid_Data[y_node][x_node] = snr_mct_node

                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_mean
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = signal / TouchFrame.sct_row_rms[x_node]
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_mean
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = signal / TouchFrame.sct_col_rms[y_node]
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node, touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SmeanNrmsR - dB
        elif index == 18:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_min
                    snr_mct_node = 20 * np.log10(signal / TouchFrame.mct_grid_rms[y_node][x_node])

                    grid_Data[y_node][x_node] = snr_mct_node

                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_mean
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = 20 * np.log10(signal / TouchFrame.sct_row_rms[x_node])
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_mean
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = 20 * np.log10(signal / TouchFrame.sct_col_rms[y_node])
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node, touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SminNaveR - dB for Huawei
        elif index == 19:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_min
                    snr_mct_node = signal / self.DataAnalyse.mct_noise_ave_grid[y_node][x_node]
                    # snr_mct_node = 20 * np.log10(snr_mct_node)
                    grid_Data[y_node][x_node] = snr_mct_node

                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_min
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = signal / self.DataAnalyse.sct_row_noise_ave_line[x_node]
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_min
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = signal / self.DataAnalyse.sct_col_noise_ave_line[y_node]
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node, touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)

        # SminNaveR - dB for Huawei
        elif index == 20:
            if self.rawDataFrame.mct_grid is not None:

                grid_Data = np.zeros_like(self.DataAnalyse.mct_noise_p2p_grid).astype(float)

                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    _, y_node, x_node = TouchFrame.mct_signal_position
                    signal = TouchFrame.mct_signal_min
                    snr_mct_node = signal / self.DataAnalyse.mct_noise_ave_grid[y_node][x_node]
                    snr_mct_node = 20 * np.log10(snr_mct_node)
                    grid_Data[y_node][x_node] = snr_mct_node

                ShareDataManager.current_grid_data = np.round(grid_Data, 1)

            if self.rawDataFrame.sct_row is not None:

                touch_data_row = np.zeros_like(self.DataAnalyse.sct_row_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_row_signal_min
                    _, x_node = TouchFrame.sct_row_signal_position
                    snr_node = signal / self.DataAnalyse.sct_row_noise_ave_line[x_node]
                    snr_node = 20 * np.log10(snr_node)
                    if touch_data_row[x_node] == 0:
                        touch_data_row[x_node] = snr_node
                    else:
                        touch_data_row[x_node] = min(snr_node, touch_data_row[x_node])
                ShareDataManager.current_row_data = np.round(touch_data_row, 1)

            if self.rawDataFrame.sct_col is not None:

                touch_data_col = np.zeros_like(self.DataAnalyse.sct_col_noise_p2p_line).astype(float)
                for TouchFrame in self.DataAnalyse.TouchFrameSets:
                    signal = TouchFrame.sct_col_signal_min
                    _, y_node = TouchFrame.sct_col_signal_position
                    snr_node = signal / self.DataAnalyse.sct_col_noise_ave_line[y_node]
                    snr_node = 20 * np.log10(snr_node)
                    if touch_data_col[y_node] == 0:
                        touch_data_col[y_node] = snr_node
                    else:
                        touch_data_col[y_node] = min(snr_node, touch_data_col[y_node])

                ShareDataManager.current_col_data = np.round(touch_data_col, 1)

            self._setNormalDataFrame(self.inverse)
            self.ui.btn_previous.setEnabled(False)
            self.ui.btn_next.setEnabled(False)
            self.ui.edit_pageNumber.setEnabled(False)
            self.ui.slider_pageNumber.setEnabled(False)


        # print(self.ui.comboBox.currentText())
        # print(self.ui.comboBox.currentIndex())

    def change_inverse_flag(self):
        self.inverse = ~self.inverse
        tmp_list = [0,3,4,5,6,7,8]
        if self.ui.comboBox.currentIndex() in tmp_list :
            page = self.ui.edit_pageNumber.text()
            page = int(page)
            self._setDataFrame(int(page), self.inverse)
        else:
            self._setNormalDataFrame(self.inverse)

    def set_slider_value(self, min, max):
        self.ui.slider_pageNumber.minimum = min
        self.ui.slider_pageNumber.maximum = max

    def change_slider_value(self):
        page = self.ui.slider_pageNumber.sliderPosition()
        self._setDataFrame(int(page), self.inverse)
        self.ui.edit_pageNumber.setText(str(page))

    @Slot()
    def previous_page(self):
        page = self.ui.edit_pageNumber.text()
        page = max(int(page) - 1, 1)
        self.ui.slider_pageNumber.setValue(page)
        self.ui.edit_pageNumber.setText(str(page))
        self._setDataFrame(page, self.inverse)

    @Slot()
    def next_page(self):
        page = self.ui.edit_pageNumber.text()
        page = min(int(page) + 1, len(self.rawDataFrame))
        self.ui.slider_pageNumber.setValue(page)
        self.ui.edit_pageNumber.setText(str(page))
        self._setDataFrame(page, self.inverse)

    def selectFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self.ui, "Open File", "", "CSV Files (*.csv)");

        if fileName == "":
            return
        self.ui.edit_path.setText(fileName)
        self.ui.edit_path.setEnabled(False)
        self.loadFile(fileName=fileName)
        self.ui.edit_minPage.clear()
        self.ui.edit_maxPage.clear()

    def resetPage(self):

        minPage_idx = self.ui.edit_minPage.text()
        maxPage_idx = self.ui.edit_maxPage.text()
        fileName = self.ui.edit_path.text()
        try:
            minPage_idx = int(minPage_idx)
            maxPage_idx = int(maxPage_idx)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return
        else:
            if minPage_idx < 1:
                minPage_idx = 1
                self.ui.edit_minPage.setText(str(minPage_idx))
            elif minPage_idx >= maxPage_idx:
                QMessageBox.warning(
                    self.ui,
                    'Error',
                    "Max page must greater than Min page!!!")
                return
            elif maxPage_idx > self.rawDataFrame.frame_num:
                QMessageBox.warning(
                    self.ui,
                    'Error',
                    f"Max page can not greater than max. frame number!!! max. frame number is {self.rawDataFrame.frame_num}")

                return



        self.loadFile(fileName,minPage_idx,maxPage_idx+1)



    def loadFile(self,fileName,min_idx = None,max_idx=None):

        self.inverse = False
        self.rawDataFrame = EtsDataframe(fileName, start_idx=min_idx, end_idx=max_idx)
        ShareDataManager.row_num = self.rawDataFrame.row_num
        ShareDataManager.colum_num = self.rawDataFrame.col_num

        columns = [f"TX {idx + 1}" for idx in range(self.rawDataFrame.col_num)]
        index = [f"RX {idx + 1}" for idx in range(self.rawDataFrame.row_num)]


        # if mutual data exists, then initial mutual to frame index 0
        # if mutual data not exists, then set mutual to all zeros
        if self.rawDataFrame.mct_grid is not None:
            mct_df = pd.DataFrame(self.rawDataFrame.mct_grid[0], columns=columns, index=index)
        else:
            mct_df = pd.DataFrame(np.zeros([self.rawDataFrame.row_num, self.rawDataFrame.col_num]), columns=columns,
                                  index=index)
        ShareDataManager.current_grid_data = mct_df.values

        if self.rawDataFrame.sct_col is not None:
            sct_col_df = pd.DataFrame(self.rawDataFrame.sct_col[0], columns=[" "], index=columns).T
            sct_col_max = self.rawDataFrame.sct_col_max
            sct_col_min = self.rawDataFrame.sct_col_min
        else:
            sct_col_df = pd.DataFrame(np.zeros(self.rawDataFrame.col_num), columns=[" "], index=columns).T
            sct_col_max = np.zeros(self.rawDataFrame.col_num)
            sct_col_min = np.zeros(self.rawDataFrame.col_num)

        ShareDataManager.current_col_data = sct_col_df.values
        ShareDataManager.current_col_data_max = sct_col_max
        ShareDataManager.current_col_data_min = sct_col_min

        if self.rawDataFrame.sct_row is not None:
            sct_row_df = pd.DataFrame(self.rawDataFrame.sct_row[0], columns=[" "], index=index)
            sct_row_max = self.rawDataFrame.sct_row_max
            sct_row_min = self.rawDataFrame.sct_row_min
        else:
            sct_row_df = pd.DataFrame(np.zeros(self.rawDataFrame.row_num), columns=[" "], index=index)
            sct_row_max = np.zeros(self.rawDataFrame.row_num)
            sct_row_min = np.zeros(self.rawDataFrame.row_num)

        ShareDataManager.current_row_data = sct_row_df.values.T
        ShareDataManager.current_row_data_max = sct_row_max
        ShareDataManager.current_sct_row_min = sct_row_min

        try:
            self._resetPlotWidget()
        except:
            pass

        # initial grid data table
        mct_model = PandasModel(mct_df)
        self.ui.gridDataViewer.setModel(mct_model)
        self.ui.gridDataViewer.resizeRowsToContents()
        self.ui.gridDataViewer.resizeColumnsToContents()

        # initial sct row table
        sct_row_model = PandasModel(sct_row_df)
        self.ui.sctColDataViewer.setModel(sct_row_model)
        self.ui.sctColDataViewer.resizeRowsToContents()
        self.ui.sctColDataViewer.resizeColumnsToContents()

        # initial sct col table
        sct_col_model = PandasModel(sct_col_df)
        self.ui.sctRowDataViewer.setModel(sct_col_model)
        self.ui.sctRowDataViewer.resizeRowsToContents()
        self.ui.sctRowDataViewer.resizeColumnsToContents()

        self.ui.edit_pageNumber.setText("1")
        self.ui.labelPage.setText(f"/ {len(self.rawDataFrame)}")

        # set buttons to true
        self.ui.slider_pageNumber.setEnabled(True)
        self.ui.slider_pageNumber.setRange(1, len(self.rawDataFrame))

        self.ui.btn_next.setEnabled(True)
        self.ui.btn_previous.setEnabled(True)

        self.ui.btn_inverse.setEnabled(True)
        self.ui.btnPlot3D.setEnabled(True)
        self.ui.btnPlotLine.setEnabled(True)
        self.ui.btnPlotSctDiff.setEnabled(True)

        self.ui.btn_resetPage.setEnabled(True)
        self.ui.edit_maxPage.setEnabled(True)
        self.ui.edit_minPage.setEnabled(True)

        # add data to combo box
        self.ui.comboBox.setFont(QtGui.QFont('Arial', 10))

        self.ui.comboBox.clear()
        self.ui.comboBox.addItem("Mutual Raw Data")
        self.ui.comboBox.addItem("Peak-Peak Noise")
        self.ui.comboBox.addItem("RMS Noise")
        self.ui.comboBox.addItem("Max Mct Pk-Pk Position")
        self.ui.comboBox.addItem("Min Mct Pk-Pk Position")
        self.ui.comboBox.addItem("Max Sct Row Pk-Pk Position")
        self.ui.comboBox.addItem("Min Sct Row Pk-Pk Position")
        self.ui.comboBox.addItem("Max Sct Col Pk-Pk Position")
        self.ui.comboBox.addItem("Min Sct Col Pk-Pk Position")
        self.ui.comboBox.addItem("Mean Value")
        self.ui.comboBox.addItem("SmeanNrmsR Single")
        self.ui.comboBox.addItem("SNppR(Custom)")
        self.ui.comboBox.addItem("Signal Overview")
        self.ui.comboBox.addItem("SmaxNppfullscreenR")
        self.ui.comboBox.addItem("SmaxNppfullscreenR(dB)")
        self.ui.comboBox.addItem("SminNppnotouchnodeR")
        self.ui.comboBox.addItem("SminNppnotouchnodeR(dB)")
        self.ui.comboBox.addItem("SmeanNrmsR Fullscreen")
        self.ui.comboBox.addItem("SmeanNrmsR(dB) Fullscreen")
        self.ui.comboBox.addItem("SminNaveR")
        self.ui.comboBox.addItem("SminNaveR(dB)")


        if str(Func_Plot2DStackBar) in ShareDataManager.subWinTable:
            self._resetStackBarPlotWidget()

    def _setDataFrame(self, pageNum, inverse_flag):
        columns = [f"TX {idx + 1}" for idx in range(self.rawDataFrame.col_num)]
        index = [f"RX {idx + 1}" for idx in range(self.rawDataFrame.row_num)]
        if self.rawDataFrame.mct_grid is not None:
            ShareDataManager.current_grid_data = self.rawDataFrame.mct_grid[pageNum - 1]
            mct_df = pd.DataFrame(ShareDataManager.current_grid_data, columns=columns, index=index)
            mct_model = PandasModel(mct_df) if not inverse_flag else PandasModel(mct_df.T)
            self.ui.gridDataViewer.setModel(mct_model)
            self.ui.gridDataViewer.resizeRowsToContents()
            self.ui.gridDataViewer.resizeColumnsToContents()

        if self.rawDataFrame.sct_row is not None:
            ShareDataManager.current_row_data = self.rawDataFrame.sct_row[pageNum - 1]
            if self.inverse:

                sct_col_df = pd.DataFrame(ShareDataManager.current_row_data, columns=[" "], index=index).T
                sct_col_model = PandasModel(sct_col_df)
                self.ui.sctRowDataViewer.setModel(sct_col_model)
                self.ui.sctRowDataViewer.resizeRowsToContents()
                self.ui.sctRowDataViewer.resizeColumnsToContents()

            else:
                sct_row_df = pd.DataFrame(ShareDataManager.current_row_data, columns=[" "], index=index)
                sct_row_model = PandasModel(sct_row_df)
                self.ui.sctColDataViewer.setModel(sct_row_model)
                self.ui.sctColDataViewer.resizeRowsToContents()
                self.ui.sctColDataViewer.resizeColumnsToContents()

        if self.rawDataFrame.sct_col is not None:
            ShareDataManager.current_col_data = self.rawDataFrame.sct_col[pageNum - 1]
            if self.inverse:
                sct_row_df = pd.DataFrame(ShareDataManager.current_col_data, columns=[" "], index=columns)
                sct_row_model = PandasModel(sct_row_df)
                self.ui.sctColDataViewer.setModel(sct_row_model)
                self.ui.sctColDataViewer.resizeRowsToContents()
                self.ui.sctColDataViewer.resizeColumnsToContents()


            else:
                sct_col_df = pd.DataFrame(ShareDataManager.current_col_data, columns=[" "], index=columns).T
                sct_col_model = PandasModel(sct_col_df)
                self.ui.sctRowDataViewer.setModel(sct_col_model)
                self.ui.sctRowDataViewer.resizeRowsToContents()
                self.ui.sctRowDataViewer.resizeColumnsToContents()

        if str(Func_Plot3Dsurface) in ShareDataManager.subWinTable:
            self._resetPlotWidget()

        if str(Func_Plot2DLine) in ShareDataManager.subWinTable:
            self._resetLinePlotWidget()

    def _setNormalDataFrame(self, inverse_flag):
        columns = [f"TX {idx + 1}" for idx in range(self.rawDataFrame.col_num)]
        index = [f"RX {idx + 1}" for idx in range(self.rawDataFrame.row_num)]
        if self.rawDataFrame.mct_grid is not None:
            mct_df = pd.DataFrame(ShareDataManager.current_grid_data, columns=columns, index=index)
            mct_model = PandasModel(mct_df) if not inverse_flag else PandasModel(mct_df.T)
            self.ui.gridDataViewer.setModel(mct_model)
            self.ui.gridDataViewer.resizeRowsToContents()
            self.ui.gridDataViewer.resizeColumnsToContents()

        if self.rawDataFrame.sct_row is not None:
            if self.inverse:
                sct_row_df = pd.DataFrame(ShareDataManager.current_row_data, columns=[" "], index=index).T
                sct_row_model = PandasModel(sct_row_df)
                self.ui.sctRowDataViewer.setModel(sct_row_model)
                self.ui.sctRowDataViewer.resizeRowsToContents()
                self.ui.sctRowDataViewer.resizeColumnsToContents()
            else:
                sct_col_df = pd.DataFrame(ShareDataManager.current_row_data, columns=[" "], index=index)
                sct_col_model = PandasModel(sct_col_df)
                self.ui.sctColDataViewer.setModel(sct_col_model)
                self.ui.sctColDataViewer.resizeRowsToContents()
                self.ui.sctColDataViewer.resizeColumnsToContents()

        if self.rawDataFrame.sct_col is not None:
            if self.inverse:
                sct_col_df = pd.DataFrame(ShareDataManager.current_col_data, columns=[" "], index=columns)
                sct_col_model = PandasModel(sct_col_df)
                self.ui.sctColDataViewer.setModel(sct_col_model)
                self.ui.sctColDataViewer.resizeRowsToContents()
                self.ui.sctColDataViewer.resizeColumnsToContents()
            else:
                sct_row_df = pd.DataFrame(ShareDataManager.current_col_data, columns=[" "], index=columns).T
                sct_row_model = PandasModel(sct_row_df)
                self.ui.sctRowDataViewer.setModel(sct_row_model)
                self.ui.sctRowDataViewer.resizeRowsToContents()
                self.ui.sctRowDataViewer.resizeColumnsToContents()

        if str(Func_Plot3Dsurface) in ShareDataManager.subWinTable:
            self._resetPlotWidget()

        if str(Func_Plot2DLine) in ShareDataManager.subWinTable:
            self._resetLinePlotWidget()

    def editPagePressed(self):
        if not self.rawDataFrame:
            QMessageBox.warning(
                self.ui,
                'File Error',
                'Could not find Mutual raw data, please select right file path first!')
        else:

            page = self.ui.edit_pageNumber.text()
            try:
                page = int(page)
            except Exception as e:
                QMessageBox.warning(
                    self.ui,
                    'Error',
                    str(e))
            else:
                page = int(page)
                if page < 1:
                    page = 1
                    self.ui.edit_pageNumber.setText(str(page))
                    self._setDataFrame(0, self.inverse)
                elif page > len(self.rawDataFrame):
                    page = len(self.rawDataFrame) + 1
                    self.ui.edit_pageNumber.setText(str(page))
                    self._setDataFrame(len(self.rawDataFrame), self.inverse)

                else:
                    self._setDataFrame(page, self.inverse)

                self.ui.slider_pageNumber.setValue(page)

    def zoom_In(self):
        font_value = self.ui.edit_fontSize.text()
        self.FontSize = min(int(font_value) + 1, 20)
        self.ui.edit_fontSize.setText(str(self.FontSize))
        self.ui.gridDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.gridDataViewer.resizeRowsToContents()
        self.ui.gridDataViewer.resizeColumnsToContents()

        self.ui.sctColDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.sctColDataViewer.resizeRowsToContents()
        self.ui.sctColDataViewer.resizeColumnsToContents()

        self.ui.sctRowDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.sctRowDataViewer.resizeRowsToContents()
        self.ui.sctRowDataViewer.resizeColumnsToContents()

    def zoom_Out(self):
        font_value = int(self.ui.edit_fontSize.text())
        self.FontSize = max(int(font_value) - 1, 5)
        self.ui.edit_fontSize.setText(str(self.FontSize))
        self.ui.gridDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.gridDataViewer.resizeRowsToContents()
        self.ui.gridDataViewer.resizeColumnsToContents()

        self.ui.sctColDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.sctColDataViewer.resizeRowsToContents()
        self.ui.sctColDataViewer.resizeColumnsToContents()

        self.ui.sctRowDataViewer.setFont(QtGui.QFont('Arial', self.FontSize))
        self.ui.sctRowDataViewer.resizeRowsToContents()
        self.ui.sctRowDataViewer.resizeColumnsToContents()

    def _open3DPlotWidget(self):
        self._openSubWin(Func_Plot3Dsurface)
        self._resetPlotWidget()

    def _open2DPlotWidget(self):
        self._openSubWin(Func_Plot2DLine)
        self._resetLinePlotWidget()

    def _open2DStackBarWidget(self):
        self._openSubWin(Func_Plot2DStackBar)
        # self._resetLinePlotWidget()

    def _resetPlotWidget(self):
        plotWidget: Func_Plot3Dsurface = ShareDataManager.subWinTable[str(Func_Plot3Dsurface)]
        plotWidget.modifier.fillSqrtSinProxy(ShareDataManager.current_grid_data)

    def _resetLinePlotWidget(self):

        plotWidget: Func_Plot2DLine = ShareDataManager.subWinTable[str(Func_Plot2DLine)]
        # reset Rx
        plotWidget.series_Rx.clear()
        plotWidget.set_Rx = QBarSet("Self Cap. Rx")
        data_Rx = ShareDataManager.current_row_data.flatten()
        plotWidget.set_Rx.append(list(data_Rx))
        plotWidget.series_Rx.append(plotWidget.set_Rx)

        plotWidget.chart_Rx.axisY(plotWidget.series_Rx).setRange(int(ShareDataManager.current_row_data.min()), int(ShareDataManager.current_row_data.max()))
        plotWidget.chart_Rx.axisY(plotWidget.series_Rx).setLabelFormat("%d")
        plotWidget.chart_Rx.update()
        # reset Tx
        plotWidget.series_Tx.clear()
        plotWidget.set_Tx = QBarSet("Self Cap. Tx")
        plotWidget.set_Tx.append(list(ShareDataManager.current_col_data.flatten()))
        plotWidget.series_Tx.append(plotWidget.set_Tx)

        plotWidget.chart_Tx.axisY(plotWidget.series_Tx).setRange(int(ShareDataManager.current_col_data.min()), int(ShareDataManager.current_col_data.max()))
        plotWidget.chart_Tx.update()

    def _resetStackBarPlotWidget(self):

        plotWidget: Func_Plot2DStackBar = ShareDataManager.subWinTable[str(Func_Plot2DStackBar)]
        # reset Rx
        plotWidget.series_Rx.clear()
        plotWidget.rx_Low = QBarSet("Min")
        plotWidget.rx_High = QBarSet("Max")
        Rx_low_data = ShareDataManager.current_sct_row_min.flatten()
        Rx_high_data = ShareDataManager.current_row_data_max.flatten()
        plotWidget.rx_Low.append(list(Rx_low_data))
        plotWidget.rx_High.append(list(Rx_high_data))
        plotWidget.series_Rx.append(plotWidget.rx_Low)
        plotWidget.series_Rx.append(plotWidget.rx_High)
        plotWidget.chart_Rx.axisY(plotWidget.series_Rx).setRange(int(self.rawDataFrame.sct_row.min()), int(self.rawDataFrame.sct_row.max()))
        plotWidget.chart_Rx.update()

        # reset Tx
        plotWidget.series_Tx.clear()
        plotWidget.tx_Low = QBarSet("Min")
        plotWidget.tx_High = QBarSet("Max")
        Tx_low_data = ShareDataManager.current_col_data_min.flatten()
        Tx_high_data = ShareDataManager.current_col_data_max.flatten()
        plotWidget.tx_Low.append(list(Tx_low_data))
        plotWidget.tx_High.append(list(Tx_high_data))
        plotWidget.series_Tx.append(plotWidget.tx_Low)
        plotWidget.series_Tx.append(plotWidget.tx_High)
        plotWidget.chart_Tx.axisY(plotWidget.series_Tx).setRange(int(self.rawDataFrame.sct_col.min()), int(self.rawDataFrame.sct_col.max()))
        plotWidget.chart_Tx.update()

    def _openSubWin(self, FuncClass):
        def createSubWin():
            subWinFunc = FuncClass()
            subWinFunc.setAttribute(Qt.WA_DeleteOnClose)
            # 存入表中，注意winFunc对象也要保存，不然对象没有引用，会销毁
            ShareDataManager.subWinTable[str(FuncClass)] = subWinFunc

            subWinFunc.show()
            # 子窗口提到最上层
            subWinFunc.setWindowState(Qt.WindowActive)

        # 如果该功能类型 实例不存在
        if str(FuncClass) not in ShareDataManager.subWinTable:
            # 创建实例
            createSubWin()
            return

        # 如果已经存在，直接show一下
        subWinFunc = ShareDataManager.subWinTable[str(FuncClass)]
        try:
            subWinFunc.show()
            # 子窗口提到最上层，并且最大化
            subWinFunc.setWindowState(Qt.WindowActive)
        except:
            # show 异常原因肯定是用户手动关闭了该窗口，subWin对象已经不存在了

            createSubWin()

#
# if __name__ == '__main__':
#     app = QApplication([])
#     mainWin = Win_Main()
#     mainWin.ui.show()
#
#     app.exec()
