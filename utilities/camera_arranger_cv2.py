from PyQt5.QtCore import QObject, pyqtSignal

from camera_thread import CameraThread

# TODO 这个类还不能使用！待以后有需求再做接口

class CameraArrangerCv2(QObject):
    sigReadyToSave = pyqtSignal()

    def __init__(self, parent=None):
        super(CameraArrangerCv2, self).__init__(parent)

    def pauseCapture(self):
        if self.cam_thread_front is not None:
            self.cam_thread_front.setPs()

    def resumeCapture(self):
        if self.cam_thread_front is not None:
            self.cam_thread_front.unsetPs()


    def startCaptureImage(self):
        self.attr = "Video"
        if not self.isCapturing:
            if self.cam_thread_front is None:
                self.cam_thread_front = CameraThread(0)
                self.cam_thread_front.sigFrame.connect(self.showCameraFront)
                self.cam_thread_front.sigStopped.connect(self.enableCameraButton)
                self.sigCaptureResume.connect(self.cam_thread_front.unsetPs)
                self.sigCaptureStop.connect(self.cam_thread_front.setPs)
                self.cam_thread_front.start()
            if self.cam_thread_left is None:
                self.cam_thread_left = CameraThread(1)
                self.cam_thread_left.sigFrame.connect(self.showCameraLeft)
                self.cam_thread_left.sigStopped.connect(self.enableCameraButton)
                self.sigCaptureResume.connect(self.cam_thread_left.unsetPs)
                self.sigCaptureStop.connect(self.cam_thread_left.setPs)
                self.cam_thread_left.start()
            if self.cam_thread_right is None:
                self.cam_thread_right = CameraThread(2)
                self.cam_thread_right.sigFrame.connect(self.showCameraRight)
                self.cam_thread_right.sigStopped.connect(self.enableCameraButton)
                self.sigCaptureResume.connect(self.cam_thread_right.unsetPs)
                self.sigCaptureStop.connect(self.cam_thread_right.setPs)
                self.cam_thread_right.start()
            if self.cam_thread_front is not None and self.cam_thread_left is not None and self.cam_thread_right is not None:
                self.sigCaptureResume.emit()
            self.getCameraButton().setEnabled(False)
            self.getCameraButton().repaint()
            self.getCameraButton().clicked.disconnect(self.startCaptureImage)
            self.getCameraButton().clicked.connect(self.stopCapture)
            self.getCameraButton().setText("拍摄")
            self.getPictureButton().setEnabled(False)
            self.getPictureButton().repaint()
            # self.getCameraView().sigLeave.connect(self.pauseCapture)
            # self.getCameraView().sigEnter.connect(self.resumeCapture)
            # self.cam_thread_front.setPs()
            stackedWidget_camera = self.getCameraStackedWidget()
            stackedWidget_camera.setCurrentIndex(1)
            self.isCapturing = True
        else:
            stackedWidget = self.getStackedWidget()
            stackedWidget.setCurrentIndex(2)
            stackedWidget_camera = self.getCameraStackedWidget()
            stackedWidget_camera.setCurrentIndex(1)


    def stopCapture(self):
        self.isCapturing = False
        self.attr = "Picture"
        # self.cam_thread_front.mutex.lock()
        self.getCameraButton().setEnabled(False)
        self.getCameraButton().repaint()
        self.getCameraButton().clicked.disconnect(self.stopCapture)
        self.getCameraButton().clicked.connect(self.startCaptureImage)
        self.getCameraButton().setText("开始采集")
        self.sigCaptureStop.emit()
        self.saveImage()
        # self.cam_thread_front.mutex.unlock()
        # self.getCameraView().sigEnter.disconnect(self.resumeCapture)
        # self.viewMutex.lock()
        # self.getCameraView().setAttr("Picture")
        # self.viewMutex.unlock()

        # self.restoreScene()
        self.getPictureButton().setEnabled(True)

    # V1 是用cv2拍摄的 v2是QCamera

    def stopCaptureWithOutSaving(self):
        self.isCapturing = False
        self.attr = "Picture"
        # self.cam_thread_front.mutex.lock()
        self.getCameraButton().setEnabled(False)
        self.getCameraButton().repaint()
        self.getCameraButton().clicked.disconnect(self.stopCapture)
        self.getCameraButton().clicked.connect(self.startCaptureImage)
        self.getCameraButton().setText("开始采集")
        self.sigCaptureStop.emit()
        # self.cam_thread_front.mutex.unlock()
        # self.getCameraView().sigEnter.disconnect(self.resumeCapture)
        # self.viewMutex.lock()
        # self.getCameraView().setAttr("Picture")
        # self.viewMutex.unlock()

        # self.restoreScene()
        self.getPictureButton().setEnabled(True)


    def showCameraFront(self, framecount:int):
        # self.viewMutexFront.lock()
        if self.cam_thread_front is not None:
            # self.cam_thread_front.mutex.lock()
            self.high_res_image_c = self.cam_thread_front.img

            # self.cam_thread_front.mutex.unlock()
            # SystemLogger.log_info("Got frame:{}".format(framecount))
            if self.lastFrameTime_c is None:
                self.lastFrameTime_c = time.time()
            else:
                delta = time.time() - self.lastFrameTime_c
                if delta >= 1 / FPS_MINIMUM / 2:
                    self.showPictureFront(self.high_res_image_c.scaledToWidth(360), attr=self.attr)
                    self.lastFrameTime_c = time.time()
                else:
                    CameraLogger.log_info("ShowCamFront Dropping Excessive frame.")
            # if framecount > 20:
            if self.isCapturing:
                self.getCameraButton().setEnabled(True)
        else:
            SystemLogger.log_info("Cam Front:",self.cam_thread_front is not None, self.nextPic)
        # self.viewMutexFront.unlock()

    def showCameraLeft(self, framecount:int):
        # self.viewMutexLeft.lock()
        if self.cam_thread_left is not None:
            # self.cam_thread_left.mutex.lock()
            self.high_res_image_l = self.cam_thread_left.img
            # self.cam_thread_left.mutex.unlock()
            # SystemLogger.log_info("Got frame:{}".format(framecount))
            if self.lastFrameTime_l is None:
                self.lastFrameTime_l = time.time()
            else:
                delta = time.time() - self.lastFrameTime_l
                if delta >= 1 / FPS_MINIMUM / 2:
                    self.showPictureLeft(self.high_res_image_l.scaledToWidth(360), attr=self.attr)
                    self.lastFrameTime_l = time.time()
                else:
                    CameraLogger.log_info("ShowCamLeft Dropping Excessive frame.")
            # if framecount > 20:
            if self.isCapturing:
                self.getCameraButton().setEnabled(True)
        else:
            SystemLogger.log_info("Cam Left:",self.cam_thread_left is not None, self.nextPic)
        # self.viewMutexLeft.unlock()

    def showCameraRight(self, framecount:int):
        # self.viewMutexRight.lock()
        if self.cam_thread_right is not None:
            # self.cam_thread_right.mutex.lock()
            self.high_res_image_r = self.cam_thread_right.img
            # self.cam_thread_right.mutex.unlock()
            # SystemLogger.log_info("Got frame:{}".format(framecount))
            if self.lastFrameTime_r is None:
                self.lastFrameTime_r = time.time()
            else:
                delta = time.time() - self.lastFrameTime_r
                if delta >= 1 / FPS_MINIMUM / 2:
                    self.showPictureRight(self.high_res_image_r.scaledToWidth(360), attr=self.attr)
                    self.lastFrameTime_r = time.time()
                else:
                    CameraLogger.log_info("ShowCamRight Dropping Excessive frame.")
            # if framecount > 20:
            if self.isCapturing:
                self.getCameraButton().setEnabled(True)
        else:
            SystemLogger.log_info("Cam Right:",self.cam_thread_right is not None, self.nextPic)
        # self.viewMutexRight.unlock()

    def showPictureLeft(self, qimage, attr="Picture"):
        viewContainer = self.getImageFrameLeft()
        viewContainer.setAttr(attr)
        scene = QGraphicsScene()
        pixmap = QPixmap.fromImage(qimage)
        item_new = QGraphicsPixmapItem(pixmap)
        self.fitView(viewContainer, item_new, renew=True)

    def showPictureRight(self, qimage, attr="Picture"):
        viewContainer = self.getImageFrameRight()
        viewContainer.setAttr(attr)
        scene = QGraphicsScene()
        pixmap = QPixmap.fromImage(qimage)
        item_new = QGraphicsPixmapItem(pixmap)
        self.fitView(viewContainer, item_new, renew=True)

    def showPictureFront(self, qimage, attr="Picture"):
        viewContainer = self.getImageFrameFront()
        viewContainer.setAttr(attr)
        scene = QGraphicsScene()
        pixmap = QPixmap.fromImage(qimage)
        item_new = QGraphicsPixmapItem(pixmap)
        self.fitView(viewContainer, item_new, renew=True)

    def saveImage(self):
        image_L = self.high_res_image_l
        image_R = self.high_res_image_r
        image_C = self.high_res_image_c
        SystemLogger.log_info(image_L, image_R, image_C)
        dateobj = datetime.datetime.now().date()
        y = dateobj.year
        m = dateobj.month
        d = dateobj.day
        ymd = "{}{}{}".format(y,m,d)
        timeobj = datetime.datetime.now().time()
        hms = "{0:02d}{1:02d}{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
        name = self.currentUser["姓名"]
        suffix = "png"
        filename_L = "{}_{}_{}_{}.{}".format(name, ymd, hms, "L", suffix)
        filename_R = "{}_{}_{}_{}.{}".format(name, ymd, hms, "R", suffix)
        filename_C = "{}_{}_{}_{}.{}".format(name, ymd, hms, "C", suffix)
        try:
            if "姓名" in self.currentUser.keys():
                hint_str = self.currentUser["姓名"]
                path_str = "c:/ceju/" + hint_str + "/photo/"
                if not os.path.exists(path_str):
                    os.makedirs(path_str)
                if image_L is not None:
                    image_L.save(os.path.join(path_str, filename_L))
                if image_R is not None:
                    image_R.save(os.path.join(path_str, filename_R))
                if image_C is not None:
                    image_C.save(os.path.join(path_str, filename_C))
                self.saveImageSuccess()
        except Exception as e:
            SystemLogger.log_info(e)
            self.error(e)
