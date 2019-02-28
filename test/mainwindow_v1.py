import copy

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QFrame, QDockWidget,
                             QSplitter, QStyleFactory, QApplication, QComboBox, QPushButton)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
import array
import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, QDesktopWidget, QMessageBox,QTextEdit,QLabel,
     QApplication,QMainWindow, QAction, qApp, QHBoxLayout, QVBoxLayout,QGridLayout,
    QLineEdit, QScrollArea)
import numpy as np
from scipy import signal
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN,KMeans
import pandas as pd
from scipy import spatial
#数据
from utils.detect_peakes import detect_peaks

raw_signal = []
with open('1ch.txt', 'r') as f1:
    test_data = f1.read(200000)
    arr = test_data.split(',')[:-1]
    for i in range(len(arr)):
        raw_signal.append(np.float32(arr[i]))
raw_signal = np.array(raw_signal)
b, a = signal.butter(8, [0.06,0.6], 'bandpass')
filtedData = signal.filtfilt(b, a, raw_signal)

#画图
N =4000
idx = 0
#paramview
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType


#waveformview,不使用一块一块的检测，使用实时检测
template = []
waveforms = []
color=['r','g','y']
rawwaveformdata = array.array('d')
rawwavefromdataindex = 0
flag = 0
peak_index = array.array('d')
#把waveform放到数组里面
waveformviews = []
plots = []
for i in range(4):
    waveformview = pg.GraphicsWindow()
    plot = waveformview.addPlot(title=str(i))
    plot.showAxis('bottom', False)
    plot.showAxis('left', False)
    waveformviews.append(waveformview)
    plots.append(plot)
waveformviews2 = []
plots2 = []
for i in range(4):
    waveformview = pg.GraphicsWindow()
    plot = waveformview.addPlot(title=str(i))
    plot.showAxis('bottom', False)
    plot.showAxis('left', False)
    waveformviews2.append(waveformview)
    plots2.append(plot)

winindex = 0

#HFtraceview
HFtraceview = pg.GraphicsWindow()
HFtraceview.setWindowTitle('HFtraceview')
p2 = HFtraceview.addPlot()
p2.setRange(xRange=[0, N-1], yRange=[-10,10])
HFtraceviewdata = array.array('d')
curve2 = p2.plot()


def printmsg():
    print('hello')

#traceview
traceview = pg.GraphicsWindow()
traceview.setWindowTitle('traceview')
p1 = traceview.addPlot()
p1.setRange(xRange=[0, N-1], yRange=[-10,10])
traceviewdata = array.array('d')
curve1 = p1.plot()

def update():
    global traceviewdata, idx, rawwaveformdata, flag, peak_index, waveforms, template, winindex
    print(winindex)
    if idx >= len(raw_signal) | idx >= len(filtedData):
        return
    tmp1 = raw_signal[idx]
    tmp2 = filtedData[idx]

    #检测waveform
    if flag == 0:
        peak_index = detect_peaks(rawwaveformdata, mph=3, mpd=50, show=False)
        # print(peak_index) #[404 593 677 921]
        if len(peak_index) == 1:
            flag = 1
            rawwaveformdata.append(tmp2)
        else:
            rawwaveformdata.append(tmp2)
    else:
        if len(rawwaveformdata) - peak_index[0] > 30:
            #检测到了，rawwaveformdata  peak_index flag = 0
            wave = rawwaveformdata[peak_index[0]-20:peak_index[0]+30]
            print('detect a wave')
            if len(template) > 0:
                # 模板匹配
                col = 'w'
                thresh_hold = 0.9
                waveform_class = [0] * len(waveforms)
                flag = 0
                for j in range(len(template)):
                    simi = 1 - spatial.distance.cosine(template[j], wave)
                    if simi > thresh_hold:
                        col = color[j]
                        flag = 1
                if flag == 0:
                    col = 'w'
                plots[0].plot(wave, pen=col)
            else:
                plots[0].plot(wave, pen='w')

            waveforms.append(wave)
            if len(waveforms) == 10:
                # p3.clear()
                #得到模板
                pca = PCA(n_components=3)
                dim_redu_waveforms = pca.fit_transform(waveforms)
                y_pred = KMeans(n_clusters=3).fit_predict(dim_redu_waveforms)
                n, m = np.shape(waveforms)
                concat = np.zeros([n, m + 1])
                concat[:, : m] = waveforms
                concat[:, -1] = y_pred
                df = pd.DataFrame(concat)
                templates = df.groupby(df[50]).mean()
                template = templates.values
                for i in range(len(template)):
                    plots[0].plot(template[i], pen=color[i])

            rawwaveformdata = []
            peak_index = []
            flag = 0
        else:
            rawwaveformdata.append(tmp2)

    if len(traceviewdata) < N:
        traceviewdata.append(tmp1)
        HFtraceviewdata.append(tmp2)
    else:
        traceviewdata[idx%N] = tmp1
        HFtraceviewdata[idx % N] = tmp2

    #更新traceview和HFtraceview
    curve1.setData(traceviewdata)
    curve2.setData(HFtraceviewdata)
    idx += 1

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.001)

class Splitter(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI(winindex)

    def initUI(self, winindex):
        self.winindex = winindex
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.resize(800, 600)

        grid = QGridLayout()
        grid.setSpacing(0)
        positions = [(i, j) for i in range(2) for j in range(2)]
        for pos, win in zip(positions, waveformviews):
            grid.addWidget(win, *pos)

        wid = QWidget()
        wid.setLayout(grid)
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(wid)
        splitter1.addWidget(waveformviews2[self.winindex])
        splitter1.addWidget(HFtraceview)

        vbox = QVBoxLayout()
        bt = QPushButton("button")
        bt.clicked.connect(self.changewin)
        vbox.addWidget(bt)
        wid2 = QWidget()
        wid2.setLayout(vbox)
        splitter1.addWidget(wid2)

        d1 = QDockWidget()
        d1.setWidget(traceview)
        self.setCentralWidget(splitter1)
        self.addDockWidget(Qt.BottomDockWidgetArea, d1)
        self.setWindowTitle('Spike sort')
        self.show()

    def changewin(self):
        global winindex
        winindex += 1
        del traceviewdata[:]
        del HFtraceviewdata[:]
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Splitter()
    sys.exit(app.exec_())