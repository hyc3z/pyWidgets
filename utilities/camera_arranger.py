import os
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraViewfinderSettings, QImageEncoderSettings, QMultimedia, \
    QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QMessageBox, QPushButton, QGridLayout

from logger import SystemLogger, CameraLogger
from pop_ups import PopUps
import platform
PLATFORM = platform.system()
# 该类用于管理摄像头
SAVE_IMAGE_CODEC = 'png'
class CameraArranger(QObject):

    sigReadyToSave = pyqtSignal()
    
    def __init__(self, parent=None):
        super(CameraArranger, self).__init__(parent)
        # 存储摄像头信息
        self.cam_v2_lists = []
        # QPushButton
        self.button = None
        self.wait_dialog = None
        # QGridLayout
        self.display_layout = None
        self.display_column = 2
        self.error_count = 0

    # 把主界面中的一个按钮绑定到开始/结束拍摄的事件上，默认第一次点击按钮是开始拍摄。
    def bindReusableButton(self, reusable_button):
        if isinstance(reusable_button, QPushButton):
            self.button = reusable_button
            self.button.clicked.connect(self.startCaptureImage_V2)
        else:
            SystemLogger.log_error("Bind button with camera arranger failed!")

    # 把主界面的一个GridLayout设为输出目的地，column_count为分几列输出
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

    def initialize(self, codec=SAVE_IMAGE_CODEC, resolution="max", camera_assert_count=3):
        self.online_webcams = QCameraInfo.availableCameras()
        CameraLogger.log_info(self.online_webcams)
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
            cam.error.connect(lambda: self.cameraAlert(cam.errorString()))
            if PLATFORM == "Windows":
                cam.load()
            CameraLogger.log_info(cam.status())
            supported_resolutions = cam.supportedViewfinderResolutions()
            cam.setViewfinder(camera_vf)
            vf_setting = QCameraViewfinderSettings()
            vfs_valid = True
            if resolution == "max":
                if len(supported_resolutions) > 0:
                    vf_setting.setResolution(supported_resolutions[-1])
                else:
                    CameraLogger.log_error("Viewfinder set max resolution failed. Failed to get supported resolutions.")
                    vfs_valid = False
            elif resolution == "min":
                if len(supported_resolutions) > 0:
                    vf_setting.setResolution(supported_resolutions[0])
                else:
                    CameraLogger.log_error("Viewfinder set min resolution failed. Failed to get supported resolutions.")
                    vfs_valid = False
            elif isinstance(resolution, QSize):
                vf_setting.setResolution(resolution)
            cam.setCaptureMode(QCamera.CaptureStillImage)
            if vfs_valid:
                cam.setViewfinderSettings(vf_setting)
            imageSettings = QImageEncoderSettings()
            imageSettings.setCodec(codec)
            imageSettings.setQuality(QMultimedia.VeryHighQuality)
            ims_valid = True
            if resolution == "max":
                if len(supported_resolutions) > 0:
                    imageSettings.setResolution(supported_resolutions[-1])
                else:
                    CameraLogger.log_error("ImageSetting set max resolution failed. Failed to get supported resolutions.")
                    ims_valid = False
            elif resolution == "min":
                if len(supported_resolutions) > 0:
                    imageSettings.setResolution(supported_resolutions[0])
                else:
                    CameraLogger.log_error("ImageSetting set min resolution failed. Failed to get supported resolutions.")
                    ims_valid = False
            elif isinstance(resolution, QSize):
                imageSettings.setResolution(resolution)
            SystemLogger.log_info("Camera {} resolution {}".format(self.online_webcams[i].description(),imageSettings.resolution()))
            capture = QCameraImageCapture(cam)
            capture.error.connect(self.captureError)
            if ims_valid:
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
            self.wait_dialog =PopUps.info_dialog("正在处理图片……", "正在处理图片，请稍候……")
            # confirmError.setWindowFlags(QtCore.Qt.FramelessWindowHint)
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
                path = os.path.join(path_str, tempstr)
                CameraLogger.log_info(path)
                capture.capture(path)
        except Exception as e:
            SystemLogger.log_info(e)
            PopUps.error(e)


    def saveImageInfo(self, success_count, fail_count):
        PopUps.info("保存图片结果", "图像已保存：{}成功,{}失败".format(success_count,fail_count))
