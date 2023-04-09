from PySide6.QtWidgets import QApplication, QMessageBox, QMdiSubWindow, QTreeWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot
import sys
from lib.share import SI
from cfg_setting import Win_CfgSetting
from data_viewer import Win_DataViewer
from BOE_snr_generator import Win_BOE_SNRGenerator
from BOE_snr_generator_2 import Win_BOE_SNRGenerator_2
from HW_THP_snr_generator import Win_HW_THP_SNRGenerator
from pattern_generator import Win_Pattern_Generator
from snr_data_viewer import Win_SNRDataViewer
from APL_Analysis import Win_APL_Analysis
from general_snr_generator import WinGeneralSNRGenerator


class Win_Main(QtWidgets.QMainWindow):
    """
    main window class
    """

    def __init__(self):
        """
        init main window class
        """
        super(Win_Main, self).__init__()
        self.ui = QUiLoader().load('data_analyser_main.ui')
        self.ui.installEventFilter(self)


        self.ui.actionSetting.triggered.connect(self.onCfgSetting)
        self.ui.actionBOE_SNR_report.triggered.connect(self.onBOE_SNRGenerator)
        self.ui.actionData_Viewer.triggered.connect(self.onDataViewer)
        self.ui.actionHW_THP_SNR_report.triggered.connect(self.onHW_THP_SNRGenerator)
        self.ui.actionPattern_Generator.triggered.connect(self.onPatternGenerator)

        self.ui.actionExit.triggered.connect(self.closeEvent)
        self.ui.action_BOE_SNR_reporter_2.triggered.connect(self.onBOE_SNRGenerator_2)
        self.ui.actionSNR_Data_Viewer.triggered.connect(self.onSNR_Data_Viewer)
        self.ui.actionAPL_Analysis.triggered.connect(self.onAPL_Analysis)
        self.ui.actionGeneral_SNR_report.triggered.connect(self.onGeneralSNRGenerator)

    def onCfgSetting(self):
        """
        open cfg setting window
        :return: None
        """
        self._openSubWin(Win_CfgSetting)

    def onSNR_Data_Viewer(self):
        """
        open SNR Data Viewer window
        :return: None
        """
        self._openSubWin(Win_SNRDataViewer)

    def onPatternGenerator(self):
        """
        open Pattern Generator window
        :return: None
        """
        self._openSubWin(Win_Pattern_Generator)

    def onAPL_Analysis(self):
        """
        open APL Analysis window
        :return: None
        """
        self._openSubWin(Win_APL_Analysis)

    def onBOE_SNRGenerator(self):
        """
        open BOE SNR Generator window
        :return: None
        """
        self._openSubWin(Win_BOE_SNRGenerator)

    def onBOE_SNRGenerator_2(self):
        """
        open BOE SNR Generator window
        :return: None
        """
        self._openSubWin(Win_BOE_SNRGenerator_2)

    def onHW_THP_SNRGenerator(self):
        """
        open HW THP SNR Generator window
        :return: None
        """
        self._openSubWin(Win_HW_THP_SNRGenerator)

    def onGeneralSNRGenerator(self):
        """
        open General SNR Generator window
        :return: None
        """
        self._openSubWin(WinGeneralSNRGenerator)

    def onDataViewer(self):
        """
        open Data Viewer window
        :return:None
        """
        self._openSubWin(Win_DataViewer)

    def _openSubWin(self,FuncClass):
        """
        generic open sub window function
        :param FuncClass: sub window class
        :return: None
        """
        def createSubWin():
            # create sub window instance
            subWinFunc = FuncClass()
            subWin = QMdiSubWindow()
            subWin.setWidget(subWinFunc.ui)
            subWin.setAttribute(Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(subWin)
            # add sub window instance to subWinTable, key is sub window class name , value is sub window instance
            # if sub window instance already exist, just show it
            SI.subWinTable[str(FuncClass)] = {'subWin':subWin,'subWinFunc':subWinFunc}
            subWin.show()
            # sub window always on top and maximized
            subWin.setWindowState(Qt.WindowActive|Qt.WindowMaximized)

        # if sub window instance not exist, create it
        if str(FuncClass) not in SI.subWinTable:
            # create sub window instance
            createSubWin()
            return

        # if sub window instance already exist, just show it
        subWin = SI.subWinTable[str(FuncClass)]['subWin']
        try:
            subWin.show()
            # sub window always on top and maximized
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
        except:
            # if sub window instance already exist but closed, create it again
            createSubWin()

    def eventFilter(self, obj, event):
        # judge if obj is self.ui and event type is close event
        if obj is self.ui and event.type() == QtCore.QEvent.Close:
            reply = QtWidgets.QMessageBox.question(self.ui, 'Message',
                                                   "Are you sure to quit?",
                                                   QtWidgets.QMessageBox.Yes |
                                                   QtWidgets.QMessageBox.No
                                                   )

            # return True to stop event propagation
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
                self.ui.removeEventFilter(self)
            else:
                event.ignore()
            return True
        return super(Win_Main, self).eventFilter(obj, event)

    def closeEvent(self):
        """
        close event
        :return: None
        """
        # message为窗口标题
        # Are you sure to quit?窗口显示内容
        # QtWidgets.QMessageBox.Yes | QtGui.QMessageBox.No窗口按钮部件
        # QtWidgets.QMessageBox.No默认焦点停留在NO上
        # reply = QtWidgets.QMessageBox.question(self, 'Message',
        #                                        "Are you sure to quit?",
        #                                        QtWidgets.QMessageBox.Yes |
        #                                        QtWidgets.QMessageBox.No,
        #                                        QtWidgets.QMessageBox.No)
        # # 判断返回结果处理相应事项
        # if reply == QMessageBox.Yes:
        QApplication.quit()
        # else:
        #     pass


if __name__ == '__main__':
    # load cfg file
    SI.loadCfgFile()
    # create main window instance
    app = QApplication(sys.argv)
    mainWin = Win_Main()
    mainWin.ui.show()

    app.exec()
