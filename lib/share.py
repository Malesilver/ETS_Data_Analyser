import os,json
from PySide6.QtCore import Signal,QObject

Customer_list = ["BOE","HW_quick","HW_thp_afe"]

class SNR_Params():
    def __init__(self,customer_name):
        self.customer_name = str(customer_name)
        if self.customer_name not in Customer_list:
            raise "Customer Name not in list, supported Customers are {}".format(Customer_list)
        self.Patterns = []
        self.SNR_cfg = {}

class SI:
    """
    share information
    """
    mainWin = None
    loginWin = None
    session = None

    # System settings includes folder paths, notouch prefix, touch prefix, firmware version, Chip, frame num for snr ,
    cfg = {}

    #APL test DUT cfg
    APL_cfg = {}
    APL_Spec = {}

    HW_SNR_cfg = {}
    # Save MDI sub window
    subWinTable = {}

    # SNR Options
    Patterns = []
    Customers = []

    HW_THP_AFE_params = SNR_Params('HW_thp_afe')
    BOE_params = SNR_Params('BOE')



    @staticmethod
    def loadCfgFile():
        if os.path.exists('cfg.json'):
            with open('cfg.json',encoding='utf8') as f:
                SI.cfg = json.load(f)
            f.close()

        if os.path.exists('APL_cfg.json'):
            with open('APL_cfg.json',encoding='utf8') as f:
                SI.APL_cfg = json.load(f)
            f.close()

        if os.path.exists('APL_Screen_Spec.json'):
            with open('APL_Screen_Spec.json',encoding='utf8') as f:
                SI.APL_Spec = json.load(f)
            f.close()

        if os.path.exists('hw_thp_snr_cfg.json'):
            with open('hw_thp_snr_cfg.json',encoding='utf8') as f:
                SI.HW_THP_AFE_params.SNR_cfg = json.load(f)
            f.close()

        if os.path.exists('boe_snr_cfg.json'):
            with open('boe_snr_cfg.json',encoding='utf8') as f:
                SI.BOE_params.SNR_cfg = json.load(f)
            f.close()




# str signal for text browser
class MySignals(QObject):

    log = Signal(str)


class sdm(object):
    """
    share data manager (SDM)
    """

    row_num = None
    colum_num = None

    current_mct_grid = None
    current_sct_row = None
    current_sct_col = None
    current_sct_row_max = None
    current_sct_row_min = None
    current_sct_col_max = None
    current_sct_col_min = None

    subWinTable = {}