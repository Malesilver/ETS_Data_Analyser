import re
import csv
import numpy as np
import os
from typing import List
import pandas as pd
from enum import Enum

from copy import deepcopy

file_dir = os.path.dirname(__file__)  # the directory that class "option" resides in
pd.set_option('display.max_columns', None)

MCT_DELTAGEN_DATA = 0
SCTY_DELTAGEN_DATA = 1
SCTX_DELTAGEN_DATA = 2
MAX_DELTA_VALUE = 3000
MIN_DELTA_VALUE = -3000

HEADER_ETS = {
    "Delta":
    [[MCT_DELTAGEN_DATA, "mct_deltas.values[0][0]", "mct_deltas", 0, 0],
    [SCTY_DELTAGEN_DATA, "sct_row_deltas[0]", "sct_row", 0, 0],
    [SCTX_DELTAGEN_DATA, "sct_col_deltas[0]", "sct_col", 0, 0]],
    "Signal":
    [[MCT_DELTAGEN_DATA, "mct_signals.mct_signals[0][0]", "mct_signals", 0, 0],
    [SCTY_DELTAGEN_DATA, "sct_signals.sct_row_signals[0]", "sct_row_signals", 0, 0],
    [SCTX_DELTAGEN_DATA, "sct_signals.sct_col_signals[0]", "sct_col_signals", 0, 0]],
    "Baseline":
    [[MCT_DELTAGEN_DATA, "mct_signals.mct_signals[0][0]", "mct_deltas", 0, 0],
    [SCTY_DELTAGEN_DATA, "sct_row_deltas[0]", "sct_row", 0, 0],
    [SCTX_DELTAGEN_DATA, "sct_col_deltas[0]", "sct_col", 0, 0]]

}


class ETS_Data_Type(Enum):
    Signal = "signals",
    Signal_IQ='signals_q',
    Delta = 'deltas',
    Baseline = 'baseline',
    Nodemap = 'tbd',
    Unknown = 255,



