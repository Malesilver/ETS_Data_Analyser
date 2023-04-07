

class APL_Share(object):
    robot_Accuracy = None
    robot_Precision = None
    robot_Linearity = None
    robot_Jitter = None

    # calibration
    before_align_df = None
    before_align_error_df = None
    align_df = None
    align_error_df = None

    # Subwin
    WinCalibResult = None
    WinAccuracyResult = None
    WinPrecisionResult = None
    WinLinearityResult = None
    #Figure List
    SubFigList = {}


