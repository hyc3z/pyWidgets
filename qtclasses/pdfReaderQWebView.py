from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import QUrl, QFile, QFileInfo
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *


class pdfReaderQWebView(QWebEngineView):

    def __init__(self, parent=None):
        super(pdfReaderQWebView, self).__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)


    def setFile(self, filename):
        Url = QUrl.fromLocalFile(QFileInfo(filename).absoluteFilePath())
        self.setUrl(QtCore.QUrl(Url))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = pdfReaderQWebView()
    gui.setFile("医生操作指南.pdf")
    gui.show()
    sys.exit(app.exec_())