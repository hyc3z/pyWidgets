from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QPointF, Qt, QLineF, QRect, QRectF
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem, QGraphicsScene, QGraphicsPixmapItem


class customedGraphicsView(QGraphicsView):

    sigLeave = QtCore.pyqtSignal()
    sigEnter = QtCore.pyqtSignal()
    sigPointSelectionFinished = QtCore.pyqtSignal(list, list)
    sigLineDrawn = QtCore.pyqtSignal(QLineF)
    sigRevert = QtCore.pyqtSignal(object)
    sigCroppedItem = QtCore.pyqtSignal(QGraphicsPixmapItem, bool)
    sigConfirmCrop = QtCore.pyqtSignal()
    sigRightClicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        self.setMouseTracking(True)
        self.lastMousePos = None
        self.pressed = False
        self.lastScale = None
        self.lastPic = None
        self.maximumPointCount = -1
        self.selectedPoint = -1
        self.selectedPointList = []
        self.lineList = []
        self.currentCursor = Qt.ArrowCursor
        self.tempCursor = None
        self.dotPen = QPen()
        self.linePen = QPen()
        self.rectPen = QPen()
        self.attr = "Picture"
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.withinTask = False
        self.lastTask = None
        self.finishedTask = False
        self.dynamicRectSelection = False
        self.dynamicRectStartPoint = None

    def setAttr(self,attr:str):
        self.attr = attr
        if attr == "Video":
            self.setCurrentCursor(Qt.ArrowCursor)

    def selectArea(self):
        self.showDot = True
        self.showLine = False
        self.showRect = True
        self.withinTask = True
        self.startDraw(2)

        self.lastTask = self.selectArea
        self.withinTask = False

    def selectAreaDynamic(self):
        self.showDot = False
        self.showLine = False
        self.showRect = True
        self.setPen()
        self.setTemporaryCursor(Qt.CrossCursor)
        self.dynamicRectSelection = True
        self.lastTask = self.selectAreaDynamic

    def drawLine(self):
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.withinTask = True

        self.lastTask = self.drawLine
        self.withinTask = False

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
        if self.finishedTask:
            return Qt.PointingHandCursor
        elif self.dynamicRectSelection:
            return Qt.CrossCursor
        else:
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

    # def returnPressed(self):
    #     if self.lastTask == self.selectArea and len(self.selectedPointList) == 2:
    #         print("({},{}),({},{})".format(self.selectedPointList[0].x(), self.selectedPointList[0].y(), self.selectedPointList[1].x(), self.selectedPointList[1].y()))

    def paintLine(self, pointA, pointB):
        scene = self.scene()
        x1 = pointA.x()
        x2 = pointB.x()
        y1 = pointA.y()
        y2 = pointB.y()
        line = QLineF(x1, y1, x2, y2)
        self.lineList.append(line)
        scene.addLine(line, pen=self.linePen)
        self.setScene(scene)

    def paintRect(self, pointA, pointB, fit=True, update=False):
        self.fitview(self.lastPic, cleartask=False, renew=True)
        scene = self.scene()
        x1 = pointA.x()
        x2 = pointB.x()
        y1 = pointA.y()
        y2 = pointB.y()
        rectf = QRectF(x1, y1, x2-x1, y2-y1)
        tl = rectf.topLeft()
        tr = rectf.topRight()
        bl = rectf.bottomLeft()
        br = rectf.bottomRight()
        min_x = min(tl.x(), tr.x(), bl.x(), br.x())
        max_x = max(tl.x(), tr.x(), bl.x(), br.x())
        min_y = min(tl.y(), tr.y(), bl.y(), br.y())
        max_y = max(tl.y(), tr.y(), bl.y(), br.y())
        rect = QRect(QPoint(int(min_x), int(min_y)),
                     QPoint(int(max_x), int(max_y)))
        scene.addRect(rectf, pen=self.rectPen)
        self.setScene(scene)
        if fit:
            self.fitview(self.lastPic, cleartask=False, renew=False)
        if update:
            self.viewport().update()
        if self.lastTask == self.selectArea:
            self.cropped_pixmap = self.lastPic.pixmap().copy(rect)
            self.sigCroppedItem.emit(QGraphicsPixmapItem(self.cropped_pixmap), False)
        elif self.lastTask == self.selectAreaDynamic:
            self.cropped_pixmap = self.lastPic.pixmap().copy(rect)



    def paintText(self, text):
        scene = self.scene()
        # text = str(round(line.length(), 2))
        txtItem = QGraphicsTextItem(text)
        # txtItem.setPos(QPointF((x1+x2)/2, (y1+y2)/2))
        self.lineTextList.append(text)
        scene.addItem(txtItem)
        self.setScene(scene)

    def revert(self):
        self.selectedPointList = []
        self.lineList = []
        self.finishedTask = False
        if self.lastPic is not None:
            self.fitview(self.lastPic, cleartask=False, renew=True)
        if self.lastTask == self.selectAreaDynamic:
            self.dynamicRectStartPoint = None
            self.lastTask()
        elif self.lastTask is not None:
            self.sigRevert.emit(self.lastTask)
            self.lastTask()

    def execLastTask(self):
        if self.lastTask is not None:
            self.lastTask()

    def restore(self):
        self.selectedPointList = []
        self.lineList = []
        if self.lastPic is not None:
            self.fitview(self.lastPic, cleartask=True, renew=True)

    def autoFit(self):
        if self.lastPic is not None:
            self.fitInView(self.lastPic, Qt.KeepAspectRatio)

    def storePoint(self, scenePos):
        self.selectedPoint += 1
        self.selectedPointList.append(scenePos)
        if self.selectedPoint == 1:
            if self.showDot:
                self.paintDot(scenePos)
        else:
            if self.showDot:
                self.paintDot(scenePos)
            if self.showLine:
                self.paintLine(self.selectedPointList[self.selectedPoint-1], self.selectedPointList[self.selectedPoint-2])
            if self.showRect:
                self.paintRect(self.selectedPointList[self.selectedPoint-1], self.selectedPointList[self.selectedPoint-2])
        if self.selectedPoint >= self.maximumPointCount:
            self.selectedPoint = -1
            self.maximumPointCount = -1
            self.unsetTemporaryCursor()
            self.finishedTask = True
            self.sigPointSelectionFinished.emit(self.selectedPointList, self.lineList)
            self.selectedPointList = []
            self.lineList = []

    def startDraw(self, pointCount: int, dotColor=Qt.blue, lineColor=Qt.blue, rectColor=Qt.blue,
                  dotPenWidth=1, linePenWidth=1, rectPenWidth=2):
        self.setTemporaryCursor(Qt.CrossCursor)
        self.selectedPoint = 0
        self.maximumPointCount = pointCount
        self.setPen(dotColor=dotColor, lineColor=lineColor, rectColor=rectColor, dotPenWidth=dotPenWidth,
                    linePenWidth=linePenWidth, rectPenWidth=rectPenWidth)

    def setPen(self, dotColor=Qt.blue, lineColor=Qt.blue, rectColor=Qt.blue,
                  dotPenWidth=1, linePenWidth=1, rectPenWidth=2):
        self.dotPen.setColor(dotColor)
        self.linePen.setColor(lineColor)
        self.rectPen.setColor(rectColor)
        self.dotPen.setWidth(dotPenWidth)
        self.linePen.setWidth(linePenWidth)
        self.rectPen.setWidth(rectPenWidth)

    def getMultipier(self):
        return round(self.transform().m11(), 2)

    def mousePressEvent(self, QMouseEvent):
        if self.attr == "Picture":
            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                if self.finishedTask == True:
                    if self.lastTask == self.selectArea:
                        self.sigConfirmCrop.emit()
                        self.finishedTask = False
                    if self.lastTask == self.selectAreaDynamic:
                        self.sigCroppedItem.emit(QGraphicsPixmapItem(self.cropped_pixmap), False)
                        self.sigConfirmCrop.emit()
                        self.finishedTask = False
                        self.dynamicRectStartPoint = None
                else:
                    self.pressed = True
                    if self.dynamicRectSelection:
                        cursorPoint = QMouseEvent.pos()
                        if self.dynamicRectStartPoint is None:
                            self.dynamicRectStartPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                            print("Anchor point selected.")
                    else:
                        print("Static point selected.")
                        if self.selectedPoint == -1:
                           self.setCurrentCursor(self.chooseCursor())
                        else:
                            cursorPoint = QMouseEvent.pos()
                            scenePos = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                            self.storePoint(scenePos)
            elif QMouseEvent.button() == QtCore.Qt.RightButton:
                self.revert()
                self.sigRightClicked.emit()

    def hasPic(self):
        return self.lastPic is not None

    def mouseReleaseEvent(self, QMouseEvent):
        if self.attr == "Picture":
            self.pressed = False
            if self.dynamicRectSelection and self.dynamicRectStartPoint:
                self.dynamicRectSelection = False
                self.unsetTemporaryCursor()
                self.finishedTask = True
            if self.selectedPoint == -1:
                self.setCurrentCursor(self.chooseCursor())

    def mouseMoveEvent(self, QMouseEvent):
        if self.attr == "Picture":
            if self.dynamicRectSelection and self.dynamicRectStartPoint is not None and self.pressed:
                self.paintRect(self.dynamicRectStartPoint, self.mapToScene(QMouseEvent.pos()))
            if self.lastMousePos is not None and self.pressed and not self.dynamicRectSelection:
                mouseDelta = self.mapToScene(QMouseEvent.pos()) - self.mapToScene(self.lastMousePos)
                self.moveScene(mouseDelta)
                self.lastMousePos = QMouseEvent.pos()


    def moveScene(self, delta: QPointF):
        delta *= self.getMultipier()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.centerOn(self.mapToScene(QPoint(self.viewport().rect().width()/2 - delta.x(), self.viewport().rect().height()/2 - delta.y())))
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

    def fitviewPixmap(self, pixmap):
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.setScene(scene)
        self.fitview(item)

    def fitview(self, item, renew=False, cleartask=True):
        if cleartask:
            self.lastTask = None
        self.lastPic = QGraphicsPixmapItem(item.pixmap().copy())
        if self.scene() is None or renew:
            scene = QGraphicsScene()
            scene.addItem(self.lastPic)
            self.setScene(scene)
        self.fitInView(self.lastPic, Qt.KeepAspectRatio)
        self.lastScale = self.getMultipier()
        self.repaint()
