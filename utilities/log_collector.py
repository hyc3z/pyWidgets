import os
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QCoreApplication, QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QApplication
from logger import SystemLogger
from ui_logCollector import Ui_Dialog
from xzutil import *
from mail import mailobj, message
LOG_FOLDER = "./log"
import smtplib

class LogCollector_backend(QObject):

    sigInfo = pyqtSignal(str)
    sigWarning = pyqtSignal(str)
    sigError = pyqtSignal(str)
    sigSuccess = pyqtSignal()
    sigFail = pyqtSignal()
    def __init__(self, parent=None):
        super(LogCollector_backend, self).__init__(parent)
        self.name = "unknown"

    def set_name(self, name):
        self.name = name

    def collect_logs(self, describe):
        log_folder = LOG_FOLDER
        if not os.path.exists(log_folder):
            self.sigWarning.emit("日志文件未找到.")
            self.sigFail.emit()
            return
        self.sigInfo.emit("正在打包日志...")
        now = get_datetime_string_now()
        compress_name = "log_{}.tar.xz".format(now)
        make_tarxz(compress_name, LOG_FOLDER)
        self.sigInfo.emit("打包日志完成.正在上传...")
        try:
            mailbox = mailobj(mail_addr='1678321951@qq.com', passwd='gdsqxcxnkbsodecj', mail_host='smtp.qq.com', port=587)
            message_mime = message('美容测距师{}'.format(self.name), 'Master', '美容测距错误日志')
            message_mime.add_text(describe)
            message_mime.add_file(compress_name)
            ret = mailbox.sendmail(message_mime, '<1678321951@qq.com>', ['<tubao9hao@126.com>'])
            if ret:
                self.sigSuccess.emit()
            else:
                self.sigFail.emit()
        except Exception as e:
            self.sigError.emit(str(e))
            self.sigFail.emit()
        try:
            os.remove(compress_name)
        except Exception as e:
            self.sigError.emit(e)

class LogCollector_frontend(QDialog, Ui_Dialog):

    sigCollect = pyqtSignal(str)
    def __init__(self, parent=None):
        super(LogCollector_frontend, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("日志上传")
        self.pushButton.clicked.connect(self.collect_logs)
        self.workerThread = QThread()
        self.worker = LogCollector_backend()
        self.worker.moveToThread(self.workerThread)
        self.worker.sigInfo.connect(self.appendInfo)
        self.worker.sigWarning.connect(self.appendWarning)
        self.worker.sigError.connect(self.appendError)
        self.worker.sigSuccess.connect(self.sendSuccess)
        self.worker.sigFail.connect(self.sendFail)
        self.sigCollect.connect(self.worker.collect_logs)
        self.workerThread.start()

    def set_name(self, name):
        self.worker.set_name(name)

    def appendText(self, text):
        self.textBrowser.append(text)

    def appendError(self, text):
        self.appendText(SystemLogger.format_error(text))

    def appendWarning(self, text):
        self.appendText(SystemLogger.format_error(text))

    def appendInfo(self, text):
        self.appendText(SystemLogger.format_info(text))

    def sendSuccess(self):
        self.appendText(SystemLogger.format_info("上传成功."))
        self.workerThread.quit()
        self.workerThread.wait()
        self.close()

    def sendFail(self):
        self.appendError("上传失败.")
        self.pushButton.setEnabled(True)
        self.pushButton.repaint()

    def collect_logs(self):
        self.sigCollect.emit(self.textEdit_describe.toPlainText())
        self.pushButton.setEnabled(False)
        self.pushButton.repaint()



if __name__ == '__main__':
    QCoreApplication.setAttribute(QtCore.Qt.AA_UseOpenGLES)
    QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app= QApplication(sys.argv)
    collector = LogCollector_frontend()
    collector.show()
    sys.exit(app.exec_())