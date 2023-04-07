import pandas as pd
import numpy as np
from Graphs import Scatter_Plot_df


def precision(df_sensor,df_robot, number_of_repeats, Precision_Requirement,setup_variables):
    edge = 10
    x_length_mm = float(setup_variables.iloc[6].item())
    y_length_mm = float(setup_variables.iloc[7].item())
    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    sensor = df_sensor[df_sensor['EVENT'] == 4].reset_index()  # filter for touch down data only - EVENT code 4 and
    # reset the index to match the robot data
    data_columns = ['XPOS', 'YPOS', 'robot_x', 'robot_y']
    data_df = pd.DataFrame(columns=data_columns)
    data_df['XPOS'] = sensor['XPOS']
    data_df['YPOS'] = sensor['YPOS']
    data_df['robot_x'] = df_robot['robot_x']
    data_df['robot_y'] = df_robot['robot_y']
    for index, row in data_df.iterrows():
        if(row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            data_df.drop(index, inplace = True)
    print(data_df)
    print(len(data_df))
    precision_columns = ['precision_error_XPOS', 'precision_error_YPOS',
                         'combined']  # create a DataFrame with these columns
    precision_table = pd.DataFrame(columns=precision_columns)
    precision_table_centre = pd.DataFrame(columns=precision_columns)
    x = []  # list of X precision data
    y = []  # list of Y precision data
    x_centre = []
    y_centre = []
    # ---- for values in the range of the length of the data repeating every number of touches per point
    for i in range(0, len(sensor), number_of_repeats):
        touch = sensor[i:i + number_of_repeats]  # DataFrame containing the data for 1 touch position
        precision_table_x = touch['XPOS'].max() - touch['XPOS'].min()  # finding the biggest variation in the X lines
        # for that position of touch sensor
        precision_table_y = touch['YPOS'].max() - touch['YPOS'].min()  # find the biggest variation in the Y lines
        x.append(precision_table_x)  # append it to the list of x line precision values
        y.append(precision_table_y)  # append it to the list of y line precision values
    precision_table[
        'precision_error_XPOS'] = x  # assign the X precision values to the precision XPOS column in DataFrame
    precision_table[
        'precision_error_YPOS'] = y  # assign the Y precision values to the precision XPOS column in DataFrame
    precision_table['combined'] = np.sqrt(
        (precision_table['precision_error_XPOS'] ** 2 + precision_table[
            'precision_error_YPOS'] ** 2))  # find the combined
    # precision error
    precision_max = precision_table['combined'].max()

    for i in range(0, len(data_df), number_of_repeats):
        touch = data_df[i:i + number_of_repeats]  # DataFrame containing the data for 1 touch position
        precision_table_x_centre = touch['XPOS'].max() - touch['XPOS'].min()  # finding the biggest variation in the X lines
        # for that position of touch sensor
        precision_table_y_centre = touch['YPOS'].max() - touch['YPOS'].min()  # find the biggest variation in the Y lines
        x_centre.append(precision_table_x_centre)  # append it to the list of x line precision values
        y_centre.append(precision_table_y_centre)  # append it to the list of y line precision values
    precision_table_centre['precision_error_XPOS'] = x_centre
    precision_table_centre['precision_error_YPOS'] = y_centre
    precision_table_centre['combined'] = np.sqrt(
        (precision_table_centre['precision_error_XPOS'] ** 2 + precision_table_centre[
            'precision_error_YPOS'] ** 2))
    precision_max_centre = precision_table_centre['combined'].max()


    if precision_max > Precision_Requirement:
        test_outcome = 'Failed'
        print('This test has Failed by: ', precision_max - Precision_Requirement, 'mm')
    else:
        test_outcome = 'Passed'
        print('This test has passed')

    if precision_max_centre > Precision_Requirement:
        test_outcome_centre = 'Failed'
        print('This test has Failed by: ', precision_max - Precision_Requirement, 'mm')
    else:
        test_outcome_centre = 'Passed'
        print('This test has passed')
    # Plot the precision error
    print(precision_table)
    print(precision_table_centre)
    Scatter_Plot_df(precision_table, 'precision_error_XPOS', 'precision_error_YPOS', 'Precision Error Scatter Plot', 'x lines (mm)', 'y lines (mm)')
    Scatter_Plot_df(precision_table_centre, 'precision_error_XPOS', 'precision_error_YPOS', 'Precision Error Scatter Plot',
                    'x lines (mm)', 'y lines (mm)')
    print("The maximum precision error is: ", precision_max)
    print('The max centre precision error is: ', precision_max_centre)
    return precision_table, precision_table_centre, test_outcome, test_outcome_centre
