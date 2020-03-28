import sys

import numpy
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsPixmapItem
import time
from logger import CameraLogger

FPS_MINIMUM = 10
FPS_RECORD_HISTORY = 5
FRAME_TIME_MAXIMUM = 0.5
FRAME_RECORD_HISTORY = 5
DOWNSAMPLING_FACTOR = 0.9036020036098448
DEFAULT_WIDTH = 3840
DEFAULT_HEIGHT = 2160
class FetchThread(QThread):


    INT_MAX = 2147483647
    sigFrame = pyqtSignal(numpy.ndarray)
    sigFail = pyqtSignal(int)

    def __init__(self, capnum=0):
        super(QThread, self).__init__()
        self.capnum = capnum
        self.cap = cv2.VideoCapture(capnum)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, DEFAULT_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DEFAULT_HEIGHT)
        # real_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # real_w =int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # real_h = 1944
        # real_w = 2592
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, real_w)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, real_h)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        self.img = None
        self.falsecount = 0
        self.successLastTime = True
        self.clock = 0
        self.fps = 100
        self.frametime = 0
        self.fps_trace = []
        self.frametime_trace = []
        self.total_frame_time = 0
        self.intended_width = DEFAULT_WIDTH
        self.intended_height = DEFAULT_HEIGHT

    def run(self):
        #线程相关的代码
        # 抓取摄像头视频图像
        while True:
            if len(self.fps_trace) == FPS_RECORD_HISTORY and sum(self.fps_trace) / FPS_RECORD_HISTORY < FPS_MINIMUM \
                    and max(self.frametime_trace) > FRAME_TIME_MAXIMUM:
                warn = "WARNING: camera {} resolution too high, scaling".format(self.capnum)
                CameraLogger.log_warning(warn)
                fps_traceback_info = "FPS traceback {}".format(self.fps_trace)
                frametime_traceback_info = "Frametime traceback {}".format(self.frametime_trace)
                CameraLogger.log_info(fps_traceback_info)
                CameraLogger.log_info(frametime_traceback_info)
                self.intended_height *= DOWNSAMPLING_FACTOR
                self.intended_width *= DOWNSAMPLING_FACTOR
                CameraLogger.log_info("Intended height:{}, intended width:{}".format(self.intended_height,self.intended_width))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.intended_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.intended_height)
                self.fps_trace = []
            delta_time = time.time()
            ret, img = self.cap.read()
            delta_time_1 = time.time()
            self.frametime = delta_time_1-delta_time
            self.clock += self.frametime
            self.total_frame_time += self.frametime
            self.fps += 1
            if self.clock > 1:
                self.clock -= 1
                info = "cam:{} fps:{} expected fps:{} height:{} width:{} avg frame time:{}".format(
                    self.capnum,
                    self.fps,
                    self.cap.get(5),
                    int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    self.total_frame_time/self.fps)
                CameraLogger.log_info(info)
                if len(self.fps_trace) >= FPS_RECORD_HISTORY:
                    self.fps_trace.pop(0)
                self.fps_trace.append(self.fps)
                if len(self.frametime_trace) >= FRAME_RECORD_HISTORY:
                    self.frametime_trace.pop(0)
                self.frametime_trace.append(self.total_frame_time/self.fps)
                self.total_frame_time = 0
                self.fps = 0
            if ret:
                self.img = img
                self.sigFrame.emit(self.img)
                self.successLastTime = True
            else:
                self.falsecount += 1
                if self.successLastTime:
                    self.successLastTime = False
                    self.sigFail.emit(self.capnum)
                    errstr = "Capture {} Err, last time it worked.".format(self.capnum)
                    CameraLogger.log_error(errstr)
                    restart_info = "Camera {} restarting capture...".format(self.capnum)
                    CameraLogger.log_info(restart_info)
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