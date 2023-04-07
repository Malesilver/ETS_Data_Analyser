import pandas as pd
import numpy as np

def jitter(df_sensor, robot_pos,  APL_cfg, APL_Spec,edge):

    x_length_mm = float(APL_cfg['DutWidth'])
    y_length_mm = float(APL_cfg['DutHeight'])
    Jitter_Requirements_Full = float(APL_Spec["StationaryJitter_Full"])
    Jitter_Requirements_Ctr = float(APL_Spec["StationaryJitter_Centre"])


    listreleaseindex = []

    Edge_x = x_length_mm - edge
    Edge_y = y_length_mm - edge

    x_jitter = []
    y_jitter = []
    jitter_columns = ['x_jitter', 'y_jitter', 'combined', 'robot_x', 'robot_y']
    jitter_df = pd.DataFrame(columns=jitter_columns)

    for index, row in df_sensor.iterrows():

        contacttype = row['Type']

        if contacttype == 'RELEASE':

            listreleaseindex.append(index)

    touch_count = len(listreleaseindex)

    df_sensor['line_no'] = ''

    touch = 0

    for index, row in df_sensor.iterrows():
        if index <= listreleaseindex[touch]:
            df_sensor.at[index, 'line_no'] = touch

        else:
            touch = touch + 1

    pd.set_option('display.max_columns', None)

    for l in range(touch_count):

        # #line_number = df_sensor.loc['line_no']
        temp = df_sensor[df_sensor['line_no'] == l].reset_index()

        jitter_error_x = temp['XPOS'].max() - temp['XPOS'].min()
        jitter_error_y = temp['YPOS'].max() - temp['YPOS'].min()

        x_jitter.append(jitter_error_x)
        y_jitter.append(jitter_error_y)

    jitter_df['x_jitter'] = x_jitter
    jitter_df['y_jitter'] = y_jitter
    jitter_df['combined'] = np.sqrt(jitter_df['x_jitter']**2 + jitter_df['y_jitter']**2)
    max_jitter = jitter_df['combined'].max()


    for index, row in jitter_df.iterrows():
            Xposition = robot_pos.iat[index,0]
            Yposition = robot_pos.iat[index,1]
            jitter_df.iloc[index, jitter_df.columns.get_loc('robot_x')] = Xposition
            jitter_df.iloc[index, jitter_df.columns.get_loc('robot_y')] = Yposition

            #jitter_df.append(Xposition)



    jitter_table_centre = jitter_df.copy()

    print('jitter row centre', jitter_table_centre)

    for index, row in jitter_table_centre.iterrows():
         if (row['robot_x'] <= edge or row['robot_y'] <= edge) or row['robot_x'] >= Edge_x or row['robot_y'] >= Edge_y:
            jitter_table_centre.drop(index, inplace=True)

    jitter_max_centre = jitter_table_centre['combined'].max()
    if jitter_max_centre <= Jitter_Requirements_Ctr:
        test_outcome_ctr = 'Passed'
    else:
        test_outcome_ctr = 'Failed'

    print('jitter centre:', jitter_max_centre)
    print('Jitter centre has ', test_outcome_ctr)

    if max_jitter> Jitter_Requirements_Full:
        test_outcome = 'Failed'
    else:
        test_outcome = 'Passed'
    print('jitter full:', max_jitter)
    print('Jitter full has ', test_outcome)

    return jitter_df, jitter_table_centre, test_outcome, test_outcome_ctr, jitter_max_centre, max_jitter


