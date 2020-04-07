import csv
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint, QPointF, Qt, QLineF, QRect, QRectF, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QPen, QPixmap, QFont, QImage
from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem, \
    QGraphicsRectItem
import math
import cv2
# from cv2 import cvtColor, HoughCircles, circle, rectangle, COLOR_BGR2BGRA
import numpy as np
import numpy
from customedQGraphicsLineItem import CustomedQGraphicsLineItem
from input_dialog import DialogInput
from logger import SystemLogger
from pop_ups import PopUps
class CircleDetector(QObject):

    sigLength = pyqtSignal(float)
    sigArea = pyqtSignal(float)
    # sigItem = pyqtSignal(QGraphicsPixmapItem)
    sigFinish = pyqtSignal(numpy.ndarray)
    sigReferenceNotFound = pyqtSignal()


    def loadData(self):
        if os.path.exists("ReferenceData.csv"):
            f = open("ReferenceData.csv", "r")
            reader = csv.DictReader(f)
            for i in reader:
                self.minR=int(i['minR'])
                self.maxR=int(i['maxR'])
                self.actSize=int(i['actSize'])
            f.close()

        else:
            self.minR=0
            self.maxR=300
            self.actSize=25

    def convertToMat(self, pixmapItem):
        '''  Converts a QImage into an opencv MAT format  '''
        # pixmapItem = self.lastPic
        if pixmapItem is not None:
            pixmap = pixmapItem.pixmap()
            image = pixmap.toImage()
            incomingImage = image.convertToFormat(4)

            width = incomingImage.width()
            height = incomingImage.height()

            ptr = incomingImage.bits()
            ptr.setsize(incomingImage.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
            return arr
        else:
            return None

    def convertFromMat(self, mat):
        img_rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2BGRA)
        qimage = QtGui.QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0],
                              QtGui.QImage.Format_RGB32)
        pixmap = QPixmap.fromImage(qimage)
        item = QGraphicsPixmapItem(pixmap)
        return item

    def detectCircle(self, pixmapItem):
        # self.sigPreparing.emit()
        try:
            self.loadData()
            mat = self.convertToMat(pixmapItem)
            gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
            SystemLogger.log_info("开始圆检测",self.minR,self.maxR)
            circle1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 3000, param1=100, param2=30, minRadius=self.minR,
                                       maxRadius=self.maxR)
            if circle1 is not None:
                circles = circle1[0, :, :]
                circles = np.uint16(np.around(circles))
                for i in circles[:]:
                    cv2.circle(mat, (i[0], i[1]), i[2], (255, 0, 0), 2)
                    cv2.circle(mat, (i[0], i[1]), 2, (255, 0, 255), 10)
                    cv2.rectangle(mat, (i[0] - i[2], i[1] + i[2]), (i[0] + i[2], i[1] - i[2]), (255, 255, 0), 5)
                    # SystemLogger.log_info('半径为', i[2])
                    Length = i[2] * 2
                    # self.sigPreparingFinished.emit()
                    # 平方毫米
                    referencePixelsArea = math.pi * i[2] * i[2]
                    # actualArea = math.pi * 12.5 * 12.5 / self.referencePixelsArea
                    # item = self.convertFromMat(mat)
                    self.sigLength.emit(Length)
                    SystemLogger.log_info("Length emitted.")
                    self.sigArea.emit(referencePixelsArea)
                    SystemLogger.log_info("Area emitted.")
                    self.sigFinish.emit(mat)
                    SystemLogger.log_info("Mat emitted.")
            else:
                self.sigReferenceNotFound.emit()
        except Exception as e:
            SystemLogger.log_error(e)


