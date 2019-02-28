from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import threading
from pyacq import WidgetNode,ThreadPollInput,register_node_type,Node

class FakeReceiver(Node):
    _input_specs = {'signals': {}}

    def __init__(self,**kargs):
        Node.__init__(self,**kargs)
        self.thread=threading.Thread(target=self.poll_socket)

    def poll_socket(self):
        while True:
            event = self.inputs['signals'].socket.poll(0)
            if event != 0:
                index, data = self.inputs['signals'].recv()
                # print("traceview poll_socket:",index,data)

    def start_receive(self):
        self.thread.start()

register_node_type(FakeReceiver)

