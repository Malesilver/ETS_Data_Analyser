from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem,QFileDialog
from PySide6.QtUiTools import QUiLoader

from PySide6.QtCore import Qt
import json
import os
from lib.share import SI

class Win_CfgSetting :

    CFG_ITEMS = [
        'Dataset Path','FW Version','Firmware Series',
        'Chip','Screen','touch file prefix','notouch file prefix',
        'start idx notouch','end idx notouch','start idx touch','end idx touch'
    ]

    def __init__(self):
        self.ui = QUiLoader().load('data_cfg.ui')
        self.loadCfgToTable()
        self.ui.splitter.setSizes([500, 100])

        # 指定单元格改动信号处理函数
        self.ui.tableCFG.cellChanged.connect(self.cfgItemChanged)

        self.ui.btnClear.clicked.connect(self.onClearLog)
        self.ui.btnSave.clicked.connect(self._saveCfgButton)
        self.ui.btnSelectFolder.clicked.connect(self._selectFolder)


    def _selectFolder(self):
        FileDirectory = QFileDialog.getExistingDirectory(self.ui, "Select Dataset")
        if FileDirectory is None:
            return
        SI.cfg['Dataset Path'] = FileDirectory

        self.ui.lineFolder.setText(FileDirectory)
        self.ui.lineFolder.setEnabled(False)
        table = self.ui.tableCFG
        table.setItem(0, 1, QTableWidgetItem(FileDirectory))


    def cfgItemChanged(self, row, column):
        table = self.ui.tableCFG

        # 获取更改内容
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, column).text()

        SI.cfg[cfgName] = cfgValue
        self._saveCfgFile()

        self.log(f'{cfgName} : {cfgValue}')

    def _saveCfgButton(self):
        self._saveCfgFile()
        self.log("Successfully save settings to cfg.json!!")


    # save config files
    def _saveCfgFile(self):

        with open('cfg.json', 'w', encoding='utf8') as f:
            json.dump(SI.cfg, f, ensure_ascii=False, indent=2)

    # 加载配置文件到界面
    def loadCfgToTable(self):

        table = self.ui.tableCFG
        for idx,cfgName in enumerate(self.CFG_ITEMS):
            # 插入一行
            table.insertRow(idx)

            # 参数名
            item = QTableWidgetItem(cfgName)
            table.setItem(idx, 0, item)
            item.setFlags(Qt.ItemIsEnabled) # 参数名字段不允许修改

            # 参数值
            table.setItem(idx, 1, QTableWidgetItem(SI.cfg.get(cfgName,'')))

    def onClearLog(self):
        self.ui.textLog.clear()

    def log(self,*texts):
        self.ui.textLog.append(' '.join(texts))
        self.ui.textLog.ensureCursorVisible()