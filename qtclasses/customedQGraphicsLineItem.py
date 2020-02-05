import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QPointF, QObject, QLineF
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QGraphicsObject, \
    QWidget


class CustomedQGraphicsLineItem(QGraphicsLineItem):

    def __init__(self, parent=None):
        super(QGraphicsLineItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.cursorPos = None
        self.line = None
        # self.clicked.connect(self.emitclick)
        # self.hovered.connect(self.highlighted)
        # self.hovered.connect(self.emitnameHovered)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pen = self.pen()
        width = pen.width()
        # pen.setWidth(2 * width)
        self.setPen(pen)
        # self.setCursor(QtCore.Qt.PointingHandCursor)
        self.cursorPos = QPointF(self.mapToScene(event.pos()))
        # self.sigPoint.emit(self.cursorPos)
        # print("Current Pos:{}, p1:{}, p2:{}, parent:{}".format(self.cursorPos, self.line.p1(), self.line.p2(), self.parentWidget()))

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pen = self.pen()
        width = pen.width()
        # pen.setWidth(0.5 * width)
        self.setPen(pen)
        # self.setCursor(QtCore.Qt.ArrowCursor)
        # if self.pos is not None:
        #     self.sigCancelPoint.emit(self.cursorPos)
    #

    #
    # def setLine(self, *args):
    #     if len(args) == 4:
    #         self.line = QLineF(args[0], args[1], args[2], args[3])
    #     elif len(args) == 1:
    #         self.line = QLineF(args[0])
    #
    # def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     if self.line is not None:
    #         print(self.pos(),self.boundingRect())
    #         painter.drawLine(self.line)
    #
    #
    # def boundingRect(self) -> QtCore.QRectF:
    #     if self.line is not None:
    #         p1 = self.line.p1()
    #         p2 = self.line.p2()
    #         x1 = p1.x()
    #         y1 = p1.y()
    #         x2 = p2.x()
    #         y2 = p2.y()
    #         return QtCore.QRectF(QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2)))