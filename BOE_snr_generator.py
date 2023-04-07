from PySide6.QtWidgets import QMessageBox
from PySide6.QtUiTools import QUiLoader

import os
from lib.share import SI, MySignals
from lib.ETS_Analysis import AnalyseData, get_touched_num, write_out_final_result_csv, HEADER_ETS
from threading import Thread

gms = MySignals()


class Win_BOE_SNRGenerator:

    def __init__(self):
        self.ui = QUiLoader().load('BOE_snr_generator.ui')
        self.Pattern = {'White': self.ui.cBoxWhite,
                        'Z1': self.ui.cBoxZ1,
                        'Z2': self.ui.cBoxZ2,
                        'Z3': self.ui.cBoxZ3,
                        'Z4': self.ui.cBoxZ4,
                        'Z5': self.ui.cBoxZ5,
                        'Z10': self.ui.cBoxZ10,
                        'Slider': self.ui.cBoxSlider,
                        'DO': self.ui.cBoxDO}

        self.Customer = {"BOE": self.ui.cBoxBOE,
                         "Huawei_quick": self.ui.cBoxHWQuick,
                         "Huawei_thp_afe": self.ui.cBoxHWTHP

                         }

        self.ui.btnClear.clicked.connect(self.onClearLog)
        self.ui.btnGenerateSNR.clicked.connect(self.onGenerateSNRReport)

        self.ui.cBoxWhite.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ1.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ2.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ3.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ4.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ5.stateChanged.connect(self.changePatternState)
        self.ui.cBoxZ10.stateChanged.connect(self.changePatternState)
        self.ui.cBoxSlider.stateChanged.connect(self.changePatternState)
        self.ui.cBoxDO.stateChanged.connect(self.changePatternState)

        # Test reports template
        self.ui.cBoxBOE.setChecked(True)
        SI.Customers.append("BOE")

        self.ui.cBoxBOE.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxHWQuick.stateChanged.connect(self.changeCustomerState)
        self.ui.cBoxHWTHP.stateChanged.connect(self.changeCustomerState)

        gms.log.connect(self.log)

        # self.ui.cBoxHWQuick.setEnabled(False)
        # self.ui.cBoxHWTHP.setEnabled(False)
        self.initSetting()

    def changePatternState(self):

        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if key not in SI.Patterns and btn.isChecked():
                SI.Patterns.append(key)
                # todo sorted with string and number combo
                SI.Patterns = sorted(list(SI.Patterns), key=str.lower)
                gms.log.emit(f"Successful add pattern: {key}. Current patterns are: {SI.Patterns}")
            elif key in SI.Patterns and not btn.isChecked():
                SI.Patterns.remove(key)
                # todo sorted with string and number combo
                SI.Patterns = sorted(list(SI.Patterns), key=str.lower)
                gms.log.emit(f"Delete pattern: {key}. Current patterns are: {SI.Patterns}")

    def changeCustomerState(self):
        for key in self.Customer.keys():
            btn = self.Customer[key]
            if key not in SI.Customers and btn.isChecked():
                SI.Customers.append(key)
                # todo sorted with string and number combo
                SI.Customers = sorted(list(SI.Customers), key=str.lower)
                gms.log.emit(f"Successful add Customer: {key}. Current Customer list: {SI.Customers}")
            elif key in SI.Customers and not btn.isChecked():
                SI.Customers.remove(key)
                # todo sorted with string and number combo
                SI.Customers = sorted(list(SI.Customers), key=str.lower)
                gms.log.emit(f"Delete Customer: {key}. Current Customer list: {SI.Customers}")

    def initSetting(self):
        if SI.cfg['Dataset Path'] is None:
            QMessageBox.warning(
                self.ui,
                'Not Valid Path',
                'Please select right Dataset folder!!!')
            return

        folders = os.listdir(SI.cfg['Dataset Path'])
        folders = [folder.capitalize() for folder in folders]
        count = 0
        SI.Patterns = []
        for key in self.Pattern.keys():
            btn = self.Pattern[key]
            if key in folders:
                SI.Patterns.append(key)
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
            self.log(f"Already select Patterns: {SI.Patterns}")

    def onGenerateSNRReport(self):

        # load configuration options
        BOE_results = []
        HW_quick_results = []
        HW_THP_AFE_results = []
        VNX_results = []

        gms.log.emit("************ start SNR calculation *******************")
        gms.log.emit(f"required patterns: {SI.Patterns}")
        gms.log.emit(f"required Customers: {SI.Customers}")
        gms.log.emit(
            f"Number of selected frames for no touch log is: {int(SI.cfg['end idx notouch']) - int(SI.cfg['start idx notouch'])}")
        gms.log.emit(
            f"Number of selected frames for touch log is: {int(SI.cfg['end idx touch']) - int(SI.cfg['start idx touch'])}")
        gms.log.emit("*" * 80)

        def threadFun():

            for pattern in SI.Patterns:
                # # rawdata folder
                # pattern_folder = opts.pattern_folder
                # print(pattern_folder)
                # pattern = os.path.basename(pattern_folder)

                # modify rawdata paths: path format is **.edl.csv, i.e:
                # notouch path "wo.edl.csv" -> prefix_notouch = "wo"
                # touch path "wi5.edl.csv" -> prefix_touch = "wi"
                prefix_notouch = SI.cfg['notouch file prefix']
                prefix_touch = SI.cfg['touch file prefix']

                if os.path.exists(os.path.join(SI.cfg['Dataset Path'], pattern, "{}.edl.csv".format(prefix_notouch))):
                    notouch_data_path = os.path.join(SI.cfg['Dataset Path'], pattern,
                                                     "{}.edl.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.cfg['Dataset Path'], pattern, prefix_touch + "{}.edl.csv")
                else:
                    notouch_data_path = os.path.join(SI.cfg['Dataset Path'], pattern, "{}.csv".format(prefix_notouch))
                    touch_path = os.path.join(SI.cfg['Dataset Path'], pattern, prefix_touch + "{}.csv")

                touch_list = get_touched_num(os.path.join(SI.cfg['Dataset Path'], pattern), prefix_touch)

                # match touch raw data file
                touch_data_path_list = [touch_path.format(i) for i in touch_list]

                # AnalyseData is main class for snr analysis
                DataAnalyse = AnalyseData(no_touch_file_path=notouch_data_path,
                                          touch_file_paths=touch_data_path_list,
                                          Header_index=HEADER_ETS,
                                          notouch_range=(
                                          int(SI.cfg['start idx notouch']), int(SI.cfg['end idx notouch'])),
                                          touch_range=(int(SI.cfg['start idx touch']), int(SI.cfg['end idx touch'])))

                # print(pd.DataFrame(DataAnalyse.BOE_snr_summary()))

                # select vendor for different report
                if "BOE" in SI.Customers:
                    BOE_ret = DataAnalyse.BOE_snr_summary()
                    DataAnalyse.write_out_csv(BOE_ret)
                    # "min_SmaxNppfullscreenR_dB": "{:.2f}".format(min_SmaxNppfullscreenR_dB),
                    # "Position_P2P": f"Touch {min_SmaxNppfullscreenR_dB_index + 1}",
                    # "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                    # "Position_RMS": f"Touch {min_SmeanNrmsR_dB_index + 1}"
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
                    # todo ******** VNX test ****************
                    VNX_ret = DataAnalyse.VNX_snr_summary()
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
                    VNX_results.append(tmp_res)


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

                if "Huawei_thp_afe" in SI.Customers:
                    HW_thp_afe_ret = DataAnalyse.HW_thp_afe_snr_summary()
                    DataAnalyse.write_out_csv(HW_thp_afe_ret)

                    tmp_res = [pattern]
                    if HW_thp_afe_ret.get("mct_summary", None) is not None:
                        tmp_res.extend([HW_thp_afe_ret["mct_summary"]["final_results"]["min_SminNppnotouch_dB"],
                                        HW_thp_afe_ret["mct_summary"]["final_results"]["min_SmeanNppnotouch_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if HW_thp_afe_ret.get("sct_row_summary", None) is not None:
                        # print(HW_thp_afe_ret)
                        tmp_res.extend(
                            [HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SminNppnotouch_dB"],
                             HW_thp_afe_ret["sct_row_summary"]["final_results"]["min_sct_row_SmeanNppnotouch_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])

                    if HW_thp_afe_ret.get("sct_col_summary", None) is not None:
                        tmp_res.extend(
                            [HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SminNppnotouch_dB"],
                             HW_thp_afe_ret["sct_col_summary"]["final_results"]["min_sct_col_SmeanNppnotouch_dB"]])
                    else:
                        tmp_res.extend(["NaN", "NaN"])
                    HW_THP_AFE_results.append(tmp_res)

                # convert mct rawdata into grid foramt
                if self.ui.cBoxLog_grid_rawdata.isChecked():
                    if DataAnalyse.NoTouchFrame.mct_grid is not None:
                        DataAnalyse.write_out_decode_mct_csv()
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
                        DataAnalyse.plot_sct_touch_signal_all()
                        DataAnalyse.plot_sct_positive_noise()
                        DataAnalyse.plot_sct_negative_noise()
                    else:
                        gms.log.emit(f"Pattern: {pattern} do not have mutual raw data!! Could not plot Noise Map!")

                # print(f"Already successful finish {pattern} !!!!!!!!!!!!!!")
                gms.log.emit(f"Already successful finish {pattern} !!!!!!!!!!!!!!")


            # write_out_final_result_csv(SI.cfg['Dataset Path'], final_results)
            gms.log.emit(f"successfull save summmary for Patterns {SI.Patterns}")
            if BOE_results:
                header = ["pattern (fullscreen)", "SNppR MCT", "SNrmsR MCT", "SNppR SCT Row",
                          "SNrmsR SCT Row", "SNppR SCT Col", "SNrmsR SCT Col"]
                out_path = os.path.join(SI.cfg['Dataset Path'], "BOE_summary.csv")
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
                header = ["pattern (fullscreen)",  "SNrmsR MCT", "SNrmsR SCT Row",  "SNrmsR SCT Col"]
                out_path = os.path.join(SI.cfg['Dataset Path'], "VNX_summary.csv")
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
                out_path = os.path.join(SI.cfg['Dataset Path'], "HW_quick_summary.csv")
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
                out_path = os.path.join(SI.cfg['Dataset Path'], "HW_thp_afe_summary.csv")
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
