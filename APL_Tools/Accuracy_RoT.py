import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .Graphs import Dart_Board, Touch_Sensor_Plot
# import Setup

from .Setup import SelectFirstTouchDownEachTap
from lib.APL_share import APL_Share

def accuracy_RoT(df_sensor, df_robot, APL_cfg, APL_Spec,edge, directory):

    x_length_mm = float(APL_cfg['DutWidth'])
    y_length_mm = float(APL_cfg['DutHeight'])
    finger_size = APL_cfg['TestFingerSize']
    Accuracy_Full = float(APL_Spec['Accuracy_Full'])
    Accuracy_Centre = float(APL_Spec['Linearity_Centre'])

    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    touch_count = -1
    ID = {}
    XPOS = []
    YPOS = []
    accuracy_columns = ['XPOS', 'YPOS', 'robot_x', 'robot_y', 'X_delta', 'Y_delta', 'combined']
    accuracy_df = pd.DataFrame(columns=accuracy_columns)

    df_sensor = SelectFirstTouchDownEachTap(df_sensor)

    for i in df_sensor.index:
        if df_sensor.iloc[i]['ID'] not in ID:
            ID.update({df_sensor.iloc[i]['ID']: 0})
            touch_count += 1
            XPOS.append(df_sensor.iloc[i]['XPOS'])
            YPOS.append(df_sensor.iloc[i]['YPOS'])

        elif df_sensor.iloc[i - 1]['Type'] == 'CONTACT':
            touch_count += 1
            ID.update({df_sensor.iloc[i]['ID']: touch_count})
            XPOS.append(df_sensor.iloc[i]['XPOS'])
            YPOS.append(df_sensor.iloc[i]['YPOS'])

    if len(XPOS)>len(df_robot['robot_x']):
        accuracy_df['XPOS'] = pd.Series(XPOS)
        accuracy_df['YPOS'] = pd.Series(YPOS)
        accuracy_df['robot_x'] = pd.Series(df_robot['robot_x'])
        accuracy_df['robot_y'] = pd.Series(df_robot['robot_y'])
    elif len(df_robot['robot_x'])>len(XPOS):
        accuracy_df['robot_x'] = pd.Series(df_robot['robot_x'])
        accuracy_df['robot_y'] = pd.Series(df_robot['robot_y'])
        accuracy_df['XPOS'] = pd.Series(XPOS)
        accuracy_df['YPOS'] = pd.Series(YPOS)
    else:
        accuracy_df['XPOS'] = pd.Series(XPOS)
        accuracy_df['YPOS'] = pd.Series(YPOS)
        accuracy_df['robot_x'] = pd.Series(df_robot['robot_x'])
        accuracy_df['robot_y'] = pd.Series(df_robot['robot_y'])
    accuracy_df['X_delta'] = accuracy_df['XPOS'] - accuracy_df['robot_x']
    accuracy_df['Y_delta'] = accuracy_df['YPOS'] - accuracy_df['robot_y']
    accuracy_df['combined'] = np.sqrt((accuracy_df['X_delta'] ** 2 + accuracy_df[
        'Y_delta'] ** 2))

    accuracy_df_centre = accuracy_df.copy()

    for index, row in accuracy_df_centre.iterrows():
        if (row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            accuracy_df_centre.drop(index, inplace=True)

    accuracy_max = accuracy_df['combined'].max()
    accuracy_max_centre = accuracy_df_centre['combined'].max()
    print(accuracy_max_centre)
    if accuracy_max > Accuracy_Full:
        test_outcome = 'Failed'
        print("This test has failed by: ", accuracy_max - Accuracy_Full, "mm")
    else:
        test_outcome = 'Passed'
        print('This test has Passed')
    if accuracy_max_centre > Accuracy_Centre:
        test_outcome_centre = 'Failed'
        print("This test has failed by: ", accuracy_max_centre - Accuracy_Centre, "mm")
    else:
        test_outcome_centre = 'Passed'
        print('This test has Passed')

    APL_Share.SubFigList["Accuracy_data_fullscreen"] = Touch_Sensor_Plot(accuracy_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y', 'Accuracy Touch Panel Plot', 'x lines',
                      'y lines', finger_size, directory)

    APL_Share.SubFigList["Accuracy_data_centre"] = Touch_Sensor_Plot(accuracy_df_centre, 'XPOS', 'YPOS', 'robot_x', 'robot_y', 'Accuracy Touch Centre', 'x lines',
                      'y lines', finger_size, directory)

    # Touch_Sensor_Plot(accuracy_df_centre, 'XPOS', 'YPOS', 'robot_x', 'robot_y', 'Accuracy Touch Panel centre',
    #                   'x lines',
    #                   'y lines')
    accuracy_df_dart_board = accuracy_df[['X_delta', 'Y_delta']]
    accuracy_df_centre_dart_board = accuracy_df_centre[['X_delta', 'Y_delta']]

    APL_Share.SubFigList["Accuracy_error_fullscreen"] = Dart_Board(accuracy_df_dart_board, 'Accuracy Error Full', Accuracy_Centre, Accuracy_Full, finger_size, directory)
    APL_Share.SubFigList["Accuracy_error_centre"] = Dart_Board(accuracy_df_centre_dart_board, 'Accuracy Error Centre', Accuracy_Centre, Accuracy_Full, finger_size, directory)
    print('the maximum accuracy error is => ', accuracy_max)  # print the maximum accuracy error
    print('the maximum centre accuracy error is => ', accuracy_max_centre)
    return accuracy_df, accuracy_df_centre, test_outcome, test_outcome_centre, accuracy_max_centre, accuracy_max

