import numpy as np
from pyacq import Node, register_node_type
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.util.mutex import Mutex

import socket
import struct

import time
import threading


# class fileDataSource(Node):
#     '''
#     this node streams decoded data from a local file.
#     '''
#     _output_specs = {'signals': dict(streamtype='analogsignal',
#                                      shape=(-1, 64), compression='', sample_rate=400000.
#                                      )}
#     def __init__(self,**kargs):
#         Node.__init__(self,**kargs)
from data.decode_data import decode


def recv_original_frames(conn,sigsize):
    buf = b''
    # n = 0
    # while len(buf) < sigsize:
    #     newbytes = conn.recv(sigsize - n)
    #     if newbytes == '':
    #         raise RuntimeError('connection broken')
    #     buf = buf + newbytes
    #     n += len(buf)
    #
    # if len(buf) >= sigsize:
    #     buf = buf[:sigsize]
    buf=conn.recv(sigsize)
    return buf

class OnlineDataSource(Node):
    '''
    this class is a bridge between pyacq and the socket-based data streaming
    provided by the recorder.
    '''
    _output_specs = {'signals':{}}
    def __init__(self,**kargs):
        Node.__init__(self,**kargs)

    def configure(self,egg_host='localhost',egg_port=8001,nb_channel=64,sample_rate=40000.):

        self.egg_host = egg_host
        self.egg_port = egg_port
        self.nb_channel=nb_channel
        self.sample_rate=sample_rate
        #todo:后面可以设置通道名称
        self.outputs['signals'].spec['shape'] = ( -1,self.nb_channel)
        self.outputs['signals'].spec['sample_rate'] = self.sample_rate
        self.outputs['signals'].spec['nb_channel'] = self.nb_channel


    def initialize(self):
        # 尝试连接，连接成功之后接收并转发
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.egg_host, self.egg_port))  # 服务器端绑定该端口
        print('Binding on port {0}. Begin to accept connection...'.format(self.egg_port))
        self.server_socket.listen(10)
        (self.conn, (ip, port)) = self.server_socket.accept()
        print(self.conn)
        print('Client {0}:{1} connected!'.format(ip, port))


        self.frame_size = int(10 * self.nb_channel / 8) + 4  # 一帧的大小和通道个数相关
        self.frames = 1  # 每次接收多少帧
        self.sigsize = self.frame_size * self.frames  # 每次接收的bit数据的大小
        self.head = 0
        self.thread=threading.Thread(target=self.send_data)

    def start_decode(self):
        self.thread.start()


    def send_data(self):
        while True:
            # 每次接收定长的二进制数据，进行解码之后发送。
            rawdata = recv_original_frames(self.conn, self.sigsize)
            dt = np.dtype('float32')
            self.sigs = np.zeros((self.frames, self.nb_channel), dtype=dt)  # 行：帧数；列：通道数
            # print(self.sigs)


            if len(rawdata)==self.sigsize:
                for i in range(self.frames):  # 逐帧解析，将解析结果放到sigs中
                    self.sigs[i, :] = decode(rawdata[i * self.frame_size:(i + 1) * self.frame_size + 1], self.nb_channel)
                # 发送数据的维度为(帧数，通道个数)
                self.outputs['signals'].send(self.sigs, index=self.head)
                self.head += self.frames
                # print('online_data_source:self.sigs', self.sigs)
            else:
                self.sigs = np.zeros((self.frames, self.nb_channel), dtype=dt)  # 行：帧数；列：通道数

    def getsignalfromfile(self):
        with open('resource/4ch.txt', 'r') as f2:
            for i in range(64):
                a = []
                self.raw_signa.append(a)
            while True:
                test_data = f2.read(2000)
                arr = test_data.split(',')[:-1]
                for i in range(len(arr)):
                    self.raw_signa[int(i % 4)].append(np.float32(arr[i]))
                    if len(self.raw_signa[4 - 1]) > 10000:
                        break
                if len(self.raw_signa[0]) > 6000:
                    break

    def stop(self):
        # self.timer.stop()
        # self.thread.join()

        self.conn.close()
        self.server_socket.close()

    def close(self):
        pass

register_node_type(OnlineDataSource)