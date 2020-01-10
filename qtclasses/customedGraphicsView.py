from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint, QPointF, Qt, QLineF, QRect, QRectF
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QPen, QPixmap, QFont, QImage
from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem
import math
import cv2
import numpy as np



class customedGraphicsView(QGraphicsView):
    sigLeave = QtCore.pyqtSignal()
    sigEnter = QtCore.pyqtSignal()
    sigPointSelectionFinished = QtCore.pyqtSignal(list, list)
    sigLineDrawn = QtCore.pyqtSignal(QLineF)
    sigRevert = QtCore.pyqtSignal(object)
    sigCroppedItem = QtCore.pyqtSignal(QGraphicsPixmapItem, bool)
    sigConfirmCrop = QtCore.pyqtSignal()
    sigRightClicked = QtCore.pyqtSignal()
    sigReferenceNotFound = QtCore.pyqtSignal()
    sigPreparing = QtCore.pyqtSignal()
    sigPreparingFinished = QtCore.pyqtSignal()
    sigTaskFinished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        self.setMouseTracking(True)
        self.lastMousePos = None
        self.cropped_pixmap = None
        self.pressed = False
        self.lastScale = None
        self.curScale = None
        self.lastPic = None
        self.captureLastPhase = None
        self.maximumPointCount = -1
        self.selectedPoint = -1
        self.selectedPointList = []
        self.lineList = []
        self.currentCursor = Qt.ArrowCursor
        self.tempCursor = None
        self.dotPen = QPen()
        self.linePen = QPen()
        self.rectPen = QPen()
        self.textPen = QPen()
        self.attr = "Picture"
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.withinTask = False
        self.lastTask = None
        self.finishedTask = False
        self.dynamicRectSelection = False
        self.dynamicRectStartPoint = None
        self.dynamicLineSelection = False
        self.dynamicLineStartPoint = None
        self.cvmat = None
        self.referenceTrueLength = 25
        self.referencePixels = None
        self.referenceReady = False
        self.dynamicAngleSelectionPhase = -1
        self.anglePoints = []
        self.mountVPoint = None
        self.mountHPoint = None
        self.result = None

    def captureToQImage(self):
        image = QImage(self.width(), self.height(), QImage.Format_RGB32)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        self.render(painter)
        painter.end()
        print("Capture size:{}".format(image.size()))
        return image

    def measureHLength(self):
        self.lastTask = self.measureHLength
        if self.referencePixels is None:
            self.referencePixels = self.detectCircle()

    def measureVLength(self):
        self.lastTask = self.measureVLength
        if self.referencePixels is None:
            self.referencePixels = self.detectCircle()

    def setAttr(self, attr: str):
        self.attr = attr
        if attr == "Video":
            self.setCurrentCursor(Qt.ArrowCursor)

    def calcAngle(self, pointA, pointB, pointC, display=False, roundnum=2):
        dx1 = pointA.x() - pointB.x()
        dy1 = pointA.y() - pointB.y()
        dx2 = pointC.x() - pointB.x()
        dy2 = pointC.y() - pointB.y()
        angle1 = math.atan2(dy1, dx1)
        angle1 = float(angle1 * 180 / math.pi)
        angle2 = math.atan2(dy2, dx2)
        angle2 = float(angle2 * 180 / math.pi)
        if angle1 * angle2 >= 0:
            angle = abs(angle2 - angle1)
        else:
            angle = abs(angle1) + abs(angle2)
        if angle > 180:
            angle = 360 - angle
        print(angle)
        if display:
            self.result = "角度：{} 度".format(str(round(angle, roundnum)))
            self.paintText(str(round(angle, roundnum)), point=self.mapToScene(pointB))
        return angle

    def convertToMat(self):
        '''  Converts a QImage into an opencv MAT format  '''
        pixmapItem = self.lastPic
        if pixmapItem is not None:
            pixmap = pixmapItem.pixmap()
            image = pixmap.toImage()
            incomingImage = image.convertToFormat(4)

            width = incomingImage.width()
            height = incomingImage.height()

            ptr = incomingImage.bits()
            ptr.setsize(incomingImage.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
            self.cvmat = arr
            return arr
        else:
            return None



    def detectCircle(self):

        self.sigPreparing.emit()
        self.convertToMat()
        gray = cv2.cvtColor(self.cvmat, cv2.COLOR_BGR2GRAY)
        circle1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 3000, param1=100, param2=30, minRadius=80, maxRadius=150)
        if circle1 is not None:
            circles = circle1[0, :, :]
            circles = np.uint16(np.around(circles))
            for i in circles[:]:
                cv2.circle(self.cvmat, (i[0], i[1]), i[2], (255, 0, 0), 2)
                cv2.circle(self.cvmat, (i[0], i[1]), 2, (255, 0, 255), 10)
                cv2.rectangle(self.cvmat,(i[0]-i[2],i[1]+i[2]),(i[0]+i[2],i[1]-i[2]),(255,255,0),5)
                print('半径为', i[2])
                Length=i[2]*2
                self.applyMat()
                self.sigPreparingFinished.emit()
                self.referenceReady = True
                return Length
        else:
            self.sigReferenceNotFound.emit()
            return None

    def applyMat(self):
        img_rgb = cv2.cvtColor(self.cvmat, cv2.COLOR_BGR2BGRA)
        qimage = QtGui.QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0],
                              QtGui.QImage.Format_RGB32)
        pixmap = QPixmap.fromImage(qimage)
        item = QGraphicsPixmapItem(pixmap)
        self.fitview(item, renew=True, cleartask=False)


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

    def drawLineDynamic(self):
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.lastTask = self.drawLineDynamic
        self.setPen()
        self.setTemporaryCursor(Qt.CrossCursor)
        self.dynamicLineSelection = True

    def drawAngleDynamic(self):
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.lastTask = self.drawAngleDynamic
        self.setPen()
        self.setTemporaryCursor(Qt.CrossCursor)
        self.dynamicAngleSelectionPhase = 0

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
                self.curScale = 1.2
            else:
                self.scale(1.0 / 1.2, 1.0 / 1.2)
                self.curScale = 1.0 / 1.2
            viewPoint = self.transform().map(scenePos)
            self.horizontalScrollBar().setValue(int(viewPoint.x() - viewWidth * hScale))
            self.verticalScrollBar().setValue(int(viewPoint.y() - viewHeight * vScale))
            self.setCurrentCursor(self.chooseCursor())

    def chooseCursor(self):
        if self.finishedTask:
            return Qt.PointingHandCursor
        elif self.dynamicRectSelection or self.dynamicLineSelection:
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
        scene.addRect(point.x() - 1, point.y() - 1, 3, 3, pen=self.dotPen)
        self.setScene(scene)

    def mountVerticalLine(self, point):
        scene = self.scene()
        multi = self.getMultipier()
        line_size = int(40 / multi) + 1
        point_size = int(5/multi) + 1
        self.setPen(lineColor=Qt.blue, dotColor=Qt.red)
        scene.addRect(point.x() - int((point_size-1)/2), point.y() - int((point_size-1)/2), point_size, point_size, pen=self.dotPen)
        scene.addLine(point.x(), point.y() - line_size, point.x(), point.y() - int((point_size-1)/2), pen=self.linePen)
        scene.addLine(point.x(), point.y() + int((point_size-1)/2), point.x(), point.y() + line_size, pen=self.linePen)
        self.setScene(scene)

    def mountHorizontalLine(self, point):
        scene = self.scene()
        multi = self.getMultipier()
        line_size = int(40 / multi) + 1
        point_size = int(5 / multi) + 1
        self.setPen(lineColor=Qt.blue, dotColor=Qt.red)
        scene.addRect(point.x() - int((point_size-1)/2), point.y() - int((point_size-1)/2), point_size, point_size, pen=self.dotPen)
        scene.addLine(point.x() - line_size, point.y(), point.x() - int((point_size-1)/2), point.y(), pen=self.linePen)
        scene.addLine(point.x() + int((point_size-1)/2), point.y(), point.x() + line_size, point.y(), pen=self.linePen)
        self.setScene(scene)

    # def returnPressed(self):
    #     if self.lastTask == self.selectArea and len(self.selectedPointList) == 2:
    #         print("({},{}),({},{})".format(self.selectedPointList[0].x(), self.selectedPointList[0].y(), self.selectedPointList[1].x(), self.selectedPointList[1].y()))

    def restorePhase(self):
        if self.captureLastPhase is not None:
            scene = QGraphicsScene()
            for i in self.captureLastPhase:
                if isinstance(i, QGraphicsPixmapItem):
                    scene.addItem(i)
            for i in self.captureLastPhase:
                if isinstance(i, QGraphicsLineItem):
                    scene.addItem(i)
            self.setScene(scene)
            self.curScale = self.getMultipier()

    def paintLine(self, pointA, pointB, appendList=True, clear=False, storephase=False, boundaryRestrict=True, assertPt=True):
        if assertPt:
            if not (self.assertPoint(pointA) and self.assertPoint(pointB)):
                return
        if clear:
            if 0 < self.dynamicAngleSelectionPhase <= 2:
                last_scale = self.curScale
                self.restorePhase()
                if round(last_scale, 2) != self.curScale:
                    print(last_scale, self.curScale, "phase")
                    # self.scale(last_scale, last_scale)
            else:
                last_scale = self.curScale
                self.fitview(self.lastPic, cleartask=False, renew=True)
                if round(last_scale, 2) != self.curScale:
                    print(last_scale, self.curScale, "not phase")
                    # self.scale(last_scale, last_scale)
        if pointB.x() < 0 or pointB.x() > self.width() or pointB.y() < 0 or pointB.y() > self.height():
            print("Warning: point ({},{}) exceeds boundary.".format(pointB.x(), pointB.y()))
        scene = self.scene()
        x1 = pointA.x()
        y1 = pointA.y()
        if boundaryRestrict:
            x2 = min(max(pointB.x(), 0), self.width())
            y2 = min(max(pointB.y(), 0), self.height())
        else:
            x2 = pointB.x()
            y2 = pointB.y()

        line = QLineF(x1, y1, x2, y2)
        if appendList:
            self.lineList.append(line)
        scene.addLine(line, pen=self.linePen)
        self.setScene(scene)
        if storephase:
            self.captureLastPhase = self.scene().items()

    def restrictedPoint(self, point):
        x = min(max(point.x(), 0), self.width())
        y = min(max(point.y(), 0), self.height())
        cls = type(point)
        print(cls(x, y))
        return cls(x, y)

    def assertPoint(self, point):
        if self.lastPic is None:
            return point.x() > 0 and point.y() > 0 and point.x() < self.width() and point.y() < self.height()
        else:
            return point.x() > 0 and point.y() > 0 and point.x() < self.lastPic.pixmap().width() and point.y() < self.lastPic.pixmap().height()

    def paintRect(self, pointA, pointB, fit=True, update=False):
        self.fitview(self.lastPic, cleartask=False, renew=True)
        scene = self.scene()
        x1 = pointA.x()
        x2 = pointB.x()
        y1 = pointA.y()
        y2 = pointB.y()
        rectf = QRectF(x1, y1, x2 - x1, y2 - y1)
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

    def paintText(self, text, point):
        scene = self.scene()
        # text = str(round(line.length(), 2))
        txtItem = QGraphicsTextItem(text)
        txtItem.setPos(point)
        txtItem.setDefaultTextColor(self.textPen.color())
        multi = self.getMultipier()
        font = QFont()
        font.setPixelSize(int(24 / multi) + 1)
        txtItem.setFont(font)
        scene.addItem(txtItem)
        self.setScene(scene)

    def revert(self):
        self.selectedPointList = []
        self.lineList = []
        self.finishedTask = False
        if self.lastPic is not None:
            self.fitview(self.lastPic, cleartask=False, renew=True)
            self.lastScale = self.getMultipier()
        if self.lastTask == self.selectAreaDynamic:
            self.dynamicRectStartPoint = None
            self.lastTask()
        elif self.lastTask == self.drawLineDynamic:
            self.dynamicLineStartPoint = None
            self.lastTask()
        elif self.lastTask == self.drawAngleDynamic:
            self.dynamicLineStartPoint = None
            self.captureLastPhase = None
            self.lastTask()
        elif self.lastTask == self.measureHLength:
            self.mountHPoint = None
        elif self.lastTask == self.measureVLength:
            self.mountVPoint = None
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
        self.withinTask = False
        self.lastTask = None
        self.finishedTask = False
        self.dynamicRectSelection = False
        self.dynamicRectStartPoint = None
        self.dynamicLineSelection = False
        self.dynamicLineStartPoint = None
        self.cvmat = None
        self.referencePixels = None
        self.referenceReady = False
        self.currentCursor = Qt.ArrowCursor
        self.tempCursor = None
        self.applyStoredCursor()
        self.dynamicAngleSelectionPhase = -1
        self.anglePoints = []
        self.mountVPoint = None
        self.mountHPoint = None
        self.result = None

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
                self.paintLine(self.selectedPointList[self.selectedPoint - 1],
                               self.selectedPointList[self.selectedPoint - 2])
            if self.showRect:
                self.paintRect(self.selectedPointList[self.selectedPoint - 1],
                               self.selectedPointList[self.selectedPoint - 2])
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

    def setPen(self, dotColor=Qt.blue, lineColor=Qt.blue, rectColor=Qt.blue, textColor=Qt.blue,
               dotPenWidth=1, linePenWidth=1, rectPenWidth=2, textPenWidth=1):
        self.dotPen.setColor(dotColor)
        self.linePen.setColor(lineColor)
        self.rectPen.setColor(rectColor)
        self.textPen.setColor(textColor)
        self.dotPen.setWidth(dotPenWidth)
        self.linePen.setWidth(linePenWidth)
        self.rectPen.setWidth(rectPenWidth)
        self.textPen.setWidth(textPenWidth)

    def getMultipier(self):
        return round(self.transform().m11(), 2)

    def mousePressEvent(self, QMouseEvent):

        if self.attr == "Picture":
            cursorPoint = QMouseEvent.pos()
            if not self.assertPoint(self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))):
                QMouseEvent.ignore()
                return
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
                        cursorPoint = self.restrictedPoint(QMouseEvent.pos())
                        if self.dynamicRectStartPoint is None:
                            self.dynamicRectStartPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                            print("Rect anchor point selected.")
                    elif self.dynamicLineSelection or 0 <= self.dynamicAngleSelectionPhase <= 2:
                        cursorPoint = self.restrictedPoint(QMouseEvent.pos())
                        if self.dynamicLineStartPoint is None:
                            self.dynamicLineStartPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                            print("Line anchor point selected.")
                            if self.dynamicAngleSelectionPhase != -1:
                                self.anglePoints.append(QPoint(cursorPoint.x(), cursorPoint.y()))
                        else:
                            if self.dynamicAngleSelectionPhase != -1:
                                self.dynamicAngleSelectionPhase += 1
                                self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y())),
                                               clear=True, storephase=True)
                                if self.dynamicAngleSelectionPhase < 2:
                                    self.dynamicLineStartPoint = self.mapToScene(
                                        QPoint(cursorPoint.x(), cursorPoint.y()))
                                    print(
                                        "Line anchor point phase {} selected.".format(self.dynamicAngleSelectionPhase))
                                    if self.dynamicAngleSelectionPhase != -1:
                                        self.anglePoints.append(QPoint(cursorPoint.x(), cursorPoint.y()))
                                else:
                                    if self.dynamicAngleSelectionPhase != -1:
                                        self.anglePoints.append(QPoint(cursorPoint.x(), cursorPoint.y()))
                                        self.calcAngle(self.anglePoints[0], self.anglePoints[1], self.anglePoints[2],
                                                       display=True, roundnum=2)
                                    self.dynamicAngleSelectionPhase = -1
                                    self.dynamicLineStartPoint = None
                                    self.anglePoints.clear()
                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()
                            else:
                                self.dynamicLineSelection = False
                                self.unsetTemporaryCursor()
                                self.dynamicLineStartPoint = None
                    elif self.lastTask == self.measureHLength:
                        if not self.referenceReady:
                            return
                        else:
                            if self.mountHPoint is None:
                                self.mountHPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                self.mountVerticalLine(self.mountHPoint)
                            else:
                                newpoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                absdiff = abs(newpoint.x() - self.mountHPoint.x())
                                ans = absdiff / self.referencePixels * self.referenceTrueLength
                                middle_point = QPoint(0.5*newpoint.x() + 0.5*self.mountHPoint.x(),
                                                      0.5*newpoint.y() + 0.5*self.mountHPoint.y())
                                self.mountVerticalLine(newpoint)
                                self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                self.paintText(str(round(float(ans), 2)), middle_point)
                                self.mountHPoint = None
                                self.sigTaskFinished.emit()
                    elif self.lastTask == self.measureVLength:
                        if not self.referenceReady:
                            return
                        else:
                            if self.mountVPoint is None:
                                self.mountVPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                self.mountHorizontalLine(self.mountVPoint)
                            else:
                                newpoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                absdiff = abs(newpoint.y() - self.mountVPoint.y())
                                ans = absdiff / self.referencePixels * self.referenceTrueLength
                                middle_point = QPoint(0.5 * newpoint.x() + 0.5 * self.mountVPoint.x(),
                                                      0.5 * newpoint.y() + 0.5 * self.mountVPoint.y())
                                self.mountHorizontalLine(newpoint)
                                self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                self.paintText(str(round(float(ans), 2)), middle_point)
                                self.mountVPoint = None
                                self.sigTaskFinished.emit()
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
                if self.lastPic is not None and self.cropped_pixmap is not None:
                    self.finishedTask = True
                else:
                    self.revert()
            if self.selectedPoint == -1:
                self.setCurrentCursor(self.chooseCursor())

    def mouseMoveEvent(self, QMouseEvent):
        if self.attr == "Picture":
            if self.dynamicRectSelection and self.dynamicRectStartPoint is not None and self.pressed:
                self.paintRect(self.dynamicRectStartPoint, self.mapToScene(QMouseEvent.pos()))
            elif self.dynamicLineSelection and self.dynamicLineStartPoint is not None:
                self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QMouseEvent.pos()), clear=True)
            elif -1 < self.dynamicAngleSelectionPhase <= 2 and self.dynamicLineStartPoint is not None:
                self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QMouseEvent.pos()), clear=True)
            if self.lastMousePos is not None and self.pressed and not self.dynamicRectSelection:
                mouseDelta = self.mapToScene(QMouseEvent.pos()) - self.mapToScene(self.lastMousePos)
                self.moveScene(mouseDelta)
                self.lastMousePos = QMouseEvent.pos()

    def moveScene(self, delta: QPointF):
        delta *= self.getMultipier()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.centerOn(self.mapToScene(
            QPoint(self.viewport().rect().width() / 2 - delta.x(), self.viewport().rect().height() / 2 - delta.y())))
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
        self.curScale = self.getMultipier()
        self.repaint()
