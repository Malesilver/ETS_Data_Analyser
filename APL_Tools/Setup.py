import os.path

import pandas as pd
import numpy as np
from .Graphs import Dart_Board, Touch_Sensor_Plot
import matplotlib.pyplot as plt
import cv2
from lib.APL_share import APL_Share
# ----config variables-----#

def ModifyTouchData(df_sensor,pre_num = 5, back_num =2):

    df_sensor_rot = pd.DataFrame(columns=df_sensor.columns)
    touch_count = 0
    num_touch = 0
    touch_range = []

    for i in df_sensor.index:

        if df_sensor.iloc[i]['Type'] == "CONTACT":
            if touch_count == 0:
                touch_start = i
            touch_count += 1
        # format
        elif df_sensor.iloc[i]['Type'] == "RELEASE":
            touch_count = 0
            touch_end = i
            touch_range.append([touch_start, touch_end + 1])
            num_touch += 1

    for touch in touch_range:
        temp_df = df_sensor.iloc[touch[0] + pre_num:touch[1] - back_num]
        temp_df.reset_index(drop=True, inplace=True)
        temp_df.at[temp_df.index[-1], 'Type'] = "RELEASE"
        df_sensor_rot = df_sensor_rot.append(temp_df, ignore_index=True)

    print(num_touch)
    return df_sensor_rot


def SelectFirstTouchDownEachTap(fulldata):

    fulldata = ModifyTouchData(fulldata)

    concisedata = pd.DataFrame(columns=fulldata.columns)
    touch_count = 0
    num_touch = 0

    for i in fulldata.index:

        if fulldata.iloc[i]['Type'] == "CONTACT":
            if touch_count == 0:

                concisedata = concisedata.append(fulldata.iloc[i], ignore_index=True)
            touch_count += 1
        # format
        elif fulldata.iloc[i]['Type'] == "RELEASE":
            touch_count = 0
            num_touch += 1


    concisedata.reset_index(drop=True, inplace=True)


    print(num_touch)
    return concisedata




def SelectAveragePosEachTap(fulldata):
    fulldata = ModifyTouchData(fulldata)

    touch_count = 0
    num_touch = 0
    touch_range = []

    for i in fulldata.index:

        if fulldata.iloc[i]['Type'] == "CONTACT":
            if touch_count == 0:
                touch_start = i
            touch_count += 1

        # format
        elif fulldata.iloc[i]['Type'] == "RELEASE":
            touch_count = 0
            touch_end = i
            touch_range.append([touch_start, touch_end + 1])
            num_touch += 1
    concisedata = pd.DataFrame(columns=['XPOS', 'YPOS'])
    for touch in touch_range:
        temp_df = fulldata.iloc[touch[0]:touch[1]]
        temp_df = temp_df[['XPOS', 'YPOS']].mean()

        concisedata = concisedata.append(temp_df, ignore_index=True)
    return concisedata



# read in robot data to use in the align function - usually accuracy data as this has one recording per data point

