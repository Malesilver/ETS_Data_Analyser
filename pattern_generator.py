from PySide6.QtWidgets import QMessageBox, QTableWidgetItem,QFileDialog
from PySide6.QtUiTools import QUiLoader

import os
from lib.share import SI, MySignals
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv, HEADER_ETS
from threading import Thread
import json
from PySide6.QtCore import Qt
from lib.create_pattern import *


gms = MySignals()


class Win_Pattern_Generator:
    def __init__(self):
        self.ui = QUiLoader().load('pattern_generator.ui')

        gms.log.connect(self.log)

        self.ui.btn_BOE.clicked.connect(self.generate_BOE_Patterns)
        self.ui.btn_HW.clicked.connect(self.generate_HW_Patterns)
        self.ui.btn_VNX.clicked.connect(self.generate_VNX_Patterns)
        self.ui.btn_CSOT.clicked.connect(self.generate_CSOT_Patterns)
        self.ui.btn_Zebra.clicked.connect(self.generate_Zebra_Patterns)
        self.ui.btn_Dot.clicked.connect(self.generate_Dot_Patterns)

        self.ui.btn_Zebra_output.clicked.connect(self._selectFileZebra)
        self.ui.btn_Dot_output.clicked.connect(self._selectFileDot)

    def _selectFileZebra(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        filepath, type = QFileDialog.getSaveFileName(self.ui, "Save Zebra file", current_directory, 'bmp(*.bmp)')
        self.ui.lineEdit_ZebraPath.setText(filepath)
        self.ui.lineEdit_ZebraPath.setEnabled(False)

    def _selectFileDot(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        filepath, type = QFileDialog.getSaveFileName(self.ui, "Save Zebra file", current_directory, 'bmp(*.bmp)')
        self.ui.lineEdit_DotPath.setText(filepath)
        self.ui.lineEdit_DotPath.setEnabled(False)



    def generate_BOE_Patterns(self):
        folder_BOE_pattern = "./pattern/BOE"
        if not os.path.exists(folder_BOE_pattern):
            os.makedirs(folder_BOE_pattern)
        height = self.ui.lineEdit_BOE_height.text()
        width = self.ui.lineEdit_BOE_width.text()

        try:
            height = int(height)
            width = int(width)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return

        create_BOE_patterns(folder_BOE_pattern,width=width,height=height)
        gms.log.emit(f"successful save BOE patterns in path :{folder_BOE_pattern}")

    def generate_HW_Patterns(self):
        folder_HW_pattern = "./pattern/HW"
        if not os.path.exists(folder_HW_pattern):
            os.makedirs(folder_HW_pattern)
        height = self.ui.lineEdit_HW_height.text()
        width = self.ui.lineEdit_HW_width.text()

        try:
            height = int(height)
            width = int(width)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return

        create_HW_patterns(folder_HW_pattern, width=width, height=height)
        gms.log.emit(f"successful save HW patterns in path :{folder_HW_pattern}")

    def generate_VNX_Patterns(self):
        folder_VNX_pattern = "./pattern/VNX"
        if not os.path.exists(folder_VNX_pattern):
            os.makedirs(folder_VNX_pattern)
        height = self.ui.lineEdit_VNX_height.text()
        width = self.ui.lineEdit_VNX_width.text()

        try:
            height = int(height)
            width = int(width)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return

        create_VNX_patterns(folder_VNX_pattern, width=width, height=height)
        gms.log.emit(f"successful save VNX patterns in path :{folder_VNX_pattern}")
    def generate_CSOT_Patterns(self):

        gms.log.emit(f"CSOT patterns not defined")


    def generate_Zebra_Patterns(self):
        output_path = self.ui.lineEdit_ZebraPath.text()

        height = self.ui.lineEdit_Zebra_height.text()
        width = self.ui.lineEdit_Zebra_width.text()
        black_num = self.ui.lineEdit_Zebra_black.text()
        white_num = self.ui.lineEdit_Zebra_White.text()

        flag_Row = 0

        try:
            height = int(height)
            width = int(width)
            black_num = int(black_num)
            white_num = int(white_num)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return

        if self.ui.rbtn_Row.isChecked() is False and self.ui.rbtn_Col.isChecked() is False:
            QMessageBox.warning(
                self.ui,
                'Error',
                "Please select Row or Col")
        elif self.ui.rbtn_Row.isChecked():
            flag_Row = 1
        else:
            flag_Row = 0


        create_Zebra_patterns(output_path=output_path,
                              width=width,
                              height=height,
                              black_num=black_num,
                              white_num=white_num,
                              flag_Row=flag_Row)

        gms.log.emit(f"successful save Zebra patterns in path :{output_path}\n"
                     f"black:{black_num},white:{white_num}")


    def generate_Dot_Patterns(self):

        output_path = self.ui.lineEdit_DotPath.text()

        height = self.ui.lineEdit_Dot_height.text()
        width = self.ui.lineEdit_Dot_width.text()
        dot_height = self.ui.lineEdit_Dot_dotHeight.text()
        dot_width = self.ui.lineEdit_Dot_dotWidth.text()




        try:
            height = int(height)
            width = int(width)
            dot_height = int(dot_height)
            dot_width = int(dot_width)
        except Exception as e:
            QMessageBox.warning(
                self.ui,
                'Error',
                str(e))
            return




        create_Dot_patterns(output_path=output_path,
                              width=width,
                              height=height,
                              dot_width=dot_width,
                              dot_height=dot_height
                              )

        gms.log.emit(f"successful save Zebra patterns in path :{output_path}\n"
                     f"dot width:{dot_width},dot height:{dot_height}")







    def onClearLog(self):
        self.ui.textBrowser.clear()

    def log(self, *texts):
        self.ui.textBrowser.append(' '.join(texts))
        self.ui.textBrowser.ensureCursorVisible()
