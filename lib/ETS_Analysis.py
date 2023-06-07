import re
import csv
import numpy as np
import os
from typing import List
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import argparse
from matplotlib import patches
from lib.EtsDataframe import EtsDataframe

file_dir = os.path.dirname(__file__)  # the directory that class "option" resides in
pd.set_option('display.max_columns', None)


class AnalyseData:
    def __init__(self,
                 no_touch_file_path: str = None,
                 touch_file_paths: List[str] = None,
                 notouch_range: (int, int) = (0, 300),
                 touch_range: (int, int) = (0, 100)):
        if touch_file_paths is None:
            touch_file_paths = []
        self.pattern = os.path.basename(os.path.dirname(no_touch_file_path))
        self.standard_width_picture = [12.99, 8.49]
        self.row_num = None
        self.col_num = None
        self.notouch_range = notouch_range
        self.touch_range = touch_range

        self.NoTouchFrame: EtsDataframe = None
        self.TouchFrameSets: List[EtsDataframe] = []
        self.init_data_frame_sets(no_touch_file_path, touch_file_paths)

        self.output_folder = os.path.join(os.path.dirname(no_touch_file_path), "output")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def init_data_frame_sets(self,
                             no_touch_file_path: str,
                             touch_file_paths: List[str],
                             ):
        self.NoTouchFrame = EtsDataframe(file_path=no_touch_file_path, start_idx=self.notouch_range[0],
                                         end_idx=self.notouch_range[1])

        self.row_num = self.NoTouchFrame.row_num
        self.col_num = self.NoTouchFrame.col_num
        for touch_file_path in touch_file_paths:
            TouchFrame = EtsDataframe(file_path=touch_file_path, start_idx=self.touch_range[0],
                                      end_idx=self.touch_range[1])
            self.TouchFrameSets.append(TouchFrame)

    # ********************************************************
    # ***********MCT Field ***********************************
    # ********************************************************

    @property
    def mct_noise_p2p_grid(self) -> np.ndarray:
        """
        :return:  grid value of peak-peak noise for no-touch frame
        """
        return self.NoTouchFrame.mct_grid_p2p

    @property
    def mct_noise_ave_grid(self) -> np.ndarray:
        """
        :return: For Huawei, the average noise means the absolute mean value for np-touch frame
        """
        return np.abs(self.NoTouchFrame.mct_grid_mean)

    @property
    def mct_noise_p2p_max(self) -> np.ndarray:
        """
        :return:  max value of peak-peak noise for no-touch frame
        """
        return self.NoTouchFrame.mct_grid_p2p.max()

    @property
    def mct_noise_p2p_mean(self) -> np.ndarray:
        """
        :return:  mean value of peak-peak noise for no-touch frame
        """
        return self.NoTouchFrame.mct_grid_p2p.mean()

    @property
    def mct_noise_p2p_min(self) -> np.ndarray:
        """
        :return: min value of peak-peak noise for no-touch frame
        """
        return self.NoTouchFrame.mct_grid_p2p.min()

    @property
    def all_mct_pos_noise_grid(self) -> np.ndarray:
        """
        :return: grid value of positive noise for all touch frame   [frame1, frame2, ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            ret.append(TouchFrame.mct_positive_noise)
        ret = np.array(ret)
        return np.nanmax(ret, axis=0)

    @property
    def all_mct_neg_noise_grid(self) -> np.ndarray:
        """
        :return: grid value of negative noise for all touch frame   [frame1, frame2, ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            ret.append(TouchFrame.mct_negative_noise)
        ret = np.array(ret)
        return np.nanmin(ret, axis=0)

    @property
    def all_touched_position(self) -> list:
        """
        return the position of max value from all frames as touch node position
        :return: list node [[node1_x, node1_y] [node2_x node2_y] ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append((y_node, x_node))
        return ret

    @property
    def all_mct_noise_p2p_notouch_node(self) -> list:
        """
        The noise is taken from no touch peak-peak grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append(self.NoTouchFrame.mct_grid_p2p[y_node][x_node])
        return ret

    @property
    def all_mct_noise_ave_notouch_node(self) -> list:
        """
        The noise is taken from no touch peak-peak grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append(self.mct_noise_ave_grid[y_node][x_node])
        return ret

    @property
    def mct_noise_ave_max(self):
        """
        max value of no touch average noise
        """
        return np.max(self.mct_noise_ave_grid)

    @property
    def all_mct_noise_p2p_touch_node(self) -> list:
        """
        The noise is taken from touch peak-peak grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append(TouchFrame.mct_grid_p2p[y_node][x_node])
        return ret

    @property
    def all_mct_noise_rms_notouch_node(self) -> list:
        """
        The noise is taken from no touch rms noise grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append(self.NoTouchFrame.mct_grid_rms[y_node][x_node])
        return ret

    @property
    def all_mct_noise_rms_touch_node(self) -> list:
        """
        The noise is taken from rms noise (in touch raw data) grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            ret.append(TouchFrame.mct_grid_rms[y_node][x_node])

        return ret

    @property
    def all_mct_signal_max(self) -> list:
        """
        :return: list of max signal [node1 node2 ...]
        """
        return [TouchData.mct_signal_max for TouchData in self.TouchFrameSets]

    @property
    def all_mct_signal_min(self) -> list:
        return [TouchData.mct_signal_min for TouchData in self.TouchFrameSets]

    @property
    def all_mct_signal_mean(self) -> list:
        return [TouchData.mct_signal_mean for TouchData in self.TouchFrameSets]

    @property
    def all_SminNppnotouchR(self) -> list:
        """
        (using in Huawei SNppR)
        Using min signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """
        ret = []

        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            noise = self.NoTouchFrame.mct_grid_p2p[y_node][x_node]
            if noise == 0:
                SmaxNpptouchR = np.inf
            else:
                SmaxNpptouchR = TouchFrame.mct_signal_min / noise
            ret.append(SmaxNpptouchR)
        return ret

    @property
    def all_SminNppnotouchR_dB(self) -> list:
        """
        (using in Huawei SNppR test)
        Using min signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """

        return [20 * np.log10(val) for val in self.all_SminNppnotouchR]

    @property
    def all_SmeanNppnotouchR(self) -> list:
        '''
        (using in Huawei SNppR)
        Using average signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        '''
        ret = []

        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            SmeanNpptouchR = TouchFrame.mct_signal_mean / self.NoTouchFrame.mct_grid_p2p[y_node][x_node]
            ret.append(SmeanNpptouchR)
        return ret

    @property
    def all_SmeanNppnotouchR_dB(self) -> list:
        """
        (using in Huawei SNppR test)
        Using mean signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """

        return [20 * np.log10(val) for val in self.all_SmeanNppnotouchR]

    @property
    def all_SmaxNppnotouchR(self) -> list:
        '''
        (using in BOE SNppR) Using max signal from touch raw data as signal, and peak-peak noise in no touch raw data
        at touched node as noise :return: list of SNR [node1 node2 ...]
        '''
        ret = []

        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            SmaxNpptouchR = TouchFrame.mct_signal_max / self.NoTouchFrame.mct_grid_p2p[y_node][x_node]
            ret.append(SmaxNpptouchR)
        return ret

    @property
    def all_SmaxNppnotouchR_dB(self) -> list:
        """
        (using in BOE SNppR) Using max signal from touch raw data as signal, and peak-peak noise in no touch raw data
        :return:
        """

        return [20 * np.log10(val) for val in self.all_SmaxNppnotouchR]

    @property
    def all_SminNpptouchR(self) -> list:
        '''
        (using in Huawei quick test)
        Using min signal from touch raw data as signal, and peak-peak noise in touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        '''
        ret = []

        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            SminNpptouchR = TouchFrame.mct_signal_min / TouchFrame.mct_grid_p2p[y_node][x_node]
            ret.append(SminNpptouchR)
        return ret

    @property
    def all_SmaxNppfullscreenR(self) -> list:
        ret = []

        for TouchFrame in self.TouchFrameSets:
            SmaxNpptouchR = TouchFrame.mct_signal_max / self.NoTouchFrame.mct_grid_p2p.max()
            ret.append(SmaxNpptouchR)
        return ret

    @property
    def all_SmaxNppfullscreenR_dB(self) -> List:

        return [20 * np.log10(val) for val in self.all_SmaxNppfullscreenR]

    @property
    def all_SminNppfullscreenR(self) -> list:
        ret = []

        for TouchFrame in self.TouchFrameSets:
            noise = self.NoTouchFrame.mct_grid_p2p.max()
            signal = TouchFrame.mct_signal_min
            SminNppfullscreenR = signal / noise
            ret.append(SminNppfullscreenR)
        return ret

    @property
    def all_SminNppfullscreenR_dB(self) -> List:

        return [20 * np.log10(val) for val in self.all_SminNppfullscreenR]

    @property
    def all_SminNppfullscreenR_grid(self) -> list:
        ret = []

        for TouchFrame in self.TouchFrameSets:
            noise = self.NoTouchFrame.mct_grid_p2p
            signal = TouchFrame.mct_signal_min
            SminNppfullscreenR_grid = signal / noise
            ret.append(SminNppfullscreenR_grid)
        return ret

    @property
    def all_SminNppfullscreenR_dB_grid(self) -> list:
        return [20 * np.log10(val) for val in self.all_SminNppfullscreenR_grid]

    @property
    def all_SmeanNrmsR(self) -> list:
        ret = []
        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            _, y_node, x_node = TouchFrame.mct_signal_position
            SmeanNrmsR = TouchFrame.mct_signal_mean / self.all_mct_noise_rms_touch_node[idx]
            ret.append(SmeanNrmsR)
        return ret

    @property
    def all_SmeanNnotouchrmsR(self) -> list:
        """
        calculate SNR using mean signal and rms noise in no touch raw data
        :return: list of SNR [TouchFrame1, TouchFrame2, ...]
        """
        ret = []
        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            noise = self.NoTouchFrame.mct_grid_rms_csot
            signal = TouchFrame.mct_signal_mean
            SmeanNnotouchrmsR = signal / noise
            ret.append(SmeanNnotouchrmsR)
        return ret

    @property
    def all_SmeanNnotouchrmsR_dB(self) -> list:
        """
        calculate SNR using mean signal and rms noise in no touch raw data in dB
        :return: list of SNR [TouchFrame1, TouchFrame2, ...]
        """
        return [20 * np.log10(val) for val in self.all_SmeanNnotouchrmsR]

    @property
    def all_SminNpptouchR_dB(self) -> list:
        """
        (using in Huawei quick test)
        Using min signal from touch raw data as signal, and peak-peak noise in touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """

        return [20 * np.log10(val) for val in self.all_SminNpptouchR]

    @property
    def all_SmeanNrmsR_dB(self):

        return [20 * np.log10(val) for val in self.all_SmeanNrmsR]

    @property
    def all_SminNavenodeR(self) -> list:
        """
        Huawei and honor snr calculation method,
        using node value from average noise as noise
        using min signal as signal
        :return: List of SNR [TouchFrame1, TouchFrame2, ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            _, y_node, x_node = TouchFrame.mct_signal_position
            signal = TouchFrame.mct_signal_min
            noise = self.mct_noise_ave_grid[y_node][x_node]
            SminNavenodeR = signal / noise
            ret.append(SminNavenodeR)
        return ret

    @property
    def all_SminNavenodeR_dB(self) -> list:
        """
        calculate SNR using min signal and average noise in touch raw data
        :return: list of SNR in dB [TouchFrame1, TouchFrame2, ...]
        """

        return [20 * np.log10(val) for val in self.all_SminNavenodeR]

    @property
    def all_SminNavefullscreenR(self) -> list:
        """
        Huawei and honor snr calculation method,
        using max value of average noise as noise
        using min signal as signal
        :return: List of SNR [TouchFrame1, TouchFrame2, ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            signal = TouchFrame.mct_signal_min
            noise = np.max(self.mct_noise_ave_grid)
            SminNavefullscreenR = signal / noise
            ret.append(SminNavefullscreenR)
        return ret

    @property
    def all_SminNavefullscreenR_dB(self) -> list:
        """
        calculate SNR using min signal and average noise in touch raw data
        :return: list of SNR in dB [TouchFrame1, TouchFrame2, ...]
        """
        return [20 * np.log10(val) for val in self.all_SminNavefullscreenR]

    @property
    def all_SminNaveR_grid(self) -> list:
        """
        Huawei and honor snr calculation method,
        using mxn average noise grid as noise
        using min signal as signal
        :return: List of SNR [Grid1, Grid2, ...]
        """
        ret = []
        for TouchFrame in self.TouchFrameSets:
            signal = TouchFrame.mct_signal_min
            noise_grid = self.mct_noise_ave_grid
            SminNaveR_grid = signal / noise_grid
            ret.append(SminNaveR_grid)
        return ret

    @property
    def all_SminNaveR_dB_grid(self) -> list:
        """
        calculate SNR using min signal and average noise in touch raw data
        :return: list of SNR in dB [Grid1, Grid2, ...]
        """
        return [20 * np.log10(val) for val in self.all_SminNaveR_grid]

    # ********************************************************
    # ***********SCT ROW Field *******************************
    # ********************************************************
    @property
    def sct_row_noise_ave_line(self) -> np.ndarray:
        return np.abs(self.NoTouchFrame.sct_row_mean)

    @property
    def sct_row_noise_ave_max(self):
        return np.max(self.sct_row_noise_ave_line)

    @property
    def sct_row_noise_p2p_line(self) -> np.ndarray:
        return self.NoTouchFrame.sct_row_p2p

    @property
    def sct_row_p2p_max(self) -> np.ndarray:
        return self.NoTouchFrame.sct_row_p2p.max()

    @property
    def sct_row_p2p_mean(self) -> np.ndarray:
        return self.NoTouchFrame.sct_row_p2p.mean()

    @property
    def sct_row_p2p_min(self) -> np.ndarray:
        return self.NoTouchFrame.sct_row_p2p.min()

    # ********************************************************
    # ***********SCT COL Field *******************************
    # ********************************************************

    @property
    def sct_col_noise_ave_line(self) -> np.ndarray:
        return np.abs(self.NoTouchFrame.sct_col_mean)

    @property
    def sct_col_noise_ave_max(self) -> np.ndarray:
        return np.max(self.sct_col_noise_ave_line)

    @property
    def sct_col_noise_p2p_line(self) -> np.ndarray:
        return self.NoTouchFrame.sct_col_p2p

    @property
    def sct_col_p2p_max(self) -> np.ndarray:
        return self.NoTouchFrame.sct_col_p2p.max()

    @property
    def sct_col_p2p_mean(self) -> np.ndarray:
        return self.NoTouchFrame.sct_col_p2p.mean()

    @property
    def sct_col_p2p_min(self) -> np.ndarray:
        return self.NoTouchFrame.sct_col_p2p.min()

    # ********************************************************
    # ***********SCT Results Field ([row],[col]) *******************************
    # ********************************************************

    @property
    def all_sct_touched_position(self) -> list:
        """
        return the position of max value from all frames as touch node position
        :return: list node [[node1_x, node1_y] [node2_x node2_y] ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            ret_row.append(x_node)

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            ret_col.append(y_node)

        return [ret_row, ret_col]

    @property
    def all_sct_noise_p2p_notouch_node(self) -> list:
        """
        The noise is taken from no touch peak-peak grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            ret_row.append(self.NoTouchFrame.sct_row_p2p[x_node])

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            ret_col.append(self.NoTouchFrame.sct_col_p2p[y_node])

        return [ret_row, ret_col]

    @property
    def all_sct_noise_ave_notouch_node(self) -> list:
        """
        The noise is taken from no touch average grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            ret_row.append(self.sct_row_noise_ave_line[x_node])

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            ret_col.append(self.sct_col_noise_ave_line[y_node])

        return [ret_row, ret_col]

    @property
    def all_sct_noise_p2p_touch_node(self) -> list:
        """
        The noise is taken from touch peak-peak grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            ret_row.append(TouchFrame.sct_row_p2p[x_node])

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            ret_col.append(TouchFrame.sct_col_p2p[y_node])

        return [ret_row, ret_col]

    @property
    def all_sct_noise_rms_touch_node(self) -> list:
        """
        The noise is taken from rms noise (in touch raw data) grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            ret_row.append(TouchFrame.sct_row_rms[x_node])

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            ret_col.append(TouchFrame.sct_col_rms[y_node])

        return [ret_row, ret_col]

    @property
    def all_sct_noise_rms_notouch_node(self) -> list:
        """
        The noise is taken from rms noise (in touch raw data) grid data at touched position
        :return: list node [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, row_node = TouchFrame.sct_row_signal_position
            ret_row.append(self.NoTouchFrame.sct_row_rms[row_node])

        for TouchFrame in self.TouchFrameSets:
            _, col_node = TouchFrame.sct_col_signal_position
            ret_col.append(self.NoTouchFrame.sct_col_rms[col_node])

        return [ret_row, ret_col]

    @property
    def all_sct_signal_max(self) -> list:
        ret_row = [TouchData.sct_row_signal_max for TouchData in self.TouchFrameSets]
        ret_col = [TouchData.sct_col_signal_max for TouchData in self.TouchFrameSets]
        return [ret_row, ret_col]

    @property
    def all_sct_signal_min(self) -> list:
        ret_row = [TouchData.sct_row_signal_min for TouchData in self.TouchFrameSets]
        ret_col = [TouchData.sct_col_signal_min for TouchData in self.TouchFrameSets]
        return [ret_row, ret_col]

    @property
    def all_sct_signal_mean(self) -> list:
        ret_row = [TouchData.sct_row_signal_mean for TouchData in self.TouchFrameSets]
        ret_col = [TouchData.sct_col_signal_mean for TouchData in self.TouchFrameSets]
        return [ret_row, ret_col]

    @property
    def all_sct_pos_noise_line(self) -> list:
        ret_row = []
        ret_col = []
        for TouchFrame in self.TouchFrameSets:
            ret_row.append(TouchFrame.sct_row_positive_noise)
            ret_col.append(TouchFrame.sct_col_positive_noise)
        ret_row = np.array(ret_row)
        ret_col = np.array(ret_col)
        return [np.nanmax(ret_row, axis=0), np.nanmax(ret_col, axis=0)]

    @property
    def all_sct_neg_noise_line(self) -> list:
        ret_row = []
        ret_col = []
        for TouchFrame in self.TouchFrameSets:
            ret_row.append(TouchFrame.sct_row_negative_noise)
            ret_col.append(TouchFrame.sct_col_negative_noise)
        ret_row = np.array(ret_row)
        ret_col = np.array(ret_col)
        return [np.nanmin(ret_row, axis=0), np.nanmin(ret_col, axis=0)]

    @property
    def all_sct_SminNppnotouchR(self) -> list:
        """
        (using in Huawei SNppR)
        Using min signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            SminNppnotouchR = TouchFrame.sct_row_signal_min / self.NoTouchFrame.sct_row_p2p[x_node]
            ret_row.append(SminNppnotouchR)

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            SminNppnotouchR = TouchFrame.sct_col_signal_min / self.NoTouchFrame.sct_col_p2p[y_node]
            ret_col.append(SminNppnotouchR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNppnotouchR(self):
        '''
        (using in Huawei SNppR)
        Using average signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        '''

        ret_row = []
        ret_col = []
        # calculate sct row SmeanNppnotouchR
        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            SmeanNppnotouchR = TouchFrame.sct_row_signal_mean / self.NoTouchFrame.sct_row_p2p[x_node]
            ret_row.append(SmeanNppnotouchR)

        # calculate sct col SmeanNppnotouchR
        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            SmeanNppnotouchR = TouchFrame.sct_col_signal_mean / self.NoTouchFrame.sct_col_p2p[y_node]
            ret_col.append(SmeanNppnotouchR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmaxNppnotouchR(self):
        '''
        (using in BOE SNppR) Using max signal from touch raw data as signal, and peak-peak noise in no touch raw data
        at touched node as noise :return: list of SNR [node1 node2 ...]
        '''
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            SmaxNppnotouchR = TouchFrame.sct_row_signal_max / self.NoTouchFrame.sct_row_p2p[x_node]
            ret_row.append(SmaxNppnotouchR)

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            SmaxNppnotouchR = TouchFrame.sct_col_signal_max / self.NoTouchFrame.sct_col_p2p[y_node]
            ret_col.append(SmaxNppnotouchR)

        return [ret_row, ret_col]

    @property
    def all_sct_SminNpptouchR(self):
        '''
        (using in Huawei quick test)
        Using min signal from touch raw data as signal, and peak-peak noise in touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        '''
        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            SminNpptouchR = TouchFrame.sct_row_signal_min / TouchFrame.sct_row_p2p[x_node]
            ret_row.append(SminNpptouchR)

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            SminNpptouchR = TouchFrame.sct_col_signal_min / TouchFrame.sct_col_p2p[y_node]
            ret_col.append(SminNpptouchR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmaxNppnotouchR_dB(self):
        ret_row = [20 * np.log10(val) for val in self.all_sct_SmaxNppnotouchR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SmaxNppnotouchR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNpptouchR_dB(self):
        """
        (using in Huawei quick test)
        Using min signal from touch raw data as signal, and peak-peak noise in touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """
        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNpptouchR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNpptouchR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNppnotouchR_dB(self):
        """
        (using in Huawei SNppR test)
        Using min signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """

        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNppnotouchR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNppnotouchR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNppnotouchR_dB(self):
        """
        (using in Huawei SNppR test)
        Using mean signal from touch raw data as signal, and peak-peak noise in no touch raw data at touched node as noise
        :return: list of SNR [node1 node2 ...]
        """
        ret_row = [20 * np.log10(val) for val in self.all_sct_SmeanNppnotouchR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SmeanNppnotouchR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SmaxNppfullscreenR(self):

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_max
            sct_row_noise = self.NoTouchFrame.sct_row_p2p.max()
            sct_row_SmaxNppfullscreenR = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SmaxNppfullscreenR)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_max
            sct_col_noise = self.NoTouchFrame.sct_col_p2p.max()
            sct_col_SmaxNppfullscreenR = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SmaxNppfullscreenR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmaxNppfullscreenR_dB(self):

        ret_row = [20 * np.log10(val) for val in self.all_sct_SmaxNppfullscreenR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SmaxNppfullscreenR[1]]
        return [ret_row, ret_col]
    @property
    def all_sct_SminNppfullscreenR(self):

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_min
            sct_row_noise = self.NoTouchFrame.sct_row_p2p.max()
            sct_row_SminNppfullscreenR = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SminNppfullscreenR)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_min
            sct_col_noise = self.NoTouchFrame.sct_col_p2p.max()
            sct_col_SminNppfullscreenR = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SminNppfullscreenR)

        return [ret_row, ret_col]

    @property
    def all_sct_SminNppfullscreenR_dB(self):

        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNppfullscreenR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNppfullscreenR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNppfullscreenR_line(self):

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_min
            sct_row_noise = self.NoTouchFrame.sct_row_p2p
            sct_row_SminNppfullscreenR_line = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SminNppfullscreenR_line)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_min
            sct_col_noise = self.NoTouchFrame.sct_col_p2p
            sct_col_SminNppfullscreenR_line = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SminNppfullscreenR_line)

        return [ret_row, ret_col]

    @property
    def all_sct_SminNppfullscreenR_dB_line(self):

        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNppfullscreenR_line[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNppfullscreenR_line[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNrmsR(self):

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            _, x_node = TouchFrame.sct_row_signal_position
            SmeanNrmsR = TouchFrame.sct_row_signal_mean / TouchFrame.sct_row_rms[x_node]
            ret_row.append(SmeanNrmsR)

        for TouchFrame in self.TouchFrameSets:
            _, y_node = TouchFrame.sct_col_signal_position
            SmeanNrmsR = TouchFrame.sct_col_signal_mean / TouchFrame.sct_col_rms[y_node]
            ret_col.append(SmeanNrmsR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNrmsR_dB(self):

        ret_row = [20 * np.log10(val) for val in self.all_sct_SmeanNrmsR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SmeanNrmsR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNnotouchrmsR(self):

        ret_row = []
        ret_col = []

        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            noise = self.NoTouchFrame.sct_row_rms_csot
            signal = TouchFrame.sct_row_signal_mean
            SmeanNnotouchrmsR = signal / noise
            ret_row.append(SmeanNnotouchrmsR)

        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            noise = self.NoTouchFrame.sct_col_rms_csot
            signal = TouchFrame.sct_col_signal_mean
            SmeanNnotouchrmsR = signal / noise
            ret_col.append(SmeanNnotouchrmsR)

        return [ret_row, ret_col]

    @property
    def all_sct_SmeanNnotouchrmsR_dB(self):
        """
        convert all_sct_SmeanNnotouchrmsR to dB
        """
        ret_row = [20 * np.log10(val) for val in self.all_sct_SmeanNnotouchrmsR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SmeanNnotouchrmsR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNavenodeR(self):
        """
        Huawei and honor snr calculation method,
        using max value of sct average noise as noise
        using min signal as signal
        :return: List of SNR [TouchFrame1, TouchFrame2, ...]
        """

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_min
            _, x_node = TouchFrame.sct_row_signal_position
            sct_row_noise = self.sct_row_noise_ave_line[x_node]
            sct_row_SminNavenodeR = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SminNavenodeR)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_min
            _, y_node = TouchFrame.sct_col_signal_position
            sct_col_noise = self.sct_col_noise_ave_line[y_node]
            sct_col_SminNaveR = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SminNaveR)

        return [ret_row, ret_col]

    @property
    def all_sct_SminNavenodeR_dB(self):
        """
        noise in dB
        """
        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNavenodeR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNavenodeR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNavefullscreenR(self):
        """
        Huawei and honor snr calculation method,
        using max value of sct average noise as noise
        using min signal as signal
        :return: List of SNR [[row 1, col 1], [row2, col 2], ...]
        """

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_min
            sct_row_noise = np.max(self.sct_row_noise_ave_line)
            sct_row_SminNavefullscreenR = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SminNavefullscreenR)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_min
            sct_col_noise = np.max(self.sct_col_noise_ave_line)
            sct_col_SminNavefullscreenR = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SminNavefullscreenR)

        return [ret_row, ret_col]

    @property
    def all_sct_SminNavefullscreenR_dB(self):
        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNavefullscreenR[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNavefullscreenR[1]]
        return [ret_row, ret_col]

    @property
    def all_sct_SminNaveR_line(self):
        """
        Huawei and honor snr calculation method,
        using line data of sct average noise as noise
        using min signal as signal
        :return: List of SNR [[line row 1, line col 1], [line row2, line col 2], ...]
        """

        ret_row = []
        ret_col = []

        for TouchFrame in self.TouchFrameSets:
            sct_row_signal = TouchFrame.sct_row_signal_min
            sct_row_noise = self.sct_row_noise_ave_line
            sct_row_SminNaveR_grid = sct_row_signal / sct_row_noise
            ret_row.append(sct_row_SminNaveR_grid)

        for TouchFrame in self.TouchFrameSets:
            sct_col_signal = TouchFrame.sct_col_signal_min
            sct_col_noise = self.sct_col_noise_ave_line
            sct_col_SminNaveR_grid = sct_col_signal / sct_col_noise
            ret_col.append(sct_col_SminNaveR_grid)

        return [ret_row, ret_col]

    def all_sct_SminNaveR_dB_line(self):
        ret_row = [20 * np.log10(val) for val in self.all_sct_SminNaveR_grid[0]]
        ret_col = [20 * np.log10(val) for val in self.all_sct_SminNaveR_grid[1]]
        return [ret_row, ret_col]

    def boe_snr_summary(self):
        ret = {"Customer": "BOE"}
        if self.NoTouchFrame.mct_grid is not None:
            min_SmaxNppfullscreenR_dB = min(self.all_SmaxNppfullscreenR_dB)
            min_SmaxNppfullscreenR_dB_index = self.all_SmaxNppfullscreenR_dB.index(
                min(self.all_SmaxNppfullscreenR_dB))
            min_SmeanNrmsR_dB = min(self.all_SmeanNrmsR_dB)
            min_SmeanNrmsR_dB_index = self.all_SmeanNrmsR_dB.index(min(self.all_SmeanNrmsR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_p2p_fullscreen": [self.mct_noise_p2p_max] * len(self.TouchFrameSets),
                    "noise_p2p_notouch": self.all_mct_noise_p2p_notouch_node,
                    "noise_rms_touch": np.round(self.all_mct_noise_rms_touch_node, 2),
                    "signal_max": self.all_mct_signal_max,
                    "signal_mean": [round(val, 2) for val in self.all_mct_signal_mean],
                    "SmaxNppmotouchR": self.all_SmaxNppnotouchR,
                    "SmaxNppnotouchR_dB": self.all_SmaxNppnotouchR_dB,
                    "SmaxNppfullscreenR": self.all_SmaxNppfullscreenR,
                    "SmaxNppfullscreenR_dB": self.all_SmaxNppfullscreenR_dB,
                    "SmeanNrmsR": self.all_SmeanNrmsR,
                    "SmeanNrmsR_dB": self.all_SmeanNrmsR_dB
                },
                "final_results": {
                    "min_SmaxNppfullscreenR_dB": "{:.2f}".format(min_SmaxNppfullscreenR_dB),
                    "Position_P2P": f"Touch {min_SmaxNppfullscreenR_dB_index + 1}",
                    "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_SmeanNrmsR_dB_index + 1}",
                    "index_P2P": min_SmaxNppfullscreenR_dB_index,
                    "index_RMS": min_SmeanNrmsR_dB_index,
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SmaxNppfullscreenR_dB = min(self.all_sct_SmaxNppfullscreenR_dB[0])
            min_sct_row_SmaxNppfullscreenR_dB_index = self.all_sct_SmaxNppfullscreenR_dB[0].index(
                min(self.all_sct_SmaxNppfullscreenR_dB[0]))
            min_sct_row_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[0])
            min_sct_row_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[0].index(
                min(self.all_sct_SmeanNrmsR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_p2p_fullscreen": [self.sct_row_p2p_max] * len(self.TouchFrameSets),
                    "noise_p2p_notouch": self.all_sct_noise_p2p_notouch_node[0],
                    "noise_rms_touch": np.round(self.all_sct_noise_rms_touch_node[0], 2),
                    "signal_max": self.all_sct_signal_max[0],
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[0]],
                    "SmaxNppmotouchR": self.all_sct_SmaxNppnotouchR[0],
                    "SmaxNppnotouchR_dB": self.all_sct_SmaxNppnotouchR_dB[0],
                    "SmaxNppfullscreenR": self.all_sct_SmaxNppfullscreenR[0],
                    "SmaxNppfullscreenR_dB": self.all_sct_SmaxNppfullscreenR_dB[0],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[0],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[0]
                },
                "final_results": {
                    "min_sct_row_SmaxNppfullscreenR_dB": "{:.2f}".format(min_sct_row_SmaxNppfullscreenR_dB),
                    "Position_P2P": f"Touch {min_sct_row_SmaxNppfullscreenR_dB_index + 1}",
                    "min_sct_row_SmeanNrmsR_dB": "{:.2f}".format(min_sct_row_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_sct_row_SmeanNrmsR_dB_index + 1}",
                    "index_P2P": min_sct_row_SmaxNppfullscreenR_dB_index,
                    "index_RMS": min_sct_row_SmeanNrmsR_dB_index,

                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SmaxNppfullscreenR_dB = min(self.all_sct_SmaxNppfullscreenR_dB[1])
            min_sct_col_SmaxNppfullscreenR_dB_index = self.all_sct_SmaxNppfullscreenR_dB[1].index(
                min(self.all_sct_SmaxNppfullscreenR_dB[1]))
            min_sct_col_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[1])
            min_sct_col_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[1].index(
                min(self.all_sct_SmeanNrmsR_dB[1]))
            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_p2p_fullscreen": [self.sct_col_p2p_max] * len(self.TouchFrameSets),
                    "noise_p2p_notouch": self.all_sct_noise_p2p_notouch_node[1],
                    "noise_rms_touch": [round(val, 2) for val in self.all_sct_noise_rms_touch_node[1]],
                    "signal_max": self.all_sct_signal_max[1],
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[1]],
                    "SmaxNppnotouchR": self.all_sct_SmaxNppnotouchR[1],
                    "SmaxNppnotouchR_dB": self.all_sct_SmaxNppnotouchR_dB[1],
                    "SmaxNppfullscreenR": self.all_sct_SmaxNppfullscreenR[1],
                    "SmaxNppfullscreenR_dB": self.all_sct_SmaxNppfullscreenR_dB[1],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[1],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[1]
                },
                "final_results": {
                    "min_sct_col_SmaxNppfullscreenR_dB": "{:.2f}".format(min_sct_col_SmaxNppfullscreenR_dB),
                    "Position_P2P": f"Touch {min_sct_col_SmaxNppfullscreenR_dB_index + 1}",
                    "min_sct_col_SmeanNrmsR_dB": "{:.2f}".format(min_sct_col_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_sct_col_SmeanNrmsR_dB_index + 1}",
                    "index_P2P": min_sct_col_SmaxNppfullscreenR_dB_index,
                    "index_RMS": min_sct_col_SmeanNrmsR_dB_index,
                }
            }
            ret["sct_col_summary"] = sct_col_ret

        return ret

    def vnx_snr_summary(self):
        ret = {"Customer": "Visionox"}
        if self.NoTouchFrame.mct_grid is not None:
            min_SmeanNrmsR_dB = min(self.all_SmeanNrmsR_dB)
            min_SmeanNrmsR_dB_index = self.all_SmeanNrmsR_dB.index(min(self.all_SmeanNrmsR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_rms_touch": self.all_mct_noise_rms_touch_node,
                    "signal_mean": self.all_mct_signal_mean,
                    "SmeanNrmsR": self.all_SmeanNrmsR,
                    "SmeanNrmsR_dB": self.all_SmeanNrmsR_dB
                },
                "final_results": {
                    "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_SmeanNrmsR_dB_index + 1}"
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[0])
            min_sct_row_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[0].index(
                min(self.all_sct_SmeanNrmsR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_rms_touch": self.all_sct_noise_rms_touch_node[0],
                    "signal_mean": self.all_sct_signal_mean[0],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[0],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[0]
                },
                "final_results": {
                    "min_sct_row_SmeanNrmsR_dB": "{:.2f}".format(min_sct_row_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_sct_row_SmeanNrmsR_dB_index + 1}"
                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[1])
            min_sct_col_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[1].index(
                min(self.all_sct_SmeanNrmsR_dB[1]))
            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_rms_touch": self.all_sct_noise_rms_touch_node[1],
                    "signal_mean": self.all_sct_signal_mean[1],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[1],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[1]
                },
                "final_results": {
                    "min_sct_col_SmeanNrmsR_dB": "{:.2f}".format(min_sct_col_SmeanNrmsR_dB),
                    "Position_RMS": f"Touch {min_sct_col_SmeanNrmsR_dB_index + 1}"
                }
            }
            ret["sct_col_summary"] = sct_col_ret

        return ret

    def hw_quick_snr_summary(self):
        """
        huawei quick test only need touch raw data!!
        only peak-peak snr is calculated!!
        :return:
        """

        ret = {"Customer": "Huawei_quick"}

        if self.NoTouchFrame.mct_grid is not None:
            min_SminNpptouch_dB = min(self.all_SminNpptouchR_dB)
            min_SminNpptouch_dB_index = self.all_SminNpptouchR_dB.index(min(self.all_SminNpptouchR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_p2p_touch": self.all_mct_noise_p2p_touch_node,
                    "signal_min": self.all_mct_signal_min,
                    "SminNpptouchR": self.all_SminNpptouchR,
                    "SminNpptouchR_dB": self.all_SminNpptouchR_dB,
                },
                "final_results": {
                    "min_SminNpptouch_dB": "{:.2f}".format(min_SminNpptouch_dB),
                    "min_SminNpptouch_dB_index": f"Touch {min_SminNpptouch_dB_index + 1}",
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SminNpptouchR_dB = min(self.all_sct_SminNpptouchR_dB[0])
            min_sct_row_SminNpptouchR_dB_index = self.all_sct_SminNpptouchR_dB[0].index(
                min(self.all_sct_SminNpptouchR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_p2p_touch": self.all_sct_noise_p2p_touch_node[0],
                    "signal_min": self.all_sct_signal_min[0],
                    "SminNpptouchR": self.all_sct_SminNpptouchR[0],
                    "SminNpptouchR_dB": self.all_sct_SminNpptouchR_dB[0]

                },
                "final_results": {
                    "min_sct_row_SminNpptouchR_dB": "{:.2f}".format(min_sct_row_SminNpptouchR_dB),
                    "Position_P2P": f"Touch {min_sct_row_SminNpptouchR_dB_index + 1}",
                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SminNpptouchR_dB = min(self.all_sct_SminNpptouchR_dB[1])
            min_sct_col_SminNpptouchR_dB_index = self.all_sct_SminNpptouchR_dB[1].index(
                min(self.all_sct_SminNpptouchR_dB[1]))

            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_p2p_touch": self.all_sct_noise_p2p_touch_node[1],
                    "signal_min": self.all_sct_signal_min[1],
                    "SminNpptouchR": self.all_sct_SminNpptouchR[1],
                    "SminNpptouchR_dB": self.all_sct_SminNpptouchR_dB[1]
                },
                "final_results": {
                    "min_sct_col_SminNpptouchR_dB": "{:.2f}".format(min_sct_col_SminNpptouchR_dB),
                    "Position_P2P": f"Touch {min_sct_col_SminNpptouchR_dB_index + 1}"
                }
            }
            ret["sct_col_summary"] = sct_col_ret
        return ret

    def hw_thp_afe_snr_summary(self):
        '''
        huawei thp afe test using no touch data as the source of noise!!
        only peak-peak snr is calculated!!
        :return:
        '''
        ret = {"Customer": "Huawei_THP_AFE"}

        if self.NoTouchFrame.mct_grid is not None:
            min_SminNppfullscreenR_dB = min(self.all_SminNppfullscreenR_dB)
            min_SminNppfullscreenR_dB_index = self.all_SminNppfullscreenR_dB.index(min(self.all_SminNppfullscreenR_dB))
            min_SminNavefullscreenR_dB = min(self.all_SminNavefullscreenR_dB)
            min_SminNavefullscreenR_dB_index = self.all_SminNavefullscreenR_dB.index(
                min(self.all_SminNavefullscreenR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_p2p_fullscreen": [self.mct_noise_p2p_max] * len(self.TouchFrameSets),
                    "noise_ave_fullscreen": [self.mct_noise_ave_max] * len(self.TouchFrameSets),
                    "signal_min": self.all_mct_signal_min,
                    "min_SminNppR": self.all_SminNppfullscreenR,
                    "min_SminNppR_dB": self.all_SminNppfullscreenR_dB,
                    "SminNaveR": self.all_SminNavefullscreenR,
                    "SminNaveR_dB": self.all_SminNavefullscreenR_dB,
                },
                "final_results": {
                    "min_SminNppR_dB": "{:.2f}".format(min_SminNppfullscreenR_dB),
                    "min_SminNppR_dB_index": f"Touch {min_SminNppfullscreenR_dB_index + 1}",
                    "min_SminNaveR_dB": "{:.2f}".format(min_SminNavefullscreenR_dB),
                    "min_SminNaveR_dB_index": f"Touch {min_SminNavefullscreenR_dB_index + 1}",
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SminNppfullscreen_dB = min(self.all_sct_SminNppfullscreenR_dB[0])
            min_sct_row_SminNppfullscreen_dB_index = self.all_sct_SminNppfullscreenR_dB[0].index(
                min(self.all_sct_SminNppfullscreenR_dB[0]))
            min_sct_row_SminNavefullscreenR_dB = min(self.all_sct_SminNavefullscreenR_dB[0])
            min_sct_row_SminNavefullscreenR_dB_index = self.all_sct_SminNavefullscreenR_dB[0].index(
                min(self.all_sct_SminNavefullscreenR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_p2p_fullscreen": [self.sct_row_p2p_max] * len(self.TouchFrameSets),
                    "noise_ave_fullscreen": [self.sct_row_noise_ave_max] * len(self.TouchFrameSets),
                    "signal_min": self.all_sct_signal_min[0],
                    "min_SminNppR": self.all_sct_SminNppfullscreenR[0],
                    "min_SminNppR_dB": self.all_sct_SminNppfullscreenR_dB[0],
                    "SminNaveR": self.all_sct_SminNavefullscreenR[0],
                    "SminNaveR_dB": self.all_sct_SminNavefullscreenR_dB[0],
                },
                "final_results": {
                    "min_sct_row_SminNppR_dB": "{:.2f}".format(min_sct_row_SminNppfullscreen_dB),
                    "Position_P2P": f"Touch {min_sct_row_SminNppfullscreen_dB_index + 1}",
                    "min_sct_row_SminNaveR_dB": "{:.2f}".format(min_sct_row_SminNavefullscreenR_dB),
                    "Position_AVE": f"Touch {min_sct_row_SminNavefullscreenR_dB_index + 1}"
                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SminNppfullscreen_dB = min(self.all_sct_SminNppfullscreenR_dB[1])
            min_sct_col_SminNppfullscreen_dB_index = self.all_sct_SminNppfullscreenR_dB[1].index(
                min(self.all_sct_SminNppfullscreenR_dB[1]))
            min_sct_col_SminNavefullscreenR_dB = min(self.all_sct_SminNavefullscreenR_dB[1])
            min_sct_col_SminNavefullscreenR_dB_index = self.all_sct_SminNavefullscreenR_dB[1].index(
                min(self.all_sct_SminNavefullscreenR_dB[1]))
            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_p2p_notouch": [self.sct_col_p2p_max] * len(self.TouchFrameSets),
                    "noise_ave_notouch": [self.sct_col_noise_ave_max] * len(self.TouchFrameSets),
                    "signal_min": self.all_sct_signal_min[1],
                    "SminNppR": self.all_sct_SminNppfullscreenR[1],
                    "SminNppR_dB": self.all_sct_SminNppfullscreenR_dB[1],
                    "SminNaveR": self.all_sct_SminNavefullscreenR[1],
                    "SminNaveR_dB": self.all_sct_SminNavefullscreenR[1]
                },
                "final_results": {
                    "min_sct_col_SminNppR_dB": "{:.2f}".format(min_sct_col_SminNppfullscreen_dB),
                    "Position_P2P": f"Touch {min_sct_col_SminNppfullscreen_dB_index + 1}",
                    "min_sct_col_SminNaveR_dB": "{:.2f}".format(min_sct_col_SminNavefullscreenR_dB),
                    "Position_AVE": f"Touch {min_sct_col_SminNavefullscreenR_dB_index + 1}"
                }
            }
            ret["sct_col_summary"] = sct_col_ret
        return ret

    def csot_snr_summary(self):
        ret = {"Customer": "CSOT"}
        if self.NoTouchFrame.mct_grid is not None:
            min_SmeanNnotouchrmsR_dB = min(self.all_SmeanNnotouchrmsR_dB)
            min_SmeanNnotouchrmsR_dB_index = self.all_SmeanNnotouchrmsR_dB.index(
                min(self.all_SmeanNnotouchrmsR_dB))
            min_SmeanNrmsR_dB = min(self.all_SmeanNrmsR_dB)
            min_SmeanNrmsR_dB_index = self.all_SmeanNrmsR_dB.index(min(self.all_SmeanNrmsR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_rms_notouch": [np.round(self.NoTouchFrame.mct_grid_rms_csot, 2)] * len(self.TouchFrameSets),
                    "noise_rms_touch": np.round(self.all_mct_noise_rms_touch_node, 2),
                    "signal_mean": [round(val, 2) for val in self.all_mct_signal_mean],
                    "SmeanNnotouchrmsR": self.all_SmeanNnotouchrmsR,
                    "SmeanNnotouchrmsR_dB": self.all_SmeanNnotouchrmsR_dB,
                    "SmeanNrmsR": self.all_SmeanNrmsR,
                    "SmeanNrmsR_dB": self.all_SmeanNrmsR_dB
                },
                "final_results": {
                    "min_SmeanNnotouchrmsR_dB": "{:.2f}".format(min_SmeanNnotouchrmsR_dB),
                    "Position_RMS_notouch": f"Touch {min_SmeanNnotouchrmsR_dB_index + 1}",
                    "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_notouch": min_SmeanNnotouchrmsR_dB_index,
                    "index_RMS_touch": min_SmeanNrmsR_dB_index,
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[0])
            min_sct_row_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[0].index(
                min(self.all_sct_SmeanNrmsR_dB[0]))
            min_sct_row_SmeanNnotouchrmsR_dB = min(self.all_sct_SmeanNnotouchrmsR_dB[0])
            min_sct_row_SmeanNnotouchrmsR_dB_index = self.all_sct_SmeanNnotouchrmsR_dB[0].index(
                min(self.all_sct_SmeanNnotouchrmsR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_rms_notouch": [np.round(self.NoTouchFrame.sct_row_rms_csot, 2)] * len(self.TouchFrameSets),
                    "noise_rms_touch": np.round(self.all_sct_noise_rms_touch_node[0], 2),
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[0]],
                    "SmeanNnotouchrmsR": self.all_sct_SmeanNnotouchrmsR[0],
                    "SmeanNnotouchrmsR_dB": self.all_sct_SmeanNnotouchrmsR_dB[0],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[0],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[0]
                },
                "final_results": {
                    "min_sct_row_SmeanNnotouchrmsR_dB": "{:.2f}".format(min_sct_row_SmeanNnotouchrmsR_dB),
                    "Position_RMS_notouch": f"Touch {min_sct_row_SmeanNnotouchrmsR_dB_index + 1}",
                    "min_sct_row_SmeanNrmsR_dB": "{:.2f}".format(min_sct_row_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_sct_row_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_notouch": min_sct_row_SmeanNnotouchrmsR_dB_index,
                    "index_RMS_touch": min_sct_row_SmeanNrmsR_dB_index,

                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[1])
            min_sct_col_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[1].index(
                min(self.all_sct_SmeanNrmsR_dB[1]))
            min_sct_col_SmeanNnotouchrmsR_dB = min(self.all_sct_SmeanNnotouchrmsR_dB[1])
            min_sct_col_SmeanNnotouchrmsR_dB_index = self.all_sct_SmeanNnotouchrmsR_dB[1].index(
                min(self.all_sct_SmeanNnotouchrmsR_dB[1]))
            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_rms_notouch": [np.round(self.NoTouchFrame.sct_col_rms_csot, 2)] * len(self.TouchFrameSets),
                    "noise_rms_touch": [round(val, 2) for val in self.all_sct_noise_rms_touch_node[1]],
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[1]],
                    "SmeanNnotouchrmsR": self.all_sct_SmeanNnotouchrmsR[1],
                    "SmeanNnotouchrmsR_dB": self.all_sct_SmeanNnotouchrmsR_dB[1],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[1],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[1]
                },
                "final_results": {
                    "min_sct_col_SmeanNnotouchrmsR_dB": "{:.2f}".format(min_sct_col_SmeanNnotouchrmsR_dB),
                    "Position_RMS_notouch": f"Touch {min_sct_col_SmeanNnotouchrmsR_dB_index + 1}",
                    "min_sct_col_SmeanNrmsR_dB": "{:.2f}".format(min_sct_col_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_sct_col_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_notouch": min_sct_col_SmeanNnotouchrmsR_dB_index,
                    "index_RMS_touch": min_sct_col_SmeanNrmsR_dB_index,
                }
            }
            ret["sct_col_summary"] = sct_col_ret

        return ret

    def lenovo_snr_summary(self):
        ret = {"Customer": "Lenovo"}
        if self.NoTouchFrame.mct_grid is not None:
            min_SmeanNrmsR_dB = min(self.all_SmeanNrmsR_dB)
            min_SmeanNrmsR_dB_index = self.all_SmeanNrmsR_dB.index(min(self.all_SmeanNrmsR_dB))
            mct_ret = {
                "snr_summary": {
                    "touched node": self.all_touched_position,
                    "noise_rms_touch": np.round(self.all_mct_noise_rms_touch_node, 2),
                    "signal_mean": [round(val, 2) for val in self.all_mct_signal_mean],
                    "SmeanNrmsR": self.all_SmeanNrmsR,
                    "SmeanNrmsR_dB": self.all_SmeanNrmsR_dB
                },
                "final_results": {
                    "min_SmeanNrmsR_dB": "{:.2f}".format(min_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_touch": min_SmeanNrmsR_dB_index,
                }
            }
            ret["mct_summary"] = mct_ret

        if self.NoTouchFrame.sct_row is not None:
            min_sct_row_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[0])
            min_sct_row_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[0].index(
                min(self.all_sct_SmeanNrmsR_dB[0]))

            sct_row_ret = {
                "snr_sct_row_summary": {
                    "touched node": self.all_sct_touched_position[0],
                    "noise_rms_touch": np.round(self.all_sct_noise_rms_touch_node[0], 2),
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[0]],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[0],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[0]
                },
                "final_results": {
                    "min_sct_row_SmeanNrmsR_dB": "{:.2f}".format(min_sct_row_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_sct_row_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_touch": min_sct_row_SmeanNrmsR_dB_index,

                }
            }
            ret["sct_row_summary"] = sct_row_ret

        if self.NoTouchFrame.sct_col is not None:
            min_sct_col_SmeanNrmsR_dB = min(self.all_sct_SmeanNrmsR_dB[1])
            min_sct_col_SmeanNrmsR_dB_index = self.all_sct_SmeanNrmsR_dB[1].index(
                min(self.all_sct_SmeanNrmsR_dB[1]))

            sct_col_ret = {
                "snr_sct_col_summary": {
                    "touched node": self.all_sct_touched_position[1],
                    "noise_rms_touch": [round(val, 2) for val in self.all_sct_noise_rms_touch_node[1]],
                    "signal_mean": [round(val, 2) for val in self.all_sct_signal_mean[1]],
                    "SmeanNrmsR": self.all_sct_SmeanNrmsR[1],
                    "SmeanNrmsR_dB": self.all_sct_SmeanNrmsR_dB[1]
                },
                "final_results": {
                    "min_sct_col_SmeanNrmsR_dB": "{:.2f}".format(min_sct_col_SmeanNrmsR_dB),
                    "Position_RMS_touch": f"Touch {min_sct_col_SmeanNrmsR_dB_index + 1}",
                    "index_RMS_touch": min_sct_col_SmeanNrmsR_dB_index,
                }
            }
            ret["sct_col_summary"] = sct_col_ret

        return ret

    def write_out_csv(self, result_dict):

        row = ["Touch {}".format(idx + 1) for idx in range(len(self.TouchFrameSets))]
        output_path = os.path.join(self.output_folder,
                                   result_dict["Customer"] + "_" + self.pattern + "_output_info.csv")

        with open(output_path, 'w', newline='') as f:

            if self.NoTouchFrame.mct_grid is not None:
                data_out = pd.DataFrame(index=row,
                                        data=result_dict["mct_summary"]["snr_summary"])
                # print(data_out)
                data_out = data_out.round(2)
                # print(data_out)
                csv_write = csv.writer(f)
                csv_write.writerow(["MCT Summary"])
                data_out.to_csv(f)

            if self.NoTouchFrame.sct_row is not None:
                data_out = pd.DataFrame(index=row,
                                        data=result_dict["sct_row_summary"]["snr_sct_row_summary"])
                data_out = data_out.round(2)
                csv_write = csv.writer(f)
                csv_write.writerow("\n")
                csv_write.writerow(["SCT Rx Summary"])

                data_out.to_csv(f)

            if self.NoTouchFrame.sct_col is not None:
                data_out = pd.DataFrame(index=row,
                                        data=result_dict["sct_col_summary"]["snr_sct_col_summary"])
                data_out = data_out.round(2)
                csv_write = csv.writer(f)
                csv_write.writerow("\n")
                csv_write.writerow(["SCT Tx Summary"])
                data_out.to_csv(f)

        if os.path.exists(output_path):
            with open(output_path, 'a+', newline='') as f:
                csv_write = csv.writer(f)

                if self.NoTouchFrame.mct_grid is not None:
                    csv_write.writerow("\n")

                    csv_write.writerow(["Final Result MCT:"])
                    for x, y in zip(list(result_dict["mct_summary"]["final_results"].keys()),
                                    list(result_dict["mct_summary"]["final_results"].values())):
                        csv_write.writerow([x, y])

                if self.NoTouchFrame.sct_row is not None:
                    csv_write.writerow("\n")

                    csv_write.writerow(["Final Result SCT Rx:"])
                    for x, y in zip(list(result_dict["sct_row_summary"]["final_results"].keys()),
                                    list(result_dict["sct_row_summary"]["final_results"].values())):
                        csv_write.writerow([x, y])

                if self.NoTouchFrame.sct_col is not None:
                    csv_write.writerow("\n")

                    csv_write.writerow(["Final Result SCT Tx:"])
                    for x, y in zip(list(result_dict["sct_col_summary"]["final_results"].keys()),
                                    list(result_dict["sct_col_summary"]["final_results"].values())):
                        csv_write.writerow([x, y])

    def generate_hw_grid_snr(self,pattern):
        for idx in range(len(self.TouchFrameSets)):
            self.write_out_decode_grid_line_csv(mct_data=self.all_SminNppfullscreenR_grid[idx] if self.NoTouchFrame.mct_flag else None,
                                                row_data=self.all_sct_SminNppfullscreenR_line[0][idx] if self.NoTouchFrame.sct_flag else None,
                                                col_data=self.all_sct_SminNppfullscreenR_line[1][idx] if self.NoTouchFrame.sct_flag else None,
                                                filename= f"{pattern}_SNppR")
            self.write_out_decode_grid_line_csv(mct_data=self.all_SminNaveR_grid[idx] if self.NoTouchFrame.mct_flag else None,
                                                row_data=self.all_sct_SminNaveR_line[0][idx] if self.NoTouchFrame.sct_flag else None,
                                                col_data=self.all_sct_SminNaveR_line[1][idx] if self.NoTouchFrame.sct_flag else None,
                                                filename= f"{pattern}_SNaveR")
    def write_out_filtered_data_csv(self):
        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            touch_out_path = os.path.join(self.output_folder,
                                          self.pattern + "_touch_num_{}.csv".format(int(idx)))
            tmp_df = TouchFrame.df_raw_data
            tmp_df = tmp_df.drop(columns=['cycle', 'duration (msec)'])
            if TouchFrame.signal_low_thr is not None:
                _, row_idx, col_idx = TouchFrame.mct_signal_position
                signal_col_name = tmp_df.columns[tmp_df.columns.str.contains(f'\[{row_idx}\]\[{col_idx}\]', regex=True)]
                signal_col_name = signal_col_name.values[0]
                tmp_df = tmp_df[(tmp_df[signal_col_name] <= TouchFrame.signal_high_thr) & (
                        tmp_df[signal_col_name] >= TouchFrame.signal_low_thr)].reset_index(drop=True)
            tmp_df.to_csv(touch_out_path)

            pass

    def write_out_decode_grid_line_csv(self, mct_data=None, row_data=None, col_data=None, filename=None):

        # write out No Touch grid mct raw data
        output_path = os.path.join(self.output_folder, f"{filename}.csv")

        with open(output_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            if mct_data is None:
                mct_data = np.zeros([self.NoTouchFrame.sct_row.shape[1], self.NoTouchFrame.sct_col.shape[1]])
            else:
                mct_data = np.round(mct_data,2)

            if row_data is not None:
                row_data = np.round(row_data,2)

            if col_data is not None:
                col_data = np.round(col_data,2)

            # write a row to the csv file
            writer.writerow(["Mutual SNR"])
            head = [f"Tx {n}" for n in range(mct_data.shape[1])]
            writer.writerow(head)
            for line_no, line in enumerate(mct_data):
                li = list(line)
                li.append(f"Rx {line_no}")
                if row_data is not None:
                    li.extend(["\n", f"Row {line_no}", row_data[line_no]])
                writer.writerow(li)

            if col_data is not None:
                writer.writerow(["Tx SNR"])
                head = [f"Col {n}" for n in range(len(col_data))]
                writer.writerow(head)
                writer.writerow(list(col_data))
            writer.writerow("\n")

        f.close()

    def write_out_decode_mct_csv(self):

        # write out No Touch grid mct raw data
        notouch_out_path = os.path.join(self.output_folder, self.pattern + "_mct_grid_rawdata_NoTouch.csv")

        with open(notouch_out_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            if self.NoTouchFrame.mct_grid is not None:
                all_mct_data = self.NoTouchFrame.mct_grid
            else:
                all_mct_data = np.zeros([self.NoTouchFrame.sct_row.shape[0], self.NoTouchFrame.sct_row.shape[1],
                                         self.NoTouchFrame.sct_col.shape[1]])
            for idx, mct_grid in enumerate(all_mct_data):
                # write a row to the csv file
                writer.writerow(["Frame {}:".format(idx + 1)])
                writer.writerow(["Mutual Data"])
                head = [f"Tx {n}" for n in range(mct_grid.shape[1])]
                writer.writerow(head)
                for line_no, line in enumerate(mct_grid):
                    li = list(line)
                    li.append(f"Rx {line_no}")
                    if self.NoTouchFrame.sct_row is not None:
                        li.extend(["\n", f"Row {line_no}", self.NoTouchFrame.sct_row[idx][line_no]])
                    writer.writerow(li)

                if self.NoTouchFrame.sct_col is not None:
                    writer.writerow(["Self Cap. Col Data"])
                    head = [f"Col {n}" for n in range(len(self.NoTouchFrame.sct_col[idx]))]
                    writer.writerow(head)
                    writer.writerow(list(self.NoTouchFrame.sct_col[idx]))
                writer.writerow("\n")

        f.close()

        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            touch_out_path = os.path.join(self.output_folder,
                                          self.pattern + "_mct_grid_rawdata_Touch_{}.csv".format(int(idx)))
            with open(touch_out_path, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                if TouchFrame.mct_grid is not None:
                    all_mct_data = TouchFrame.mct_grid
                else:
                    all_mct_data = np.zeros(
                        [TouchFrame.sct_row.shape[0], TouchFrame.sct_row.shape[1], TouchFrame.sct_col.shape[1]])
                for idx, mct_grid in enumerate(all_mct_data):
                    # write a row to the csv file
                    writer.writerow(["Frame {}:".format(idx + 1)])
                    head = [f"Tx {n}" for n in range(mct_grid.shape[1])]
                    writer.writerow(head)

                    for line_no, line in enumerate(mct_grid):
                        li = list(line)
                        li.append(f"Rx {line_no}")
                        if TouchFrame.sct_row is not None:
                            li.extend(["\n", f"Row {line_no}", TouchFrame.sct_row[idx][line_no]])
                        writer.writerow(li)

                    if TouchFrame.sct_col is not None:
                        writer.writerow("\n")
                        head = [f"Col {n}" for n in range(len(TouchFrame.sct_col[idx]))]
                        writer.writerow(head)
                        writer.writerow(list(TouchFrame.sct_col[idx]))
                    writer.writerow("\n")
            f.close()

    def plot_mct_noise_rms(self):
        ret = []
        touched_node_list = self.all_touched_position
        for idx, TouchFrame in enumerate(self.TouchFrameSets):
            ynode, xnode = touched_node_list[idx]
            grid_Data = TouchFrame.mct_grid_rms
            fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
            ax = sns.heatmap(data=grid_Data, annot=True, fmt='.0f', vmin=0)
            ax.set_ylabel('Row')
            ax.set_xlabel('Column')
            plt.title('Grid RMS Noise without Touch [%d , %d]\n touched node is [%d,%d] -> RMS Noise is %.0f' % (
                self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, ynode, xnode, grid_Data[ynode][xnode])
                      )
            # annotate touched position
            self.annotate_grid_figure(ax=ax, ynode=ynode, xnode=xnode, Text=f"Touch {idx + 1}")

            plt.tight_layout()
            fig.savefig(os.path.join(self.output_folder, "Figure_MCT_rms_noise_touch_{}.png").format(idx))
            print("Successfully generate figure {}!!!!!".format("Figure_MCT_rms_noise_touch_{}.png").format(idx))
            ret.append(fig)
        return ret

    def plot_mct_noise_p2p_annotated(self):
        grid_Data = self.NoTouchFrame.mct_grid_p2p
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_Data, annot=True, fmt='.0f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('Grid Peak-Peak Noise without Touch [%d , %d]\n Mean=%.0f; Min=%.0f; Max=%.0f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, grid_Data.mean(), grid_Data.min(),
            grid_Data.max())
                  )

        for idx, (ynode, xnode) in enumerate(self.all_touched_position):
            self.annotate_grid_figure(ax=ax, ynode=ynode, xnode=xnode, Text=f"Touch {idx + 1}")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_p2p_noise_annotated.png"))
        print("Successfully generate figure {}!!!!!".format("Figure_MCT_p2p_noise_annotated.png"))
        return fig

    def plot_mct_noise_p2p(self):
        grid_Data = self.NoTouchFrame.mct_grid_p2p
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_Data, annot=True, fmt='.0f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('MCT Peak-Peak Noise without Touch [%d , %d]\n Mean=%.0f; Min=%.0f; Max=%.0f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, grid_Data.mean(), grid_Data.min(),
            grid_Data.max())
                  )

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_p2p_noise.png"))
        return fig

    def plot_mct_noise_average(self):
        grid_Data = self.mct_noise_ave_grid
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_Data, annot=True, fmt='.2f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('MCT Average Noise without Touch [%d , %d]\n Mean=%.2f; Min=%.2f; Max=%.2f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, grid_Data.mean(), grid_Data.min(),
            grid_Data.max())
                  )

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_average_noise.png"))
        return fig

    def plot_mct_positive_annotate(self):
        grid_data = self.all_mct_pos_noise_grid
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_data, annot=True, fmt='.0f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('Grid positive Noise [%d , %d]\n Mean=%.0f; Min=%.0f; Max=%.0f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, grid_data.mean(), grid_data.min(),
            grid_data.max()))

        for idx, (ynode, xnode) in enumerate(self.all_touched_position):
            self.annotate_grid_figure(ax=ax, ynode=ynode, xnode=xnode, Text=f"Touch {idx + 1}")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_positive_annotated.png"))
        print("Successfully generate figure {}!!!!!".format("Figure_MCT_positive_annotated.png"))
        return fig

    def plot_mct_negative_annotate(self):
        grid_data = self.all_mct_neg_noise_grid
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_data, annot=True, fmt='.0f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('Grid Negative Noise [%d , %d]\n Mean=%.0f; Min=%.0f; Max=%.0f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num, grid_data.mean(), grid_data.min(),
            grid_data.max()))

        for idx, (ynode, xnode) in enumerate(self.all_touched_position):
            self.annotate_grid_figure(ax=ax, ynode=ynode, xnode=xnode, Text=f"Touch {idx + 1}")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_negative_annotated.png"))
        print("Successfully generate figure {}!!!!!".format("Figure_MCT_negative_annotated.png"))
        return fig

    def plot_mct_touch_signal_all(self):
        touch_data = []
        signal_list = []
        for TouchFrame in self.TouchFrameSets:
            signal = TouchFrame.mct_signal_max
            touch_grid = TouchFrame.mct_grid_mean
            _, ynode, xnode = TouchFrame.mct_signal_position
            touch_grid[ynode][xnode] = signal
            touch_data.append(touch_grid)
            signal_list.append(signal)

        touch_data = np.array(touch_data)
        signal_array = np.array(signal_list)
        grid_Data = touch_data.max(axis=0)
        fig = plt.figure(figsize=self.standard_width_picture, dpi=110)
        ax = sns.heatmap(data=grid_Data, annot=True, fmt='.0f', vmin=0, vmax=1000)
        ax.set_ylabel('Row')
        ax.set_xlabel('Column')
        plt.title('Grid signal with Touch [%d , %d] \nMean=%.0f; Min=%.0f; Max=%.0f' % (
            self.NoTouchFrame.row_num, self.NoTouchFrame.col_num,
            signal_array.mean(), signal_array.min(), signal_array.max())
                  )

        plt.tight_layout()

        fig.savefig(os.path.join(self.output_folder, "Figure_MCT_all_signals.png"))
        return fig

    def plot_sct_touch_signal_all(self):
        # plt.figure()
        sns.set_style('darkgrid')
        # sns.barplot(data =df,x = "value",y = "x_label",color = 'deepskyblue' )
        # plt.xlabel("Interval")
        # plt.show()
        signal_row_mean = np.mean(self.all_sct_signal_mean[0])
        signal_col_mean = np.mean(self.all_sct_signal_mean[1])
        fig, ax = plt.subplots(1, 2, figsize=self.standard_width_picture, dpi=110)
        ax[0].vlines(signal_row_mean, ymin=-2, ymax=self.row_num, colors='grey', linestyle=':', label='Target Value')
        ax[0].vlines([signal_row_mean * 1.2, signal_row_mean * 0.8],
                     ymin=-2, ymax=self.row_num, colors='grey', linestyle='-.', label='Limits')
        ax[0].legend()

        touch_data_row = []
        for TouchFrame in self.TouchFrameSets:
            touch_row = TouchFrame.sct_row_mean
            touch_data_row.append(touch_row)
        touch_data_row = np.array(touch_data_row).astype(int)
        touch_data_row = touch_data_row.max(axis=0)
        df_row = pd.DataFrame({
            "value": touch_data_row,
            "idx": [f"{i}" for i in range(len(touch_data_row))]
        })
        sns.barplot(data=df_row, x="value", y="idx", color='deepskyblue', ax=ax[0])
        ax[0].set_xlabel('Signal')
        ax[0].set_ylabel('Rows/Rx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[0].set_yticks(range(0, self.row_num))

        ax[1].hlines(signal_col_mean, xmin=0, xmax=self.col_num, colors='grey', linestyle=':', label='Target Value')
        ax[1].hlines([signal_col_mean * 1.1, signal_col_mean * 0.9],
                     xmin=0, xmax=self.col_num, colors='grey', linestyle='-.', label='Limits')
        ax[1].legend()

        touch_data_col = []
        for TouchFrame in self.TouchFrameSets:
            touch_col = TouchFrame.sct_col_mean
            touch_data_col.append(touch_col)
        touch_data_col = np.array(touch_data_col).astype(int)
        touch_data_col = touch_data_col.max(axis=0)
        df_col = pd.DataFrame({
            "value": touch_data_col,
            "idx": [f"{i}" for i in range(len(touch_data_col))]
        })
        sns.barplot(data=df_col, x="idx", y="value", color='deepskyblue', ax=ax[1])
        ax[1].set_ylabel('Signal')
        ax[1].set_xlabel('Cols/Tx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[1].set_xticks(range(0, self.col_num))

        fig.suptitle('Line All Touch Signal \nRow Mean=%.0f; Row Min=%.0f; Row Max=%.0f \nCol Mean=%.0f; Col '
                     'Min=%.0f; Col Max=%.0f' % (
                         np.mean(self.all_sct_signal_max[0]), np.min(self.all_sct_signal_min[0]),
                         np.max(self.all_sct_signal_mean[0]),
                         np.mean(self.all_sct_signal_max[1]), np.min(self.all_sct_signal_min[1]),
                         np.max(self.all_sct_signal_mean[1])))

        plt.tight_layout()

        fig.savefig(os.path.join(self.output_folder, "Figure_sct_signals.png"))

    def plot_sct_positive_noise(self):
        sns.set_style('darkgrid')

        fig, ax = plt.subplots(1, 2, sharey=False, sharex=False, figsize=self.standard_width_picture, dpi=110)

        touch_data_row = self.all_sct_pos_noise_line[0]
        df_row = pd.DataFrame({
            "value": touch_data_row,
            "idx": [f"{i}" for i in range(len(touch_data_row))]
        })
        sns.barplot(data=df_row, x="value", y="idx", color='deepskyblue', ax=ax[0])
        ax[0].set_xlabel('Signal')
        ax[0].set_ylabel('Rows/Rx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[0].set_yticks(range(0, self.row_num))

        touch_data_col = self.all_sct_pos_noise_line[1]

        df_col = pd.DataFrame({
            "value": touch_data_col,
            "idx": [f"{i}" for i in range(len(touch_data_col))]
        })
        sns.barplot(data=df_col, x="idx", y="value", color='deepskyblue', ax=ax[1])
        ax[1].set_ylabel('Signal')
        ax[1].set_xlabel('Cols/Tx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[1].set_xticks(range(0, self.col_num))

        fig.suptitle('Line All Touch Positive Noise \nRow Mean=%.0f; Row Min=%.0f; Row Max=%.0f \nCol Mean=%.0f; Col '
                     'Min=%.0f; Col Max=%.0f' % (
                         np.mean(self.all_sct_pos_noise_line[0]), np.min(self.all_sct_pos_noise_line[0]),
                         np.max(self.all_sct_pos_noise_line[0]),
                         np.mean(self.all_sct_pos_noise_line[1]), np.min(self.all_sct_pos_noise_line[1]),
                         np.max(self.all_sct_pos_noise_line[1])))

        plt.tight_layout()

        fig.savefig(os.path.join(self.output_folder, "Figure_sct_positive_noise.png"))

    def plot_sct_negative_noise(self):
        sns.set_style('darkgrid')

        fig, ax = plt.subplots(1, 2, sharey=False, sharex=False, figsize=self.standard_width_picture, dpi=110)

        touch_data_row = self.all_sct_neg_noise_line[0]
        df_row = pd.DataFrame({
            "value": touch_data_row,
            "idx": [f"{i}" for i in range(len(touch_data_row))]
        })
        sns.barplot(data=df_row, x="value", y="idx", color='deepskyblue', ax=ax[0])
        ax[0].set_xlabel('Signal')
        ax[0].set_ylabel('Rows/Rx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[0].set_yticks(range(0, self.row_num))

        touch_data_col = self.all_sct_neg_noise_line[1]

        df_col = pd.DataFrame({
            "value": touch_data_col,
            "idx": [f"{i}" for i in range(len(touch_data_col))]
        })
        sns.barplot(data=df_col, x="idx", y="value", color='deepskyblue', ax=ax[1])
        ax[1].set_ylabel('Signal')
        ax[1].set_xlabel('Cols/Tx')
        # ax[0].set_ylim(0, plot_axis_limit)
        # ax[0].set_xlim(-1, self.Columns)
        ax[1].set_xticks(range(0, self.col_num))

        fig.suptitle('Line All Touch Negative Noise \nRow Mean=%.0f; Row Min=%.0f; Row Max=%.0f \nCol Mean=%.0f; Col '
                     'Min=%.0f; Col Max=%.0f' % (
                         np.mean(self.all_sct_neg_noise_line[0]), np.min(self.all_sct_neg_noise_line[0]),
                         np.max(self.all_sct_neg_noise_line[0]),
                         np.mean(self.all_sct_neg_noise_line[1]), np.min(self.all_sct_neg_noise_line[1]),
                         np.max(self.all_sct_neg_noise_line[1])))

        plt.tight_layout()

        fig.savefig(os.path.join(self.output_folder, "Figure_sct_negative_noise.png"))

    def annotate_grid_figure(self, ax, ynode, xnode, Text, boxcoler="cyan", arrowcolor="cyan"):

        ax.add_patch(patches.Rectangle((xnode, ynode), 1, 1, fill=False,
                                       facecolor=None, edgecolor=boxcoler, linewidth=4.0))
        if xnode < (self.col_num * 2) / 3:
            # exit arrow on the right side
            if ynode < (self.row_num * 2) / 3:
                # exit arrow on the bottom
                arrow_x, arrow_y = xnode + 1, ynode + 1
                textbox_x, textbox_y = xnode + 1.5, ynode + 3

            else:
                # exit arrow on the top
                arrow_x, arrow_y = xnode + 1, ynode
                textbox_x, textbox_y = xnode + 1.5, ynode - 2
        else:
            # exit on the left
            # exit arrow on the right side
            if ynode < (self.row_num * 2) / 3:
                # exit arrow on the bottom
                arrow_x, arrow_y = xnode, ynode + 1
                textbox_x, textbox_y = xnode - 1.5, ynode + 3

            else:
                # exit arrow on the top
                arrow_x, arrow_y = xnode, ynode
                textbox_x, textbox_y = xnode - 1.5, ynode - 2

        ax.annotate(Text,
                    xy=(arrow_x, arrow_y), xycoords='data',
                    xytext=(textbox_x, textbox_y), textcoords='data',
                    bbox=dict(boxstyle="round", fc=boxcoler, alpha=0.65),
                    arrowprops=dict(arrowstyle="->", edgecolor=arrowcolor,
                                    connectionstyle="angle,angleA=90,angleB=0,rad=10"))


def get_touched_num(folder, prefix):
    """

    :param folder: raw data folder
    :return: index number list. i.e [wi1.csv,w2.csv,w5.csv] -> [1,2,5]
    """
    files = os.listdir(folder)
    ret = []

    for file in files:
        if re.search('{}(\d+)'.format(prefix), file):
            ret.append(re.search('{}(\d+)'.format(prefix), file).group(1))

    return ret


def write_out_final_result_csv(out_path, header, data):
    # write out No Touch grid mct raw data
    # out_path = os.path.join(folder, "result_summary.csv")
    with open(out_path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(header)
        for idx, line in enumerate(data):
            li = list(line)
            writer.writerow(li)

    f.close()
