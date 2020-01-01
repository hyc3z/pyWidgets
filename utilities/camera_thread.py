import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import cv2
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsPixmapItem
import time
from fetch_thread import FetchThread

class CameraThread(QThread):


    sigFrame = pyqtSignal(int)
    sigStopped = pyqtSignal()

    def __init__(self):
        super(QThread, self).__init__()
        self.img = None
        self.mutex = QMutex()
        self.nextFrm = QMutex()
        self.setTerminationEnabled(True)
        self.framecount=0
        self.brk = 0
        self.ps = 0
        self.stopcount = 0
          # 创建内置摄像头变量
        self.fetchThread = FetchThread()
        self.fetchThread.sigFrame.connect(self.getNextFrame)


    def sigterm(self):
        self.brk = 1
        self.ps = 1
        self.fetchThread.setTerminationEnabled(True)
        self.fetchThread.terminate()
        self.fetchThread.wait()
        self.fetchThread.deleteLater()
        return True


    def run(self):
        #线程相关的代码
        # 抓取摄像头视频图像
        while not self.fetchThread.isRunning():
            self.fetchThread.start()
            self.wait(1000)


    def setPs(self):
        self.ps = 1


    def unsetPs(self):
        self.ps = 0

    def getNextFrame(self, img):
        if self.ps == 0:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            qimage = QtGui.QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0],
                                  QtGui.QImage.Format_RGB32)
            self.mutex.lock()
            self.img = qimage
            self.mutex.unlock()
            self.sigFrame.emit(self.framecount)
        else:
            self.sigStopped.emit()
        # if self.ps != 1:
        # print("framesent:", self.framecount)

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    thread = CameraThread()
    thread.start()
    sys.exit(app.exec_())