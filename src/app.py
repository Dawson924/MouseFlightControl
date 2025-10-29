from PySide2 import QtWidgets


class App(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.translators = []