def data_Setup(df_sensor, APL_cfg, APL_Spec, align_tuning=False):


    X_Pixels = int(APL_cfg['SCREEN_WIDTH'])
    Y_Pixels = int(APL_cfg['SCREEN_HEIGHT'])
    X_Length_mm = float(APL_cfg['DutWidth'])
    Y_Length_mm = float(APL_cfg['DutHeight'])

    X_invert = eval(str(APL_Spec['X_invert']))
    Y_invert = eval(str(APL_Spec['Y_invert']))
    Axis_Swap = eval(str(APL_Spec['Axis_Swap']))

    X_Pixel_density = X_Pixels / X_Length_mm  # X Pixel density in Pixels/mm
    Y_Pixel_density = Y_Pixels / Y_Length_mm  # Y Pixel density in Pixels/mm

    pd.set_option('display.max_columns', None)

    sensor = df_sensor[['duration (msec)', 'ID', 'Type', 'X(pixels)', 'Y(pixels)']]  # select the touch event and position detected by the touch sensor

    # ---if axis needs to be swapped---#
    # ---swaps the column headings so that the X and Y axis are the right way around--#
    if X_invert:
        x = (X_Pixels - 1) - sensor['X(pixels)']
        sensor['X(pixels)'] = x

    if Y_invert:
        y = (Y_Pixels - 1) - sensor['Y(pixels)']
        sensor['Y(pixels)'] = y

    if Axis_Swap:
        sensor.columns = [' duration (msec)','ID', 'Type', 'Y(pixels)', 'X(pixels)']
        column_titles = [' duration (msec)','ID', 'Type', 'X(pixels)', 'Y(pixels)']
        sensor = sensor.reindex(columns=column_titles)
        X_Pixel_density = Y_Pixels / X_Length_mm  # X Pixel density in Pixels/mm
        Y_Pixel_density = X_Pixels / Y_Length_mm # Y Pixel density in Pixels/mm

    x_pos_mm = sensor['X(pixels)'] / X_Pixel_density  # value of x position in mm
    sensor = sensor.assign(XPOS=x_pos_mm)  # resign to XPOS row
    y_pos_mm = sensor['Y(pixels)'] / Y_Pixel_density  # value of y position in mm
    sensor = sensor.assign(YPOS=y_pos_mm)  # resign to YPOS row
    sensor = sensor.reset_index(drop=True)  # reset the index of the DataFrame

    if align_tuning:
        x_scaling_factor, x_offset_factor, y_scaling_factor, y_offset_factor = [1, 0, 1, 0]
    else:
        x_scaling_factor, x_offset_factor, y_scaling_factor, y_offset_factor = float(APL_cfg['DutXScalingFactor']), \
                                                                               float(APL_cfg['DutActiveOffsetLR']), \
                                                                               float(APL_cfg['DutYScalingFactor']), \
                                                                               float(APL_cfg['DutActiveOffsetUD'])


    x_adjust = (sensor['XPOS'] - x_offset_factor) / x_scaling_factor  # applying the scaling factor to the touch
    # data
    sensor = sensor.assign(XPOS=x_adjust)  # assign it to the XPOS axis

    y_adjust = (sensor['YPOS'] - y_offset_factor) / y_scaling_factor
    sensor = sensor.assign(YPOS=y_adjust)  # assign it to the YPOS axis

    return sensor  # return the DataFrame sensor to be used in the calculations

