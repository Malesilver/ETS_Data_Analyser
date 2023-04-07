import pandas as pd
import numpy as np

path = r"C:\workspace\Robot\River_Analysis\Test_Results\APL\accuracy.trl.csv"
df = pd.read_csv(path)

df2 = df[['duration (msec)', 'ID', 'Type', 'X(pixels)', 'Y(pixels)']].copy()
y = (3040 - 1) - df2['Y(pixels)']
df2.loc[:,'Y(pixels)'] = y