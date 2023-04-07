import pandas as pd
import csv

def returnvariablevalue(filesource, variablename):

    reader = csv.reader(open(filesource, 'r'))
    for row in reader:
        if row[0] == variablename:
            variablevalue = row[1:]
            return variablevalue
    return