def align(touch_data, robot_data,APL_cfg,APL_Spec, directory):

    # align the touch coordinate space with the robot coordinate space
    touch_data = data_Setup(touch_data, APL_cfg,APL_Spec,align_tuning=True)
    Accuracy_Requirement_Centre = float(APL_Spec["Accuracy_Centre"])
    Accuracy_Requirement_Full= float(APL_Spec["Accuracy_Full"])

    firsttouchsensor = SelectFirstTouchDownEachTap(touch_data)
    finger_size = APL_cfg['TestFingerSize']

    # touch_data = sensor[sensor['EVENT'] == 4].reset_index()  # filter for event 4 which is touch down
    # create a dataframe with touch position x and robot x
    align_column_x = ['XPOS', 'robot_x']
    align_x_df = pd.DataFrame(columns=align_column_x)
    # create a dataframe with touch position y and robot y
    align_column_y = ['YPOS', 'robot_y']
    align_y_df = pd.DataFrame(columns=align_column_y)
    # assign the relevant columns to the corresponding columns in align_x_df
    align_x_df['XPOS'] = firsttouchsensor['XPOS']
    align_x_df['robot_x'] = robot_data['robot_x']
    # assign the relevant columns to the corresponding columns in align_y_df
    align_y_df['YPOS'] = firsttouchsensor['YPOS']
    align_y_df['robot_y'] = robot_data['robot_y']
    before_align_df = pd.DataFrame(columns=['robot_x', 'robot_y', 'XPOS', 'YPOS'])
    before_align_df['robot_x'] = align_x_df['robot_x']
    before_align_df['robot_y'] = align_y_df['robot_y']
    before_align_df['XPOS'] = align_x_df['XPOS']
    before_align_df['YPOS'] = align_y_df['YPOS']

    APL_Share.before_align_df = before_align_df
    APL_Share.SubFigList["Calibration_rawdata_before"] = Touch_Sensor_Plot(before_align_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y','Alignment Scan Before Correction', 'x lines (mm)', 'y_lines (mm)', finger_size, directory)

    before_align = pd.DataFrame(columns=['X_delta', 'Y_delta'])
    before_align['X_delta'] = align_x_df['XPOS'] - align_x_df['robot_x']
    before_align['Y_delta'] = align_y_df['YPOS'] - align_y_df['robot_y']

    APL_Share.before_align_error_df = before_align
    APL_Share.SubFigList["Calibration_error_before"] = Dart_Board(before_align, 'Alignment Scan Before Correction', Accuracy_Requirement_Centre, Accuracy_Requirement_Full, finger_size, directory)

    unique_x = robot_data['robot_x'].unique()  # a list of all the unique x values in the robot data
    unique_y = robot_data['robot_y'].unique()  # a list of all the unique y values in the robot data
    x_mean = []  # list with the mean touch sensor x for each unique x robot coordinate
    y_mean = []  # list with the mean touch sensor y for each unique y robot coordinate
    for i in unique_x:  # for value in unique list
        temp_x = align_x_df[align_x_df['robot_x'] == i]  # create a temp DataFrame containing the robot and touch x
        # position for that unique robot x value
        x_mean.append(temp_x['XPOS'].mean())  # calculate the mean value of the touch position for that value of robot x

    for j in unique_y:  # for value in unique list
        temp_y = align_y_df[align_y_df['robot_y'] == j]  # create a temp DataFrame containing the robot and touch y
        # position for that unique robot x value
        y_mean.append(temp_y['YPOS'].mean())  # calculate the mean value of the touch position for that value of robot y

    align_coef_x = np.polyfit(unique_x, x_mean, 1)  # calculate the linear (y = mx +c) line of best fit coefficients
    # for unique_x against x_mean the output is [m,c]
    align_coef_y = np.polyfit(unique_y, y_mean, 1)  # calculate the linear (y = mx +c) line of best fit coefficients
    # for unique_y against y_mean the output is [m,c]

    m_x = float(align_coef_x[0])  # assign gradient to first value in list
    c_x = float(align_coef_x[1])  # assign y intersect to second value in list

    m_y = float(align_coef_y[0])  # assign gradient to first value in list
    c_y = float(align_coef_y[1])  # assign y intersect to second value in list

    align_column = ['XPOS', 'YPOS', 'robot_x', 'robot_y']  # columns for a DataFrame containing the aligned touch
    # data and robot data
    align_df = pd.DataFrame(columns=align_column)  # create DataFrame of aligned DataFrame

    align_df['XPOS'] = (align_x_df['XPOS'] - c_x) / m_x  # in order to align the touch data to the robot data the
    # formula has to be invested so that the touch data is the input value and the output is the aligned touch data
    # which should be better aligned to the robot data
    align_df['robot_x'] = align_x_df['robot_x']  # copy the robot data over to the new DataFrame
    align_df['YPOS'] = (align_y_df['YPOS'] - c_y) / m_y  # in order to align the touch data to the robot data the
    # formula has to be invested so that the touch data is the input value and the output is the aligned touch data
    # which should be better aligned to the robot data
    align_df['robot_y'] = align_y_df['robot_y']  # copy the robot data over to the new DataFrame

    APL_Share.align_df = align_df
    APL_Share.SubFigList["Calibration_rawdata_after"] = Touch_Sensor_Plot(align_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y','Alignment Scan After Correction', 'x lines (mm)', 'y_lines (mm)', finger_size, directory)
    list_coef = [align_coef_x, align_coef_y]  # list containing the alignment coefficients that will be used on the
    # touch data for each calculation - the format is [[mx, cx], [my, cy]]
    # print(list_coef)
    align_error_df = pd.DataFrame(columns=['X_delta', 'Y_delta'])
    align_error_df['X_delta'] = align_df['XPOS'] - align_df['robot_x']
    align_error_df['Y_delta'] = align_df['YPOS'] - align_df['robot_y']

    APL_Share.align_error_df = align_error_df
    APL_Share.SubFigList["Calibration_error_after"] = Dart_Board(align_error_df, 'Alignment Scan After Correction', Accuracy_Requirement_Centre, Accuracy_Requirement_Full, finger_size, directory)

    # plt.show()

    return list_coef,before_align,align_error_df


def data_Setup_Affine_Transform(df_sensor, APL_cfg, APL_Spec, test_directory,align_tuning=False):

    X_Pixels = int(APL_cfg['SCREEN_WIDTH'])
    Y_Pixels = int(APL_cfg['SCREEN_HEIGHT'])
    X_Length_mm = float(APL_cfg['DutWidth'])
    Y_Length_mm = float(APL_cfg['DutHeight'])

    X_invert = eval(str(APL_Spec['X_invert']))
    Y_invert = eval(str(APL_Spec['Y_invert']))
    Axis_Swap = eval(str(APL_Spec['Axis_Swap']))

    X_Pixel_density = X_Pixels / X_Length_mm  # X Pixel density in Pixels/mm
    Y_Pixel_density = Y_Pixels / Y_Length_mm  # Y Pixel density in Pixels/mm

    pd.set_option('display.max_columns', None)

    sensor = df_sensor[['duration (msec)', 'ID', 'Type', 'X(pixels)', 'Y(pixels)']].copy()  # select the touch event and position detected by the touch sensor

    # ---if axis needs to be swapped---#
    # ---swaps the column headings so that the X and Y axis are the right way around--#
    if X_invert:
        x = (X_Pixels - 1) - sensor['X(pixels)']
        sensor.loc[:,'X(pixels)'] = x

    if Y_invert:
        y = (Y_Pixels - 1) - sensor['Y(pixels)']
        sensor.loc[:,'Y(pixels)'] = y

    if Axis_Swap:
        sensor.columns = [' duration (msec)','ID', 'Type', 'Y(pixels)', 'X(pixels)']
        column_titles = [' duration (msec)','ID', 'Type', 'X(pixels)', 'Y(pixels)']
        sensor = sensor.reindex(columns=column_titles)
        X_Pixel_density = Y_Pixels / X_Length_mm  # X Pixel density in Pixels/mm
        Y_Pixel_density = X_Pixels / Y_Length_mm # Y Pixel density in Pixels/mm

    x_pos_mm = sensor['X(pixels)'] / X_Pixel_density  # value of x position in mm
    sensor = sensor.assign(XPOS=x_pos_mm)  # resign to XPOS row
    y_pos_mm = sensor['Y(pixels)'] / Y_Pixel_density  # value of y position in mm
    sensor = sensor.assign(YPOS=y_pos_mm)  # resign to YPOS row
    sensor = sensor.reset_index(drop=True)  # reset the index of the DataFrame
    cal_path = os.path.join(test_directory,"calibration_matrix.npy")
    if align_tuning or not os.path.exists(cal_path):
        print("using data without any calibration")

    else:
        touch_data = sensor[['XPOS','YPOS']]
        sensor_array = touch_data.values


        H = np.load(cal_path)
        print("using data  calibration data")
        print('calibartion matrix is :')
        print(H)

        sensor_array = np.column_stack((sensor_array, np.ones(len(sensor_array))))

        sensor_aligned_array = np.dot(H, sensor_array.T)
        sensor['XPOS'] = sensor_aligned_array[0, :]
        sensor['YPOS'] = sensor_aligned_array[1, :]


    return sensor  # return the DataFrame sensor to be used in the calculations


def align_Affine_Transform(touch_data, robot_data,APL_cfg,APL_Spec, directory,method):

    # align the touch coordinate space with the robot coordinate space
    touch_data = data_Setup_Affine_Transform(touch_data, APL_cfg, APL_Spec,directory,align_tuning=True)

    Accuracy_Requirement_Centre = float(APL_Spec["Accuracy_Centre"])
    Accuracy_Requirement_Full = float(APL_Spec["Accuracy_Full"])

    firsttouchsensor = SelectAveragePosEachTap(touch_data)
    finger_size = APL_cfg['TestFingerSize']

    # touch_data = sensor[sensor['EVENT'] == 4].reset_index()  # filter for event 4 which is touch down
    # create a dataframe with touch position x and robot x
    align_column_x = ['XPOS', 'robot_x']
    align_x_df = pd.DataFrame(columns=align_column_x)
    # create a dataframe with touch position y and robot y
    align_column_y = ['YPOS', 'robot_y']
    align_y_df = pd.DataFrame(columns=align_column_y)
    # assign the relevant columns to the corresponding columns in align_x_df
    align_x_df['XPOS'] = firsttouchsensor['XPOS']
    align_x_df['robot_x'] = robot_data['robot_x']
    # assign the relevant columns to the corresponding columns in align_y_df
    align_y_df['YPOS'] = firsttouchsensor['YPOS']
    align_y_df['robot_y'] = robot_data['robot_y']
    before_align_df = pd.DataFrame(columns=['robot_x', 'robot_y', 'XPOS', 'YPOS'])
    before_align_df['robot_x'] = align_x_df['robot_x']
    before_align_df['robot_y'] = align_y_df['robot_y']
    before_align_df['XPOS'] = align_x_df['XPOS']
    before_align_df['YPOS'] = align_y_df['YPOS']

    APL_Share.before_align_df = before_align_df
    APL_Share.SubFigList["Calibration_rawdata_before"] = Touch_Sensor_Plot(before_align_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y','Alignment Scan Before Correction', 'x lines (mm)', 'y_lines (mm)', finger_size, directory)

    before_align = pd.DataFrame(columns=['X_delta', 'Y_delta'])
    before_align['X_delta'] = align_x_df['XPOS'] - align_x_df['robot_x']
    before_align['Y_delta'] = align_y_df['YPOS'] - align_y_df['robot_y']

    APL_Share.before_align_error_df = before_align
    APL_Share.SubFigList["Calibration_error_before"] = Dart_Board(before_align, 'Alignment Scan Before Correction', Accuracy_Requirement_Centre, Accuracy_Requirement_Full, finger_size, directory)

    sensor_array = np.float32(firsttouchsensor.values)
    robot_array = np.float32(robot_data.values[:, :-1])


    if method =="Affine":

        H, _ = cv2.estimateAffine2D(sensor_array, robot_array, method=cv2.RANSAC, ransacReprojThreshold=5)

    if method =="Homography":

        H, _ = cv2.findHomography(sensor_array, robot_array, method=cv2.RANSAC, ransacReprojThreshold=5)

    cal_path = os.path.join(directory, "calibration_matrix.npy")
    np.save(cal_path, H)
    cal_path_txt = os.path.join(directory, "calibration_matrix.txt")
    np.savetxt(cal_path_txt,H,fmt='%.18e',
              delimiter=' ',
              newline='\n',)

    sensor_array = np.column_stack((sensor_array, np.ones(len(sensor_array))))

    sensor_aligned_array = np.dot(H, sensor_array.T)



    align_column = ['XPOS', 'YPOS', 'robot_x', 'robot_y']  # columns for a DataFrame containing the aligned touch
    # data and robot data
    align_df = pd.DataFrame(columns=align_column)  # create DataFrame of aligned DataFrame

    align_df['XPOS'] =sensor_aligned_array[0,:]  # in order to align the touch data to the robot data the
    # formula has to be invested so that the touch data is the input value and the output is the aligned touch data
    # which should be better aligned to the robot data
    align_df['robot_x'] = align_x_df['robot_x']  # copy the robot data over to the new DataFrame
    align_df['YPOS'] = sensor_aligned_array[1,:]  # in order to align the touch data to the robot data the
    # formula has to be invested so that the touch data is the input value and the output is the aligned touch data
    # which should be better aligned to the robot data
    align_df['robot_y'] = align_y_df['robot_y']  # copy the robot data over to the new DataFrame

    APL_Share.align_df = align_df
    APL_Share.SubFigList["Calibration_rawdata_after"] = Touch_Sensor_Plot(align_df, 'XPOS', 'YPOS', 'robot_x', 'robot_y','Alignment Scan After Correction', 'x lines (mm)', 'y_lines (mm)', finger_size, directory)

    align_error_df = pd.DataFrame(columns=['X_delta', 'Y_delta'])
    align_error_df['X_delta'] = align_df['XPOS'] - align_df['robot_x']
    align_error_df['Y_delta'] = align_df['YPOS'] - align_df['robot_y']
    APL_Share.align_error_df = align_error_df
    APL_Share.SubFigList["Calibration_error_after"] = Dart_Board(align_error_df, 'Alignment Scan After Correction', Accuracy_Requirement_Centre, Accuracy_Requirement_Full, finger_size, directory)


    # plt.show()

    return H, before_align, align_error_df
