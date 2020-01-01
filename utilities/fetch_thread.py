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

    def __init__(self):
        super(QThread, self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.img = None
        self.falsecount = 0

    def run(self):
        #线程相关的代码
        # 抓取摄像头视频图像
        while True:
            ret, img = self.cap.read()
            if ret:
                self.img = img
                self.sigFrame.emit(self.img)
            else:
                self.falsecount += 1
                print("Capture Err:", self.falsecount)
                print("Restarting capture...")
                if self.cap.isOpened():
                    self.cap.release()
                    self.cap.open(0)
                else:
                    self.cap.open(0)

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    thread = FetchThread()
    thread.start()
    sys.exit(app.exec_())