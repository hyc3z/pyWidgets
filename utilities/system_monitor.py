
import psutil

class SystemMonitor:

    def __init__(self):
        pass

    @staticmethod
    def getCpuUsage(interval=1):
        return (" CPU: " + str(psutil.cpu_percent(interval)) + "%")

    @staticmethod
    def getMemorystate():
        phymem = psutil.virtual_memory()
        data = {
            "percent": phymem.percent,
            "used": int(phymem.used / 1024 / 1024),
            "total": int(phymem.total / 1024 / 1024),
        }
        return data


if __name__ == '__main__':
    while True:
        print(SystemMonitor.getCpuUsage())
        print(SystemMonitor.getMemorystate())
