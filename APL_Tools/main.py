# -----libraries-----------#
import pandas as pd
import os
import sys
import Setup
import RiverOnTree
import Accuracy
import Precision
import Linearity
import Linearity_RoT
import Precision_RoT
import Accuracy_RoT
import Jitter
import select_file

import get_variable_value

def outputfile(variablefilename):

    newname1 = variablefilename.replace("DUT_Info", "Analysis")
    newname2 = newname1.replace(".csv", ".xlsx")


    return newname2


def isitriverdata(touchdata):

    rivertouchdatheadings = pd.DataFrame(columns=['cycle', 'duration (msec)', 'Class', "ID", 'Type', 'X(pixels)', 'Y(pixels)', 'Width(mm)', 'Height(mm)'])

    columnnumber = 0

    touchheadings = touchdata.iloc[0:0]

    while columnnumber < len(rivertouchdatheadings.columns):
        if rivertouchdatheadings.columns.values[columnnumber] == touchheadings.columns.values[columnnumber]:
            riverdata = True
            columnnumber = columnnumber + 1
        else:
            riverdata = False
            columnnumber = len(rivertouchdatheadings.columns) + 1

    return riverdata

def execution(APL_tests, setup_variables, comment):

    Accuracy_Requirement_Centre = float(testrequirements.loc['Accuracy_Centre'].item())
    Accuracy_Requirement_Full = float(testrequirements.loc['Accuracy_Full'].item())
    Precision_Requirement_Centre = float(testrequirements.loc['Precision_Centre'].item())
    Precision_Requirement_Full = float(testrequirements.loc['Precision_Full'].item())
    Linearity_Requirement_Full = float(testrequirements.loc['Linearity_Full'].item())
    StationaryJitter_Requirement_Centre = float(testrequirements.loc['StationaryJitter_Centre'].item())
    StationaryJitter_Requirement_Full = float(testrequirements.loc['StationaryJitter_Full'].item())
    edge = float(testrequirements.loc['Edge'].item())
    Linearity_Requirement_Centre = float(testrequirements.loc['Linearity_Centre'].item())
    number_of_repeats = setup_variables.loc['TestNoTaps']
    just_aligned = False

    test_directory = (os.path.dirname(setupfilename) + '\\')
    print('Test directory ', test_directory)

    for test in APL_tests:

        robot_data, touch_data, test_type, output_file = test
        output_file = r"C:\Eswin_Optofidelity\Robot_Tests\Test_Results"
        touch_data = pd.read_csv(touch_data)
        robot_data = pd.read_csv(robot_data)
        # IF the RoT flag is set to true then call RoT function to convert RoT data to match format of Tree Data
        pd.set_option('display.max_columns', None)

        sensor = Setup.data_Setup(touch_data, setup_variables, screenorientation)

        print(test_type)

        if test_type[0] == "Accuracy":

            alignment_required = input("Do you want to run alignment pass y/n")

            if alignment_required == "y" or alignment_required == "y":
                print('alignment needed')
                Setup.align(touch_data, robot_data, setup_variables, screenorientation, setupfilename,
                            Accuracy_Requirement_Centre, Accuracy_Requirement_Full, test_directory)
                just_aligned = True
            else:
                output_data, output_data_centre, results, results_centre, centre_value, full_value = Accuracy_RoT.accuracy_RoT(sensor, robot_data,
                                                                                                     Accuracy_Requirement_Centre, Accuracy_Requirement_Full,
                                                                                                     setup, edge, test_directory)

        if test_type[0] == "Linearity":
                output_data, output_data_centre, results, results_centre, centre_value, full_value = Linearity_RoT.linearity_RoT(sensor, Linearity_Requirement_Centre,
                                                                                                       Linearity_Requirement_Full,
                                                                                                       setup, edge, test_directory)

        if test_type[0] == "Precision":

            number_of_repeats = int(setup_variables.value['TestNoTaps'])

            output_data, output_data_centre, results, results_centre, centre_value, full_value = Precision_RoT.precision_RoT(sensor,robot_data, number_of_repeats, Precision_Requirement_Centre,  Precision_Requirement_Full,
                                                                                                       setup, edge,test_directory)

        if test_type[0] == "StationaryJitter":

            output_data, output_data_centre, results, results_centre, centre_value, full_value = Jitter.jitter(sensor, robot_data, StationaryJitter_Requirement_Centre, StationaryJitter_Requirement_Full, setup, edge, test_directory)


        if not just_aligned:

            test_directory = (os. path. dirname(setupfilename)+'\\')

            filename = str(outputfile(setupfilename))


            output_data.to_excel(filename, index=False, header=True)

            with pd.ExcelWriter(filename) as writer:

                output_data.to_excel(writer, sheet_name='Full touch sensor', index=False, header=True, startrow=2,
                                         startcol=0)

                output_data_centre.to_excel(writer, sheet_name='Centre', index=False, header=True, startrow=1,
                                                    startcol=0)

                text_2 = 'The results for the centre ' + test_type[0] + " : " + results_centre + " - " + str(
                    centre_value) + "mm" + "\n"
                worksheet = writer.sheets['Centre']
                worksheet.write(0, 0, text_2)

                worksheet = writer.sheets['Full touch sensor']
                text_1 = 'The result of the full touch sensor ' + test_type[0] + " : " + results + " - " + str(
                    full_value) + "mm" + "\n"
                worksheet.write(1, 0, text_1)
                worksheet.write(0, 0, comment)

                setupvariables = pd.read_csv(setupfilename)
                setupvariables.to_excel(writer, sheet_name='Settings', index=False, header=True, startrow=0,
                                            startcol=0)


