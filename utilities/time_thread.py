from PyQt5.QtCore import QThread, pyqtSignal
import datetime
import time
class TimeThread(QThread):

    sigUpdateDate = pyqtSignal(str)
    def __init__(self):
        super(QThread, self).__init__()
        self.date = None

    def run(self):
        #线程相关的代码
        while(True):
            now = datetime.datetime.now()
            timeobj = now.time()
            date = str(now.date())
            newtime = "{0:02d}:{1:02d}:{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
            self.sigUpdateDate.emit(date+" "+newtime)
            time.sleep(1)


if __name__ == '__main__':
    print(datetime.datetime.now().date())
    timeobj = datetime.datetime.now().time()
    print("{0:02d}:{1:02d}:{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second))