# -*- coding: utf-8 -*-
import numpy
import threading
import time
from pyacq import Node

class OnechannelDataprocessor(Node):
    def __init__(self, id, tracecurve):
        self.id = id
        self.tracecurve = tracecurve
        self.data = []
        self.index = 0
        self.step = 4000
        self.traceview_array = []
        self.data_thread = threading.Thread(target=self.data_thread)
        self.data_thread.start()
        # self.draw_thread = threading.Thread(target=self.draw_thread)

    def test(self):
        print(self.id)

    # def start_thread(self):
    #     self.draw_thread.start()

    def data_thread(self):
        while True:
            time.sleep(0.001)
            if len(self.data) > 100000:
                print('存储，改变index值')
                break
            #     time.sleep(3)
            # self.data.extend(numpy.random.rand(1000))
            self.data.extend(numpy.arange(0, numpy.pi, 0.001))

    def draw_thread(self):
        # while True:
        #     s = time.time()
            try:
                if self.index+self.step < len(self.data):
                    self.traceview_array[self.index%40000:(self.index+self.step)%40000] = \
                        self.data[self.index:self.index+self.step]
                    self.tracecurve.setData(self.traceview_array)
                    self.index += self.step
                    # print(time.time() - s)
            except Exception as e:
                print(e)