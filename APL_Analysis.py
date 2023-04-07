from PySide6.QtWidgets import QMessageBox, QTableWidgetItem,QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore

import os
from lib.share import SI, MySignals
from threading import Thread
import json
from PySide6.QtCore import Qt
import pandas as pd
from APL_Tools import Setup,Accuracy_RoT,Jitter,Precision_RoT,Linearity_RoT
from enum import Enum
from lib.apl_calibration_plot import Func_PlotAPLCalib
from lib.apl_accuracy_plot import Func_PlotAPLAccuracy
from lib.apl_precision_plot import Func_PlotAPLPrecision
from lib.apl_linearity_plot import Func_PlotAPLLinearity
from lib.APL_share import APL_Share


gms = MySignals()

class TestSpec(str,Enum):
    Edge = "lineEditEdge"
    AccuracyFull = 'lineEdit_AccuracyFull'
    AccuracyCentre = 'lineEdit_AccuracyCtr'
    PrecisionFull = 'lineEdit_PrecisionFull'
    PrecisionCentre = 'lineEdit_PrecisionCtr'
    LinearityFull = 'lineEdit_LinearityFull'
    LinearityCentre = 'lineEdit_LinearityCtr'
    JitterFull = 'lineEdit_JitterFull'
    JitterCentre = 'lineEdit_JitterCtr'
    InverseX = "cBoxInverseX"
    InverseY = "cBoxInverseY"
    SwapAxis = "cBoxSwapeAxis"


