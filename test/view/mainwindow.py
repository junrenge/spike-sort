import threading
from functools import partial

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

# import online_sorting
from pyacq import Node, register_node_type

from utils.onechanel_controller import OnechannelDataprocessor
from pyqtgraph.Qt import QtGui
app2 = QtGui.QApplication([])

#
# def save():
#     global state
#     state = p.saveState()
#     print('saving data')
#
# p.sigTreeStateChanged.connect(change)
# p.param('Save data', 'Save State').sigActivated.connect(save)#测试用

from test.view.select_waveformview import SelectWaveformView
from test.view import HFTraceView
from test.view import TraceView
from test.view.waveformview import WaveformView
from canvas.realtime_signals import Canvas as RealtimeCanvas

class MainWindow(QMainWindow, Node):

    _input_specs = {'signals': {}}

    def __init__(self, mt, chanelnum, threads, raw_signal, dict):
        super().__init__()

        self.mt = mt
        self.chanelnum = chanelnum
        self.threads = threads
        self.raw_signal = raw_signal
        self.dict = dict

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        #上半部分图
        splitter = QSplitter(Qt.Horizontal)
        waveform = WaveformView()
        self.waveformplots = waveform.getPlots(chanelnum)
        for i in range(chanelnum):
            self.waveformplots[i].sigClicked.connect(partial(self.change, i))

        bigwaveform = SelectWaveformView()
        self.bigwaveformplot = bigwaveform.getPlot()

        # paramview = ParamView()
        # paramview.p.sigTreeStateChanged.connect(self.change)
        splitter.addWidget(mt)
        splitter.addWidget(waveform)
        splitter.addWidget(bigwaveform)

        #下半部分图
        scroll = QScrollArea()
        tab = QTabWidget()
        traceview = TraceView()
        self.traceviewcurves = traceview.getCurves(chanelnum)

        hftraceview = HFTraceView()
        self.hftraceviewcurves = hftraceview.getCurves(chanelnum)

        self.canvas = RealtimeCanvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        tab.addTab(self.canvas.native, "traceview")
        tab.addTab(hftraceview, "HFtraceview")

        scroll.setWidget(tab)

        splitter.addWidget(tab)
        # hbox = QHBoxLayout()
        # hbox.addWidget(splitter)
        # hbox.addWidget(scroll)
        # self.setLayout(hbox)
        self.setCentralWidget(splitter)
        self.setWindowTitle('Spike sort')
        self.showMaximized()

        self.thread = threading.Thread(target=self.poll_socket)

    def create_channelcontroller(self):
        for i in range(self.chanelnum):
            onechanneldataprocessor = OnechannelDataprocessor(str(i), self.traceviewcurves[i])
            self.threads.append(onechanneldataprocessor)

    def poll_socket(self):
        while True:
            event = self.inputs['signals'].socket.poll(0)
            if event != 0:
                index, data = self.inputs['signals'].recv()
                # print("mainwindow:poll_socket:", index, data)
                for i in range(self.chanelnum):
                    self.threads[i].recvdata(data[0][i])#分发

    def start_receive(self):
        self.thread.start()

    def change(self, num):
        self.threads[num].draw_select_waveform(num)

register_node_type(MainWindow)
