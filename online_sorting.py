import sys

from PyQt5 import QtWidgets

from canvas.vispy_window import MainWindow

if __name__ == '__main__':
    appQt = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()