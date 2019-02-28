#!/usr/bin/env python
from PyQt5 import QtGui, QtCore, QtWidgets

OBJECT = {'param': [('wave_number', 3, 30, 'int', 3),
                     ('thresh_hold', 0.1, 1.0, 'double', 0.8),
                    ],}

class ObjectParam(object):
    """
    OBJECT parameter test
    """
    def __init__(self, name, list_param):
        self.name = name
        self.list_param = list_param
        self.props = {}
        self.props['visible'] = True
        for nameV, minV, maxV, typeV, iniV in list_param:
            self.props[nameV] = iniV

class ObjectWidget(QtWidgets.QWidget):
    """
    Widget for editing OBJECT parameters
    """
    signal_objet_changed = QtCore.pyqtSignal(ObjectParam, name='objectChanged')
    signal_start = QtCore.pyqtSignal(int)
    signal_save = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, param=None):
        super(ObjectWidget, self).__init__(parent)

        #spinbox
        self.gb_c = QtWidgets.QGroupBox()
        lL = []
        self.sp = []
        gb_c_lay = QtWidgets.QGridLayout()
        self.param = ObjectParam('param', OBJECT['param'])
        for nameV, minV, maxV, typeV, iniV in self.param.list_param:
            lL.append(QtWidgets.QLabel(nameV, self.gb_c))
            if typeV == 'double':
                self.sp.append(QtWidgets.QDoubleSpinBox(self.gb_c))
                self.sp[-1].setDecimals(2)
                self.sp[-1].setSingleStep(0.1)
                self.sp[-1].setLocale(QtCore.QLocale(QtCore.QLocale.English))
            elif typeV == 'int':
                self.sp.append(QtWidgets.QSpinBox(self.gb_c))
            self.sp[-1].setMinimum(minV)
            self.sp[-1].setMaximum(maxV)
            self.sp[-1].setValue(iniV)
        # Layout
        for pos in range(len(lL)):
            gb_c_lay.addWidget(lL[pos], pos, 0)
            gb_c_lay.addWidget(self.sp[pos], pos, 1)
            # Signal
            self.sp[pos].valueChanged.connect(self.spinbox)

        #combox
        methods = ["kmeans", "dbscan"]
        method_lable = QtWidgets.QLabel('method')
        self.param.props['method'] = methods[0]
        combox = QtWidgets.QComboBox()
        combox.addItems(methods)
        combox.activated[str].connect(self.method)
        gb_c_lay.addWidget(method_lable, 2, 0)
        gb_c_lay.addWidget(combox, 2, 1)
        self.gb_c.setLayout(gb_c_lay)

        #pushbutton
        self.b = QtWidgets.QPushButton('save')
        self.b.clicked.connect(self.save)
        self.b1 = QtWidgets.QPushButton('start')
        self.b1.clicked.connect(self.start)

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(self.b1)
        hbox.addWidget(self.b)
        hbox.addWidget(self.gb_c)

        hbox.addStretch(1.0)
        vbox.addLayout(hbox)
        vbox.addStretch(1.0)

        self.setLayout(vbox)
    def method(self, m):
        self.param.props['method'] = m
        self.signal_objet_changed.emit(self.param)

    def save(self):
        self.signal_save.emit(1)

    def start(self, option):
        self.signal_start.emit(1)

    def spinbox(self, option):
        keys = map(lambda x: x[0], self.param.list_param)
        for pos, nameV in enumerate(keys):
            self.param.props[nameV] = self.sp[pos].value()
        # emit signal
        self.signal_objet_changed.emit(self.param)
