import pandas as pd
import numpy as np
from .Graphs import Scatter_Plot_df,Touch_Sensor_Plot
from lib.APL_share import APL_Share
import matplotlib.pyplot as plt


# calculate mean square error
def mean_squared_error(y_true, y_pred):
    return np.mean(np.square(y_pred - y_true))


def precision_RoT(df_sensor, df_robot, number_of_repeats, APL_cfg, APL_Spec, edge, directory):

    x_length_mm = float(APL_cfg['DutWidth'])
    y_length_mm = float(APL_cfg['DutHeight'])
    finger_size = APL_cfg['TestFingerSize']
    Precision_Requirement_Full = float(APL_Spec["Precision_Full"])
    Precision_Requirement_Ctr = float(APL_Spec["Precision_Centre"])

    # x_length_mm = float(setup_variables.iloc[6].item())
    # y_length_mm = float(setup_variables.iloc[7].item())
    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    touch_count = -1
    ID = {}
    XPOS = []
    YPOS = []
    precision_columns = ['XPOS', 'YPOS', 'robot_x', 'robot_y']
    precision_df = pd.DataFrame(columns=precision_columns)
    for i in df_sensor.index:
        if df_sensor.iloc[i]['ID'] not in ID:
            ID.update({df_sensor.iloc[i]['ID']: 0})
            touch_count += 1
            XPOS.append(df_sensor.iloc[i]['XPOS'])
            YPOS.append(df_sensor.iloc[i]['YPOS'])
        elif df_sensor.iloc[i - 1]['Type'] == "RELEASE":
            touch_count += 1
            ID.update({df_sensor.iloc[i]['ID']: touch_count})
            XPOS.append(df_sensor.iloc[i]['XPOS'])
            YPOS.append(df_sensor.iloc[i]['YPOS'])
    if len(XPOS) > len(df_robot['robot_x']):
        precision_df['XPOS'] = pd.Series(XPOS)
        precision_df['YPOS'] = pd.Series(YPOS)
        precision_df['robot_x'] = pd.Series(df_robot['robot_x'])
        precision_df['robot_y'] = pd.Series(df_robot['robot_y'])
    elif len(df_robot['robot_x']) > len(XPOS):
        precision_df['robot_x'] = pd.Series(df_robot['robot_x'])
        precision_df['robot_y'] = pd.Series(df_robot['robot_y'])
        precision_df['XPOS'] = pd.Series(XPOS)
        precision_df['YPOS'] = pd.Series(YPOS)
    else:
        precision_df['XPOS'] = pd.Series(XPOS)
        precision_df['YPOS'] = pd.Series(YPOS)
        precision_df['robot_x'] = pd.Series(df_robot['robot_x'])
        precision_df['robot_y'] = pd.Series(df_robot['robot_y'])
    print(precision_df)
    precision_columns = ['robot_x', 'robot_y', 'precision_error_XPOS', 'precision_error_YPOS',
                         'combined', 'mse_error_XPOS', 'mse_error_YPOS', 'mse_error']
    precision_table = pd.DataFrame(columns=precision_columns)
    precision_x_list = []
    precision_y_list = []
    robot_x_list = []
    robot_y_list = []
    mse_x_list = []
    mse_y_list = []
    mse_list = []
    for i in range(0, len(precision_df), number_of_repeats):
        temp = precision_df[i:i + number_of_repeats]
        robot_x_list.append(temp.at[i, 'robot_x'])
        robot_y_list.append(temp.at[i,'robot_y'])
        precision_x = temp['XPOS'].max() - temp['XPOS'].min()
        precision_y = temp['YPOS'].max() - temp['YPOS'].min()
        precision_x_list.append(precision_x)
        precision_y_list.append(precision_y)
        mse_error_x = mean_squared_error(temp['XPOS'], temp['robot_x'])
        mse_error_y = mean_squared_error(temp['YPOS'], temp['robot_y'])
        mse_x_list.append(mse_error_x)
        mse_y_list.append(mse_error_y)
        mse_error = max(mse_error_x, mse_error_y)
        mse_list.append(mse_error)
    precision_table['robot_x'] = robot_x_list
    precision_table['robot_y'] = robot_y_list
    precision_table['precision_error_XPOS'] = precision_x_list
    precision_table['precision_error_YPOS'] = precision_y_list
    precision_table['combined'] = np.sqrt(
        (precision_table['precision_error_XPOS'] ** 2 + precision_table[
            'precision_error_YPOS'] ** 2))
    precision_table['mse_error_XPOS'] = mse_x_list
    precision_table['mse_error_YPOS'] = mse_y_list
    precision_table['mse_error'] = mse_list
    print(precision_table)
    precision_table_centre = precision_table.copy()
    #print(precision_table)
    for index, row in precision_table_centre.iterrows():
        if (row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            precision_table_centre.drop(index, inplace=True)
    print('centre information')

    precision_df_centre = precision_df.copy()

    for index, row in precision_df_centre.iterrows():
        if (row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            precision_df_centre.drop(index, inplace=True)

    precision_max = precision_table['combined'].max()
    precision_max_centre = precision_table_centre['combined'].max()

    if precision_max > Precision_Requirement_Full:
        test_outcome = 'Failed'
        print('This test has Failed by: ', precision_max - Precision_Requirement_Full, 'mm')
    else:
        test_outcome = 'Passed'
        print('This test has passed')

    if precision_max_centre > Precision_Requirement_Ctr:
        test_outcome_centre = 'Failed'
        print('This test has Failed by: ', precision_max_centre - Precision_Requirement_Ctr, 'mm')
    else:
        test_outcome_centre = 'Passed'
        print('This test has passed')

    APL_Share.SubFigList["Precision_data_fullscreen"] = Touch_Sensor_Plot(precision_df, 'XPOS', 'YPOS', 'robot_x',
                                                                         'robot_y', 'Precision Touch Panel Plot',
                                                                         'x lines',
                                                                         'y lines', finger_size, directory)

    APL_Share.SubFigList["Precision_data_centre"] = Touch_Sensor_Plot(precision_df_centre, 'XPOS', 'YPOS', 'robot_x',
                                                                     'robot_y', 'Precision Touch Panel Centre Plot', 'x lines',
                                                                     'y lines', finger_size, directory)
    APL_Share.SubFigList["Precision_error_fullscreen"] = Scatter_Plot_df(precision_table, 'precision_error_XPOS', 'precision_error_YPOS', 'Precision Full',
                    'x lines (mm)', 'y lines (mm)', finger_size, directory)
    APL_Share.SubFigList["Precision_error_centre"] = Scatter_Plot_df(precision_table_centre, 'precision_error_XPOS', 'precision_error_YPOS',
                    'Precision Centre',
                    'x lines (mm)', 'y lines (mm)', finger_size, directory)
    print("The maximum precision error is: ", precision_max)
    print('The max centre precision error is: ', precision_max_centre)

    return precision_table, precision_table_centre, test_outcome, test_outcome_centre, precision_max_centre, precision_max

