import pandas as pd
import os
import numpy as np
import re
from enum import Enum

pd.set_option('display.max_columns', 7)
filepath=r"C:\Users\Yifan\Desktop\log_raw_data\mct_sct_q_signal.edl.csv"

class ETS_Data_Type(Enum):
    Signal = "signals",
    Signal_IQ='signals_q',
    Delta = 'deltas',
    Baseline = 'baseline',
    Nodemap = 'tbd',
    Unknown = 255,

MCT_DATA = 0
SCT_ROW_DATA = 1
SCT_COL_DATA = 2
# 0: mct/sct, 1: data exsist flag, 2:start index, 3:end index
HEADER_ETS = [
    [MCT_DATA,  0, 0, 0],
    [SCT_ROW_DATA,  0, 0, 0],
    [SCT_COL_DATA,  0, 0, 0],
]

df = pd.read_csv(filepath)
header = list(df.columns)
flag_start_index = 0
flag_end_index = 0
DataType = None

# get flag name
for index,name in enumerate(header):
    if "duration" in name:
        flag_start_index = index+1
        continue
    if re.search(r'\d', name) and flag_start_index != 0:
        flag_end_index = index
        break

flag_name_list = header[flag_start_index:flag_end_index]

# define touch type
if 'signals' in flag_name_list[0]:
    for name in flag_name_list:
        if name.endswith('signals_q'):
            DataType = ETS_Data_Type.Signal_IQ
            break
        DataType = ETS_Data_Type.Signal

elif 'baseline' in flag_name_list[0]:
    DataType = ETS_Data_Type.Baseline

elif 'deltas' in flag_name_list[0]:
    DataType = ETS_Data_Type.Delta

elif 'touches' in flag_name_list[0]:
    DataType = ETS_Data_Type.Nodemap
else:
    DataType = ETS_Data_Type.Unknown

# get index
for name in flag_name_list:
    if 'mct' in name:
        HEADER_ETS[MCT_DATA][1] = 1

    if 'sct' in name:
        HEADER_ETS[SCT_COL_DATA][1] = 1
        HEADER_ETS[SCT_ROW_DATA][1] = 1

row_num = 0
col_num = 0

if DataType is ETS_Data_Type.Delta or DataType is ETS_Data_Type.Signal or DataType is ETS_Data_Type.Baseline:


    if HEADER_ETS[MCT_DATA][1] == 1 and HEADER_ETS[SCT_ROW_DATA][1] == 1:
        mct_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains(f"mct_{DataType.value[0]}",regex=True)]
        sct_row_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains(f"sct_row_{DataType.value[0]}",regex=True)]
        sct_col_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains(f"sct_col_{DataType.value[0]}", regex=True)]

        row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
        assert row == re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
        assert col == re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)
        row_num = int(row)+1
        col_num = int(col)+1

        mct_grid = df[mct_name].values.reshape([len(df),row_num,col_num])
        sct_row = df[sct_row_name].values.reshape([len(df),row_num])
        sct_col = df[sct_col_name].values.reshape([len(df),col_num])

    elif HEADER_ETS[MCT_DATA][1] == 1:
        mct_name = df.columns[df.columns.str.contains('\d', regex=True) &
                              df.columns.str.contains(f"mct_{DataType.value[0]}", regex=True)]
        row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
        row_num = int(row) + 1
        col_num = int(col) + 1
        mct_grid = df[mct_name].values.reshape([len(df), row_num, col_num])

    elif HEADER_ETS[SCT_COL_DATA][1] == 1:
        sct_row_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_row_signals", regex=True)]
        sct_col_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_col_signals", regex=True)]

        row = re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
        col = re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)

        row_num = int(row) + 1
        col_num = int(col) + 1

        sct_row = df[sct_row_name].values.reshape([len(df), row_num])
        sct_col = df[sct_col_name].values.reshape([len(df), col_num])
    else:
        raise('error')


elif DataType is ETS_Data_Type.Signal_IQ:
    if HEADER_ETS[MCT_DATA][1] == 1 and HEADER_ETS[SCT_ROW_DATA][1] == 1:
        mct_name = df.columns[df.columns.str.contains('\d', regex=True) &
                              df.columns.str.contains("mct_signals") &
                              ~df.columns.str.contains("_q")]

        mct_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                              df.columns.str.contains("mct_signals") &
                              df.columns.str.contains("_q")]

        sct_row_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_row_signals") &
                                  ~df.columns.str.contains("_q")]

        sct_row_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_row_signals") &
                                  df.columns.str.contains("_q")]

        sct_col_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_col_signals") &
                                  ~df.columns.str.contains("_q")]

        sct_col_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_col_signals") &
                                  df.columns.str.contains("_q")]

        row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
        assert row == re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
        assert col == re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)
        row_num = int(row) + 1
        col_num = int(col) + 1

        mct_grid_i = df[mct_name].values.reshape([len(df), row_num, col_num])
        mct_grid_q = df[mct_q_name].values.reshape([len(df), row_num, col_num])
        sct_row_i = df[sct_row_name].values.reshape([len(df), row_num])
        sct_row_q = df[sct_row_q_name].values.reshape([len(df), row_num])
        sct_col_i = df[sct_col_name].values.reshape([len(df), col_num])
        sct_col_q = df[sct_col_q_name].values.reshape([len(df), col_num])

        mct_grid = np.abs(mct_grid_i + 1j*mct_grid_q)
        sct_row = np.abs(sct_row_i + 1j*sct_row_q)
        sct_col = np.abs(sct_col_i + 1j * sct_col_q)
        pass
    elif HEADER_ETS[MCT_DATA][1] == 1:
        mct_name = df.columns[df.columns.str.contains('\d', regex=True) &
                              df.columns.str.contains("mct_signals") &
                              ~df.columns.str.contains("_q")]

        mct_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                df.columns.str.contains("mct_signals") &
                                df.columns.str.contains("_q")]
        row, col = re.findall(r"[\[](.*?)[\]]", mct_name[-1])[:2]
        row_num = int(row) + 1
        col_num = int(col) + 1
        mct_grid_i = df[mct_name].values.reshape([len(df), row_num, col_num])
        mct_grid_q = df[mct_q_name].values.reshape([len(df), row_num, col_num])

        mct_grid = np.abs(mct_grid_i + 1j * mct_grid_q)

    elif HEADER_ETS[SCT_COL_DATA][1] == 1:
        sct_row_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_row_signals") &
                                  ~df.columns.str.contains("_q")]

        sct_row_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                    df.columns.str.contains("sct_row_signals") &
                                    df.columns.str.contains("_q")]

        sct_col_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                  df.columns.str.contains("sct_col_signals") &
                                  ~df.columns.str.contains("_q")]

        sct_col_q_name = df.columns[df.columns.str.contains('\d', regex=True) &
                                    df.columns.str.contains("sct_col_signals") &
                                    df.columns.str.contains("_q")]

        row = re.search(r"[\[](.*?)[\]]", sct_row_name[-1]).group(1)
        col = re.search(r"[\[](.*?)[\]]", sct_col_name[-1]).group(1)

        row_num = int(row) + 1
        col_num = int(col) + 1

        sct_row_i = df[sct_row_name].values.reshape([len(df), row_num])
        sct_row_q = df[sct_row_q_name].values.reshape([len(df), row_num])
        sct_col_i = df[sct_col_name].values.reshape([len(df), col_num])
        sct_col_q = df[sct_col_q_name].values.reshape([len(df), col_num])

        sct_row = np.abs(sct_row_i + 1j * sct_row_q)
        sct_col = np.abs(sct_col_i + 1j * sct_col_q)
    else:
        raise('error')





