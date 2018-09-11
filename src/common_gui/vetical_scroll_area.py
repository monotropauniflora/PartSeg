from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea


class VerticalScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        print("buka1")
        if self.widget() and self.width() > 0:
            print("buka2")
            self.widget().setMinimumWidth(self.width() - self.verticalScrollBar().width())