class customedGraphicsView(QGraphicsView):
    isNose: int
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
    sigDetectCircle = pyqtSignal(QGraphicsPixmapItem)

    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        self.setMouseTracking(True)
        self.setRenderHint(QPainter.HighQualityAntialiasing)
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
        self.lineItem = None
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
        self.actualArea=1
        self.high_res_qimage= None

        # self.referenceTrueLength = 25
        self.referenceTrueLength = self.getActSize()
        self.referencePixelsArea=None
        self.referencePixels = None
        self.referenceReady = False
        self.dynamicAngleSelectionPhase = -1
        self.anglePoints = []
        self.mountVPoint = None
        self.mountHPoint = None
        self.result = None

        # measure nose length
        self.nosePoints=[]
        self.isNose=-1

        # dot to line length
        self.isDotToLine=-1
        self.dotLine=[]

        self.tempLine = None
        #测面积
        self.isArea=-1
        self.areaPoints=[]
        #用于确定框选区域是否完成
        self.areaDone=False

        #测量曲线距离
        self.isCurve=-1
        self.curvePoints=[]
        self.curveDone=False

        #测体积
        self.isVol=-1
        self.volPoint=[]
        self.volDone=False

        #测距离多线程
        self.workerThread = QThread()
        self.worker = CircleDetector()
        self.worker.moveToThread(self.workerThread)
        # self.workerThread.finished.connect(self.worker.deleteLater)
        self.worker.sigFinish.connect(self.applyMat)
        self.worker.sigArea.connect(self.setReferencePixelArea)
        self.worker.sigLength.connect(self.setReferencePixels)
        self.sigDetectCircle.connect(self.worker.detectCircle)
        # connect(&workerThread, &QThread::finished, worker, &QObject::deleteLater)
        # connect(this, &Controller::operate, worker, &Worker::doWork)
        # connect(worker, &Worker::resultReady, this, &Controller::handleResults);
        self.workerThread.start()
        self.setPen()

    def getActSize(self):
        actsize = 0
        if os.path.exists("ReferenceData.csv"):
            f = open("ReferenceData.csv", "r")
            reader = csv.DictReader(f)

            for i in reader:
                actsize=i['actSize']
            f.close()
        else:
            actsize=25
        return int(actsize)

    def inputDepth(self):
        dialog = DialogInput(self)
        err_range = "输入值有误"
        err_value = "输入值有误"
        err_noInput = "未输入数值"
        dialog.setStyleSheet(
            "QPushButton {"
            " font: bold 24px;"
            "padding-left: 3ex;"
            "padding-right: 3ex;"
            "padding-top: 1ex;"
            "padding-bottom: 1ex;"
            "margin-left:0px;"
            "}"
            "QLabel { font:24px}"
            "QLineEdit { font:24px}"
        )
        dialog.setUnit("mm")
        errstr = " "
        while len(errstr) > 0:
            val = dialog.exec()
            errstr = ""
            try:
                valnum = float(val)
                if valnum < 0:
                    errstr += "\n{}".format(err_range)
            except ValueError:
                errstr += "\n{}".format(err_value)
            except TypeError:
                errstr += "\n{}".format(err_noInput)
            if len(errstr) > 0:
                SystemLogger.log_error(errstr)
        return val
    def chooseNeizi(self,type1):
        SystemLogger.log_info(type1)
        self.result =type1
        self.sigTaskFinished.emit()
        pass
    def setReferencePixels(self, pixels:float):
        SystemLogger.log_info("Length get!")
        self.referencePixels = pixels
        self.actual = self.referenceTrueLength * 1.0 / self.referencePixels

    def setReferencePixelArea(self, area:float):
        SystemLogger.log_info("Area get!")
        self.referencePixelsArea = area

    def measureVol(self):
        self.isVol=0
        self.showDot = True
        self.showLine = True
        self.lastTask = self.measureVol
        if self.referencePixels is None:
            self.detectCircle()
        self.setTemporaryCursor(Qt.CrossCursor)

    def calcCurveLength(self,cpoint):
        num=len(cpoint)
        ans=0
        for i in range(num-1):
            dx=cpoint[i].x()-cpoint[i+1].x()
            dy=cpoint[i].y()-cpoint[i+1].y()
            ans+=math.sqrt(dx*dx+dy*dy)
        return ans

    def curveLength(self):
        self.isCurve=0
        self.showDot=True
        self.showLine=True
        self.lastTask=self.curveLength
        if self.referencePixels is None:
            self.detectCircle()
            # self.referenceReady = True
        self.setTemporaryCursor(Qt.CrossCursor)


    def calcArea(self,cpoint):
        num=len(cpoint)
        ans=0
        for i in range(1,num):
            ans+=float(cpoint[i].x()*cpoint[i-1].y()-cpoint[i].y()*cpoint[i-1].x())/2.0 #

        ans+=(cpoint[0].x()*cpoint[num-1].y()-cpoint[0].y()*cpoint[num-1].x())/2.0
        if ans<0:ans=-ans
        return ans

    def measureArea(self):
        self.isArea=0
        self.showDot = True
        self.showLine = True
        self.lastTask=self.measureArea
        if self.referencePixels is None:
            self.detectCircle()
            # self.actual = self.referenceTrueLength * 1.0 / self.referencePixels
            # self.referenceReady = True
        self.setTemporaryCursor(Qt.CrossCursor)

    def captureToQImage(self, scale=False):
        if self.scene() is not None:
            sw = self.scene().width()
            sh = self.scene().height()
            swh = sw/sh
            SystemLogger.log_info("sw:{} sh:{} w/h:{}".format(sw, sh, swh))
            image = QImage(sw, sh, QImage.Format_RGB32)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.LosslessImageRendering)
            self.scene().render(painter)
            painter.end()
        else:
            w = self.width()
            h = self.height()
            wh = w / h
            SystemLogger.log_info("w:{} h:{} w/h:{}".format(w, h, wh))
            image = QImage(w, h, QImage.Format_RGB32)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.LosslessImageRendering)
            self.scene().render(painter)
            painter.end()
        if not scale:
            return image

    def exportImage(self):
        for i in self.items():
            if isinstance(i, QGraphicsPixmapItem):
                return i.pixmap().toImage()

    def dotToline(self):
        self.showDot=True
        self.showLine=True
        self.isDotToLine=0
        self.lastTask=self.dotToline
        # self.referenceReady=True
        # self.referencePixels=25
        if self.referencePixels is None:
            self.detectCircle()
            # self.actual=self.referenceTrueLength*1.0/self.referencePixels
        self.setTemporaryCursor(Qt.CrossCursor)

    def noseLength(self):
        self.isNose=0
        # self.referenceReady=True
        self.lastTask = self.noseLength

        # self.referencePixels=25
        if self.referencePixels is None:
            self.detectCircle()
            # self.actual = self.referenceTrueLength * 1.0 / self.referencePixels
        #if self.referencePixels is None:
        self.drawNoseLength()

    def drawNoseLength(self):
        self.showDot=True
        self.showLine=True
        self.setTemporaryCursor(Qt.CrossCursor)

    def measureHLength(self, revert=False):
        # if not revert:
        #     self.setPen(lineColor=Qt.red, dotColor=Qt.blue)
        self.lastTask = self.measureHLength
        if self.referencePixels is None:
            self.detectCircle()
        self.setTemporaryCursor(Qt.CrossCursor)

    def measureVLength(self,  revert=False):
        # if not revert:
        #     self.setPen(lineColor=Qt.red, dotColor=Qt.blue)
        self.lastTask = self.measureVLength
        if self.referencePixels is None:
           self.detectCircle()
        self.setTemporaryCursor(Qt.CrossCursor)

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
        SystemLogger.log_info(angle)
        if display:
            self.result = "角度：{}°".format(str(round(angle, roundnum)))
            # self.paintText(str(round(angle, roundnum)), point=self.mapToScene(pointB))
            tmp = str(round(angle, roundnum)) + "°"
            self.paintText(tmp, point=self.mapToScene(pointB))
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
        self.referenceReady = False
        self.sigDetectCircle.emit(self.lastPic)
        return None

    def applyMat(self, mat):
        SystemLogger.log_info("Item get!")
        img_rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2BGRA)
        qimage = QtGui.QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0],
                              QtGui.QImage.Format_RGB32)
        pixmap = QPixmap.fromImage(qimage)
        item = QGraphicsPixmapItem(pixmap)
        self.fitview(item, renew=True, cleartask=False)
        self.referenceReady = True


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
        self.setTemporaryCursor(Qt.CrossCursor)
        self.dynamicLineSelection = True

    def drawAngleDynamic(self):
        if self.referencePixels is None:
            self.detectCircle()
        self.showDot = True
        self.showLine = True
        self.showRect = False
        self.lastTask = self.drawAngleDynamic
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

        scene.addRect(point.x() - int((point_size-1)/2), point.y() - int((point_size-1)/2), point_size, point_size, pen=self.dotPen)
        scene.addLine(point.x(), point.y() - line_size, point.x(), point.y() - int((point_size-1)/2), pen=self.linePen)
        scene.addLine(point.x(), point.y() + int((point_size-1)/2), point.x(), point.y() + line_size, pen=self.linePen)
        self.setScene(scene)

    def mountHorizontalLine(self, point):
        scene = self.scene()
        multi = self.getMultipier()
        line_size = int(40 / multi) + 1
        point_size = int(5 / multi) + 1
        scene.addRect(point.x() - int((point_size-1)/2), point.y() - int((point_size-1)/2), point_size, point_size, pen=self.dotPen)
        scene.addLine(point.x() - line_size, point.y(), point.x() - int((point_size-1)/2), point.y(), pen=self.linePen)
        scene.addLine(point.x() + int((point_size-1)/2), point.y(), point.x() + line_size, point.y(), pen=self.linePen)
        self.setScene(scene)

    # def returnPressed(self):
    #     if self.lastTask == self.selectArea and len(self.selectedPointList) == 2:
    #         SystemLogger.log_info("({},{}),({},{})".format(self.selectedPointList[0].x(), self.selectedPointList[0].y(), self.selectedPointList[1].x(), self.selectedPointList[1].y()))

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

    def paintLine(self, pointA, pointB, appendList=True, clear=False, storephase=False, boundaryRestrict=False, assertPt=True):
        if assertPt:
            if not (self.assertPoint(pointA) and self.assertPoint(pointB)):
                return
        if clear:
            if 0 < self.dynamicAngleSelectionPhase <= 2:
                last_scale = self.curScale
                # self.restorePhase()
                if round(last_scale, 2) != self.curScale:
                    SystemLogger.log_info(last_scale, self.curScale, "phase")
                    # self.scale(last_scale, last_scale)
            else:
                last_scale = self.curScale
                # self.fitview(self.lastPic, cleartask=False, renew=True)
                if round(last_scale, 2) != self.curScale:
                    SystemLogger.log_info(last_scale, self.curScale, "not phase")
                    # self.scale(last_scale, last_scale)
        if pointB.x() < 0 or pointB.x() > self.width() or pointB.y() < 0 or pointB.y() > self.height():
            SystemLogger.log_info("Warning: point ({},{}) exceeds boundary.".format(pointB.x(), pointB.y()))
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
            # self.fitview(self.lastPic, cleartask=False, renew=True)
            self.lineList.append(line)
            # self.lineList.append(lineItem)
            scene = self.scene()
            # for i in self.lineList:
            #     # scene.addLine(i, pen=self.linePen)
            self.lineItem = CustomedQGraphicsLineItem()
            self.lineItem.setLine(line)
            self.lineItem.setPen(self.linePen)
            scene.addItem(self.lineItem)
        else:

            # self.fitview(self.lastPic, cleartask=False, renew=True)
            # scene = self.scene()
            # for i in self.lineList:
            #     # scene.addLine(i, pen=self.linePen)
            #     self.lineItem = CustomedQGraphicsLineItem()
            #     self.lineItem.setLine(i)
            #     self.lineItem.setPen(self.linePen)
            #     scene.addItem(self.lineItem)
            # scene.addLine(line, pen=self.linePen)
            if self.lineItem is None:
                self.lineItem = CustomedQGraphicsLineItem()
                self.lineItem.setLine(line)
                self.lineItem.setPen(self.linePen)
                scene = self.scene()
                scene.addItem(self.lineItem)
            else:
                self.lineItem.setLine(line)
                self.lineItem.setPen(self.linePen)
            # scene.addItem(self.lineItem)
        # if len(self.volPoint)>1:
        #     for i in range(len(self.volPoint)-1):
        #         line = QLineF(self.volPoint[i].x(), self.volPoint[i].y(), self.volPoint[i+1].x(), self.volPoint[i+1].y())
        #         scene.addLine(line,pen=self.linePen)
        #
        # if len(self.areaPoints)>1:
        #     for i in range(len(self.areaPoints)-1):
        #         line = QLineF(self.areaPoints[i].x(), self.areaPoints[i].y(), self.areaPoints[i+1].x(), self.areaPoints[i+1].y())
        #         scene.addLine(line,pen=self.linePen)
        # if len(self.curvePoints)>1:
        #     for i in range(len(self.curvePoints)-1):
        #         line = QLineF(self.curvePoints[i].x(), self.curvePoints[i].y(), self.curvePoints[i + 1].x(),
        #                       self.curvePoints[i + 1].y())
        #         scene.addLine(line, pen=self.linePen)

        # self.setScene(scene)


    def restrictedPoint(self, point):
        x = min(max(point.x(), 0), self.width())
        y = min(max(point.y(), 0), self.height())
        cls = type(point)
        SystemLogger.log_info(cls(x, y))
        return cls(x, y)

    def assertPoint(self, point):
        if self.lastPic is None:
            return point.x() > 0 and point.y() > 0 and point.x() < self.width() and point.y() < self.height()
        else:
            return point.x() > 0 and point.y() > 0 and point.x() < self.lastPic.pixmap().width() and point.y() < self.lastPic.pixmap().height()

    def paintRect(self, pointA, pointB, fit=True, update=False):

        # self.fitview(self.lastPic, cleartask=False, renew=True)
        # scene = self.scene()
        # items = scene.items()
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
        scene = self.scene()
        items = scene.items()
        has_rect = False
        for i in items:
            if isinstance(i, QGraphicsRectItem):
                has_rect = True
                i.setRect(rectf)
        if not has_rect:
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
        multi = self.getMultipier()
        pixel_size = int(24 / multi) + 1
        txtItem = QGraphicsTextItem(text)
        x = point.x()
        y = point.y()
        if len(self.anglePoints) > 0:
            pt = self.anglePoints[0]
            min_x = pt.x()
            min_y = pt.y()
            max_x = pt.x()
            max_y = pt.y()
            for i in self.anglePoints:
                min_x = min(i.x(), min_x)
                max_x = max(i.x(), max_x)
                min_y = min(i.y(), min_y)
                max_y = max(i.y(), max_y)
            if min_y >= point.y():
                y -= pixel_size*4
            elif max_y <= point.y():
                y += pixel_size
            if min_x >= point.x():
                x -= pixel_size*6
            elif max_x >= point.x():
                x += pixel_size
        txtItem.setPos(x, y)
        txtItem.setDefaultTextColor(self.textPen.color())
        font = QFont()
        font.setPixelSize(pixel_size)
        txtItem.setFont(font)
        scene.addItem(txtItem)
        self.setScene(scene)

    def revert(self):
        self.selectedPointList = []
        self.lineList = []
        self.lineItem = None
        self.finishedTask = False
        self.volDone = False
        self.areaDone = False


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
            self.anglePoints = []
            self.lastTask()
        elif self.lastTask == self.measureHLength:
            self.mountHPoint = None
            self.lastTask(True)
        elif self.lastTask == self.measureVLength:
            self.mountVPoint = None
            self.lastTask(True)
        elif self.lastTask==self.noseLength:
            self.dynamicLineStartPoint=None
            self.nosePoints = []
            self.lastTask()
        elif self.lastTask==self.dotToline:
            self.dynamicLineStartPoint=None
            self.lastTask()
        elif self.lastTask==self.measureArea:
            self.lastTask()
        elif self.lastTask == self.measureVol:
            self.volPoint = []
            self.lastTask()
        elif self.lastTask==self.curveLength:
            self.lastTask()
        elif self.lastTask is not None:
            self.sigRevert.emit(self.lastTask)
            self.lastTask()

    def execLastTask(self):
        if self.lastTask is not None:
            self.lastTask()

    def restore(self, clearReference=True):
        self.selectedPointList = []
        self.lineList = []
        self.lineItem = None

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
        if clearReference:
            self.referencePixels = None
            self.referenceReady = False
            self.actual = 1

        self.currentCursor = Qt.ArrowCursor
        self.tempCursor = None
        self.applyStoredCursor()
        self.dynamicAngleSelectionPhase = -1
        self.anglePoints = []
        self.mountVPoint = None
        self.mountHPoint = None
        self.result = None

        #reprent the actual length of the every pixs

        # nose
        self.isNose=-1
        self.nosePoints=[]

        self.isDotToLine=-1
        self.dotLine=[]

        self.isArea=-1
        self.areaPoints=[]

        self.isCurve=-1
        self.curvePoints=[]

        self.isVol=-1
        self.volPoint=[]

        self.volDone = False
        self.areaDone = False


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
        # self.setPen(dotColor=dotColor, lineColor=lineColor, rectColor=rectColor, dotPenWidth=dotPenWidth,
        #             linePenWidth=linePenWidth, rectPenWidth=rectPenWidth)

    def setPen(self, dotColor=Qt.blue, lineColor=Qt.blue, rectColor=Qt.blue, textColor=Qt.blue,
               dotPenWidth=1, linePenWidth=2, rectPenWidth=2, textPenWidth=1, setColor=True):
        if self.scene() is not None:
            scene = self.scene()
            ref_h = 1080
            ref_w = 1920
            w = scene.width()
            h = scene.height()
            if w > h:
                ratio = w / ref_w
            else:
                ratio = h / ref_h
            width = 10*ratio
            SystemLogger.log_info("Set pen width:{} height:{} ratio:{} pen_width:{}".format(w, h, ratio, width))
            self.dotPen.setWidth(width)
            self.linePen.setWidth(width)
            self.rectPen.setWidth(width)
            self.textPen.setWidth(width)
        else:
            self.dotPen.setWidth(dotPenWidth)
            self.linePen.setWidth(linePenWidth)
            self.rectPen.setWidth(rectPenWidth)
            self.textPen.setWidth(textPenWidth)
        if setColor:
            self.dotPen.setColor(dotColor)
            self.linePen.setColor(lineColor)
            self.rectPen.setColor(rectColor)
            self.textPen.setColor(textColor)

    def getDotColor(self):
        return self.dotPen.color()

    def setDotColor(self, color):
        self.dotPen.setColor(color)
        scene = self.scene()
        if scene is not None:
            for i in scene.items():
                if isinstance(i, QGraphicsRectItem):
                    i.setPen(self.dotPen)
                    self.update()

    def getLineColor(self):
        return self.linePen.color()

    def setLineColor(self, color):
        self.linePen.setColor(color)
        scene = self.scene()
        if scene is not None:
            for i in scene.items():
                if isinstance(i, CustomedQGraphicsLineItem):
                    i.setPen(self.linePen)
                    self.update()

    def getRectColor(self):
        return self.rectPen.color()

    def setRectColor(self, color):
        self.rectPen.setColor(color)
        scene = self.scene()
        if scene is not None:
            for i in scene.items():
                if isinstance(i, QGraphicsRectItem):
                    i.setPen(self.rectPen)
                    self.update()

    def getTextColor(self):
        return self.textPen.color()

    def setTextColor(self, color):
        self.textPen.setColor(color)
        scene = self.scene()
        if scene is not None:
            for i in scene.items():
                if isinstance(i, QGraphicsTextItem):
                    i.setDefaultTextColor(color)
                    self.update()

    def getMultipier(self):
        return round(self.transform().m11(), 2)
    def getMiddlePoint(self,data):
        maxidx=0
        minidx=0
        for i in range(len(data)):
            if data[i].x()<data[minidx].x():
                minidx=i
            if data[i].x()> data[maxidx].x():
                maxidx=i
        point = QPoint(0.5*data[maxidx].x() + 0.5 * data[minidx].x() ,
                              0.5 * data[maxidx].y() + 0.5 * data[minidx].y())
        return point

    def mousePressEvent(self, QMouseEvent):
        try:
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
                        if self.dynamicRectSelection :
                            cursorPoint = self.restrictedPoint(QMouseEvent.pos())
                            if self.dynamicRectStartPoint is None:
                                self.dynamicRectStartPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                SystemLogger.log_info("Rect anchor point selected.")
                        elif self.lastTask==self.measureVol:
                            if not self.referenceReady:
                                return
                            cursorPoint=self.restrictedPoint(QMouseEvent.pos())
                            if self.isVol!=-1:
                                if self.volDone:
                                    ans = self.calcArea(self.volPoint)

                                    ans = ans * math.pi * 12.5 * 12.5 / self.referencePixelsArea
                                    middle_point = QPoint(0.5 * self.areaPoints[1].x() + 0.5 * self.areaPoints[0].x() + 20,
                                                          0.5 * self.areaPoints[1].y() + 0.5 * self.areaPoints[0].y() - 50)
                                    # middle_point=self.getMiddlePoint(self.areaPoints)
                                    self.result = "体积：{} mm³".format(str(round(float(ans), 2)))
                                    tmp = str(round(float(ans), 2)) + " mm³"
                                    self.paintText(tmp, middle_point)
                                    self.volPoint = []
                                    self.isVol = -1
                                    self.volDone=False
                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()
                                else:
                                    self.isVol+=1
                                    self.volPoint.append(self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y())))
                                    num=len(self.volPoint)
                                    if num>1:
                                        self.paintLine(self.volPoint[num-2],self.volPoint[num-1],clear=True,storephase=True)
                        elif self.lastTask==self.measureArea:
                            if not self.referenceReady:
                                return
                            cursorPoint=self.restrictedPoint(QMouseEvent.pos())
                            if self.isArea!=-1:
                                if self.areaDone:
                                    ans = self.calcArea(self.areaPoints)

                                    ans = ans * math.pi * 12.5 * 12.5 / self.referencePixelsArea
                                    middle_point = QPoint(0.5 * self.areaPoints[1].x() + 0.5 * self.areaPoints[0].x() + 20,
                                                          0.5 * self.areaPoints[1].y() + 0.5 * self.areaPoints[0].y() - 50)
                                    # middle_point = self.getMiddlePoint(self.areaPoints)
                                    self.result = "面积：{} mm²".format(str(round(float(ans), 2)))
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    tmp = str(round(float(ans), 2)) + " mm²"
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    self.paintText(tmp, middle_point)

                                    self.areaPoints = []
                                    self.isArea = -1
                                    self.areaDone=False
                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()

                                else:
                                    self.isArea+=1
                                    self.areaPoints.append(self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y())))
                                    num=len(self.areaPoints)
                                    if num>1:
                                        self.paintLine(self.areaPoints[num-2],self.areaPoints[num-1],clear=True,storephase=True)
                        elif self.lastTask==self.curveLength:

                            if not self.referenceReady:
                                return
                            cursorPoint=self.restrictedPoint(QMouseEvent.pos())

                            if self.isCurve!=-1:

                                if self.curveDone:
                                    ans=self.calcCurveLength(self.curvePoints)
                                    ans=ans*self.actual
                                    middle_point = QPoint(0.5 * self.curvePoints[1].x() + 0.5 * self.curvePoints[0].x() + 20,
                                                          0.5 * self.curvePoints[1].y() + 0.5 * self.curvePoints[0].y() - 50)
                                    self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    # middle_point = self.getMiddlePoint(self.areaPoints)
                                    tmp = str(round(float(ans), 2)) + " mm"
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    self.paintText(tmp, middle_point)
                                    self.curvePoints = []
                                    self.isCurve = -1
                                    self.curveDone = False
                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()

                                else:
                                    self.isCurve+=1
                                    self.curvePoints.append(self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y())))
                                    num=len(self.curvePoints)
                                    if num>1:
                                        self.paintLine(self.curvePoints[num-2],self.curvePoints[num-1],clear=True,storephase=True)

                        elif self.lastTask==self.noseLength:
                            if not self.referenceReady:
                                return
                            cursorPoint = self.restrictedPoint(QMouseEvent.pos())
                            if self.isNose!=-1:
                                if self.dynamicLineStartPoint is None:
                                    self.dynamicLineStartPoint=self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                    self.paintDot(self.dynamicLineStartPoint)
                                    self. nosePoints.append(self.dynamicLineStartPoint)
                                else:
                                    endpoint = self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y()))
                                    self.nosePoints.append(endpoint)
                                    self.paintDot(endpoint)
                                    self.paintLine(self.dynamicLineStartPoint,endpoint,clear=True,storephase=True)
                                    dx=self.nosePoints[0].x()-self.nosePoints[1].x()
                                    dy=self.nosePoints[0].y()-self.nosePoints[1].y()
                                    ans=dx*dx+dy*dy
                                    ans=math.sqrt(ans)
                                    # ans=ans*self.actual
                                    ans = ans * 1.0 / self.referencePixels * self.referenceTrueLength

                                    middle_point = QPoint(0.5 * self.nosePoints[1].x() + 0.5 * self.nosePoints[0].x()+20,
                                                          0.5 * self.nosePoints[1].y() + 0.5 * self.nosePoints[0].y()-50)
                                    self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    tmp = str(round(float(ans), 2)) + " mm"
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    self.paintText(tmp, middle_point)
                                    self.nosePoints=[]
                                    self.isNose=-1
                                    self.dynamicLineStartPoint=None

                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()
                        elif self.lastTask==self.dotToline:
                            if not self.referenceReady:
                                return
                            cursorPoint=self.restrictedPoint(QMouseEvent.pos())
                            if self.isDotToLine!=-1:
                                if self.dynamicLineStartPoint is None:
                                    self.dynamicLineStartPoint=self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y()))
                                    self.paintDot(self.dynamicLineStartPoint)
                                    self.dotLine.append(self.dynamicLineStartPoint)
                                else:
                                    if len(self.dotLine)==1:
                                        self.dotLine.append(self.mapToScene((QPoint(cursorPoint.x(),cursorPoint.y()))))
                                        self.paintLine(self.dynamicLineStartPoint,self.dotLine[1],clear=True,storephase=False)
                                        self.isDotToLine+=1
                                    elif len(self.dotLine)==2:
                                        SystemLogger.log_info(len(self.dotLine))
                                        self.dotLine.append(self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y())))
                                        self.paintDot(self.mapToScene(QPoint(cursorPoint.x(),cursorPoint.y())))
                                        if self.dotLine[0].x()!=self.dotLine[1].x():
                                            SystemLogger.log_info(self.dotLine)
                                            dy=self.dotLine[1].y()-self.dotLine[0].y()
                                            dx=self.dotLine[1].x()-self.dotLine[0].x()
                                            k=dy*1.0/dx
                                            A=k
                                            B=-1
                                            C=-k*self.dotLine[0].x()+self.dotLine[0].y()
                                            fz=A*self.dotLine[2].x()+B*self.dotLine[2].y()+C
                                            fm=math.sqrt(A*A+B*B)
                                            ans=math.fabs(fz)*1.0/fm
                                            ans = ans * self.actual
                                            middle_point = QPoint(
                                                0.5 * self.dotLine[1].x() + 0.5 * self.dotLine[0].x() + 20,
                                                0.5 * self.dotLine[1].y() + 0.5 * self.dotLine[0].y() - 50)
                                            self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                            # self.paintText(str(round(float(ans), 2)), middle_point)
                                            tmp = str(round(float(ans), 2)) + " mm"
                                            # self.paintText(str(round(float(ans), 2)), middle_point)
                                            self.paintText(tmp, middle_point)
                                            self.dotLine=[]
                                            self.isDotToLine=-1
                                            self.dynamicLineStartPoint=None
                                            self.unsetTemporaryCursor()
                                            self.sigTaskFinished.emit()
                                        else:
                                            ans=self.dotLine[2].x()-self.dotLine[0].x()
                                            ans=ans*self.actual
                                            # ans = ans*1.0/ self.referencePixels * self.referenceTrueLength
                                            middle_point = QPoint(
                                                0.5 * self.dotLine[1].x() + 0.5 * self.dotLine[0].x() + 20,
                                                0.5 * self.dotLine[1].y() + 0.5 * self.dotLine[0].y() - 50)
                                            self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                            # self.paintText(str(round(float(ans), 2)), middle_point)
                                            tmp = str(round(float(ans), 2)) + " mm"
                                            # self.paintText(str(round(float(ans), 2)), middle_point)
                                            self.paintText(tmp, middle_point)
                                            self.dotLine = []
                                            self.isDotToLine = -1
                                            self.dynamicLineStartPoint = None
                                            self.unsetTemporaryCursor()
                                            self.sigTaskFinished.emit()

                        elif self.dynamicLineSelection or 0 <= self.dynamicAngleSelectionPhase <= 2:
                            if not self.referenceReady:
                                return
                            cursorPoint = self.restrictedPoint(QMouseEvent.pos())
                            if self.dynamicLineStartPoint is None:
                                self.dynamicLineStartPoint = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                SystemLogger.log_info("Line anchor point selected.")
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
                                        SystemLogger.log_info(
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
                                    # self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    tmp = str(round(float(ans), 2)) + " mm"
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    self.paintText(tmp, middle_point)
                                    self.mountHPoint = None
                                    self.unsetTemporaryCursor()
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
                                    # self.paintText(str(round(float(ans), 2)), middle_point)
                                    tmp = str(round(float(ans), 2)) + " mm"
                                    self.paintText(tmp, middle_point)
                                    self.mountVPoint = None
                                    self.unsetTemporaryCursor()
                                    self.sigTaskFinished.emit()
                        else:
                            SystemLogger.log_info("Static point selected.")
                            if self.selectedPoint == -1:
                                self.setCurrentCursor(self.chooseCursor())
                            else:
                                cursorPoint = QMouseEvent.pos()
                                scenePos = self.mapToScene(QPoint(cursorPoint.x(), cursorPoint.y()))
                                self.storePoint(scenePos)
                elif QMouseEvent.button() == QtCore.Qt.RightButton:
                    if self.lineItem is not None:
                        scene = self.scene()
                        if scene is not None:
                            scene.removeItem(self.lineItem)
                    if self.volDone==False and self.isVol>-1:
                        self.volDone = True
                        num = len(self.volPoint)
                        if num >= 2:
                            self.paintLine(self.volPoint[0], self.volPoint[num - 1], clear=True, storephase=True)
                            ans = self.calcArea(self.volPoint)

                            ans = ans * math.pi * 12.5 * 12.5 / self.referencePixelsArea
                            middle_point = QPoint(0.5 * self.volPoint[1].x() + 0.5 * self.volPoint[0].x() + 20,
                                                  0.5 * self.volPoint[1].y() + 0.5 * self.volPoint[0].y() - 50)
                            ans=1.0/3*ans*float(self.inputDepth())
                            self.result = "体积：{} mm³".format(str(round(float(ans), 2)))
                            # middle_point = self.getMiddlePoint(self.areaPoints)
                            # self.paintText(str(round(float(ans), 2)), middle_point)
                            tmp = str(round(float(ans), 2)) + " mm³"
                            self.paintText(tmp, middle_point)
                            self.volPoint = []
                            self.isVol = -1
                            self.volDone = False
                            self.unsetTemporaryCursor()
                            self.sigTaskFinished.emit()
                            return

                    if self.areaDone==False and self.isArea>-1:
                        self.areaDone=True
                        num=len(self.areaPoints)
                        if num >= 2:
                            self.paintLine(self.areaPoints[0],self.areaPoints[num-1],clear=True,storephase=True)
                            ans = self.calcArea(self.areaPoints)

                            ans = ans * math.pi * 12.5 * 12.5 / self.referencePixelsArea
                            middle_point = QPoint(0.5 * self.areaPoints[1].x() + 0.5 * self.areaPoints[0].x() + 20,
                                                  0.5 * self.areaPoints[1].y() + 0.5 * self.areaPoints[0].y() - 50)
                            self.result = "面积：{} mm²".format(str(round(float(ans), 2)))
                            # self.paintText(str(round(float(ans), 2)), middle_point)
                            # middle_point = self.getMiddlePoint(self.areaPoints)
                            tmp = str(round(float(ans), 2)) + " mm²"
                            self.paintText(tmp, middle_point)
                            self.areaPoints = []
                            self.isArea = -1
                            self.areaDone = False
                            self.unsetTemporaryCursor()
                            self.sigTaskFinished.emit()
                            return
                    if self.curveDone==False and self.isCurve>-1:
                        self.curveDone=True
                        num=len(self.curvePoints)
                        if num >= 2:
                        # self.paintLine(self.curvePoints[0],self.curvePoints[num-1],clear=True,storephase=True)
                            self.paintLine(self.curvePoints[0],self.curvePoints[1],clear=True,storephase=True)
                            ans = self.calcCurveLength(self.curvePoints)
                            ans = ans * self.actual
                            middle_point = QPoint(0.5 * self.curvePoints[1].x() + 0.5 * self.curvePoints[0].x() + 20,
                                                  0.5 * self.curvePoints[1].y() + 0.5 * self.curvePoints[0].y() - 50)
                            self.result = "距离：{} mm".format(str(round(float(ans), 2)))
                            # self.paintText(str(round(float(ans), 2)), middle_point)
                            tmp = str(round(float(ans), 2)) + " mm"
                            self.paintText(tmp, middle_point)
                            self.curvePoints = []
                            self.isCurve = -1
                            self.curveDone = False
                            self.unsetTemporaryCursor()
                            self.sigTaskFinished.emit()
                            return
                    self.revert()
                    self.sigRightClicked.emit()
        except Exception as e:
            SystemLogger.log_error("QGraphicsView_MousePressEvent Error"+str(e))

    def hasPic(self):
        return self.lastPic is not None

    def mouseReleaseEvent(self, QMouseEvent):
        try:
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
        except Exception as e:
            SystemLogger.log_error("QGraphicsView_MouseReleaseEvent Error"+str(e))

    def mouseMoveEvent(self, QMouseEvent):
        try:
            if self.attr == "Picture":


                if len(self.curvePoints)>0 and self.curveDone==False:
                    num = len(self.curvePoints)
                    self.paintLine(self.curvePoints[num - 1], self.mapToScene(QMouseEvent.pos()), clear=True, appendList=False)
                if len(self.volPoint)>0 and self.volDone==False:
                    num = len(self.volPoint)
                    self.paintLine(self.volPoint[num - 1], self.mapToScene(QMouseEvent.pos()), clear=True,
                                   appendList=False)

                if len(self.areaPoints)>0 and self.areaDone==False:
                    num=len(self.areaPoints)
                    self.paintLine(self.areaPoints[num-1],self.mapToScene(QMouseEvent.pos()),clear=True, appendList=False)
                if len(self.nosePoints)==1 and self.dynamicLineStartPoint is not None:
                    self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QMouseEvent.pos()), clear=True, appendList=False)
                if len(self.dotLine)==1 and self.dynamicLineStartPoint is not None:
                    self.paintLine(self.dynamicLineStartPoint,self.mapToScene(QMouseEvent.pos()),clear=True, appendList=False)

                if self.dynamicRectSelection and self.dynamicRectStartPoint is not None and self.pressed:
                    self.paintRect(self.dynamicRectStartPoint, self.mapToScene(QMouseEvent.pos()))
                elif self.dynamicLineSelection and self.dynamicLineStartPoint is not None:
                    self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QMouseEvent.pos()), clear=True, appendList=False)
                elif -1 < self.dynamicAngleSelectionPhase <= 2 and self.dynamicLineStartPoint is not None:
                    self.paintLine(self.dynamicLineStartPoint, self.mapToScene(QMouseEvent.pos()), clear=True, appendList=False)
                if self.lastMousePos is not None and self.pressed and not self.dynamicRectSelection:
                    mouseDelta = self.mapToScene(QMouseEvent.pos()) - self.mapToScene(self.lastMousePos)
                    self.moveScene(mouseDelta)
                    self.lastMousePos = QMouseEvent.pos()
                QGraphicsView.mouseMoveEvent(self,QMouseEvent)
        except Exception as e:
            SystemLogger.log_error("QGraphicsView_MouseMoveEvent Error"+str(e))

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
        self.setPen(setColor=False)


    def clear(self):
        self.lastTask = None
        scene = QGraphicsScene()
        self.setScene(scene)
        self.lastScale = self.getMultipier()
        self.curScale = self.getMultipier()
        self.repaint()