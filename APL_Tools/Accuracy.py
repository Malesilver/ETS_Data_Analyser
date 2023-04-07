import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Graphs import Dart_Board, Touch_Sensor_Plot


def accuracy(df_sensor, df_robot, Accuracy_Requirement, setup_variables):
    edge = 10
    x_length_mm = float(setup_variables.iloc[6].item())
    y_length_mm = float(setup_variables.iloc[7].item())
    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    sensor = df_sensor[df_sensor['EVENT'] == 4].reset_index()  # filter the data for only the touchdown data - EVENT
    # CODE 4 and resets the index so that it matches the robot data

    accuracy_columns = ['XPOS', 'YPOS', 'robot_x', 'robot_y', 'X_delta', 'Y_delta', 'combined']  # column headings for
    # Dataframe to store accuracy data
    accuracy_df = pd.DataFrame(columns=accuracy_columns)  # create a new dataframe with the column headings
    # accuracy_columns

    accuracy_df['XPOS'] = sensor['XPOS']  # import data from touch sensor and robot data to relevant column in
    # accuracy DataFrame
    accuracy_df['YPOS'] = sensor['YPOS']
    accuracy_df['robot_x'] = df_robot['robot_x']
    accuracy_df['robot_y'] = df_robot['robot_y']
    accuracy_df_centre = pd.DataFrame(columns=accuracy_columns)  # create a new dataframe with the column headings
    accuracy_df_centre['XPOS'] = sensor['XPOS']  # import data from touch sensor and robot data to relevant column in
    # accuracy DataFrame
    accuracy_df_centre['YPOS'] = sensor['YPOS']
    accuracy_df_centre['robot_x'] = df_robot['robot_x']
    accuracy_df_centre['robot_y'] = df_robot['robot_y']

    for index, row in accuracy_df_centre.iterrows():
        if (row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            accuracy_df_centre.drop(index, inplace=True)

    print(accuracy_df_centre)
    Touch_Sensor_Plot(accuracy_df_centre, 'XPOS', 'YPOS', 'robot_x', 'robot_y', 'Accuracy Touch Panel centre',
                      'x lines',
                      'y lines')

    x_delta_centre = accuracy_df_centre['XPOS'] - accuracy_df_centre['robot_x']  # find the X error
    accuracy_df_centre = accuracy_df_centre.assign(X_delta=x_delta_centre)  # assign to X delta

    y_delta_centre = accuracy_df_centre['YPOS'] - accuracy_df_centre['robot_y']  # find the Y error
    accuracy_df_centre = accuracy_df_centre.assign(Y_delta=y_delta_centre)  # assign to Y delta

    combined = np.sqrt((accuracy_df_centre['X_delta'] ** 2 + accuracy_df_centre[
        'Y_delta'] ** 2))  # find the combined error for each touch point using Pythagoras
    accuracy_df_centre = accuracy_df_centre.assign(combined=combined)  # assign to combined error field
    accuracy_max_centre = accuracy_df_centre['combined'].max()  # find the max combined error

    x_delta = accuracy_df['XPOS'] - accuracy_df['robot_x']  # find the X error
    accuracy_df = accuracy_df.assign(X_delta=x_delta)  # assign to X delta

    y_delta = accuracy_df['YPOS'] - accuracy_df['robot_y']  # find the Y error
    accuracy_df = accuracy_df.assign(Y_delta=y_delta)  # assign to Y delta

    combined = np.sqrt((accuracy_df['X_delta'] ** 2 + accuracy_df[
        'Y_delta'] ** 2))  # find the combined error for each touch point using Pythagoras
    accuracy_df = accuracy_df.assign(combined=combined)  # assign to combined error field
    accuracy_max = accuracy_df['combined'].max()  # find the max combined error
    if accuracy_max > Accuracy_Requirement:
        test_outcome = 'Failed'
        print("This test has failed by: ", accuracy_max - Accuracy_Requirement, "mm")
    else:
        test_outcome = 'Passed'
        print('This test has Passed')
    if accuracy_max_centre > Accuracy_Requirement:
        test_outcome_centre = 'Failed'
        print("This test has failed by: ", accuracy_max_centre - Accuracy_Requirement, "mm")
    else:
        test_outcome_centre = 'Passed'
        print('This test has Passed')
    Touch_Sensor_Plot(accuracy_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y', 'Accuracy Touch Panel Plot', 'x lines',
                      'y lines')
    accuracy_df_2 = accuracy_df[['X_delta', 'Y_delta']]
    Dart_Board(accuracy_df_2, 'Accuracy Error')
    accuracy_df_2_centre = accuracy_df_centre[['X_delta', 'Y_delta']]
    Dart_Board(accuracy_df_2_centre, 'Accuracy Error Centre')
    print('the maximum accuracy error is => ', accuracy_max)  # print the maximum accuracy error
    print('the maximum centre accuracy error is => ', accuracy_max_centre)
    plt.show()
    return accuracy_df, accuracy_df_centre, test_outcome, test_outcome_centre
