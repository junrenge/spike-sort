# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui
app2 = QtGui.QApplication([])
import numpy as np
from scipy import signal
class Datasource():
    raw_signa = []

    def getsignalfromfile(self):
        path = ''
        with open('resource/4ch.txt', 'r') as f2:
            for i in range(4):
                a = []
                self.raw_signa.append(a)
            while True:
                test_data = f2.read(200000)
                arr = test_data.split(',')[:-1]
                for i in range(len(arr)):
                    self.raw_signa[int(i % 4)].append(np.float32(arr[i]))
                    if len(self.raw_signa[4 - 1]) > 10000:
                        break
                if len(self.raw_signa[0]) > 6000:
                    break
        # self.raw_signal = self.raw_signa[int(self.id) % 4]
        return self.raw_signa


    def getsignalfromsocket(self):
        if len(self.buffer) > 4100:
            self.raw_signal = self.buffer[:4000]
            self.buffer = self.buffer[4000:]
            b, a = signal.butter(8, [0.06, 0.6], 'bandpass')
            self.filtedData = signal.filtfilt(b, a, self.raw_signal)
            self.count = 0
    # def receiver(self, recv):
    #     while True:
    #         print(self.id)
    #         try:
    #             d = recv.recv()
    #             print(d[..., int(self.id)])
    #             self.buffer.append(d[..., int(self.id)])
    #             print(len(self.buffer))
    #             # print(self.buffer)
    #             # print('#######################')
    #         except Exception as e:
    #             print(traceback.print_exc())
    # def startreceiver(self):
    #     thread = threading.Thread(target=self.receiver, args=(recv,))
    #     thread.start()
    #     # data.onlinedataserver.start_server()
    #     self.getrawsignal()