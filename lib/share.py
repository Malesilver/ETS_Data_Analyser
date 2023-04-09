import os, json
from PySide6.QtCore import Signal, QObject

Customer_list = ["BOE", "HW_quick", "HW_thp_afe","VNX", "CSOT", "LENOVO","General"]


class SNR_Params():
    def __init__(self, customer_name):
        self.customer_name = str(customer_name)
        if self.customer_name not in Customer_list:
            raise "Customer Name not in list, supported Customers are {}".format(Customer_list)
        self.Patterns = []
        self.SNR_cfg = {}
        if self.customer_name == "General":
            self.customer_list = []


class SI(object):
    """
    share info class
    """
    mainWin = None
    loginWin = None
    session = None

    # System settings includes folder paths, notouch prefix, touch prefix, firmware version, Chip, frame num for snr ,
    cfg = {}

    # APL test DUT cfg
    APL_cfg = {}
    APL_Spec = {}

    HW_SNR_cfg = {}
    # Save MDI sub window
    subWinTable = {}

    HW_THP_AFE_params = SNR_Params('HW_thp_afe')
    BOE_params = SNR_Params('BOE')
    General_params = SNR_Params('General')

    @staticmethod
    def loadCfgFile():
        if os.path.exists('cfg.json'):
            with open('cfg.json', encoding='utf8') as f:
                SI.cfg = json.load(f)
            f.close()

        if os.path.exists('APL_cfg.json'):
            with open('APL_cfg.json', encoding='utf8') as f:
                SI.APL_cfg = json.load(f)
            f.close()

        if os.path.exists('APL_Screen_Spec.json'):
            with open('APL_Screen_Spec.json', encoding='utf8') as f:
                SI.APL_Spec = json.load(f)
            f.close()

        if os.path.exists('hw_thp_snr_cfg.json'):
            with open('hw_thp_snr_cfg.json', encoding='utf8') as f:
                SI.HW_THP_AFE_params.SNR_cfg = json.load(f)
            f.close()

        if os.path.exists('boe_snr_cfg.json'):
            with open('boe_snr_cfg.json', encoding='utf8') as f:
                SI.BOE_params.SNR_cfg = json.load(f)
            f.close()

        if os.path.exists('general_snr_cfg.json'):
            with open('general_snr_cfg.json', encoding='utf8') as f:
                SI.General_params.SNR_cfg = json.load(f)
            f.close()


# str signal for text browser
class MySignals(QObject):
    """
    my signals class
    """
    log = Signal(str)


class ShareDataManager(object):
    """
    share data manager (SDM)
    """

    row_num = None
    colum_num = None

    current_grid_data = None
    current_row_data = None
    current_col_data = None
    current_row_data_max = None
    current_row_data_min = None
    current_col_data_max = None
    current_col_data_min = None

    subWinTable = {}
