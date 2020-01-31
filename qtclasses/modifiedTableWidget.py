from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QProxyStyle, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem


class modifiedTableWidget(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(modifiedTableWidget, self).__init__(parent)
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
        self.horizontalHeader().sectionClicked.connect(self.sort)
        self.color = QColor(40, 65, 79)
        self.asc=False

    def sort(self, index:int):
        if self.asc:
            self.sortItems(index, Qt.AscendingOrder)
        else:
            self.sortItems(index, Qt.DescendingOrder)
        self.asc = not self.asc

    def leaveEvent(self, event):
        item = self.item(self.previousColorRow, 0)
        if item is not None:
            self.setRowColor(self.previousColorRow, self.lastRowBkColor)
        event.accept()

    def setBGColor(self, color):
        # Blue:QColor(193,210,240)
        self.color = color

    def mouseOnRow(self, row: int, column: int) -> None:
        item = self.item(self.previousColorRow, 0)
        if item is not None:
            self.setRowColor(self.previousColorRow, self.lastRowBkColor)
        item = self.item(row, column)
        if item is not None and not item.isSelected():
            self.setRowColor(row, self.color)
        self.previousColorRow = row

    def setRowColor(self, row: int, color: QColor):
        for i in range(0, self.columnCount()):
            item = self.item(row, i)
            if isinstance(item, QTableWidgetItem):
                item.setBackground(color)

