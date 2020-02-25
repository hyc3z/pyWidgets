from PyQt5.QtWidgets import QCheckBox


class CheckedBox(QCheckBox):

    def __init__(self, parent=None):
        super(QCheckBox, self).__init__(parent)

    def click(self) -> None:
        return

    def nextCheckState(self) -> None:
        self.setChecked(True)


