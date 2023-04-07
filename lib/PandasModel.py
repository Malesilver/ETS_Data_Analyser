import pandas as pd

from PySide6.QtWidgets import QTableView, QApplication
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6 import QtGui
import numpy as np
import sys

COLORS = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f']
class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe
        self._range = np.max(self._dataframe.values) - np.min(self._dataframe.values)
        self._minValue = np.min(self._dataframe.values)

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.index)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])


        if role == Qt.BackgroundRole:
            if self._range ==0:
                return QtGui.QColor('black')

            value = int(self._dataframe.iloc[index.row(), index.column()])

            value = int((value - self._minValue) *10 / self._range)
            return QtGui.QColor(COLORS[value])
        if role == Qt.ForegroundRole:
            value = int(self._dataframe.iloc[index.row(), index.column()])
            if self._range ==0:
                return QtGui.QColor('white')

            value = int((value - self._minValue) * 10 / self._range)
            if  value > 2:
                return QtGui.QColor('black')
            else :

                return QtGui.QColor('white')


        return None


    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

