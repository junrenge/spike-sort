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
import os
import threading
import time
import numpy as np
from scipy import signal
from sklearn.decomposition import PCA
from matplotlib import pyplot as pl
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN,KMeans
import pandas as pd

from utils.detect_peakes import detect_peaks

from PyQt5.QtWidgets import QScrollArea, QFileDialog

try:
    from sip import setapi
    setapi("QVariant", 2)
    setapi("QString", 2)
except ImportError:
    pass

from PyQt5 import QtCore, QtWidgets
import sys
from canvas.realtime_signals import Canvas as RealtimeCanvas
from canvas.waveforms import WaveCanvas as WaveCanvas
from canvas.selected_waveforms import Canvas as SelectedWaveCanvas
from canvas.camera import Canvas as VideoCavas
from canvas.param import ObjectWidget
from pyacq import Node, register_node_type, create_manager
from pyacq.rec import RawRecorder
from data.testnode.raw_recorder import NewRawRecorder

class MainWindow(QtWidgets.QMainWindow, Node):

    _input_specs = {'signals': {},'img':{}}

    def __init__(self, chanelnum, workdir):
        QtWidgets.QMainWindow.__init__(self)

        self.workdir = workdir
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)


        self.resize(1000, 800)
        self.setWindowTitle('online-sorting')

        self.props_widget = ObjectWidget(self)
        self.props_widget.signal_objet_changed.connect(self.update_view)
        self.props_widget.signal_start.connect(self.start)
        self.props_widget.signal_save.connect(self.start_new_recording)
        self.props_widget.signal_stop.connect(self.stop_new_recording)

        self.paramview = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.paramview.addWidget(self.props_widget)

        self.real_time_canvas = RealtimeCanvas()
        self.real_time_canvas.create_native()
        self.waveform_canvas = WaveCanvas()
        self.waveform_canvas.create_native()
        self.waveform_canvas.native.setParent(self)
        # self.selected_waveform_canvas = SelectedWaveCanvas()
        self.selected_waveform_canvas = self.waveform_canvas.get_sub_view()
        self.selected_waveform_canvas.create_native()
        self.video_canvas = VideoCavas()
        self.video_canvas.create_native()
        self.sub_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.sub_splitter.addWidget(self.selected_waveform_canvas.native)
        self.sub_splitter.addWidget(self.video_canvas.native)
        self.s = QScrollArea()
        self.s.setWidget(self.real_time_canvas.native)
        self.s.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.real_time_canvas.native.setParent(self)
        # self.selected_waveform_canvas.native.setParent(self)
        # Central Widget
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.paramview)
        splitter.addWidget(self.waveform_canvas.native)
        splitter.addWidget(self.sub_splitter)
        splitter.addWidget(self.s)
        self.setCentralWidget(splitter)

        self.thread = threading.Thread(target=self.poll_socket)

    def select_channel(self, i):
        print('select_channel', i)
        self.real_time_canvas.color_change(i)

    def update_view(self, param):
        self.canvas.paramchange(param)

    # def start(self, i):
    #     print('start', i)
    #     self.selected_waveform_canvas.channel_change(i)
    #     self.real_time_canvas.color_change(i)

    def start_new_recording(self):
        directory = QFileDialog.getExistingDirectory(self,"选取文件夹",self.workdir)
        self.workdir=directory
        self.raw_sigs_dir = os.path.join(self.workdir, 'raw_sigs/', str(time.time()))
        print("start_new_recording")

        self.rec=NewRawRecorder()
        self.rec.configure(streams=[self.input.params], autoconnect=True, dirname=self.raw_sigs_dir)
        self.rec.initialize()
        self.rec.start()
        #这里要修改的话就是模仿rec写一个节点，不过可以自动更换保存文件的那种。


    def stop_new_recording(self):
        self.rec.stop()
        self.rec.close()

    def poll_socket(self):
        while True:
            event = self.inputs['signals'].socket.poll(0)
            if event != 0:
                index, data = self.inputs['signals'].recv()

                # print("poll_socket:", index, data.shape)
                self.real_time_canvas.recv(data)
                # b, a = signal.butter(8, [0.06, 0.6], 'bandpass')
                # filtedData = signal.filtfilt(b, a, data)
                self.waveform_canvas.recv(data)

    def start_receive(self):
        self.thread.start()

    def node(self):
        man = create_manager(auto_close_at_exit=False)
        nodegroup = man.create_nodegroup('nodegroup')
        nodegroup.register_node_type_from_module('canvas.waveforms', 'WaveCanvas')
        nodegroup.register_node_type_from_module('canvas.selected_waveforms', 'Canvas')

        # create ndoes
        sender = nodegroup.create_node('WaveCanvas', name='sender')
        stream_spec = dict(protocol='tcp', interface='127.0.0.1', port='*',
                           transfermode='plaindata', streamtype='analogsignal',
                           dtype='float32', shape=(-1, 16), compression='',
                           scale=None, offset=None, units='')
        sender.configure(sample_interval=0.001)
        # sender.outputs['test'].configure(**stream_spec)
        sender.initialize()

        receiver = nodegroup.create_node('Canvas', name='receiver')
        receiver.configure()
        receiver.inputs['test'].connect(sender.outputs['test'])
        receiver.initialize()

    def node2(self):
        import pyqtgraph as pg
        app = pg.mkQApp()
        sender = self.waveform_canvas
        stream_spec = dict(protocol='tcp', interface='127.0.0.1', port='*',
                           transfermode='plaindata', streamtype='analogsignal',
                           dtype='float32', shape=(-1, 16), compression='',
                           scale=None, offset=None, units='')
        sender.configure(sample_interval=0.001)
        sender.outputs['test'].configure(**stream_spec)
        sender.output.configure(**stream_spec)
        sender.initialize()
        sender.send_data()

        receiver = self.selected_waveform_canvas
        receiver.configure()
        receiver.inputs['test'].connect(sender.outputs['test'])
        receiver.input.connect(sender.output)
        receiver.initialize()

        sender.send_data()
        app.exec_()

register_node_type(MainWindow)

if __name__ == '__main__':

    appQt = QtWidgets.QApplication(sys.argv)
    win = MainWindow(64, 's')
    win.show()
    appQt.exec_()
