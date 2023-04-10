from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PySide6.QtUiTools import QUiLoader

import os
from lib.share import SI, MySignals
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv
from threading import Thread
import json
from PySide6.QtCore import Qt

gms = MySignals()


class Win_BOE_SNRGenerator_2:
    CFG_ITEMS = [
        'Dataset Path', 'touch file prefix', 'notouch file prefix',
        'start idx notouch', 'end idx notouch', 'start idx touch', 'end idx touch'
    ]

    def __init__(self):
        self.ui = QUiLoader().load('BOE_snr_generator_2.ui')
        self.Pattern = {'White': self.ui.cBoxWhite,
                        'Z1': self.ui.cBoxZ1,
                        'Z2': self.ui.cBoxZ2,
                        'Z3': self.ui.cBoxZ3,
                        'Z4': self.ui.cBoxZ4,
                        'Z5': self.ui.cBoxZ5,
                        'Z10': self.ui.cBoxZ10,
                        'Slider': self.ui.cBoxSlider,
                        'DO': self.ui.cBoxDO}

        self.ui.btnClear.clicked.connect(self.onClearLog)

        self.loadCfgToTable()
        self.ui.btnGenerateSNR.clicked.connect(self.onGenerateSNRReport)
        self.ui.btnReset.clicked.connect(self.initSetting)

        self.ui.cBoxWhite.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ1.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ2.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ3.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ4.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ5.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ10.stateChanged.connect(self.changePatternState)
        self.ui.cBoxSlider.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDO.stateChanged.connect(self.changePatternState)

        gms.log.connect(self.log)

        self.ui.tableCFG.cellChanged.connect(self.cfgItemChanged)

        self.ui.btnSelectFolder.clicked.connect(self._selectFolder)

        self.initSetting()

    def changePatternState(self):

        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if key not in SI.BOE_params.Patterns and btn.isChecked():
                SI.BOE_params.Patterns.append(key)
                # todo sorted with string and number combo
                SI.BOE_params.Patterns = sorted(list(SI.BOE_params.Patterns), key=str.lower)
                gms.log.emit(f"Successful add pattern: {key}. Current patterns are: {SI.BOE_params.Patterns}")
            elif key in SI.BOE_params.Patterns and not btn.isChecked():
                SI.BOE_params.Patterns.remove(key)
                # todo sorted with string and number combo
                SI.BOE_params.Patterns = sorted(list(SI.BOE_params.Patterns), key=str.lower)
                gms.log.emit(f"Delete pattern: {key}. Current patterns are: {SI.BOE_params.Patterns}")

    def _saveCfgFile(self):

        with open('boe_snr_cfg.json', 'w', encoding='utf8') as f:
            json.dump(SI.BOE_params.SNR_cfg, f, ensure_ascii=False, indent=2)

    def _selectFolder(self):
        FileDirectory = QFileDialog.getExistingDirectory(self.ui, "Select Dataset")
        if FileDirectory is None:
            return
        SI.BOE_params.SNR_cfg['Dataset Path'] = FileDirectory

        self.ui.lineFolder.setText(FileDirectory)
        self.ui.lineFolder.setEnabled(False)
        table = self.ui.tableCFG
        table.setItem(0, 1, QTableWidgetItem(FileDirectory))
        self.initSetting()

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
            table.setItem(idx, 1, QTableWidgetItem(SI.BOE_params.SNR_cfg.get(cfgName, '')))

    def cfgItemChanged(self, row, column):
        table = self.ui.tableCFG

        # 获取更改内容
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, column).text()

        SI.BOE_params.SNR_cfg[cfgName] = cfgValue
        self._saveCfgFile()

        self.log(f'{cfgName} : {cfgValue}')

    def initSetting(self):
        if SI.BOE_params.SNR_cfg.get('Dataset Path', None) is None:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Dataset folder!!!')
            return

        path = SI.BOE_params.SNR_cfg['Dataset Path']
        if not os.path.exists(path):
            return
        folders = os.listdir(path)
        folders = [folder.upper() for folder in folders]
        count = 0
        SI.BOE_params.Patterns = []
        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if key.upper() in folders:
                SI.BOE_params.Patterns.append(key)
                btn.setChecked(True)
                btn.setEnabled(True)
                count += 1
            else:
                btn.setChecked(False)
                btn.setEnabled(False)
        if count == 0:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Dataset folder!!!')
            return
        else:
            self.log(f"Already select Patterns: {SI.BOE_params.Patterns}")

    def onGenerateSNRReport(self):

        # load configuration options
        BOE_results = []
        HW_quick_results = []
        HW_THP_AFE_results = []
        VNX_results = []

        gms.log.emit("************ start SNR calculation *******************")
        gms.log.emit(f"required patterns: {SI.BOE_params.Patterns}")
        gms.log.emit(f"required Customers: BOE")
        gms.log.emit(
            f"Number of selected frames for no touch log is: {int(SI.BOE_params.SNR_cfg['end idx notouch']) - int(SI.BOE_params.SNR_cfg['start idx notouch'])}")
        gms.log.emit(
            f"Number of selected frames for touch log is: {int(SI.BOE_params.SNR_cfg['end idx touch']) - int(SI.BOE_params.SNR_cfg['start idx touch'])}")
        gms.log.emit("*" * 80)

        def threadFun():

            for pattern in SI.BOE_params.Patterns:
                # # rawdata folder
                # pattern_folder = opts.pattern_folder
                # print(pattern_folder)
                # pattern = os.path.basename(pattern_folder)

                # modify rawdata paths: path format is **.edl.csv, i.e:
                # notouch path "wo.edl.csv" -> prefix_notouch = "wo"
                # touch path "wi5.edl.csv" -> prefix_touch = "wi"
                prefix_notouch = SI.BOE_params.SNR_cfg['notouch file prefix']
                prefix_touch = SI.BOE_params.SNR_cfg['touch file prefix']

                if os.path.exists(os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern,
                                               "{}.edl.csv".format(prefix_notouch))):
                    notouch_data_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern,
                                                     "{}.edl.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern,
                                              prefix_touch + "{}.edl.csv")
                else:
                    notouch_data_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern,
                                                     "{}.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern, prefix_touch + "{}.csv")

                touch_list = get_touched_num(os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], pattern), prefix_touch)

                # match touch raw data file
                touch_data_path_list = [touch_path.format(i) for i in touch_list]

                # AnalyseData is main class for snr analysis
                DataAnalyse = AnalyseData(no_touch_file_path=notouch_data_path,
                                          touch_file_paths=touch_data_path_list,
                                          notouch_range=(
                                              int(SI.BOE_params.SNR_cfg['start idx notouch']),
                                              int(SI.BOE_params.SNR_cfg['end idx notouch'])),
                                          touch_range=(int(SI.BOE_params.SNR_cfg['start idx touch']),
                                                       int(SI.BOE_params.SNR_cfg['end idx touch'])))

                # print(pd.DataFrame(DataAnalyse.BOE_snr_summary()))

                # select vendor for different report
                # if "BOE" in SI.Customers:
                # todo calculate BOE SNR
                BOE_ret = DataAnalyse.boe_snr_summary()
                DataAnalyse.write_out_csv(BOE_ret)
                # "min_SmaxNppfullscreenR_dB": "{:.2f}".format(min_SmaxNppfullscreenR_dB),
                # "Position_P2P": f"Touch {min_SmaxNppfullscreenR_dB_index + 1}",
                # "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                # "Position_RMS": f"Touch {min_SmeanNrmsR_dB_index + 1}"
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
                BOE_results.append(tmp_res)
                # # todo ******** VNX test ****************
                # VNX_ret = DataAnalyse.VNX_snr_summary()
                # DataAnalyse.write_out_csv(VNX_ret)
                # tmp_res = [pattern]
                # if VNX_ret.get("mct_summary", None) is not None:
                #     tmp_res.extend([VNX_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"]])
                # else:
                #     tmp_res.extend(["NaN"])
                #
                # if VNX_ret.get("sct_row_summary", None) is not None:
                #     tmp_res.extend(
                #         [VNX_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"]])
                # else:
                #     tmp_res.extend(["NaN"])
                #
                # if VNX_ret.get("sct_col_summary", None) is not None:
                #     tmp_res.extend(
                #         [VNX_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"]])
                # else:
                #     tmp_res.extend(["NaN"])
                # VNX_results.append(tmp_res)
                #
                # #
                # # if "Huawei_quick" in SI.Customers:
                # #     HW_quick_ret = DataAnalyse.HW_quick_snr_summary()
                # #     DataAnalyse.write_out_csv(HW_quick_ret)
                # #
                # #     tmp_res = [pattern]
                # #     if HW_quick_ret.get("mct_summary", None) is not None:
                # #         tmp_res.extend([HW_quick_ret["mct_summary"]["final_results"]["min_SminNpptouch_dB"]])
                # #     else:
                # #         tmp_res.extend(["NaN"])
                # #
                # #     if HW_quick_ret.get("sct_row_summary", None) is not None:
                # #         tmp_res.extend(
                # #             [HW_quick_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNpptouchR_dB"]])
                # #     else:
                # #         tmp_res.extend(["NaN"])
                # #
                # #     if HW_quick_ret.get("sct_col_summary", None) is not None:
                # #         tmp_res.extend(
                # #             [HW_quick_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNpptouchR_dB"]])
                # #     else:
                # #         tmp_res.extend(["NaN"])
                # #     HW_quick_results.append(tmp_res)
                #
                # # if "Huawei_thp_afe" in SI.Customers:
                # # todo calculate HW THP AFE SNR
                # HW_thp_afe_ret = DataAnalyse.HW_thp_afe_snr_summary()
                # DataAnalyse.write_out_csv(HW_thp_afe_ret)
                #
                # tmp_res = [pattern]
                # if HW_thp_afe_ret.get("mct_summary", None) is not None:
                #     tmp_res.extend([HW_thp_afe_ret["mct_summary"]["final_results"]["min_SminNppnotouch_dB"],
                #                     HW_thp_afe_ret["mct_summary"]["final_results"]["min_SminNaveR_dB"]])
                # else:
                #     tmp_res.extend(["NaN", "NaN"])
                #
                # if HW_thp_afe_ret.get("sct_row_summary", None) is not None:
                #     # print(HW_thp_afe_ret)
                #     tmp_res.extend(
                #         [HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNppnotouch_dB"],
                #          HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNaveR_dB"]])
                # else:
                #     tmp_res.extend(["NaN", "NaN"])
                #
                # if HW_thp_afe_ret.get("sct_col_summary", None) is not None:
                #     tmp_res.extend(
                #         [HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNppnotouch_dB"],
                #          HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNaveR_dB"]])
                # else:
                #     tmp_res.extend(["NaN", "NaN"])
                # HW_THP_AFE_results.append(tmp_res)

                # convert mct rawdata into grid foramt
                if self.ui.cBoxLog_grid_rawdata.isChecked():
                    DataAnalyse.write_out_decode_mct_csv()
                    # if DataAnalyse.NoTouchFrame.mct_grid is not None:
                    #     DataAnalyse.write_out_decode_mct_csv()
                    # else:
                    #     gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not generate grid rawdata!")

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

                if self.ui.cBoxPlotSctSignal.isChecked():
                    if DataAnalyse.NoTouchFrame.sct_row is not None and DataAnalyse.NoTouchFrame.sct_col is not None:
                        DataAnalyse.plot_sct_touch_signal_all()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have self cap. raw data!! Could not plot Signal Map!")

                if self.ui.cBoxPlotPosNoise.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.plot_mct_positive_annotate()
                        DataAnalyse.plot_mct_negative_annotate()
                        DataAnalyse.plot_sct_touch_signal_all()
                        DataAnalyse.plot_sct_positive_noise()
                        DataAnalyse.plot_sct_negative_noise()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                # print(f"Already successful finish {pattern} !!!!!!!!!!!!!!")
                gms.log.emit(f"Already successful finish {pattern} !!!!!!!!!!!!!!")

            # write_out_final_result_csv(SI.BOE_params.SNR_cfg['Dataset Path'], final_results)
            gms.log.emit(f"successfull save summmary for Patterns {SI.BOE_params.Patterns}")
            if BOE_results:
                header = ["pattern (fullscreen)", "noise mct(p2p)", "noise mct(rms)", "signal mct(p2p)",
                          "signal mct(rms)", "SNppR MCT", "SNrmsR MCT",
                          "noise sct row(p2p)", "noise sct row(rms)", "signal sct row(p2p)", "signal sct row(rms)",
                          "SNppR SCT Row", "SNrmsR SCT Row",
                          "noise sct col(p2p)", "noise sct col(rms)", "signal sct col(p2p)", "signal sct col(rms)",
                          "SNppR SCT Col", "SNrmsR SCT Col"]
                out_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], "BOE_summary.csv")
                write_out_final_result_csv(out_path, header, BOE_results)
                gms.log.emit("******************** BOE final results *********************")
                gms.log.emit(str(header))

                def align_str(l1, l2):

                    for idx, text in enumerate(l2):
                        text = str(text)
                        text = text + " " * (len(str(l1[idx])) - len(text))
                        l2[idx] = text

                for res in BOE_results:
                    align_str(header, res)
                    gms.log.emit(str(res))
            if VNX_results:
                header = ["pattern (fullscreen)", "SNrmsR MCT", "SNrmsR SCT Row", "SNrmsR SCT Col"]
                out_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], "VNX_summary.csv")
                write_out_final_result_csv(out_path, header, VNX_results)
                gms.log.emit("******************** BOE final results *********************")
                gms.log.emit(str(header))

                def align_str(l1, l2):

                    for idx, text in enumerate(l2):
                        text = str(text)
                        text = text + " " * (len(str(l1[idx])) - len(text))
                        l2[idx] = text

                for res in VNX_results:
                    align_str(header, res)
                    gms.log.emit(str(res))

            if HW_quick_results:
                header = ["pattern (touch node)", "SNppR MCT", "SNppR SCT Row", "SNppR SCT Col"]
                out_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], "HW_quick_summary.csv")
                write_out_final_result_csv(out_path, header, HW_quick_results)

                gms.log.emit("******************** HW QUICK final results *********************")
                gms.log.emit(str(header))

                def align_str(l1, l2):

                    for idx, text in enumerate(l2):
                        text = str(text)
                        text = text + " " * (len(str(l1[idx])) - len(text))
                        l2[idx] = text

                for res in HW_quick_results:
                    align_str(header, res)
                    gms.log.emit(str(res))

            if HW_THP_AFE_results:
                header = ["pattern (no touch node)", "SminNppR MCT", "SmeanNppR MCT", "SminNppR SCT Row",
                          "SmeanNppR SCT Row", "SminNppR SCT Col", "SmeanNppR SCT Col"]
                out_path = os.path.join(SI.BOE_params.SNR_cfg['Dataset Path'], "HW_thp_afe_summary.csv")
                write_out_final_result_csv(out_path, header, HW_THP_AFE_results)

                gms.log.emit("******************** HW THP final results *********************")
                gms.log.emit(str(header))

                def align_str(l1, l2):

                    for idx, text in enumerate(l2):
                        text = str(text)
                        text = text + " " * (len(str(l1[idx])) - len(text))
                        l2[idx] = text

                for res in HW_THP_AFE_results:
                    align_str(header, res)
                    gms.log.emit(str(res))

        Thread(target=threadFun).start()

    def onClearLog(self):
        self.ui.textBrowser.clear()

    def log(self, *texts):
        self.ui.textBrowser.append(' '.join(texts))
        self.ui.textBrowser.ensureCursorVisible()
