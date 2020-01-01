
from PyQt5 import QtChart, QtCore



class CustomedQChartView(QtChart.QChartView):

    Signal_pos = QtCore.pyqtSignal(QtCore.QPointF)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

