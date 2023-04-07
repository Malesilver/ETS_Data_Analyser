from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem,QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
import os
from lib.share import SI, MySignals
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv, HEADER_ETS
from threading import Thread
import json
gms = MySignals()



class Win_HW_THP_SNRGenerator:
    CFG_ITEMS = [
        'Dataset Path', 'touch file prefix', 'notouch file prefix',
        'start idx notouch', 'end idx notouch', 'start idx touch', 'end idx touch'
    ]

    def __init__(self):
        self.ui = QUiLoader().load('HW_THP_snr_generator.ui')
        self.Pattern = {'White': self.ui.cBoxWhite,
                        'Black': self.ui.cBoxBlack,
                        'Red': self.ui.cBoxRed,
                        'Blue': self.ui.cBoxBlue,
                        'Green': self.ui.cBoxGreen,
                        'Col': self.ui.cBoxCol,
                        'Inverse_Col': self.ui.cBoxColInv,
                        'ColGP': self.ui.cBoxCol_GP,
                        'Inverse_ColGP': self.ui.cBoxCol_GPInv,
                        'Row': self.ui.cBoxRow,
                        'Inverse_Row': self.ui.cBoxRowInv,
                        'Dot': self.ui.cBoxDot,
                        'Inverse_Dot': self.ui.cBoxDotInv,
                        'DoubleDot': self.ui.cBoxDouble_dot,
                        'Inverse_DoubleDot': self.ui.cBoxDouble_dotInv,
                        'Vertical': self.ui.cBoxVertical,
                        'Horizontal': self.ui.cBoxHorizontal}

        self.loadCfgToTable()
        self.ui.btnClear.clicked.connect(self.onClearLog)
        self.ui.btnGenerateSNR.clicked.connect(self.onGenerateSNRReport)
        self.ui.btnReset.clicked.connect(self.initSetting)

        self.ui.cBoxWhite.stateChanged.connect(self.changePatternState)
        self.ui.cBoxBlack.stateChanged.connect(self.changePatternState)
        self.ui.cBoxRed.stateChanged.connect(self.changePatternState)
        self.ui.cBoxBlue.stateChanged.connect(self.changePatternState)
        self.ui.cBoxGreen.stateChanged.connect(self.changePatternState)
        self.ui.cBoxCol.stateChanged.connect(self.changePatternState)
        self.ui.cBoxColInv.stateChanged.connect(self.changePatternState)
        self.ui.cBoxCol_GP.stateChanged.connect(self.changePatternState)
        self.ui.cBoxCol_GPInv.stateChanged.connect(self.changePatternState)
        self.ui.cBoxRow.stateChanged.connect(self.changePatternState)
        self.ui.cBoxRowInv.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDot.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDotInv.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDouble_dot.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDouble_dotInv.stateChanged.connect(self.changePatternState)
        self.ui.cBoxVertical.stateChanged.connect(self.changePatternState)
        self.ui.cBoxHorizontal.stateChanged.connect(self.changePatternState)

        self.ui.tableCFG.cellChanged.connect(self.cfgItemChanged)

        self.ui.btnSelectFolder.clicked.connect(self._selectFolder)


        gms.log.connect(self.log)

        # self.ui.cBoxHWQuick.setEnabled(False)
        # self.ui.cBoxHWTHP.setEnabled(False)

        self.initSetting()

    def initSetting(self):
        if SI.HW_THP_AFE_params.SNR_cfg.get('Dataset Path',None) is None:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Dataset folder!!!')
            return
        path = SI.HW_THP_AFE_params.SNR_cfg['Dataset Path']
        if not os.path.exists(path):
            return
        folders = os.listdir(path)
        folders = [folder.upper() for folder in folders]
        print(folders)
        print(self.Pattern.keys())
        count = 0
        SI.HW_THP_AFE_params.Patterns = []

        # reset all btn
        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            btn.setChecked(False)
            btn.setEnabled(False)


        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if key.upper() in folders:
                SI.HW_THP_AFE_params.Patterns.append(key)
                btn.setEnabled(True)
                btn.setChecked(True)

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
            self.log(f"Already select Patterns: {SI.HW_THP_AFE_params.Patterns}")
    def _selectFolder(self):
        FileDirectory = QFileDialog.getExistingDirectory(self.ui, "Select Dataset")
        if FileDirectory is None:
            return
        SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'] = FileDirectory

        self.ui.lineFolder.setText(FileDirectory)
        self.ui.lineFolder.setEnabled(False)
        table = self.ui.tableCFG
        table.setItem(0, 1, QTableWidgetItem(FileDirectory))
        self.initSetting()

    def changePatternState(self):

        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if btn.isEnabled():
                if key not in SI.HW_THP_AFE_params.Patterns and btn.isChecked():
                    SI.HW_THP_AFE_params.Patterns.append(key)
                    # todo sorted with string and number combo
                    SI.HW_THP_AFE_params.Patterns = sorted(list(SI.HW_THP_AFE_params.Patterns), key=str.lower)
                    gms.log.emit(f"Successful add pattern: {key}. Current patterns are: {SI.HW_THP_AFE_params.Patterns}")
                elif key in SI.HW_THP_AFE_params.Patterns and not btn.isChecked():
                    SI.HW_THP_AFE_params.Patterns.remove(key)
                    # todo sorted with string and number combo
                    SI.HW_THP_AFE_params.Patterns = sorted(list(SI.HW_THP_AFE_params.Patterns), key=str.lower)
                    gms.log.emit(f"Delete pattern: {key}. Current patterns are: {SI.HW_THP_AFE_params.Patterns}")

        # 加载配置文件到界面
    def _saveCfgFile(self):

        with open('hw_thp_snr_cfg.json', 'w', encoding='utf8') as f:
            json.dump(SI.HW_THP_AFE_params.SNR_cfg, f, ensure_ascii=False, indent=2)


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
            table.setItem(idx, 1, QTableWidgetItem(SI.HW_THP_AFE_params.SNR_cfg.get(cfgName, '')))

    def cfgItemChanged(self, row, column):
        table = self.ui.tableCFG

        # 获取更改内容
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, column).text()

        SI.HW_THP_AFE_params.SNR_cfg[cfgName] = cfgValue
        self._saveCfgFile()

        self.log(f'{cfgName} : {cfgValue}')



    def onGenerateSNRReport(self):

        # load configuration options
        BOE_results = []
        HW_quick_results = []
        HW_THP_AFE_results = []

        gms.log.emit("************ start SNR calculation *******************")
        gms.log.emit(f"required patterns: {SI.HW_THP_AFE_params.Patterns}")
        gms.log.emit(f"required Customers: {SI.Customers}")
        gms.log.emit(
            f"Number of selected frames for no touch log is: {int(SI.HW_THP_AFE_params.SNR_cfg['end idx notouch']) - int(SI.HW_THP_AFE_params.SNR_cfg['start idx notouch'])}")
        gms.log.emit(
            f"Number of selected frames for touch log is: {int(SI.HW_THP_AFE_params.SNR_cfg['end idx touch']) - int(SI.HW_THP_AFE_params.SNR_cfg['start idx touch'])}")
        gms.log.emit("*" * 80)

        def threadFun():

            for pattern in SI.HW_THP_AFE_params.Patterns:


                # modify rawdata paths: path format is **.edl.csv, i.e:
                # notouch path "wo.edl.csv" -> prefix_notouch = "wo"
                # touch path "wi5.edl.csv" -> prefix_touch = "wi"
                prefix_notouch = SI.HW_THP_AFE_params.SNR_cfg['notouch file prefix']
                prefix_touch = SI.HW_THP_AFE_params.SNR_cfg['touch file prefix']

                if os.path.exists(os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern, "{}.edl.csv".format(prefix_notouch))):
                    notouch_data_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern,
                                                     "{}.edl.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern, prefix_touch + "{}.edl.csv")
                else:
                    notouch_data_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern, "{}.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern, prefix_touch + "{}.csv")

                touch_list = get_touched_num(os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], pattern), prefix_touch)

                # check touch list
                if len(touch_list) == 0:
                    gms.log.emit(f"Cannot find any touch file!!!!\n "
                                 f"Please check path and prefix!!")


                # match touch raw data file
                touch_data_path_list = [touch_path.format(i) for i in touch_list]


                # AnalyseData is main class for snr analysis
                DataAnalyse = AnalyseData(no_touch_file_path=notouch_data_path,
                                          touch_file_paths=touch_data_path_list,
                                          Header_index=HEADER_ETS,
                                          notouch_range=(
                                          int(SI.HW_THP_AFE_params.SNR_cfg['start idx notouch']), int(SI.HW_THP_AFE_params.SNR_cfg['end idx notouch'])),
                                          touch_range=(int(SI.HW_THP_AFE_params.SNR_cfg['start idx touch']), int(SI.HW_THP_AFE_params.SNR_cfg['end idx touch'])))

                # print(pd.DataFrame(DataAnalyse.BOE_snr_summary()))

                # select vendor for different report
                # if "BOE" in SI.Customers:
                BOE_ret = DataAnalyse.BOE_snr_summary()
                DataAnalyse.write_out_csv(BOE_ret)

                tmp_res = [pattern]
                if BOE_ret.get("mct_summary", None) is not None:
                    tmp_res.extend([BOE_ret["mct_summary"]["final_results"]["min_SmaxNppfullscreenR_dB"],
                                    BOE_ret["mct_summary"]["final_results"]["min_SmeanNrmsR_dB"]])
                else:
                    tmp_res.extend(["NaN", "NaN"])

                if BOE_ret.get("sct_row_summary", None) is not None:
                    tmp_res.extend(
                        [BOE_ret["sct_row_summary"]["final_results"]["min_sct_row_SmaxNppfullscreenR_dB"],
                         BOE_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNrmsR_dB"]])
                else:
                    tmp_res.extend(["NaN", "NaN"])

                if BOE_ret.get("sct_col_summary", None) is not None:
                    tmp_res.extend(
                        [BOE_ret["sct_col_summary"]["final_results"]["min_sct_col_SmaxNppfullscreenR_dB"],
                         BOE_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNrmsR_dB"]])
                else:
                    tmp_res.extend(["NaN", "NaN"])
                BOE_results.append(tmp_res)
                if "Huawei_quick" in SI.Customers:
                    HW_quick_ret = DataAnalyse.HW_quick_snr_summary()
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
                    HW_quick_results.append(tmp_res)

                # todo calculate Huawei THP AFE
                HW_thp_afe_ret = DataAnalyse.HW_thp_afe_snr_summary()
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
                HW_THP_AFE_results.append(tmp_res)

                # convert mct rawdata into grid foramt
                if self.ui.cBoxLog_grid_rawdata.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.write_out_filtered_data_csv()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not generate grid rawdata!")

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


                # print(f"Already successful finish {pattern} !!!!!!!!!!!!!!")
                gms.log.emit(f"Already successful finish {pattern} !!!!!!!!!!!!")


            # write_out_final_result_csv(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], final_results)
            gms.log.emit(f"successfull save summmary for Patterns {SI.HW_THP_AFE_params.Patterns}")
            if BOE_results:
                header = ["pattern (fullscreen)", "SNppR MCT", "SNrmsR MCT", "SNppR SCT Row",
                          "SNrmsR SCT Row", "SNppR SCT Col", "SNrmsR SCT Col"]
                out_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], "BOE_summary.csv")
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

            if HW_quick_results:
                header = ["pattern (touch node)", "SNppR MCT", "SNppR SCT Row", "SNppR SCT Col"]
                out_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], "HW_quick_summary.csv")
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
                header = ["pattern (no touch node)", "SminNppR MCT", "SminNaveR MCT", "SminNppR SCT Row",
                          "SminNaveR SCT Row", "SminNppR SCT Col", "SminNaveR SCT Col"]
                out_path = os.path.join(SI.HW_THP_AFE_params.SNR_cfg['Dataset Path'], "HW_thp_afe_summary.csv")
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
