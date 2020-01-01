from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QProxyStyle, QTableWidget, QAbstractItemView, QHeaderView


class Table(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        self.setMouseTracking(True)
        self.lastRowBkColor = QColor(0x00, 0xff, 0x00, 0x00)
        self.previousColorRow = -1
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setHidden(True)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.setShowGrid(False)
        # self.setSizeAdjustPolicy(
        #     QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.cellEntered.connect(self.mouseOnRow)

    def leaveEvent(self, event):
        item = self.item(self.previousColorRow, 0)
        if item is not None:
            self.setRowColor(self.previousColorRow, self.lastRowBkColor)
        event.accept()

    def mouseOnRow(self, row: int, column: int) -> None:
        item = self.item(self.previousColorRow, 0)
        if item is not None:
            self.setRowColor(self.previousColorRow, self.lastRowBkColor)
        item = self.item(row, column)
        if item is not None and not item.isSelected():
            self.setRowColor(row, QColor(40, 65, 79))
        self.previousColorRow = row

    def setRowColor(self, row: int, color: QColor):
        for i in range(0, self.columnCount()):
            item = self.item(row, i)
            item.setBackground(color)

