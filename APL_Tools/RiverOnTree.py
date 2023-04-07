import pandas as pd
# Function to convert the RoT Touch report messaged to be in the same format as the tree T100 messages

def RoT(df_sensor):


    df_sensor.rename(columns={"Type": "EVENT", "X(pixels)": "XPOS", "Y(pixels)": "YPOS"}, inplace=True)
    # replaces column headings from the RoT to be the same as Tree
    df_sensor['EVENT'].replace("CONTACT", 4, inplace=True)  # replaces CONTACT with Event code 4 to match Tree
    # format
    df_sensor.replace("RELEASE", 5, inplace=True)  # replaces RELEASE with Event code 5 to match Tree
    # format
    return df_sensor
