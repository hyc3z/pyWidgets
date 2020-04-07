import datetime
import os
PRINT_LEVEL_REF = {
        'info': 0,
        'warning': 1,
        'error': 2,
        'emergecy': 4,
    }
LOG_LEVEL_REF = {
        'info': 0,
        'warning': 1,
        'error': 2,
        'emergecy': 4,
    }


class SystemLogger:

    print_level = 1
    log_level = 0

    @classmethod
    def getFileObj(cls):
        date = cls.getDate()
        pathname = "log/{}/system/system_log_{}.txt".format(date, date)
        # exist = os.path.exists(pathname)
        try:
            f = open(pathname, mode='ab+', buffering=0)
        except FileNotFoundError:
            os.makedirs("log/{}/system".format(date))
            f = open(pathname, mode='ab+', buffering=0)
        return f

    @staticmethod
    def getTimeStamp():
        now = datetime.datetime.now()
        date = now.date()
        timeobj = now.time()
        timestr = "{0:02d}{1:02d}{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
        return "{}{}{}".format(date, "-", timestr)

    @staticmethod
    def getDate():
        now = datetime.datetime.now()
        date = now.date()
        return "{}".format(date)

    @classmethod
    def processArgs(cls, args, sep:str=' '):
        retList = []
        for i in args:
            retList.append(str(i))
        return sep.join(retList)

    @classmethod
    def log(cls, *args):
        logstr = cls.processArgs(args)
        f = cls.getFileObj()
        f.write(logstr.encode('utf-8') + b"\n")


    @classmethod
    def log_info(cls, *args):
        info_str = cls.processArgs(args)
        logstr = "[ii INFO {}] {}".format(cls.getTimeStamp(), info_str)
        if cls.log_level <= LOG_LEVEL_REF['info']:
            cls.log(logstr)
        if cls.print_level <= PRINT_LEVEL_REF['info']:
            print(logstr)

    @classmethod
    def log_warning(cls, *args):
        info_str = cls.processArgs(args)
        logstr = "[WW WARNING {}] {}".format(cls.getTimeStamp(), info_str)
        if cls.log_level <= LOG_LEVEL_REF['warning']:
            cls.log(logstr)
        if cls.print_level <= PRINT_LEVEL_REF['warning']:
            print(logstr)

    @classmethod
    def log_error(cls, *args):
        info_str = cls.processArgs(args)
        logstr = "[!! ERROR {}] {}".format(cls.getTimeStamp(), info_str)
        if cls.log_level <= LOG_LEVEL_REF['error']:
            cls.log(logstr)
        if cls.print_level <= PRINT_LEVEL_REF['error']:
            print(logstr)

    @classmethod
    def set_print_level(cls, level_str):
        try:
            cls.print_level = PRINT_LEVEL_REF[level_str]
        except Exception as e:
            print('Set print level failed.{}'.format(e))

    @classmethod
    def set_log_level(cls, level_str):
        try:
            cls.log_level = LOG_LEVEL_REF[level_str]
        except Exception as e:
            print('Set log level failed.{}'.format(e))

    @staticmethod
    def send_log():
        pass


class CameraLogger(SystemLogger):
    @classmethod
    def getFileObj(cls):
        date = cls.getDate()
        pathname = "log/{}/camera/camera_log_{}.txt".format(date,date)
        # exist = os.path.exists(pathname)
        try:
            f = open(pathname, mode='ab+', buffering=0)
        except FileNotFoundError:
            os.makedirs("log/{}/camera".format(date))
            f = open(pathname, mode='ab+', buffering=0)
        return f

class DatabaseLogger(SystemLogger):
    @classmethod
    def getFileObj(cls):
        date = cls.getDate()
        pathname = "log/{}/database/database_log_{}.txt".format(date, date)
        # exist = os.path.exists(pathname)
        try:
            f = open(pathname, mode='ab+', buffering=0)
        except FileNotFoundError:
            os.makedirs("log/{}/database".format(date))
            f = open(pathname, mode='ab+', buffering=0)
        return f

if __name__ == '__main__':
    SystemLogger.log_info({'2':["3","3"]}, "233")