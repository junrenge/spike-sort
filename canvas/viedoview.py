import socket
import threading
import numpy as np
import struct
from PyQt5.QtWidgets import (QWidget,QGraphicsScene,QGraphicsView,QApplication,QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QImage,QPixmap
import sys
from PyQt5.QtCore import pyqtSignal,QObject
import cv2
import matplotlib.image as mpimg

class Videoview(QGraphicsView):

    def __init__(self):
        super().__init__()
        # self.mainLyout = QVBoxLayout()
        self.m_image_item = 0
        self.m_scene = QGraphicsScene(self)
        self.m_view = QGraphicsView(self)
        self.m_view.setScene(self.m_scene)
        self.resize(40, 40)
        # self.mainLyout.addWidget(self.m_view)
        # self.setLayout(self.mainLyout)
        self.showImage([])

    # def resizeEvent(self, event):
    #     self.fitInView(1,1,1,1)

    def showImage(self, imgList):
        # print("长度",len(imgList))
        img = mpimg.imread('D:/online-sorting-2/canvas/1.jpg')
        img = cv2.resize(img, (640, 480))

        # img = np.array(imgList, dtype=np.uint8)
        img = img.reshape((480, 640, -1))
        # print("接收形状",img.shape)
        if self.m_image_item:
            self.m_scene.removeItem(self.m_image_item)
            self.m_image_item = 0
        img = QImage(img, 640, 480, QImage.Format_RGB888)
        # print("显示前形状",img.shape)
        self.m_image_item = self.m_scene.addPixmap(QPixmap.fromImage(img))

class receiveSever(QObject):
    receveComplete = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.tcpSever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSever.bind(('localhost', 8003))
        self.tcpSever.listen(100)  # 最多链接5个

    def listen(self):
        sock, addr = self.tcpSever.accept()
        t = threading.Thread(target=self.tcplink2, args=(sock, addr))
        t.start()

    def recv_original_frames(self,conn, sigsize):
        buf = b''
        n = 0
        while len(buf) < sigsize:
            newbytes = conn.recv(sigsize - n)
            if newbytes == '':
                raise RuntimeError('connection broken')
            buf = buf + newbytes
            n += len(newbytes)

        if len(buf) >= sigsize:
            buf = buf[:sigsize]
        return buf

    def tcplink2(self,sock, addr):
        print('Accept new connection from %s:%s...' % addr)
        error_num = 0
        i = 0
        while i < 1:
            one_frame_data = self.recv_original_frames(sock, 3686400)
            if len(one_frame_data) != 3686400:
                error_num += 1
                print("出错的地方len(data):", len(one_frame_data))
            # 对二进制数据解码
            buffer = struct.unpack("921600i", one_frame_data)
            buffer = list(buffer)
            # img = np.array(buffer)
            # img = img.reshape((640, 480, -1))
            i += 1
            self.receveComplete[list].emit(buffer)
        print(error_num)


class Video():
    def __init__(self):
        app = QApplication(sys.argv)
        self.win = Videoview()
        self.sever = receiveSever()
        self.sever.receveComplete.connect(self.win.showImage)
        listenThread = threading.Thread(target=self.sever.listen)
        listenThread.start()
        cv2.waitKey(0)
        sys.exit(app.exec_())

    def getView(self):
        return self.win

if __name__ == '__main__':
    s = Video()