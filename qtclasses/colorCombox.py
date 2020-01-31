from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QToolButton, QGridLayout, QAction, QWidget, QMenu, QVBoxLayout, QSizePolicy

colors = [
    [QColor(0, 0, 0, 255), QColor(170, 0, 0, 255), QColor(0, 85, 0, 255), QColor(170, 85, 0, 255),
     QColor(0, 170, 0, 255), QColor(170, 170, 0, 255), QColor(0, 255, 0, 255), QColor(170, 250, 0, 255)],

    [QColor(0, 0, 127, 255), QColor(170, 0, 127, 255), QColor(0, 85, 127, 255), QColor(170, 85, 127, 255),
     QColor(0, 170, 127, 255), QColor(170, 170, 127, 255), QColor(0, 255, 127, 255), QColor(170, 255, 127, 255)],

    [QColor(0, 0, 255, 255), QColor(170, 0, 255, 255), QColor(0, 85, 255, 255), QColor(170, 85, 255, 255),
     QColor(0, 170, 255, 255), QColor(170, 170, 255, 255), QColor(0, 255, 255, 255), QColor(170, 255, 255, 255)],

    [QColor(85, 0, 0, 255), QColor(255, 0, 0, 255), QColor(85, 85, 0, 255), QColor(255, 85, 0, 255),
     QColor(85, 170, 0, 255), QColor(255, 170, 0, 255), QColor(85, 255, 0, 255), QColor(255, 255, 0, 255)],

    [QColor(85, 0, 127, 255), QColor(255, 0, 127, 255), QColor(85, 85, 127, 255), QColor(255, 85, 127, 255),
     QColor(85, 170, 127, 255), QColor(255, 170, 127, 255), QColor(85, 255, 127, 255), QColor(255, 255, 127, 255)],

    [QColor(85, 0, 255, 255), QColor(255, 0, 255, 255), QColor(85, 85, 255, 255), QColor(255, 85, 255, 255),
     QColor(85, 170, 255, 255), QColor(255, 170, 255, 255), QColor(85, 255, 255, 255), QColor(255, 255, 255, 255)]
     ]

class ColorCombox(QToolButton):

    sigColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super(QToolButton, self).__init__(parent)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.setMenu(self.createColorMenu(self.OnColorChanged))
        self.setAutoFillBackground(True)
        self.setArrowType(Qt.NoArrow)
        self.setIcon(self.createColorIcon(Qt.red))
        self.clicked.connect(self.showFkMenu)
        self.menu().aboutToHide.connect(self.enableMenu)

    def setIconColor(self, color):
        print("Icon color:{}".format(hex(color.rgb())))
        self.setIcon(self.createMenuIcon(color))
        self.setIconSize(self.size())

    def enableMenu(self):
        self.clicked.connect(self.showFkMenu)

    def showFkMenu(self):
        self.clicked.disconnect(self.showFkMenu)
        self.showMenu()

    def createColorIcon(self, color):
        pixmap = QPixmap(16, 16)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.fillRect(QRect(0, 0, 16, 16), color)
        painter.end()
        return QIcon(pixmap)

    def createMenuIcon(self, color):
        w = self.width()
        h = self.height()
        print(w,h)
        pixmap = QPixmap(w, h)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.fillRect(QRect(0, 0, w, h), color)
        painter.end()
        return QIcon(pixmap)

    def createColorMenu(self, slot):
        pGridLayout = QGridLayout()
        pGridLayout.setAlignment(Qt.AlignCenter)
        pGridLayout.setContentsMargins(0, 0, 0, 0)
        pGridLayout.setSpacing(2)
        for iRow in range(6):
            for iCol in range(8):
                action = QAction()
                # print(colors[iRow][iCol])
                action.setData(colors[iRow][iCol])
                action.setIcon(self.createColorIcon(colors[iRow][iCol]))
                # connect(action, SIGNAL(triggered()), this, slot)
                action.triggered.connect(slot)
                pBtnColor = QToolButton()
                pBtnColor.setFixedSize(QSize(16, 16))
                pBtnColor.setAutoRaise(True)
                pBtnColor.setDefaultAction(action)
                pBtnColor.setToolTip(hex((colors[iRow][iCol]).rgb()))
                pGridLayout.addWidget(pBtnColor, iRow, iCol)
        widget = QWidget()
        widget.setLayout(pGridLayout)
        pvLayout = QVBoxLayout()
        pvLayout.addWidget(widget)
        colorMenu = QMenu(self)
        colorMenu.setLayout(pvLayout)
        return colorMenu

    def OnColorChanged(self, triggered):
        pFillColorAction = self.sender()
        if isinstance(pFillColorAction, QAction):
            color = QColor(pFillColorAction.data())
            print("Color set:{}".format(hex(color.rgb())))
            self.menu().close()
            self.sigColorChanged.emit(color)
            self.setIconColor(color)