class ETS_Dataframe:
    def __init__(self, file_path=None, Header_index=None,start_idx=None,end_idx = None):

        self.mct_grid = None
        self.sct_row = None
        self.sct_col = None
        self.row_num = None
        self.col_num = None
        self.Header_index = deepcopy(Header_index)
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.frame_num = None
        self.DataType = None
        self.mct_flag = False
        self.sct_flag = False

        self.file_ext = os.path.basename(file_path).split(".")[-1]
        if self.file_ext == "csv":
            self.data_init = self.load_data_from_ets_csv(file_path)
        elif self.file_ext == "txt":
            pass
        elif self.file_ext == "json":
            pass

        # temp_funciton
        self.signal_low_thr = None
        self.signal_high_thr = None
        self.df_raw_data = pd.read_csv(file_path)

    def load_data_from_ets_csv(self,file_path):

        df_data = pd.read_csv(file_path)

        header = list(df_data.columns)
        flag_start_index = 0
        flag_end_index = 0
        # get flag name
        for index, name in enumerate(header):
            if "duration" in name:
                flag_start_index = index + 1
                continue
            if re.search(r'\d', name) and flag_start_index != 0:
                flag_end_index = index
                break

        flag_name_list = header[flag_start_index:flag_end_index]
        for flag in flag_name_list:
            df_data=df_data[df_data[flag] == 1]



        # define touch type
        if 'signals' in flag_name_list[0]:
            for name in flag_name_list:
                if name.endswith('signals_q'):
                    self.DataType = ETS_Data_Type.Signal_IQ
                    break
                self.DataType = ETS_Data_Type.Signal

        elif 'baseline' in flag_name_list[0]:
            self.DataType = ETS_Data_Type.Baseline

        elif 'deltas' in flag_name_list[0]:
            self.DataType = ETS_Data_Type.Delta

        elif 'touches' in flag_name_list[0]:
            self.DataType = ETS_Data_Type.Nodemap
        else:
            self.DataType = ETS_Data_Type.Unknown

        # get index
        for name in flag_name_list:
            if 'mct' in name:
                self.mct_flag = True

            if 'sct' in name:
                self.sct_flag = True

        # initialise mct and sct data
        if self.DataType is ETS_Data_Type.Delta or self.DataType is ETS_Data_Type.Signal or self.DataType is ETS_Data_Type.Baseline:

            if self.mct_flag is True and self.sct_flag is True:
                mct_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains(f"mct_{self.DataType.value[0]}", regex=True)]
                sct_row_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                                df_data.columns.str.contains(f"sct_row_{self.DataType.value[0]}", regex=True)]
                sct_col_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                                df_data.columns.str.contains(f"sct_col_{self.DataType.value[0]}", regex=True)]

                row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
                assert row == re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
                assert col == re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)
                self.row_num = int(row) + 1
                self.col_num = int(col) + 1

                self.mct_grid = df_data[mct_name].values.reshape([len(df_data), self.row_num, self.col_num])
                self.sct_row = df_data[sct_row_name].values.reshape([len(df_data), self.row_num])
                self.sct_col = df_data[sct_col_name].values.reshape([len(df_data), self.col_num])

            elif self.mct_flag is True:
                mct_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains(f"mct_{self.DataType.value[0]}", regex=True)]
                row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
                self.row_num = int(row) + 1
                self.col_num = int(col) + 1
                self.mct_grid = df_data[mct_name].values.reshape([len(df_data), self.row_num, self.col_num])

            elif self.sct_flag is True:
                sct_row_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains(f"sct_row_{self.DataType.value[0]}", regex=True)]
                sct_col_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains(f"sct_col_{self.DataType.value[0]}", regex=True)]

                row = re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
                col = re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)

                self.row_num = int(row) + 1
                self.col_num = int(col) + 1

                self.sct_row = df_data[sct_row_name].values.reshape([len(df_data), self.row_num])
                self.sct_col = df_data[sct_col_name].values.reshape([len(df_data), self.col_num])
            else:
                raise ('error')


        elif self.DataType is ETS_Data_Type.Signal_IQ:
            if self.mct_flag is True and self.sct_flag is True:
                mct_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                        df_data.columns.str.contains("mct_signals") &
                                        ~df_data.columns.str.contains("_q")]

                mct_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                        df_data.columns.str.contains("mct_signals") &
                                        df_data.columns.str.contains("_q")]

                sct_row_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains("sct_row_signals") &
                                          ~df_data.columns.str.contains("_q")]

                sct_row_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains("sct_row_signals") &
                                            df_data.columns.str.contains("_q")]

                sct_col_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains("sct_col_signals") &
                                          ~df_data.columns.str.contains("_q")]

                sct_col_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains("sct_col_signals") &
                                            df_data.columns.str.contains("_q")]

                row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
                assert row == re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
                assert col == re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)
                self.row_num = int(row) + 1
                self.col_num = int(col) + 1

                mct_grid_i = df_data[mct_name].values.reshape([len(df_data), self.row_num, self.col_num])
                mct_grid_q = df_data[mct_q_name].values.reshape([len(df_data), self.row_num, self.col_num])
                sct_row_i = df_data[sct_row_name].values.reshape([len(df_data), self.row_num])
                sct_row_q = df_data[sct_row_q_name].values.reshape([len(df_data), self.row_num])
                sct_col_i = df_data[sct_col_name].values.reshape([len(df_data), self.col_num])
                sct_col_q = df_data[sct_col_q_name].values.reshape([len(df_data), self.col_num])

                self.mct_grid = np.abs(mct_grid_i + 1j * mct_grid_q).astype(int)
                self.sct_row = np.abs(sct_row_i + 1j * sct_row_q).astype(int)
                self.sct_col = np.abs(sct_col_i + 1j * sct_col_q).astype(int)
                pass
            elif self.mct_flag is True:
                mct_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                      df_data.columns.str.contains("mct_signals") &
                                      ~df_data.columns.str.contains("_q")]

                mct_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                        df_data.columns.str.contains("mct_signals") &
                                        df_data.columns.str.contains("_q")]
                row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
                self.row_num = int(row) + 1
                self.col_num = int(col) + 1
                mct_grid_i = df_data[mct_name].values.reshape([len(df_data), self.row_num, self.col_num])
                mct_grid_q = df_data[mct_q_name].values.reshape([len(df_data), self.row_num, self.col_num])

                self.mct_grid = np.abs(mct_grid_i + 1j * mct_grid_q).astype(int)

            elif self.sct_flag is True:
                sct_row_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains("sct_row_signals") &
                                          ~df_data.columns.str.contains("_q")]

                sct_row_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains("sct_row_signals") &
                                            df_data.columns.str.contains("_q")]

                sct_col_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                          df_data.columns.str.contains("sct_col_signals") &
                                          ~df_data.columns.str.contains("_q")]

                sct_col_q_name = df_data.columns[df_data.columns.str.contains('\d', regex=True) &
                                            df_data.columns.str.contains("sct_col_signals") &
                                            df_data.columns.str.contains("_q")]

                row = re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1).astype(int)
                col = re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1).astype(int)

                self.row_num = int(row) + 1
                self.col_num = int(col) + 1

                sct_row_i = df_data[sct_row_name].values.reshape([len(df_data), self.row_num])
                sct_row_q = df_data[sct_row_q_name].values.reshape([len(df_data), self.row_num])
                sct_col_i = df_data[sct_col_name].values.reshape([len(df_data), self.col_num])
                sct_col_q = df_data[sct_col_q_name].values.reshape([len(df_data), self.col_num])

                self.sct_row = np.abs(sct_row_i + 1j * sct_row_q)
                self.sct_col = np.abs(sct_col_i + 1j * sct_col_q)
            else:
                raise ('error')

        self.frame_num = self.__len__()
        if self.start_idx is None or self.end_idx is None:
            self.start_idx = 0
            self.end_idx = self.frame_num

        if self.mct_flag is True:
            self.mct_grid = self.mct_grid[self.start_idx: self.end_idx, :, :]

        if self.sct_flag is True:
            self.sct_row = self.sct_row[self.start_idx: self.end_idx, :]
            self.sct_col = self.sct_col[self.start_idx: self.end_idx, :]



    def load_data_from_ets_csv_old(self, file_path):
        mutual_raw = []
        col_raw = []
        row_raw = []
        with open(file_path) as f:
            reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
            for csv_line_idx, csv_line in enumerate(reader):
                # Split comma separated data in line into list
                # in case line end with space ""
                if csv_line[-1] == "":
                    csv_data = csv_line[:-1]
                else:
                    csv_data = csv_line

                # Process header at first line
                if csv_line_idx == 0:
                    header = csv_data
                    for col in csv_data[:5]:

                        if "deltas" in col:
                            self.Header_index = self.Header_index["Delta"]
                            break
                        elif "signals" in col:
                            self.Header_index = self.Header_index["Signal"]
                            break
                        elif "baseline" in col:
                            self.Header_index = self.Header_index["Baseline"]
                            break
                    # Search header in first row to identify column indices for playback data
                    # print(csv_data[3])
                    for column_idx, column_str in enumerate(csv_line):
                        # print(column_str)
                        for idx, playback_data in enumerate(self.Header_index):
                            # print(playback_data[1])
                            if playback_data[1] in column_str:
                                # print("Found start of " + column_str + " idx=" + str(column_idx))
                                # print("Looking for end at " + str(playback_data[2]))
                                playback_data[3] = int(column_idx)

                            elif playback_data[2] in column_str:
                                self.Header_index[idx][4] = int(column_idx)

                    for playback_data in self.Header_index:
                        if playback_data[3] > playback_data[4]:
                            playback_data[4] = len(csv_data)-1

                    # print(self.Header_index)
                else:

                    mct_data = list(map(int, csv_data[self.Header_index[MCT_DELTAGEN_DATA][3]:
                                                      self.Header_index[MCT_DELTAGEN_DATA][4] + 1]))

                    row_data = list(map(int, csv_data[self.Header_index[SCTY_DELTAGEN_DATA][3]:
                                                      self.Header_index[SCTY_DELTAGEN_DATA][4] + 1]))

                    col_data = list(map(int, csv_data[self.Header_index[SCTX_DELTAGEN_DATA][3]:
                                                      self.Header_index[SCTX_DELTAGEN_DATA][4] + 1]))

                    if self.Header_index[MCT_DELTAGEN_DATA][4] > self.Header_index[MCT_DELTAGEN_DATA][3]:
                        if (max(mct_data)>MAX_DELTA_VALUE) or (min(mct_data)<MIN_DELTA_VALUE):
                            continue
                        if (sum(mct_data)) == 0:
                            continue
                    if self.Header_index[SCTX_DELTAGEN_DATA][4] > self.Header_index[SCTX_DELTAGEN_DATA][3]:
                        if (max(col_data)>MAX_DELTA_VALUE) or (min(col_data)<MIN_DELTA_VALUE):
                            continue
                        if (sum(col_data)) == 0:
                            continue
                    if self.Header_index[SCTY_DELTAGEN_DATA][4] > self.Header_index[SCTY_DELTAGEN_DATA][3]:
                        if (max(row_data)>MAX_DELTA_VALUE) or (min(row_data)<MIN_DELTA_VALUE):
                            continue
                        if (sum(row_data)) == 0:
                            continue

                    mutual_raw.append(mct_data)
                    col_raw.append(col_data)
                    row_raw.append(row_data)

                self.frame_num = csv_line_idx
        f.close()

        if self.start_idx is None or self.end_idx is None:
            self.start_idx = 0
            self.end_idx = self.frame_num


        # header[self.Header_index[MCT_DELTAGEN_DATA][4]]) : [row][col]
        # header[self.Header_index[SCTX_DELTAGEN_DATA][4]] : [row]
        # header[self.Header_index[SCTY_DELTAGEN_DATA][4]] : [col]

        if self.Header_index[MCT_DELTAGEN_DATA][4] > self.Header_index[MCT_DELTAGEN_DATA][3]:  # if  mct data exist
            # find the tx num and rx num using re
            row, col = re.findall(r"[\[](.*?)[\]]", header[self.Header_index[MCT_DELTAGEN_DATA][4]])
            self.row_num = int(row) + 1
            self.col_num = int(col) + 1
            self.mct_grid = np.array(mutual_raw).reshape([len(mutual_raw), self.row_num, self.col_num])

            self.mct_grid = self.mct_grid[self.start_idx : self.end_idx,:,:]
            # print(f"using {self.mct_grid.shape[0]} frames for evaluation!!")
        else:  # only sct data
            col = re.search(r"[\[](.*?)[\]]", header[self.Header_index[SCTX_DELTAGEN_DATA][4]]).group(1)
            row = re.search(r"[\[](.*?)[\]]", header[self.Header_index[SCTY_DELTAGEN_DATA][4]]).group(1)
            self.row_num = int(row) + 1
            self.col_num = int(col) + 1

        if self.Header_index[SCTX_DELTAGEN_DATA][4] > self.Header_index[SCTX_DELTAGEN_DATA][3]:  # if sct row data exist
            self.sct_row = np.array(row_raw)
            self.sct_row = self.sct_row[self.start_idx : self.end_idx, :]
        if self.Header_index[SCTY_DELTAGEN_DATA][4] > self.Header_index[SCTY_DELTAGEN_DATA][3]:  # if sct col data exist
            self.sct_col = np.array(col_raw)
            self.sct_col = self.sct_col[self.start_idx : self.end_idx, :]

    # *******************************************************************
    # ************    mutual grid field *********************************
    # *******************************************************************
    @property
    def mct_grid_max(self):
        """
        Calculate the maximum value of each node in all frames
        """
        return self.mct_grid.max(axis=0)

    @property
    def mct_grid_min(self):
        """
        Calculate the minimum value of each node in all frames
        """
        return self.mct_grid.min(axis=0)

    @property
    def mct_grid_mean(self):
        """
        Calculate the average value of each node in all frames
        """
        return self.mct_grid.mean(axis=0)

    @property
    def mct_grid_p2p(self):
        """
        Calculate the peak peak noise value of each node in all frames
        """
        return self.mct_grid_max - self.mct_grid_min

    @property
    def mct_positive_noise(self):
        mct_max = self.mct_grid_max.astype(float)
        _,y_node,x_node = self.mct_signal_position
        for y in range(y_node-2,y_node+3):
            for x in range(x_node-2,x_node+3):
                if x < 0 or y < 0 or x >= self.col_num or y >= self.row_num:
                    continue
                else:
                    mct_max[y][x] = np.NaN
        return mct_max

    @property
    def mct_negative_noise(self):
        mct_max = self.mct_grid_min.astype(float)
        _, y_node, x_node = self.mct_signal_position
        for y in range(y_node - 2, y_node + 3):
            for x in range(x_node - 2, x_node + 3):
                if x < 0 or y < 0 or x >= self.col_num or y >= self.row_num:
                    continue
                else:
                    mct_max[y][x] = np.NaN
        return mct_max


    @property
    def mct_grid_rms(self):
        # alternative method
        # return np.sqrt(((self.mct_grid - self.mct_grid_mean) ** 2).mean(axis=0))
        return np.sqrt(np.var(self.mct_grid, axis=0))

    @property
    def mct_signal_position(self):
        n, y_node, x_node = np.unravel_index(self.mct_grid.argmax(), self.mct_grid.shape)
        return n, y_node, x_node

    @property
    def mct_signal_max(self):
        _, y_node, x_node = self.mct_signal_position
        return self.mct_grid_max[y_node][x_node]

    @property
    def mct_signal_min(self):
        _, y_node, x_node = self.mct_signal_position
        return self.mct_grid_min[y_node][x_node]

    @property
    def mct_signal_mean(self):
        _, y_node, x_node = self.mct_signal_position
        return self.mct_grid_mean[y_node][x_node]

    @property
    def mct_grid_p2p_position(self):
        y_node, x_node = np.unravel_index(self.mct_grid_p2p.argmax(), self.mct_grid_p2p.shape)

        # size for single node: [len,1,1]
        max_noise_node = self.mct_grid[:,y_node,x_node]
        max_index = np.unravel_index(max_noise_node.argmax(), max_noise_node.shape)
        min_index = np.unravel_index(max_noise_node.argmin(), max_noise_node.shape)
        return (min_index[0],max_index[0])

    # *******************************************************************
    # ************************    self cap row field ********************
    # *******************************************************************

    @property
    def sct_row_max(self):
        return self.sct_row.max(axis=0)

    @property
    def sct_row_min(self):
        return self.sct_row.min(axis=0)

    @property
    def sct_row_mean(self):
        return self.sct_row.mean(axis=0)

    @property
    def sct_row_p2p(self):
        return self.sct_row_max - self.sct_row_min

    @property
    def sct_row_rms(self):
        # alternative method
        return np.sqrt(np.var(self.sct_row, axis=0))

    @property
    def sct_row_signal_position(self):
        n, x_node = np.unravel_index(self.sct_row.argmax(), self.sct_row.shape)
        return n, x_node

    @property
    def sct_row_signal_max(self):
        _, y_node = self.sct_row_signal_position
        return self.sct_row_max[y_node]

    @property
    def sct_row_signal_min(self):
        _, y_node = self.sct_row_signal_position
        return self.sct_row_min[y_node]

    @property
    def sct_row_signal_mean(self):
        _, y_node = self.sct_row_signal_position
        return self.sct_row_mean[y_node]

    @property
    def sct_row_p2p_position(self):
        x_node = np.unravel_index(self.sct_row_p2p.argmax(), self.sct_row_p2p.shape)

        # size for single node: [len,1,1]
        max_noise_node = self.sct_row[:, x_node]
        max_index = np.unravel_index(max_noise_node.argmax(), max_noise_node.shape)
        min_index = np.unravel_index(max_noise_node.argmin(), max_noise_node.shape)
        return (min_index[0], max_index[0])

    @property
    def sct_row_positive_noise(self):
        sct_row_max = self.sct_row_max.astype(float)
        _, y_node = self.sct_row_signal_position
        for y in range(y_node - 2, y_node + 3):
            if y < 0 or y >= self.row_num:
                continue
            else:
                sct_row_max[y] = np.NaN
        return sct_row_max

    @property
    def sct_row_negative_noise(self):
        sct_row_max = self.sct_row_min.astype(float)
        _, y_node = self.sct_row_signal_position
        for y in range(y_node - 2, y_node + 3):
            if y < 0 or y >= self.row_num:
                continue
            else:
                sct_row_max[y] = np.NaN
        return sct_row_max

    # *******************************************************************
    # ************************  self cap columns field ******************
    # *******************************************************************

    @property
    def sct_col_max(self):
        return self.sct_col.max(axis=0)

    @property
    def sct_col_min(self):
        return self.sct_col.min(axis=0)

    @property
    def sct_col_mean(self):
        return self.sct_col.mean(axis=0)

    @property
    def sct_col_p2p(self):
        return self.sct_col_max - self.sct_col_min

    @property
    def sct_col_rms(self):
        # alternative method
        return np.sqrt(np.var(self.sct_col, axis=0))

    @property
    def sct_col_signal_position(self):
        n, y_node = np.unravel_index(self.sct_col.argmax(), self.sct_col.shape)
        return n, y_node

    @property
    def sct_col_signal_max(self):
        _, y_node = self.sct_col_signal_position
        return self.sct_col_max[y_node]

    @property
    def sct_col_signal_min(self):
        _, y_node = self.sct_col_signal_position
        return self.sct_col_min[y_node]

    @property
    def sct_col_signal_mean(self):
        _, y_node = self.sct_col_signal_position
        return self.sct_col_mean[y_node]

    @property
    def sct_col_p2p_position(self):
        y_node = np.unravel_index(self.sct_col_p2p.argmax(), self.sct_col_p2p.shape)

        # size for single node: [len,1,1]
        max_noise_node = self.sct_col[:, y_node]
        max_index = np.unravel_index(max_noise_node.argmax(), max_noise_node.shape)
        min_index = np.unravel_index(max_noise_node.argmin(), max_noise_node.shape)
        return (min_index[0], max_index[0])

    @property
    def sct_col_positive_noise(self):
        sct_col_max = self.sct_col_max.astype(float)
        _, x_node = self.sct_col_signal_position
        for x in range(x_node - 2, x_node + 3):
            if x < 0 or x >= self.row_num:
                continue
            else:
                sct_col_max[x] = np.NaN
        return sct_col_max

    @property
    def sct_col_negative_noise(self):
        sct_col_max = self.sct_col_min.astype(float)
        _, x_node = self.sct_col_signal_position
        for x in range(x_node - 2, x_node + 3):
            if x < 0 or x >= self.row_num:
                continue
            else:
                sct_col_max[x] = np.NaN
        return sct_col_max


    def __len__(self):
        if self.mct_grid is not None:
            return len(self.mct_grid)

        elif self.sct_row is not None:
            return  len(self.sct_row)

        else:
            return 0
