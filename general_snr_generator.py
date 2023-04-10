from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QTableWidgetItem, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
import os
from lib.share import SI, MySignals
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv
from threading import Thread
import json

gms = MySignals()


class WinGeneralSNRGenerator:
    CFG_ITEMS = [
        'Dataset Path', 'touch file prefix', 'notouch file prefix',
        'start idx notouch', 'end idx notouch', 'start idx touch', 'end idx touch'
    ]

    def __init__(self):
        self.ui = QUiLoader().load('General_snr_generator.ui')
        self.customer_list = {'BOE': self.ui.cBoxBOE,
                              'HW_QUICK': self.ui.cBoxHW_quick,
                              'HW_THP': self.ui.cBoxHW_thp,
                              'VNX': self.ui.cBoxVNX,
                              'CSOT': self.ui.cBoxCSOT,
                              'LENOVO': self.ui.cBoxLenovo,
                              }
        self.header_summary = {
            'BOE': ["pattern", "noise mct(p2p)", "noise mct(rms)", "signal mct(p2p)",
                    "signal mct(rms)", "SNppR MCT", "SNrmsR MCT",
                    "noise sct row(p2p)", "noise sct row(rms)", "signal sct row(p2p)", "signal sct row(rms)",
                    "SNppR SCT Row", "SNrmsR SCT Row",
                    "noise sct col(p2p)", "noise sct col(rms)", "signal sct col(p2p)", "signal sct col(rms)",
                    "SNppR SCT Col", "SNrmsR SCT Col"],
            'HW_QUICK': ["pattern", "SNppR MCT(dB)", "SNppR SCT Row(dB)", "SNppR SCT Col(dB)"],
            'HW_THP': ["pattern", "SminNppR MCT(dB)", "SmeanNppR MCT(dB)", "SminNppR SCT Row(dB)",
                       "SmeanNppR SCT Row(dB)", "SminNppR SCT Col(dB)", "SmeanNppR SCT Col(dB)"],
            'VNX': ["pattern", "SNrmsR MCT(dB)", "SNrmsR SCT Row(dB)", "SNrmsR SCT Col(dB)"],
            'CSOT': ["pattern", "SNrmsR MCT(dB)","SNnotouchrmsR MCT(dB)", "SNrmsR SCT Row(dB)",
                     "SNnotouchrmsR SCT ROW(dB)", "SNrmsR SCT Col(dB)" ,"SNnotouchrmsR SCT COL(dB)"],
            'LENOVO': ["pattern", "SNrmsR MCT(dB)", "SNrmsR SCT Row(dB)", "SNrmsR SCT Col(dB)"],
        }

        self.isFullTouch = True

        self.loadCfgToTable()
        self.ui.btnClear.clicked.connect(self.onClearLog)
        self.ui.btnGenerateSNR.clicked.connect(self.onGenerateSNRReport)
        self.ui.btnReset.clicked.connect(self.initSetting)

        self.ui.cBoxBOE.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxHW_quick.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxHW_thp.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxVNX.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxCSOT.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxLenovo.stateChanged.connect(self.changeCustomerState)

        self.ui.tableCFG.cellChanged.connect(self.cfgItemChanged)

        self.ui.btnSelectFolder.clicked.connect(self._selectFolder)

        self.ui.btnSwitch.clicked.connect(self.onSwitchMode)
        self.ui.btnSwitch.setStyleSheet("background-color: lightgreen;")

        gms.log.connect(self.log)

        self.initSetting()

    def initSetting(self):
        if SI.General_params.SNR_cfg.get('Dataset Path', None) is None:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Dataset folder!!!')
            return
        path = SI.General_params.SNR_cfg['Dataset Path']
        if not os.path.exists(path):
            return
        folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

        SI.General_params.Patterns = folders

        self.init_pattern_checklist()

        # reset all customer button
        for key in self.customer_list.keys():
            btn = self.customer_list[key]
            btn.setChecked(False)
            btn.setEnabled(True)

    def init_pattern_checklist(self):
        self.ui.listPattern.clear()
        for pattern in SI.General_params.Patterns:
            # create QListWidgetItem
            item = QListWidgetItem(pattern)
            # set checkable property
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # set checked state to checked
            item.setCheckState(Qt.Checked)
            # add item to the list
            self.ui.listPattern.addItem(item)

    def onSwitchMode(self):
        if self.isFullTouch:
            self.ui.btnSwitch.setText('SNR Active Stylus')
            self.ui.label.setText('Click to switch Fulltouch')
            # set button color to light red
            self.ui.btnSwitch.setStyleSheet("background-color: lightcoral;")
            self.isFullTouch = False
        else:
            self.ui.btnSwitch.setText('SNR Fulltouch')
            self.ui.label.setText('Click to switch Active Stylus')
            # set button color to light green
            self.ui.btnSwitch.setStyleSheet("background-color: lightgreen;")
            self.isFullTouch = True

    def _selectFolder(self):
        FileDirectory = QFileDialog.getExistingDirectory(self.ui, "Select Dataset")
        if FileDirectory is None:
            return
        SI.General_params.SNR_cfg['Dataset Path'] = FileDirectory

        self.ui.lineFolder.setText(FileDirectory)
        self.ui.lineFolder.setEnabled(False)
        table = self.ui.tableCFG
        table.setItem(0, 1, QTableWidgetItem(FileDirectory))
        self.initSetting()

    def changeCustomerState(self):

        for key in self.customer_list.keys():
            btn = self.customer_list[key]
            if btn.isEnabled():
                if key not in SI.General_params.customer_list and btn.isChecked():
                    SI.General_params.customer_list.append(key)
                    # sorted with string and number combo
                    SI.General_params.customer_list = sorted(list(SI.General_params.customer_list), key=str.lower)
                    gms.log.emit(
                        f"Successful add customer: {key}. Current customers are: {SI.General_params.customer_list}")
                elif key in SI.General_params.customer_list and not btn.isChecked():
                    SI.General_params.customer_list.remove(key)
                    # todo sorted with string and number combo
                    SI.General_params.customer_list = sorted(list(SI.General_params.customer_list), key=str.lower)
                    gms.log.emit(f"Delete customer: {key}. Current customers are: {SI.General_params.customer_list}")

        # 加载配置文件到界面

    def _saveCfgFile(self):

        with open('general_snr_cfg.json', 'w', encoding='utf8') as f:
            json.dump(SI.General_params.SNR_cfg, f, ensure_ascii=False, indent=2)

    def loadCfgToTable(self):

        table = self.ui.tableCFG
        for idx, cfgName in enumerate(self.CFG_ITEMS):
            # 插入一行
            table.insertRow(idx)

            # 参数名
            item = QTableWidgetItem(cfgName)
            table.setItem(idx, 0, item)
            item.setFlags(Qt.ItemIsEnabled)  # 参数名字段不允许修改

            # 参数值
            table.setItem(idx, 1, QTableWidgetItem(SI.General_params.SNR_cfg.get(cfgName, '')))

    def cfgItemChanged(self, row, column):
        table = self.ui.tableCFG

        # 获取更改内容
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, column).text()

        SI.General_params.SNR_cfg[cfgName] = cfgValue
        self._saveCfgFile()

        self.log(f'{cfgName} : {cfgValue}')

    def onGenerateSNRReport(self):

        # load configuration options
        # BOE_results = []
        # HW_quick_results = []
        # HW_THP_AFE_results = []

        # summary results
        result_summary = {}
        for customer in SI.General_params.customer_list:
            result_summary[customer] = []

        gms.log.emit("************ start SNR calculation *******************")
        gms.log.emit(f"required patterns: {SI.General_params.Patterns}")
        gms.log.emit(
            f"Number of selected frames for no touch log is: {int(SI.General_params.SNR_cfg['end idx notouch']) - int(SI.General_params.SNR_cfg['start idx notouch'])}")
        gms.log.emit(
            f"Number of selected frames for touch log is: {int(SI.General_params.SNR_cfg['end idx touch']) - int(SI.General_params.SNR_cfg['start idx touch'])}")
        gms.log.emit("*" * 80)

        def threadFun():

            # check toggle status of listPattern
            for idx in range(self.ui.listPattern.count()):
                item = self.ui.listPattern.item(idx)
                if item.checkState() == Qt.Checked:
                    if item.text() not in SI.General_params.Patterns:
                        SI.General_params.Patterns.append(item.text())
                else:
                    if item.text() in SI.General_params.Patterns:
                        SI.General_params.Patterns.remove(item.text())

            for pattern in SI.General_params.Patterns:

                # modify rawdata paths: path format is **.edl.csv, i.e:
                # notouch path "wo.edl.csv" -> prefix_notouch = "wo"
                # touch path "wi5.edl.csv" -> prefix_touch = "wi"
                prefix_notouch = SI.General_params.SNR_cfg['notouch file prefix']
                prefix_touch = SI.General_params.SNR_cfg['touch file prefix']

                if os.path.exists(os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern,
                                               "{}.edl.csv".format(prefix_notouch))):
                    notouch_data_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern,
                                                     "{}.edl.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern,
                                              prefix_touch + "{}.edl.csv")
                else:
                    notouch_data_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern,
                                                     "{}.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern,
                                              prefix_touch + "{}.csv")

                touch_list = get_touched_num(os.path.join(SI.General_params.SNR_cfg['Dataset Path'], pattern),
                                             prefix_touch)

                # check touch list
                if len(touch_list) == 0:
                    gms.log.emit(f"Cannot find any touch file!!!!\n "
                                 f"Please check path and prefix!!")

                # match touch raw data file
                touch_data_path_list = [touch_path.format(i) for i in touch_list]

                # AnalyseData is main class for snr analysis
                DataAnalyse = AnalyseData(no_touch_file_path=notouch_data_path,
                                          touch_file_paths=touch_data_path_list,
                                          notouch_range=(
                                              int(SI.General_params.SNR_cfg['start idx notouch']),
                                              int(SI.General_params.SNR_cfg['end idx notouch'])),
                                          touch_range=(int(SI.General_params.SNR_cfg['start idx touch']),
                                                       int(SI.General_params.SNR_cfg['end idx touch'])))

                # print(pd.DataFrame(DataAnalyse.BOE_snr_summary()))

                # select vendor for different report
                # if "BOE" in SI.Customers:
                if self.ui.cBoxBOE.isChecked():
                    BOE_ret = DataAnalyse.boe_snr_summary()
                    DataAnalyse.write_out_csv(BOE_ret)

                    tmp_res = [pattern]
                    if BOE_ret.get("mct_summary", None) is not None:
                        touch_index_p2p = BOE_ret["mct_summary"]["final_results"]["index_P2P"]
                        touch_index_rms = BOE_ret["mct_summary"]["final_results"]["index_RMS"]
                        tmp_res.extend([BOE_ret["mct_summary"]["snr_summary"]["noise_p2p_fullscreen"][0],
                                        BOE_ret["mct_summary"]["snr_summary"]["noise_rms_touch"][touch_index_rms],
                                        BOE_ret["mct_summary"]["snr_summary"]["signal_max"][touch_index_p2p],
                                        BOE_ret["mct_summary"]["snr_summary"]["signal_mean"][touch_index_rms],
                                        BOE_ret["mct_summary"]["final_results"]["min_SmaxNppfullscreenR_dB"],
                                        BOE_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"] * 6)

                    if BOE_ret.get("sct_row_summary", None) is not None:

                        touch_index_p2p = BOE_ret["sct_row_summary"]["final_results"]["index_P2P"]
                        touch_index_rms = BOE_ret["sct_row_summary"]["final_results"]["index_RMS"]
                        tmp_res.extend(
                            [BOE_ret["sct_row_summary"]["snr_sct_row_summary"]["noise_p2p_fullscreen"][0],
                             BOE_ret["sct_row_summary"]["snr_sct_row_summary"]["noise_rms_touch"][touch_index_rms],
                             BOE_ret["sct_row_summary"]["snr_sct_row_summary"]["signal_max"][touch_index_p2p],
                             BOE_ret["sct_row_summary"]["snr_sct_row_summary"]["signal_mean"][touch_index_rms],
                             BOE_ret["sct_row_summary"]["final_results"]["min_sct_row_SmaxNppfullscreenR_dB"],
                             BOE_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"] * 6)

                    if BOE_ret.get("sct_col_summary", None) is not None:

                        touch_index_p2p = BOE_ret["sct_col_summary"]["final_results"]["index_P2P"]
                        touch_index_rms = BOE_ret["sct_col_summary"]["final_results"]["index_RMS"]
                        tmp_res.extend(
                            [
                                BOE_ret["sct_col_summary"]["snr_sct_col_summary"]["noise_p2p_fullscreen"][0],
                                BOE_ret["sct_col_summary"]["snr_sct_col_summary"]["noise_rms_touch"][touch_index_rms],
                                BOE_ret["sct_col_summary"]["snr_sct_col_summary"]["signal_max"][touch_index_p2p],
                                BOE_ret["sct_col_summary"]["snr_sct_col_summary"]["signal_mean"][touch_index_rms],
                                BOE_ret["sct_col_summary"]["final_results"]["min_sct_col_SmaxNppfullscreenR_dB"],
                                BOE_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"] * 6)
                    result_summary["BOE"].append(tmp_res)

                if self.ui.cBoxHW_thp.isChecked():

                    HW_quick_ret = DataAnalyse.hw_quick_snr_summary()
                    DataAnalyse.write_out_csv(HW_quick_ret)

                    tmp_res = [pattern]
                    if HW_quick_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([HW_quick_ret["mct_summary"]["final_results"]["min_SminNpptouch_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if HW_quick_ret.get("sct_row_summary", None) is not None:
                        tmp_res.extend(
                            [HW_quick_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNpptouchR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if HW_quick_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [HW_quick_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNpptouchR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    result_summary["HW_QUICK"].append(tmp_res)

                if self.ui.cBoxHW_thp.isChecked():
                    HW_thp_afe_ret = DataAnalyse.hw_thp_afe_snr_summary()
                    DataAnalyse.write_out_csv(HW_thp_afe_ret)

                    tmp_res = [pattern]
                    if HW_thp_afe_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([HW_thp_afe_ret["mct_summary"]["final_results"]["min_SminNppnotouch_dB"],
                                        HW_thp_afe_ret["mct_summary"]["final_results"]["min_SminNaveR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if HW_thp_afe_ret.get("sct_row_summary", None) is not None:
                        # print(HW_thp_afe_ret)
                        tmp_res.extend(
                            [HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNppnotouch_dB"],
                             HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNaveR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if HW_thp_afe_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNppnotouch_dB"],
                             HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNaveR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    result_summary["HW_THP"].append(tmp_res)

                # visionox report is selected
                if self.ui.cBoxVNX.isChecked():
                    VNX_ret = DataAnalyse.vnx_snr_summary()
                    DataAnalyse.write_out_csv(VNX_ret)

                    tmp_res = [pattern]
                    if VNX_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([VNX_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if VNX_ret.get("sct_row_summary", None) is not None:
                        tmp_res.extend(
                            [VNX_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if VNX_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [VNX_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])
                    result_summary["VNX"].append(tmp_res)

                # lenovo report is selected
                if self.ui.cBoxLenovo.isChecked():
                    Lenovo_ret = DataAnalyse.lenovo_snr_summary()
                    DataAnalyse.write_out_csv(Lenovo_ret)

                    tmp_res = [pattern]
                    if Lenovo_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([Lenovo_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if Lenovo_ret.get("sct_row_summary", None) is not None:
                        tmp_res.extend(
                            [Lenovo_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])

                    if Lenovo_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [Lenovo_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN"])
                    result_summary["LENOVO"].append(tmp_res)

                if self.ui.cBoxCSOT.isChecked():
                    CSOT_ret = DataAnalyse.csot_snr_summary()
                    DataAnalyse.write_out_csv(CSOT_ret)

                    tmp_res = [pattern]
                    if CSOT_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([CSOT_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"],
                                        CSOT_ret["mct_summary"]["final_results"]["min_SmeanNnotouchrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if CSOT_ret.get("sct_row_summary", None) is not None:
                        tmp_res.extend(
                            [CSOT_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"],
                             CSOT_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNnotouchrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if CSOT_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [CSOT_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"],
                             CSOT_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNnotouchrmsR_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])
                    result_summary["CSOT"].append(tmp_res)

                # convert mct rawdata into grid foramt
                if self.ui.cBoxLog_grid_rawdata.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.write_out_filtered_data_csv()
                    else:
                        gms.log.emit(
                            f"Pattern: {pattern} do not have mutual raw data!! Could not generate grid rawdata!")

                # plot no touch p2p noise heatmap
                if self.ui.cBoxPlotNoiseptp.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_noise_p2p()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                # plot no touch rms noise heatmap
                if self.ui.cBoxPlotRms.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_noise_rms()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                # plot all touch signal in one heatmap
                if self.ui.cBoxPlotallTouch.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_touch_signal_all()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                if self.ui.cBoxPlot_p2p_annotated.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_noise_p2p_annotated()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot "
                                     f"positive/negative Noise Map!")

                if self.ui.cBoxPlotPosNoise.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_positive_annotate()
                        DataAnalyse.plot_mct_negative_annotate()


                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                if self.ui.cBoxPlotSctPosNoise.isChecked():
                    if DataAnalyse.NoTouchFrame.sct_row is not None and DataAnalyse.NoTouchFrame.sct_col is not None:
                        DataAnalyse.plot_sct_positive_noise()
                        DataAnalyse.plot_sct_negative_noise()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have self cap. raw data!! Could not plot Noise Map!")

                if self.ui.cBoxPlotSctSignal.isChecked():
                    if DataAnalyse.NoTouchFrame.sct_row is not None and DataAnalyse.NoTouchFrame.sct_col is not None:
                        DataAnalyse.plot_sct_touch_signal_all()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have self cap. raw data!! Could not plot Signal Map!")

                if self.ui.cBoxPlotMctAveNoise.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_noise_average()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot "
                                     f"average Noise Map!")

                gms.log.emit(f"Already successful finish {pattern} !!!!!!!!!!!!")

            # write_out_final_result_csv(SI.General_params.SNR_cfg['Dataset Path'], final_results)
            gms.log.emit(f"successfull save summmary for Patterns {SI.General_params.Patterns}")
            if self.ui.cBoxBOE.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "BOE_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["BOE"], result_summary["BOE"])
                gms.log.emit(f"successfull save BOE summmary for Patterns {SI.General_params.Patterns}")

            if self.ui.cBoxCSOT.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "CSOT_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["CSOT"], result_summary["CSOT"])
                gms.log.emit(f"successfull save CSOT summmary for Patterns {SI.General_params.Patterns}")

            if self.ui.cBoxHW_quick.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "HW_quick_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["HW_QUICK"], result_summary["HW_QUICK"])
                gms.log.emit(f"successfull save HW_quick summmary for Patterns {SI.General_params.Patterns}")

            if self.ui.cBoxHW_thp.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "HW_thp_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["HW_THP"], result_summary["HW_THP"])
                gms.log.emit(f"successfull save HW_thp summmary for Patterns {SI.General_params.Patterns}")

            if self.ui.cBoxVNX.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "VNX_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["VNX"], result_summary["VNX"])
                gms.log.emit(f"successfull save VNX summmary for Patterns {SI.General_params.Patterns}")

            if self.ui.cBoxLenovo.isChecked():
                out_put_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "Lenovo_summary.csv")
                write_out_final_result_csv(out_put_path, self.header_summary["LENOVO"], result_summary["LENOVO"])
                gms.log.emit(f"successfull save Lenovo summmary for Patterns {SI.General_params.Patterns}")


            # if BOE_results:
            #     header = ["pattern (fullscreen)", "SNppR MCT", "SNrmsR MCT", "SNppR SCT Row",
            #               "SNrmsR SCT Row", "SNppR SCT Col", "SNrmsR SCT Col"]
            #     out_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "BOE_summary.csv")
            #     write_out_final_result_csv(out_path, header, BOE_results)
            #     gms.log.emit("******************** BOE final results *********************")
            #     gms.log.emit(str(header))
            #
            #     def align_str(l1, l2):
            #
            #         for idx, text in enumerate(l2):
            #             text = str(text)
            #             text = text + " " * (len(str(l1[idx])) - len(text))
            #             l2[idx] = text
            #
            #     for res in BOE_results:
            #         align_str(header, res)
            #         gms.log.emit(str(res))
            #
            # if HW_quick_results:
            #     header = ["pattern (touch node)", "SNppR MCT", "SNppR SCT Row", "SNppR SCT Col"]
            #     out_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "HW_quick_summary.csv")
            #     write_out_final_result_csv(out_path, header, HW_quick_results)
            #
            #     gms.log.emit("******************** HW QUICK final results *********************")
            #     gms.log.emit(str(header))
            #
            #     def align_str(l1, l2):
            #
            #         for idx, text in enumerate(l2):
            #             text = str(text)
            #             text = text + " " * (len(str(l1[idx])) - len(text))
            #             l2[idx] = text
            #
            #     for res in HW_quick_results:
            #         align_str(header, res)
            #         gms.log.emit(str(res))
            #
            # if HW_THP_AFE_results:
            #     header = ["pattern (no touch node)", "SminNppR MCT", "SminNaveR MCT", "SminNppR SCT Row",
            #               "SminNaveR SCT Row", "SminNppR SCT Col", "SminNaveR SCT Col"]
            #     out_path = os.path.join(SI.General_params.SNR_cfg['Dataset Path'], "HW_thp_afe_summary.csv")
            #     write_out_final_result_csv(out_path, header, HW_THP_AFE_results)
            #
            #     gms.log.emit("******************** HW THP final results *********************")
            #     gms.log.emit(str(header))
            #
            #     def align_str(l1, l2):
            #
            #         for idx, text in enumerate(l2):
            #             text = str(text)
            #             text = text + " " * (len(str(l1[idx])) - len(text))
            #             l2[idx] = text
            #
            #     for res in HW_THP_AFE_results:
            #         align_str(header, res)
            #         gms.log.emit(str(res))

        Thread(target=threadFun).start()

    def onClearLog(self):
        self.ui.textBrowser.clear()

    def log(self, *texts):
        self.ui.textBrowser.append(' '.join(texts))
        self.ui.textBrowser.ensureCursorVisible()
