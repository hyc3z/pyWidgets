import sys

import numpy
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsPixmapItem
import time

class FetchThread(QThread):


    sigFrame = pyqtSignal(numpy.ndarray)
    sigFail = pyqtSignal(int)

    def __init__(self, capnum=0):
        super(QThread, self).__init__()
        self.capnum = capnum
        self.cap = cv2.VideoCapture(capnum)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 5000)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 5000)
        real_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        real_w =int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, real_w)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, real_h)
        self.img = None
        self.falsecount = 0
        self.successLastTime = True

    def run(self):
        #线程相关的代码
        # 抓取摄像头视频图像
        while True:
            ret, img = self.cap.read()
            if ret:
                self.img = img
                self.sigFrame.emit(self.img)
                self.successLastTime = True
            else:
                self.falsecount += 1
                if self.successLastTime:
                    self.successLastTime = False
                    self.sigFail.emit(self.capnum)
                # print("Capture {} Err:".format(self.capnum), self.falsecount)
                # print("Restarting capture...")
                if self.cap.isOpened():
                    self.cap.release()
                    self.cap.open(self.capnum)
                else:
                    self.cap.open(self.capnum)

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    thread = FetchThread()
    thread.start()
    sys.exit(app.exec_())