class Win_APL_Analysis(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load('APL_Analysis.ui')
        self.ETSPath = None
        self.RobotPath = None

        gms.log.connect(self.log)
        self._loadCfgToTable()
        self._loadTestSpec()

        self.ui.btnLoadCfg.clicked.connect(self._loadCfgCSV)
        self.ui.btnClear.clicked.connect(self.onClearLog)
        self.ui.tableCFG.cellChanged.connect(self.cfgItemChanged)
        self.ui.btnLoadETS.clicked.connect(self._selectFileETS)
        self.ui.btnLoadRobot.clicked.connect(self._selectFileRobot)

        self.ui.btnCalibration.clicked.connect(self.onCalibration)
        self.ui.btnAccuracy.clicked.connect(self.onAccuracy)
        self.ui.btnPrecision.clicked.connect(self.onPrecision)
        self.ui.btnLinear.clicked.connect(self.onLinearity)
        self.ui.btnJitter.clicked.connect(self.onJitter)


        self.ui.cBoxInverseX.stateChanged.connect(self.changeCheckBox)
        self.ui.cBoxInverseY.stateChanged.connect(self.changeCheckBox)
        self.ui.cBoxSwapeAxis.stateChanged.connect(self.changeCheckBox)




    def _loadCfgCSV(self):
        root_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = os.path.join(root_directory,"APL_Result")
        if not os.path.exists(current_directory):
            os.makedirs(current_directory)
        filepath, type = QFileDialog.getOpenFileName(self.ui, "Select DUT info fime", current_directory, 'csv(*.csv)')

        if filepath is not None:

            cfg_df = pd.read_csv(filepath)
            cfg_df = cfg_df.set_index("variable name")["value"]

            # convert dataframe to dict
            SI.APL_cfg = cfg_df.to_dict()
            self._saveCfgFile()
            self._loadCfgToTable()

    def _loadTestSpec(self):

        if SI.APL_Spec:
            if eval(SI.APL_Spec.get("X_invert", 'False')):
                self.ui.cBoxInverseX.setChecked(True)
            else:
                self.ui.cBoxInverseX.setChecked(False)
            if eval(SI.APL_Spec.get("Y_invert", 'False')):
                self.ui.cBoxInverseY.setChecked(True)
            else:
                self.ui.cBoxInverseY.setChecked(False)
            if eval(SI.APL_Spec.get("Axis_Swap", 'False')):
                self.ui.cBoxSwapeAxis.setChecked(True)
            else:
                self.ui.cBoxSwapeAxis.setChecked(False)


            self.ui.lineEditEdge.setText(SI.APL_Spec.get("Edge", '0'))
            self.ui.lineEdit_AccuracyFull.setText(SI.APL_Spec.get("Accuracy_Full", '0'))
            self.ui.lineEdit_AccuracyCtr.setText(SI.APL_Spec.get("Accuracy_Centre", '0'))
            self.ui.lineEdit_PrecisionFull.setText(SI.APL_Spec.get("Precision_Full", '0'))
            self.ui.lineEdit_PrecisionCtr.setText(SI.APL_Spec.get("Precision_Centre", '0'))
            self.ui.lineEdit_LinearityFull.setText(SI.APL_Spec.get("Linearity_Full", '0'))
            self.ui.lineEdit_LinearityCtr.setText(SI.APL_Spec.get("Linearity_Centre", '0'))
            self.ui.lineEdit_JitterFull.setText(SI.APL_Spec.get("StationaryJitter_Full", '0'))
            self.ui.lineEdit_JitterCtr.setText(SI.APL_Spec.get("StationaryJitter_Centre", '0'))

            self.ui.lineEditEdge.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_AccuracyFull.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_AccuracyCtr.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_PrecisionFull.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_PrecisionCtr.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_LinearityFull.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_LinearityCtr.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_JitterFull.editingFinished.connect(self.changeLineEdit)
            self.ui.lineEdit_JitterCtr.editingFinished.connect(self.changeLineEdit)



    # 加载配置文件到界面
    def _loadCfgToTable(self):
        table = self.ui.tableCFG
        table.blockSignals(True)
        table.setRowCount(0)
        table.clearContents()
        for idx, cfgName in enumerate(SI.APL_cfg.keys()):
            # 插入一行
            table.insertRow(idx)

            # 参数名
            item = QTableWidgetItem(cfgName)
            table.setItem(idx, 0, item)
            item.setFlags(Qt.ItemIsEnabled)  # 参数名字段不允许修改

            # 参数值
            table.setItem(idx, 1, QTableWidgetItem(str(SI.APL_cfg.get(cfgName, ''))))

        table.blockSignals(False)
    def cfgItemChanged(self, row, column):
        table = self.ui.tableCFG

        # 获取更改内容
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, column).text()

        SI.APL_cfg[cfgName] = cfgValue
        self._saveCfgFile()

        self.log(f'{cfgName} : {cfgValue}')


    def _saveCfgFile(self):

        with open('APL_cfg.json', 'w', encoding='utf8') as f:
            json.dump(SI.APL_cfg, f, ensure_ascii=False, indent=2)

    def _saveSpecFile(self):

        with open('APL_Screen_Spec.json', 'w', encoding='utf8') as f:
            json.dump(SI.APL_Spec, f, ensure_ascii=False, indent=2)

    def _selectFileETS(self):
        root_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = os.path.join(root_directory, "APL_Result")
        filepath, type = QFileDialog.getOpenFileName(self.ui, "Select ETS Data", current_directory, 'csv(*.csv)')
        if filepath is None:
            return
        self.ETSPath = filepath
        self.ui.lineEditETSPath.setText(filepath)
        self.ui.lineEditETSPath.setEnabled(False)

    def _selectFileRobot(self):
        root_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = os.path.join(root_directory, "APL_Result")
        filepath, type = QFileDialog.getOpenFileName(self.ui, "Select Robot Data", current_directory, 'csv(*.csv)')
        if filepath is None:
            return
        self.RobotPath = filepath
        self.ui.lineEditRobotPath.setText(filepath)
        self.ui.lineEditRobotPath.setEnabled(False)

    def _saveAPLResults(self,output_data,output_data_centre,test_type,full_value,results,centre_value,results_centre,filename):
        comment = "this should contain the finger size and speed of the finger and any other important information for the tests conditions"

        output_data.to_excel(filename, index=False, header=True)

        with pd.ExcelWriter(filename) as writer:
            output_data.to_excel(writer, sheet_name='Full touch sensor', index=False, header=True, startrow=2,
                                 startcol=0)

            output_data_centre.to_excel(writer, sheet_name='Centre', index=False, header=True, startrow=1,
                                        startcol=0)

            text_2 = 'The results for the centre ' + test_type + " : " + results_centre + " - " + str(
                centre_value) + "mm" + "\n"
            worksheet = writer.sheets['Centre']
            worksheet.write(0, 0, text_2)

            worksheet = writer.sheets['Full touch sensor']
            text_1 = 'The result of the full touch sensor ' + test_type + " : " + results + " - " + str(
                full_value) + "mm" + "\n"
            worksheet.write(1, 0, text_1)
            worksheet.write(0, 0, comment)

            setupvariables = pd.DataFrame.from_dict(SI.APL_cfg,orient='index')
            setupvariables.to_excel(writer, sheet_name='Settings', index=False, header=True, startrow=0,
                                    startcol=0)


    def onCalibration(self):

        robot_data = self.RobotPath
        touch_data = self.ETSPath
        try:
            touch_data = pd.read_csv(touch_data)
            robot_data = pd.read_csv(robot_data)
        except:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Data Path for ETS and Robot!!!')
            return
        root_directory = os.path.dirname(os.path.abspath(__file__))
        test_directory = os.path.join(root_directory, "APL_Result")

        # try:
        if self.ui.rScalleOffset.isChecked():

            list_coef, before_align, after_align = Setup.align(touch_data, robot_data, SI.APL_cfg,SI.APL_Spec, test_directory)

            SI.APL_cfg['DutXScalingFactor'] = (float(list_coef[0][0]))
            SI.APL_cfg['DutActiveOffsetLR'] = (float(list_coef[0][1]))
            SI.APL_cfg['DutYScalingFactor'] = (float(list_coef[1][0]))
            SI.APL_cfg['DutActiveOffsetUD'] = (float(list_coef[1][1]))

            self._loadCfgToTable()
            gms.log.emit("*****************before calibration**************")
            gms.log.emit(str(before_align))

            gms.log.emit("*****************After Scale Offset calibration**************")
            gms.log.emit(str(after_align))




        if self.ui.rAffine.isChecked():
            calibration_matrix, before_align, after_align = Setup.align_Affine_Transform(touch_data, robot_data, SI.APL_cfg, SI.APL_Spec,
                                                               test_directory,method = "Affine")


            self._loadCfgToTable()
            gms.log.emit("*****************before calibration**************")
            gms.log.emit(str(before_align))

            gms.log.emit("*****************After Affine Transform calibration**************")
            gms.log.emit(str(after_align))

            gms.log.emit("***************** Affine Transform Matrix**************")
            gms.log.emit(str(calibration_matrix))

        if self.ui.rHomograph.isChecked():
            calibration_matrix, before_align, after_align = Setup.align_Affine_Transform(touch_data, robot_data, SI.APL_cfg, SI.APL_Spec,
                                                               test_directory,method = "Homography")


            self._loadCfgToTable()
            gms.log.emit("*****************before calibration**************")
            gms.log.emit(str(before_align))

            gms.log.emit("*****************After Affine Transform calibration**************")
            gms.log.emit(str(after_align))

            gms.log.emit("***************** Affine Transform Matrix**************")
            gms.log.emit(str(calibration_matrix))
        # except:
        #     gms.log.emit("***************** Calibration failed **************")
        #     gms.log.emit("***************** Please check raw data **************")

        APL_Share.WinCalibResult = Func_PlotAPLCalib()
        APL_Share.WinCalibResult.show()


    def onAccuracy(self):

        robot_data = self.RobotPath
        touch_data = self.ETSPath
        try:
            touch_data = pd.read_csv(touch_data)
            robot_data = pd.read_csv(robot_data)
        except:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Data Path for ETS and Robot!!!')
            return
        root_directory = os.path.dirname(os.path.abspath(__file__))
        test_directory = os.path.join(root_directory, "APL_Result")

        edge = int(self.ui.lineEditEdge.text())

        if self.ui.rScalleOffset.isChecked():
            sensor = Setup.data_Setup(touch_data, SI.APL_cfg, SI.APL_Spec,align_tuning=False)

        else:
            sensor = Setup.data_Setup_Affine_Transform(touch_data, SI.APL_cfg, SI.APL_Spec,test_directory, align_tuning=False)

        output_data, output_data_centre, results, results_centre, centre_value, full_value = Accuracy_RoT.accuracy_RoT(
            sensor, robot_data, SI.APL_cfg, SI.APL_Spec,edge, test_directory)

        self._saveAPLResults(output_data=output_data,output_data_centre=output_data_centre,test_type="Accuracy",full_value=full_value,
                             results=results,centre_value=centre_value,results_centre=results_centre,
                             filename=os.path.join(test_directory,"APL_Result_Accuracy.xlsx"))
        APL_Share.WinAccuracyResult = Func_PlotAPLAccuracy()
        APL_Share.WinAccuracyResult.show()

        gms.log.emit("*"*30)
        gms.log.emit(f"The result for Accuracy fullscreen is {results}, and worst case for fullscreen is {full_value}")
        gms.log.emit(f"The result for Accuracy centre is {results_centre}, and worst case for centre is {centre_value}")
        gms.log.emit(f"Result figure is saved to the path: {test_directory}")

        gms.log.emit("*" * 30)


    def onPrecision(self):

        robot_data = self.RobotPath
        touch_data = self.ETSPath
        try:
            touch_data = pd.read_csv(touch_data)
            robot_data = pd.read_csv(robot_data)
        except:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Data Path for ETS and Robot!!!')
            return
        root_directory = os.path.dirname(os.path.abspath(__file__))
        test_directory = os.path.join(root_directory, "APL_Result")

        edge = int(self.ui.lineEditEdge.text())
        number_of_repeats = int(SI.APL_cfg["TestNoTaps"])

        if self.ui.rScalleOffset.isChecked():
            sensor = Setup.data_Setup(touch_data, SI.APL_cfg, SI.APL_Spec,align_tuning=False)

        else:
            sensor = Setup.data_Setup_Affine_Transform(touch_data, SI.APL_cfg, SI.APL_Spec,test_directory, align_tuning=False)

        output_data, output_data_centre, results, results_centre, centre_value, full_value = Precision_RoT.precision_RoT(
            sensor, robot_data,number_of_repeats, SI.APL_cfg, SI.APL_Spec,edge, test_directory)

        self._saveAPLResults(output_data=output_data, output_data_centre=output_data_centre, test_type="Precision",
                             full_value=full_value,
                             results=results, centre_value=centre_value, results_centre=results_centre,
                             filename=os.path.join(test_directory, "APL_Result_Precision.xlsx"))

        APL_Share.WinPrecisionResult = Func_PlotAPLPrecision()
        APL_Share.WinPrecisionResult.show()

        gms.log.emit("*"*30)
        gms.log.emit(f"The result for Precision fullscreen is {results}, and worst case for fullscreen is {full_value}")
        gms.log.emit(f"The result for Precision centre is {results_centre}, and worst case for centre is {centre_value}")
        gms.log.emit(f"Result figure is saved to the path: {test_directory}")

        gms.log.emit("*" * 30)

    def onLinearity(self):

        robot_data = self.RobotPath
        touch_data = self.ETSPath
        try:
            touch_data = pd.read_csv(touch_data)
            robot_data = pd.read_csv(robot_data)
        except:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Data Path for ETS and Robot!!!')
            return
        root_directory = os.path.dirname(os.path.abspath(__file__))
        test_directory = os.path.join(root_directory, "APL_Result")

        edge = int(self.ui.lineEditEdge.text())

        if self.ui.rScalleOffset.isChecked():
            sensor = Setup.data_Setup(touch_data, SI.APL_cfg, SI.APL_Spec,align_tuning=False)

        else:
            sensor = Setup.data_Setup_Affine_Transform(touch_data, SI.APL_cfg, SI.APL_Spec,test_directory, align_tuning=False)

        output_data, output_data_centre, results, results_centre, centre_value, full_value = Linearity_RoT.linearity_RoT(
            sensor, SI.APL_cfg, SI.APL_Spec,edge, test_directory)

        self._saveAPLResults(output_data=output_data, output_data_centre=output_data_centre, test_type="Linearity",
                             full_value=full_value,
                             results=results, centre_value=centre_value, results_centre=results_centre,
                             filename=os.path.join(test_directory, "APL_Result_Linearity.xlsx"))

        APL_Share.WinLinearityResult = Func_PlotAPLLinearity()
        APL_Share.WinLinearityResult.show()

        gms.log.emit("*"*30)
        gms.log.emit(f"The result for Linearity fullscreen is {results}, and worst case for fullscreen is {full_value}")
        gms.log.emit(f"The result for Linearity centre is {results_centre}, and worst case for centre is {centre_value}")
        gms.log.emit(f"Result figure is saved to the path: {test_directory}")

        gms.log.emit("*" * 30)


    def onJitter(self):

        robot_data = self.RobotPath
        touch_data = self.ETSPath
        try:
            touch_data = pd.read_csv(touch_data)
            robot_data = pd.read_csv(robot_data)
        except:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Data Path for ETS and Robot!!!')
            return
        root_directory = os.path.dirname(os.path.abspath(__file__))
        test_directory = os.path.join(root_directory, "APL_Result")

        edge = int(self.ui.lineEditEdge.text())

        if self.ui.rScalleOffset.isChecked():
            sensor = Setup.data_Setup(touch_data, SI.APL_cfg, SI.APL_Spec,align_tuning=False)

        else:
            sensor = Setup.data_Setup_Affine_Transform(touch_data, SI.APL_cfg, SI.APL_Spec,test_directory, align_tuning=False)

        output_data, output_data_centre, results, results_centre, centre_value, full_value = Jitter.jitter(
            sensor, robot_data,SI.APL_cfg, SI.APL_Spec,edge)

        self._saveAPLResults(output_data=output_data, output_data_centre=output_data_centre, test_type="Jitter",
                             full_value=full_value,
                             results=results, centre_value=centre_value, results_centre=results_centre,
                             filename=os.path.join(test_directory, "APL_Result_Jitter.xlsx"))

        gms.log.emit("*"*30)
        gms.log.emit(f"The result for Jitter fullscreen is {results}, and worst case for fullscreen is {full_value}")
        gms.log.emit(f"The result for Jitter centre is {results_centre}, and worst case for centre is {centre_value}")
        gms.log.emit(f"Result figure is saved to the path: {test_directory}")

        gms.log.emit("*" * 30)

    def changeLineEdit(self):

        obj = self.sender().objectName()
        if obj == TestSpec.Edge:
            value = self.ui.lineEditEdge.text()
            SI.APL_Spec["Edge"] = value
        elif obj == TestSpec.AccuracyFull:
            value = self.ui.lineEdit_AccuracyFull.text()
            SI.APL_Spec["Accuracy_Full"] = value
        elif obj == TestSpec.AccuracyCentre:
            value = self.ui.lineEdit_AccuracyCtr.text()
            SI.APL_Spec["Accuracy_Centre"] = value
        elif obj == TestSpec.PrecisionFull:
            value = self.ui.lineEdit_PrecisionFull.text()
            SI.APL_Spec["Precision_Full"] = value
        elif obj == TestSpec.PrecisionCentre:
            value = self.ui.lineEdit_PrecisionCtr.text()
            SI.APL_Spec["Precision_Centre"] = value
        elif obj == TestSpec.JitterFull:
            value = self.ui.lineEdit_JitterFull.text()
            SI.APL_Spec["StationaryJitter_Full"] = value
        elif obj == TestSpec.JitterCentre:
            value = self.ui.lineEdit_JitterCtr.text()
            SI.APL_Spec["StationaryJitter_Centre"] = value
        elif obj == TestSpec.LinearityFull:
            value = self.ui.lineEdit_LinearityFull.text()
            SI.APL_Spec["Linearity_Full"] = value
        elif obj == TestSpec.LinearityCentre:
            value = self.ui.lineEdit_LinearityCtr.text()

            SI.APL_Spec["Linearity_Centre"] = value
        else:
            value = "None"

        self._saveSpecFile()

        gms.log.emit(f"Already change {obj} to {value}")

    def changeCheckBox(self):

        obj = self.sender().objectName()
        if obj == TestSpec.InverseX:
            value = "True" if self.ui.cBoxInverseX.isChecked() else "False"
            SI.APL_Spec["X_invert"] = value
        elif obj == TestSpec.InverseY:
            value = "True" if self.ui.cBoxInverseY.isChecked() else "False"
            SI.APL_Spec["Y_invert"] = value
        elif obj == TestSpec.SwapAxis:
            value = "True" if self.ui.cBoxSwapeAxis.isChecked() else "False"
            SI.APL_Spec["Axis_Swap"] = value
        self._saveSpecFile()
        gms.log.emit(f"Already change {obj} to {value}")

    def onClearLog(self):
        self.ui.textBrowser.clear()

    def log(self, *texts):
        self.ui.textBrowser.append(' '.join(texts))
        self.ui.textBrowser.ensureCursorVisible()