if __name__ == "__main__":

    os.chdir(r"C:\workspace\Robot\River_Analysis\Test_Results")
    robotpositionfilename = select_file.getfilename('robot positions')
    touchreportfilename = select_file.getfilename('touch reports')
    setupfilename = select_file.getfilename('setup variables')
    screenorientationfilename = select_file.getfilename('screen orientation')
    testrequirementsfilename = select_file.getfilename('test requirements')
    screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)

    # # China_River
    # robotpositionfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\China_08-09-2022\123_Accuracy_13PT_4mmFingerSize_RobotPos_2022-09-07_17.06.25.432475.csv'
    # touchreportfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\China_08-09-2022\ETS_accuracy.csv'
    # setupfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\China_08-09-2022\123_Accuracy_13PT_4mmFingerSize_DUTInfo_2022-09-07_17.06.25.432475.csv'
    # screenorientationfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\China_08-09-2022\_Screen_Orientation.csv'
    # testrequirementsfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\China_08-09-2022\_Test_Spec.csv'
    # screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    # testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)

    # Mikes Meon Accuracy
    # robotpositionfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Accuracy_RobotPos.csv'
    # touchreportfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Accuracy_THR20.trl.csv'
    # setupfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\MEON_Pixel4_Accuracy_13PT_7mmFingerSize_DUTInfo.csv'
    # screenorientationfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Screen_Orientation.csv'
    # testrequirementsfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Test_Spec.csv'
    # screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    # testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)

    # #Mikes Meon Linearity
    # robotpositionfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Linearity_RobotPos.csv'
    # touchreportfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Linearity_10mmS_THR20.trl.csv'
    # setupfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\MEON_Pixel4_Linearity_WorstCase_7mmFingerSize_DUTInfo.csv'
    # screenorientationfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Screen_Orientation.csv'
    # testrequirementsfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Test_Spec.csv'
    # screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    # testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)

    # Mikes Meon Precision
    # robotpositionfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Precision_RobotPos.csv'
    # touchreportfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Precision_THR20.trl.csv'
    # setupfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\MEON_Pixel4_Precision_13PT_7mmFingerSize_DUTInfo.csv'
    # screenorientationfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Screen_Orientation.csv'
    # testrequirementsfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Test_Spec.csv'
    # screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    # testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)

    # Mikes Meon Jitter
    # robotpositionfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Jitter_RobotPos.csv'
    # touchreportfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\Jitter_THR130_Snap_ON.trl.csv'
    # setupfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\MEON_Pixel4_StationaryJitter_13PT_7mmFingerSize_DUTInfo.csv'
    # screenorientationfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Screen_Orientation.csv'
    # testrequirementsfilename = r'C:\Eswin_Optofidelity\Robot_Tests\Test_Results\APL_Data_MEON_Pixel4\_Test_Spec.csv'
    # screenorientation = pd.read_csv(screenorientationfilename, index_col=0)
    # testrequirements = pd.read_csv(testrequirementsfilename, index_col=0)


    setup = pd.read_csv(setupfilename, index_col=0)

    test = get_variable_value.returnvariablevalue(setupfilename, 'TestType')

    tests = [

        [
            robotpositionfilename,
            touchreportfilename,
            test,
            r'C:\Users\E0005347\Downloads\APL_Final_Config\APL_Final_Config']
    ]

    print(setup)

    check = input("Are the config variables correct? (y/n)")

    print(tests)
    comment = "this should contain the finger size and speed of the finger and any other important information for the tests conditions"
    if check == 'y' or check == 'Y':
        execution(tests, setup, comment)
    else:
        print("Update Variables")
        sys.exit()
