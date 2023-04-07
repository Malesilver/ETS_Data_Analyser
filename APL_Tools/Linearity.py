
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from .Graphs import Scatter_Plot_List_of_Lists, Line_Plot


def linearity_calc(frame):
    swapaxes = False  # a flag to determine which formula is used depending on the axis which is greater
    # this is important for vertical and horizontal lines since it will be seen in one axis but not in the other

    # poly fit finds the coefficients of the line of best fit and the output is in the form of a list
    # the last term sets the polynomial power so in this case it is 1 which means straight line y = mx + c
    # so the output is [m,c]
    linearcoef_a = np.polyfit(frame['XPOS'], frame['YPOS'], 1)  # find the linear line of best fit for XPOS as x and
    # YPOS as y
    linearcoef_b = np.polyfit(frame['YPOS'], frame['XPOS'], 1)  # find the linear line of best fit for YPOS as x and
    # XPOS as y

    # these if statements look at the c in mx+c and and seeing which is the biggest and picks that linearcoef
    if linearcoef_a[1] and linearcoef_b[1] > 0:
        if linearcoef_a[1] > linearcoef_b[1]:
            linearcoef = linearcoef_a
        else:
            swapaxes = True
            linearcoef = linearcoef_b
    else:
        if linearcoef_a[1] > 0:
            linearcoef = linearcoef_a
        if linearcoef_b[1] > 0:
            swapaxes = True
            linearcoef = linearcoef_b
        # else:
        #     print('Problem with the data')

    a = linearcoef[0]  # m in the mx+c
    b = -1
    c = linearcoef[1]  # c in mx+c
    if swapaxes:
        lin_error = np.absolute(a * frame['YPOS'] + b * frame['XPOS'] + c) / math.sqrt(a ** 2 + b ** 2)  # formula to
        # calculate the error between the line of best fit and the touch sensor data
    else:
        lin_error = np.absolute(a * frame['XPOS'] + b * frame['YPOS'] + c) / math.sqrt(a ** 2 + b ** 2)  # formula to
        # calculate the error between the line of best fit and the touch sensor data
    return lin_error  # return the error value


def linearity(df_sensor, Linearity_Requirement,setup_variables):
    edge = 10
    x_length_mm = float(setup_variables.iloc[6].item())
    y_length_mm = float(setup_variables.iloc[7].item())
    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    a = []  # list containing the pattern line number
    b = []  # list containing the touch sensor x value for the pattern line
    c = []  # list containing the touch sensor y value for the pattern line
    line_no = -1  # a count for the pattern line number - starts at -1 since the first line is 0
    linearity_df = pd.DataFrame(columns=['Line no', 'XPOS', 'YPOS'])  # create a DataFrame to hold the Linearity data
    for i in df_sensor.index:  # iterate through each row in the DataFrame
        if df_sensor['EVENT'].loc[i] == 4:  # if the row is a touch down
            line_no += 1  # increment the line number
            xpos = df_sensor['XPOS'].loc[i]  # x position for that index
            ypos = df_sensor['YPOS'].loc[i]  # y position for that index
            a.append(line_no)  # append to list a
            b.append(xpos)  # append to list b
            c.append(ypos)  # append to list c
        if (df_sensor['EVENT'].loc[i] == 1) or (df_sensor['EVENT'].loc[i] == 0):  # if the event is a move or no event
            xpos = df_sensor['XPOS'].loc[i]  # x position for that index
            ypos = df_sensor['YPOS'].loc[i]  # y position for that index
            a.append(line_no)  # append to list a
            b.append(xpos)  # append to list b
            c.append(ypos)  # append to list c

    linearity_df['Line no'] = a  # assign the list to the line number column of the DataFrame
    linearity_df['XPOS'] = b  # assign the list to the XPOS column of the DataFrame
    linearity_df['YPOS'] = c  # assign the list to the YPOS column of the DataFrame

    line_no = linearity_df['Line no'].nunique()  # number of line in the pattern

    # create a DataFrame containing the linearity error
    error_y = []  # list to store data
    error_y_centre = []
    error_list = []
    max_error_list = []
    max_error_list_centre = []
    error_list_centre = []
    data_list = []
    data_list_centre = []
    for l in range(line_no):  # iterate through the line numbers
        temp_list = []
        temp = linearity_df[linearity_df['Line no'] == l]  # create a temp DataFrame containing all the rows
        temp = temp.reset_index()
        temp_list.append(temp['XPOS'].to_list())
        temp_list.append(temp['YPOS'].to_list())
        # containing l as the pattern line no
        error = linearity_calc(temp)  # calculate the error for that line pattern
        temp = temp.assign(error=error)  # assign it the error column of the temp DataFrame
        max_error = temp['error'].max()  # find the max error for that line pattern
        max_error_list.append(max_error)  # append max value for that line pattern to a list
        # print('maximum linearity error: ', max_error)
        # line of best fit
        error_y.append(temp)
        # plot the linearity pattern error for each line and whole pattern
        error_list.append(error)
        data_list.append(temp_list)
        Line_Plot(error, l)
    final_data = pd.concat(error_y)  # convert list of dataframes into a single dataframe
    Scatter_Plot_List_of_Lists(data_list)

    linearity_max_error = max(max_error_list)

    if linearity_max_error > Linearity_Requirement:
        test_outcome = 'Failed'
        print('This test has Failed by: ', linearity_max_error - Linearity_Requirement, 'mm')
    else:
        test_outcome = 'Passed'
        print('This test has passed')

    for l in range(line_no):  # iterate through the line numbers
        temp_list_centre = []
        temp_centre = linearity_df[linearity_df['Line no'] == l]  # create a temp DataFrame containing all the rows
        temp_centre = temp_centre.reset_index()

        for index, row in temp_centre.iterrows():
            if (row['XPOS'] <= edge or row['YPOS'] <= edge or row['XPOS'] >= Edge_x or row['YPOS'] >= Edge_y):
                temp_centre.drop(index, inplace=True)
        temp_centre = temp_centre.reset_index()
        if temp_centre.empty == False:

            temp_list_centre.append(temp_centre['XPOS'].to_list())
            temp_list_centre.append(temp_centre['YPOS'].to_list())
            # containing l as the pattern line no
            error_centre = linearity_calc(temp_centre)  # calculate the error for that line pattern
            temp_centre = temp_centre.assign(error=error_centre)  # assign it the error column of the temp DataFrame
            max_error_centre = temp_centre['error'].max()  # find the max error for that line pattern
            print(temp_centre['error'])
            max_error_list_centre.append(max_error_centre)  # append max value for that line pattern to a list
            # print('maximum linearity error: ', max_error)
            # line of best fit
            error_y_centre.append(temp_centre)
            # plot the linearity pattern error for each line and whole pattern
            error_list_centre.append(error_centre)
            data_list_centre.append(temp_list_centre)
            Line_Plot(error_centre, l)


    final_data_centre = pd.concat(error_y_centre)

    Scatter_Plot_List_of_Lists(data_list_centre)
    linearity_max_error_centre = max(max_error_list_centre)
    if linearity_max_error_centre > Linearity_Requirement:
        test_outcome_centre = 'Failed'
        print('This test has Failed by: ', linearity_max_error_centre - Linearity_Requirement, 'mm')
    else:
        test_outcome_centre = 'Passed'
        print('This test has passed')
    print(error)
    print('The maximum linearity error is => ',linearity_max_error)  # print the maximum linearity error
    print('The maximum centre linearity error is => ',linearity_max_error_centre)
    plt.show()
    return final_data, final_data_centre, test_outcome, test_outcome_centre
