import csv
import os

import cv2
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from logger import SystemLogger


class CircleDetector(QObject):

    sigLength = pyqtSignal(float)
    sigArea = pyqtSignal(float)
    # sigItem = pyqtSignal(QGraphicsPixmapItem)
    sigFinish = pyqtSignal(np.ndarray)
    sigReferenceNotFound = pyqtSignal()


    def loadData(self):
        if os.path.exists("ReferenceData.csv"):
            f = open("ReferenceData.csv", "r")
            reader = csv.DictReader(f)
            for i in reader:
                self.minR=int(i['minR'])
                self.maxR=int(i['maxR'])
                self.actSize=float(i['actSize'])
            f.close()

        else:
            self.minR=100
            self.maxR=150
            self.actSize=15.0

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

    def CannyThreshold(self,img):
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lowThreshold = 48
        max_lowThreshold = 100
        ratio = 3
        kernel_size = 3
        detected_edges = cv2.GaussianBlur(gray, (3, 3), 0)
        detected_edges = cv2.Canny(detected_edges, lowThreshold, lowThreshold * ratio, apertureSize=kernel_size)
        dst = cv2.bitwise_and(img, img, mask=detected_edges)
        cv2.imshow('canny demo', dst)
        cv2.waitKey(0)
        return dst

    def detectCircle(self, pixmapItem):
        # self.sigPreparing.emit()
        try:
            self.loadData()
            mat = self.convertToMat(pixmapItem)
            gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
            eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')  # 人眼
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)

            sx = 10000
            sy = 0
            symin = 100000
            h = 0
            w = 0
            flag = 0
            for (ex, ey, ew, eh) in eyes:
                sx = min(sx, ex)
                sy = max(sy, ey)
                symin = min(sy, symin)
                h = max(h, eh)
                w = max(w, ew)
                if (eh > 200 or ew > 200): flag = 1
                # mat = cv2.rectangle(mat, (ex, ey), (ex + ew, ey + eh), (250, 0, 0), 5)

            yy = np.shape(mat)[1]
            xx = np.shape(mat)[0]

            sh = max(symin - 3 * h, 0)
            xh = min(sy + 2 * h, xx)
            # zw=sx
            # yw=min(sx+3*w,yy)
            deltax = 0
            deltay = 0

            if flag == 1 and len(eyes) > 1:

                # roi = img[sh:xh, zw:yw]
                roi = mat[sh:xh, 0:yy]
                # cv2.imwrite("g:/test.jpg",roi)
                deltax = 0
                deltay = sh
                gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
            else:
                deltay = 0
                deltax = 0
                gray = cv2.cvtColor(mat, cv2.COLOR_RGB2GRAY)

            SystemLogger.log_info("开始圆检测",self.minR,self.maxR)
            circle1 = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 0.5, 3000, param1=100, param2=30, minRadius=self.minR,
                                       maxRadius=self.maxR)
            if circle1 is not None:
                circles_orig = circle1[0, :, :]
                # circles = np.uint16(np.around(circles))
                print(circles_orig)
                circles = np.uint16(np.around(circles_orig))

                for i in circles[:]:
                    cv2.circle(mat, (deltax + i[0], deltay + i[1]), i[2], (255, 0, 0), 1)
                    cv2.circle(mat, (deltax + i[0], deltay + i[1]), 2, (255, 0, 255), 2)
                    cv2.rectangle(mat, (deltax + i[0] - i[2], deltay + i[1] + i[2]), (deltax + i[0] + i[2], deltay + i[1] - i[2]), (255, 255, 0), 1)

                    # cv2.circle(gray, ( i[0],  i[1]), i[2], (255, 0, 0), 2)
                    # cv2.circle(gray, (i[0],  i[1]), 2, (255, 0, 255), 10)
                    # cv2.rectangle(gray, ( i[0] - i[2], i[1] + i[2]),
                    #               ( i[0] + i[2],  i[1] - i[2]), (255, 255, 0), 5)
                    # cv2.imwrite("g:/test2.jpg", gray)
                    true_radius = circles_orig[0][2]
                    SystemLogger.log_info('半径为', true_radius)
                    Length = true_radius * 2
                    # self.sigPreparingFinished.emit()
                    # 平方毫米
                    referencePixelsArea = math.pi * true_radius * true_radius
                    # actualArea = math.pi * self.referencePixels * self.referencePixels / self.referencePixelsArea
                    # item = self.convertFromMat(mat)
                    self.sigLength.emit(Length)
                    SystemLogger.log_info("Length emitted.")
                    self.sigArea.emit(referencePixelsArea)
                    SystemLogger.log_info("Area emitted.")
                    self.sigFinish.emit(mat)
                    SystemLogger.log_info("Mat emitted.")
                    return
            else:
                self.sigReferenceNotFound.emit()
        except Exception as e:
            SystemLogger.log_error(e)
            self.sigReferenceNotFound.emit()
