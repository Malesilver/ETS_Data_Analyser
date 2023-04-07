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


class Win_Main(QtWidgets.QMainWindow):

    def __init__(self):
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

    def onCfgSetting(self):
        self._openSubWin(Win_CfgSetting)

    def onSNR_Data_Viewer(self):
        self._openSubWin(Win_SNRDataViewer)

    def onPatternGenerator(self):
        self._openSubWin(Win_Pattern_Generator)

    def onAPL_Analysis(self):
        self._openSubWin(Win_APL_Analysis)

    def onBOE_SNRGenerator(self):
        self._openSubWin(Win_BOE_SNRGenerator)

    def onBOE_SNRGenerator_2(self):
        self._openSubWin(Win_BOE_SNRGenerator_2)

    def onHW_THP_SNRGenerator(self):
        self._openSubWin(Win_HW_THP_SNRGenerator)

    def onDataViewer(self):
        self._openSubWin(Win_DataViewer)

    def _openSubWin(self,FuncClass):
        def createSubWin():
            subWinFunc = FuncClass()
            subWin = QMdiSubWindow()
            subWin.setWidget(subWinFunc.ui)
            subWin.setAttribute(Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(subWin)
            # 存入表中，注意winFunc对象也要保存，不然对象没有引用，会销毁
            SI.subWinTable[str(FuncClass)] = {'subWin':subWin,'subWinFunc':subWinFunc}
            subWin.show()
            # 子窗口提到最上层，并且最大化
            subWin.setWindowState(Qt.WindowActive|Qt.WindowMaximized)

        # 如果该功能类型 实例不存在
        if str(FuncClass) not in SI.subWinTable:
            #创建实例
            createSubWin()
            return

        # 如果已经存在，直接show一下
        subWin = SI.subWinTable[str(FuncClass)]['subWin']
        try:
            subWin.show()
            # 子窗口提到最上层，并且最大化
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
        except:
            # show 异常原因肯定是用户手动关闭了该窗口，subWin对象已经不存在了
            createSubWin()

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
        return super(Win_Main, self).eventFilter(obj, event)

    def closeEvent(self):
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
    SI.loadCfgFile()
    app = QApplication(sys.argv)
    mainWin = Win_Main()
    mainWin.ui.show()


    app.exec()
