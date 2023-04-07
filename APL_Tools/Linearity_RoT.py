import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
from .Linearity import linearity_calc
from .Graphs import Line_Plot,Line_Plot_all
from lib.APL_share import APL_Share

#setup = pd.read_csv(r"Setup Variables.csv", index_col=0)

def linearity_RoT(df_sensor, APL_cfg, APL_Spec,edge, directory):
    #df_sensor.to_csv(r'C:\Users\E0005347\Desktop\Data\ETS\sensor.csv')
    print('linearity', df_sensor)

    x_length_mm = float(APL_cfg['DutWidth'])
    y_length_mm = float(APL_cfg['DutHeight'])
    finger_size = APL_cfg['TestFingerSize']
    speed = APL_cfg['TestSpeed']
    Linearity_Requirement_Full = float(APL_Spec["Linearity_Full"])
    Linearity_Requirement_Ctr = float(APL_Spec["Linearity_Centre"])

    # x_pixels = float(setup_variables.iloc[6].item())
    # y_pixels = float(setup_variables.iloc[7].item())

    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge
    line_no = {}
    line_no_count = -1
    df_sensor['line_no'] = ''
    for i in df_sensor.index:
        if df_sensor.iloc[i]['ID'] not in line_no:
            line_no.update({df_sensor.iloc[i]['ID']: 0})
            line_no_count += 1
            line_no[df_sensor.iloc[i]['ID']] = line_no_count
            df_sensor.at[i, 'line_no'] = line_no_count
        elif df_sensor.iloc[i - 1]['Type'] == "RELEASE":
            line_no_count += 1
            line_no[df_sensor.iloc[i]['ID']] = line_no_count
            df_sensor.at[i, 'line_no'] = line_no_count
        else:
            df_sensor.at[i, 'line_no'] = line_no[df_sensor.iloc[i]['ID']]

    df_sensor = df_sensor.astype({'line_no': 'int64'})
    df_list = []
    df_list_centre = []
    max_error_list = []
    max_error_list_centre = []
    error_list = []
    error_list_centre = []
    for l in range(line_no_count + 1):
        temp = df_sensor[df_sensor['line_no'] == l].reset_index()
        error = linearity_calc(temp)
        temp = temp.assign(error=error)
        # df_list.append(temp[temp['error'] < 0.14])
        df_list.append(temp)
        max_error = temp['error'].max()
        max_error_list.append(max_error)
        error_list.append(error)
        # Line_Plot(error, l, 'Linearity Full Error', finger_size, directory, speed)
    APL_Share.SubFigList["Linearity_error_fullscreen"] = Line_Plot_all(error_list,'Linearity Full Error', finger_size, directory, speed)
    for l in range(line_no_count+1):
        temp_centre = df_sensor[df_sensor['line_no'] == l].reset_index()

        for index, row in temp_centre.iterrows():
            if (row['XPOS'] <= edge or row['YPOS'] <= edge or row['XPOS'] >= Edge_x or row['YPOS'] >= Edge_y):
                temp_centre.drop(index, inplace=True)
        temp_centre = temp_centre.reset_index()
        if temp_centre.empty == False:
            error_centre = linearity_calc(temp_centre)
            temp_centre = temp_centre.assign(error=error_centre)
            df_list_centre.append(temp_centre)
            max_error_centre = temp_centre['error'].max()
            max_error_list_centre.append(max_error_centre)
            error_list_centre.append(error_centre)
            # Line_Plot(error_centre,l,'Linearity Centre Error', finger_size, directory, speed)
    APL_Share.SubFigList["Linearity_error_centre"] = Line_Plot_all(error_list_centre, 'Linearity Centre Error', finger_size, directory, speed)
    max_linearity_error = max(max_error_list)
    max_linearity_error_centre = max(max_error_list_centre)
    print('Linearity full: ',max_linearity_error)
    print('Linearity centre: ',max_linearity_error_centre)
    if max_linearity_error > Linearity_Requirement_Full:
        test_outcome = 'Failed'
        print('This test has Failed by: ', max_linearity_error - Linearity_Requirement_Full, 'mm')
    else:
        test_outcome = 'Passed'
        print('This test has passed')
    if max_linearity_error_centre > Linearity_Requirement_Ctr:
        test_outcome_centre = 'Failed'
        print('This test has Failed by: ', max_linearity_error - Linearity_Requirement_Ctr, 'mm')
    else:
        test_outcome_centre = 'Passed'
        print('This test has passed')

    df_linearity = pd.concat(df_list, ignore_index=True)
    df_linearity_2 = df_linearity.astype({'line_no': 'str'})

    df_linearity_centre = pd.concat(df_list_centre, ignore_index=True)
    df_linearity_centre_2 = df_linearity_centre.astype({'line_no': 'str'})

    fig_full = plt.figure()

    # sns.scatterplot(data=df_linearity_2, x='XPOS', y='YPOS', hue='line_no', edgecolor="none", s=8).set(title='Linearity - '+finger_size +' - '+speed+'mmS')
    #
    graph_title_with_size='Linearity Full - '+finger_size
    filename = directory+'\plots\\'+graph_title_with_size+'-Scatter_plot'

    for i,data in enumerate(df_list):

        color = 'C' + str(i)
        plt.plot(data["XPOS"], data["YPOS"],"-", linewidth=3,color=color)
        plt.title(graph_title_with_size)
        plt.xlabel('X lines')
        plt.ylabel('Y lines')
        plt.legend(range(i+1), markerscale=1, bbox_to_anchor=(1.1, 1))
        plt.tight_layout()
    plt.savefig(filename)

    APL_Share.SubFigList["Linearity_data_full"] = fig_full

    fig_centre = plt.figure()
    sns.scatterplot(data=df_linearity_centre_2, x='XPOS', y='YPOS', hue='line_no', edgecolor="none", s=8,).set(title='Linearity Centre - '+finger_size+' - '+speed+'mmS')
    graph_title_with_size='Linearity Centre - '+finger_size
    filename = directory+'\plots\\'+graph_title_with_size+'-Scatter_plot'
    plt.savefig(filename)

    APL_Share.SubFigList["Linearity_data_centre"] = fig_centre


    return df_linearity, df_linearity_centre, test_outcome, test_outcome_centre, max_linearity_error_centre, max_linearity_error

