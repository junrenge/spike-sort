#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Abstract: show mesh primitive
# Keywords: cone, arrow, sphere, cylinder, qt
# -----------------------------------------------------------------------------

"""
Test the fps capability of Vispy with meshdata primitive
"""
try:
    from sip import setapi
    setapi("QVariant", 2)
    setapi("QString", 2)
except ImportError:
    pass

from PyQt5 import QtCore, QtWidgets
import sys
from canvas.realtime_signals import Canvas as RealtimeCanvas
from canvas.waveforms import Canvas as WaveCanvas
from canvas.param import ObjectWidget

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.resize(700, 500)
        self.setWindowTitle('pyqt5+vispy example')

        self.props_widget = ObjectWidget(self)
        self.props_widget.signal_objet_changed.connect(self.update_view)
        self.props_widget.signal_start.connect(self.start)
        self.props_widget.signal_save.connect(self.save)

        self.splitter_v = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter_v.addWidget(self.props_widget)

        self.canvas = RealtimeCanvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        self.canvas2 = WaveCanvas()
        self.canvas2.create_native()
        self.canvas2.native.setParent(self)
        # Central Widget
        splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.splitter_v)
        splitter1.addWidget(self.canvas2.native)
        splitter1.addWidget(self.canvas.native)
        self.setCentralWidget(splitter1)

    def update_view(self, param):
        self.canvas.paramchange(param)

    def start(self,i):
        print('start',i)

    def save(self,i):
        print('start',i)

# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    appQt = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()
