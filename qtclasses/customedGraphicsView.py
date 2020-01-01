from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QPointF, Qt, QLineF
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QPen
from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem


class customedGraphicsView(QGraphicsView):

    sigLeave =  QtCore.pyqtSignal()
    sigEnter =  QtCore.pyqtSignal()
    sigPointSelectionFinished = QtCore.pyqtSignal(list, list)
    sigLineDrawn = QtCore.pyqtSignal(QLineF)
    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        self.setMouseTracking(True)
        self.lastMousePos = None
        self.pressed = False
        self.lastScale = None
        self.maximumPointCount = -1
        self.selectedPoint = -1
        self.selectedPointList = []
        self.lineList = []
        self.currentCursor = Qt.ArrowCursor
        self.tempCursor = None
        self.dotPen = QPen()
        self.linePen = QPen()
        self.attr = "Picture"

    def setAttr(self,attr:str):
        self.attr = attr
        if attr == "Video":
            self.setCurrentCursor(Qt.ArrowCursor)

    def wheelEvent(self, QWheelEvent):
        if self.attr == "Picture":
            cursorPoint = QWheelEvent.pos()
            scenePos = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
            viewWidth = self.viewport().width()
            viewHeight = self.viewport().height()
            hScale = cursorPoint.x() / viewWidth
            vScale = cursorPoint.y() / viewHeight
            deltaval = QWheelEvent.angleDelta().y()
            if deltaval > 0:
                self.scale(1.2, 1.2)
            else:
                self.scale(1.0 / 1.2, 1.0 / 1.2)
            viewPoint = self.transform().map(scenePos)
            self.horizontalScrollBar().setValue(int(viewPoint.x() - viewWidth * hScale))
            self.verticalScrollBar().setValue(int(viewPoint.y() - viewHeight * vScale))
            self.setCurrentCursor(self.chooseCursor())

    def chooseCursor(self):
        if self.attr == "Picture":
            if self.tempCursor is not None:
                return self.tempCursor
            else:
                if self.lastScale is not None:
                    if self.getMultipier() > self.lastScale:
                        return Qt.OpenHandCursor if not self.pressed else Qt.ClosedHandCursor
                    else:
                        return Qt.ArrowCursor
                else:
                    return Qt.ArrowCursor
        elif self.attr == "Video":
            return Qt.OpenHandCursor

    def setCurrentCursor(self, cursor):
        self.storeCursor(cursor)
        self.applyStoredCursor()

    def storeCursor(self, cursor):
        self.currentCursor = cursor

    def setTemporaryCursor(self, cursor):
        self.tempCursor = cursor
        self.setCursor(cursor)

    def unsetTemporaryCursor(self):
        self.tempCursor = None
        self.applyStoredCursor()

    def applyStoredCursor(self):
        self.setCursor(self.currentCursor)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.sigLeave.emit()
        a0.accept()

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.sigEnter.emit()
        a0.accept()


    def paintDot(self, point):
        scene = self.scene()
        scene.addRect(point.x()-1, point.y()-1, 3, 3, pen=self.dotPen)
        self.setScene(scene)

    def paintLine(self, pointA, pointB):
        scene = self.scene()
        x1 = pointA.x()
        x2 = pointB.x()
        y1 = pointA.y()
        y2 = pointB.y()
        line = QLineF(x1, y1, x2, y2)
        self.lineList.append(line)
        scene.addLine(line, pen=self.linePen)
        # text = str(round(line.length(), 2))
        # txtItem = QGraphicsTextItem(text)
        # txtItem.setPos(QPointF((x1+x2)/2, (y1+y2)/2))
        # self.lineTextList.append(text)
        # scene.addItem(txtItem)
        self.setScene(scene)

    def storePoint(self, scenePos):
        self.selectedPoint += 1
        self.selectedPointList.append(scenePos)
        if self.selectedPoint == 1:
            self.paintDot(scenePos)
        else:
            self.paintDot(scenePos)
            self.paintLine(self.selectedPointList[self.selectedPoint-1], self.selectedPointList[self.selectedPoint-2])
        if self.selectedPoint >= self.maximumPointCount:
            self.selectedPoint = -1
            self.maximumPointCount = -1
            self.unsetTemporaryCursor()
            self.sigPointSelectionFinished.emit(self.selectedPointList, self.lineList)
            self.selectedPointList = []
            self.lineList = []

    def startDraw(self, pointCount: int):
        self.setTemporaryCursor(Qt.CrossCursor)
        self.selectedPoint = 0
        self.maximumPointCount = pointCount
        color = Qt.blue
        self.dotPen.setColor(color)
        self.linePen.setColor(color)
        self.dotPen.setWidth(1)
        self.linePen.setWidth(1)

    def getMultipier(self):
        return round(self.transform().m11(), 2)

    def mousePressEvent(self, QMouseEvent):
        if self.attr == "Picture":
            self.pressed = True
            if self.selectedPoint == -1:
               self.setCurrentCursor(self.chooseCursor())
            else:
                cursorPoint = QMouseEvent.pos()
                scenePos = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                self.storePoint(scenePos)

    def mouseReleaseEvent(self, QMouseEvent):
        if self.attr == "Picture":
            self.pressed = False
            if self.selectedPoint == -1:
                self.setCurrentCursor(self.chooseCursor())

    def mouseMoveEvent(self, QMouseEvent):
        if self.attr == "Picture":
            if self.lastMousePos is not None and self.pressed:
                mouseDelta = self.mapToScene(QMouseEvent.pos()) - self.mapToScene(self.lastMousePos)
                self.moveScene(mouseDelta)
            self.lastMousePos = QMouseEvent.pos()

    def moveScene(self, delta: QPointF):
        delta *= self.getMultipier()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.centerOn(self.mapToScene(QPoint(self.viewport().rect().width()/2 - delta.x(), self.viewport().rect().height()/2 - delta.y())))
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

    def fitview(self, item):
        self.fitInView(item, Qt.KeepAspectRatio)
        self.lastScale = self.getMultipier()
