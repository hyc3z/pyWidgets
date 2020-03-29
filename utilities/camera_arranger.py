import os
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraViewfinderSettings, QImageEncoderSettings, QMultimedia, \
    QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QMessageBox, QPushButton, QGridLayout

from source.logger import SystemLogger, CameraLogger


class CameraArranger(QObject):

    sigReadyToSave = pyqtSignal()
    
    def __init__(self, parent=None):
        super(CameraArranger, self).__init__(parent)
        self.cam_v2_lists = []
        # QPushButton
        self.button = None
        self.wait_dialog = None
        # QGridLayout
        self.display_layout = None
        self.display_column = 2
        self.error_count = 0

    def bindReusableButton(self, reusable_button):
        if isinstance(reusable_button, QPushButton):
            self.button = reusable_button
            self.button.clicked.connect(self.startCaptureImage_V2)
        else:
            SystemLogger.log_error("Bind button with camera arranger failed!")

    def setLayout(self, display_layout:QGridLayout, column_count=2):
        self.display_layout = display_layout
        self.display_column = column_count

    def checksum(self):
        if self.image_saved_count + self.error_count == len(self.cam_v2_lists):
            for i in self.cam_v2_lists:
                i[0].stop()
            if self.wait_dialog is not None:
                self.wait_dialog.close()
            self.saveImageInfo(self.image_saved_count, self.error_count)

    def startCaptureImage_V2(self, checked=False, reusable_button=None):
        if reusable_button is None:
            button = self.button
        else:
            button = reusable_button
        for i in self.cam_v2_lists:
            # i: [QCamera, QCameraViewFinder, QCameraImageCapture]
            i[0].start()
        if button is not None:
            button.setEnabled(False)
            button.repaint()
            button.clicked.disconnect(self.startCaptureImage_V2)
            button.clicked.connect(self.stopCapture_V2)
            button.setText("拍摄")
            button.setEnabled(True)
            button.repaint()

    def initialize(self, codec="png", resolution="max", camera_assert_count=3):
        self.online_webcams = QCameraInfo.availableCameras()
        cameracount = len(self.online_webcams)
        if cameracount < camera_assert_count:
            SystemLogger.log_warning("Camera count < {}! Current cameras online:{}".format(camera_assert_count,cameracount))
        if self.display_layout is None:
            SystemLogger.log_error("Camera arranger initialization failed, no display layout specified.")
            return
        self.cam_v2_lists = []
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        for i in range(cameracount):
            camera_vf = QCameraViewfinder()
            camera_vf.setSizePolicy(sizePolicy)
            camera_layout = self.display_layout
            camera_layout.addWidget(camera_vf, int(i/self.display_column), i % self.display_column)
            cam = QCamera(self.online_webcams[i])
            cam.load()
            supported_resolutions = cam.supportedViewfinderResolutions()
            cam.setViewfinder(camera_vf)
            vf_setting = QCameraViewfinderSettings()
            if resolution == "max":
                vf_setting.setResolution(supported_resolutions[-1])
            elif resolution == "min":
                vf_setting.setResolution(supported_resolutions[0])
            elif isinstance(resolution, QSize):
                vf_setting.setResolution(resolution)
            cam.setCaptureMode(QCamera.CaptureStillImage)
            cam.error.connect(lambda: self.cameraAlert(cam.errorString()))
            cam.setViewfinderSettings(vf_setting)
            imageSettings = QImageEncoderSettings()
            imageSettings.setCodec(codec)
            imageSettings.setQuality(QMultimedia.VeryHighQuality)
            if resolution == "max":
                imageSettings.setResolution(supported_resolutions[-1])
            elif resolution == "min":
                imageSettings.setResolution(supported_resolutions[0])
            elif isinstance(resolution, QSize):
                imageSettings.setResolution(resolution)
            SystemLogger.log_info("Camera {} resolution {}".format(self.online_webcams[i].description(),imageSettings.resolution()))
            capture = QCameraImageCapture(cam)
            capture.error.connect(self.captureError)
            capture.setEncodingSettings(imageSettings)
            capture.setCaptureDestination(QCameraImageCapture.CaptureToFile)
            capture.imageSaved.connect(self.imageSaved)
            self.cam_v2_lists.append([cam, camera_vf, capture])
            
    def captureError(self, id, err, str):
        SystemLogger.log_error("Capture error {} {} {}".format(id, err, str))
        self.error_count += 1
        self.checksum()

    def cameraAlert(self, s):
        """
        This handle errors and displaying alerts.
        """
        sender = self.sender()
        CameraLogger.log_error("Camera error: ",s)

    def stopCapture_V2(self,checked=False, reusable_button=None, wait_for_saving=True):
        self.error_count = 0
        if reusable_button is None:
            button = self.button
        else:
            button = reusable_button
        if button is not None:
            button.setEnabled(False)
            button.repaint()
        if wait_for_saving:
            self.wait_dialog =QMessageBox(QMessageBox.Information, "正在处理图片……", "正在处理图片，请稍候……", QMessageBox.Yes)
            # confirmError.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.wait_dialog.button(QMessageBox.Yes).setText("确认")
            self.wait_dialog.setStyleSheet(
                "QPushButton {"
                " font: bold 24px;"
                "padding-left: 3ex;"
                "padding-right: 3ex;"
                "padding-top: 1ex;"
                "padding-bottom: 1ex;"
                "margin-left:0px;"
                "}"
                "QLabel { font:24px}"
            )
            self.wait_dialog.setModal(True)
            self.wait_dialog.show()
            self.sigReadyToSave.emit()
        if button is not None:
            button.clicked.disconnect(self.stopCapture_V2)
            button.clicked.connect(self.startCaptureImage_V2)
            button.setText("开始采集")
            button.setEnabled(True)

    def imageSaved(self, id, filename):
        self.image_saved_count += 1
        self.checksum()

    def saveImage_V2(self, path_str, name="image", time_format="YMDhms", join_char="_", position_prefix=None):
        if position_prefix is None:
            position_prefix = []
        self.image_saved_count = 0
        dateobj = datetime.now().date()
        format_prefix = []
        y = dateobj.year
        m = dateobj.month
        d = dateobj.day
        ymd = "{0:02d}{1:02d}{2:02d}".format(y,m,d)
        timeobj = datetime.now().time()
        hms = "{0:02d}{1:02d}{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
        format_prefix.append(name)
        if "YMD" in time_format:
            format_prefix.append(ymd)
        if "hms" in time_format:
            format_prefix.append(hms)
        file_str = join_char.join(format_prefix)
        try:
            if not os.path.exists(path_str):
                os.makedirs(path_str)
            cam_count = len(self.cam_v2_lists)
            for i in range(cam_count):
                capture = self.cam_v2_lists[i][2]
                if i < len(position_prefix):
                    tempstr = file_str + join_char + position_prefix[i]
                else:
                    tempstr = file_str
                capture.capture(os.path.join(path_str, tempstr))
        except Exception as e:
            SystemLogger.log_info(e)
            self.error(e)

    def error(self, errstr):
        warn = QMessageBox(QMessageBox.Warning, "", "{}".format(errstr), QMessageBox.Yes)
        warn.button(QMessageBox.Yes).setText("确认")
        warn.setStyleSheet(
            "QPushButton {"
            " font: bold 24px;"
            "padding-left: 3ex;"
            "padding-right: 3ex;"
            "padding-top: 1ex;"
            "padding-bottom: 1ex;"
            "margin-left:0px;"
            "}"
            "QLabel { font:24px}"
        )
        return warn.exec()

    def saveImageInfo(self, success_count, fail_count):
        info = QMessageBox(QMessageBox.Information, "保存图片结果", "图像已保存：{}成功,{}失败".format(success_count,fail_count), QMessageBox.Yes)
        info.button(QMessageBox.Yes).setText("确认")
        info.setStyleSheet(
                "QPushButton {"
                " font: bold 24px;"
                "padding-left: 3ex;"
                "padding-right: 3ex;"
                "padding-top: 1ex;"
                "padding-bottom: 1ex;"
                "margin-left:0px;"
                "}"
                "QLabel { font:24px}"
            )
        ret = info.exec()
        return
