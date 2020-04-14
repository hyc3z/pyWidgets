import fileinput
import os
import platform
import subprocess

import psutil

class SystemMonitor:

    def __init__(self):
        pass

    @staticmethod
    def getCpuUsage(interval=1):
        return (" CPU: " + str(psutil.cpu_percent(interval)) + "%")

    @staticmethod
    def get_mac_cpu_speed():
        commond = 'system_profiler SPHardwareDataType | grep "Processor Speed" | cut -d ":" -f2'
        proc = subprocess.Popen([commond], shell=True, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        output = output.decode()  # bytes 转str
        speed = output.lstrip().rstrip('\n')
        return speed

    @staticmethod
    def get_linux_cpu_speed():
        for line in fileinput.input('/proc/cpuinfo'):
            if 'MHz' in line:
                value = line.split(':')[1].strip()
                value = float(value)
                speed = round(value / 1024, 1)
                return "{speed} GHz".format(speed=speed)

    @staticmethod
    def get_windows_cpu_speed():
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        speed, type = winreg.QueryValueEx(key, "~MHz")
        speed = round(float(speed) / 1024, 1)
        return "{speed} GHz".format(speed=speed)

    @staticmethod
    def get_cpu_speed():
        osname = platform.system()  # 获取操作系统的名称
        speed = ''
        if osname == "Darwin":
            speed = SystemMonitor.get_mac_cpu_speed()
        if osname == "Linux":
            speed = SystemMonitor.get_linux_cpu_speed()
        if osname in ["Windows", "Win32"]:
            speed = SystemMonitor.get_windows_cpu_speed()
        return speed

    @staticmethod
    def getMemorystate():
        phymem = psutil.virtual_memory()
        data = {
            "percent": phymem.percent,
            "used": int(phymem.used / 1024 / 1024),
            "total": int(phymem.total / 1024 / 1024),
        }
        return data

    @staticmethod
    def cpu_info():
        try:
            name = os.popen('wmic cpu get name').readlines()
            cpuname = name[-4].replace('\n', '')
        except:
            cpuname = ' '
        cpucount = psutil.cpu_count()  # 获取CPU核心
        cpu = str(cpuname) + '{} Core@{}'.format(str(cpucount),SystemMonitor.get_cpu_speed())
        return cpu

    @staticmethod
    def disk_info():
        result = []
        parts = psutil.disk_partitions()
        for i in parts:
            result.append([i, "Total {} GiB".format(psutil.disk_usage(i.mountpoint).total / 1024**3), "Free {} GiB".format(psutil.disk_usage(i.mountpoint).free / 1024**3)])
        return result


if __name__ == '__main__':
    print(SystemMonitor.cpu_info())
