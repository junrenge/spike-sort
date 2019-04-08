import os
import socket
import struct
import sys
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QWidget, QVBoxLayout, QApplication
from vispy import gloo
from vispy import app
import numpy as np
import math


def recv_original_frames(conn,sigsize):
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

class recvThread(threading.Thread):

    def __init__(self, ip, port, conn, channel_num, signal):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.channel_num = channel_num
        self.signal = signal
        print("[+] New server socket thread started for " + ip + ':' + str(port))

    def run(self):
        try:
            while True:
                one_frame_data = recv_original_frames(self.conn, 3686400)
                buffer = struct.unpack("921600i", one_frame_data)
                buffer = list(buffer)
                img = np.array(buffer, dtype=np.uint8)
                img = img.reshape((480, 640, -1))
                print(img)
                self.signal[list].emit(buffer)
                #     渲染界面 保存数据
                #     img = np.uint8(img)
                #     fileSize = os.path.getsize(fileDir)
                #     if fileSize > 10 ** 3:
                #         self.videoWriter.release()
                #         self.count += 1
                #         fileDir = self.fileName + str(self.count) + '.mp4'
                #         self.videoWriter = cv2.VideoWriter(fileDir, self.fourcc, 50, (640, 480))
                #         self.videoWriter.write(img)
                #     else:
                #         self.videoWriter.write(img)
        except Exception as e:
            print('exception:', e)


class VedioCanvas(QWidget):

    def __init__(self):
        super().__init__()
        self.mainLyout = QVBoxLayout()
        self.setLayout(self.mainLyout)
        self.m_image_item = 0
        self.m_scene = QGraphicsScene(self)
        self.m_view = QGraphicsView(self)
        self.m_view.setScene(self.m_scene)
        self.resize(1400, 1400)
        self.mainLyout.addWidget(self.m_view)
        self.show()

    def showImage(self, imgList):
        img = np.array(imgList,dtype=np.uint8)
        img = img.reshape((480, 640, -1))
        if self.m_image_item:
            self.m_scene.removeItem(self.m_image_item)
            self.m_image_item = 0
        img = QImage(img, 640, 480, QImage.Format_RGB888)
        self.m_image_item = self.m_scene.addPixmap(QPixmap.fromImage(img))



class Video():

    def __init__(self):
        self.vc = VedioCanvas()
        self.receveComplete = pyqtSignal(list)
        thread = threading.Thread(target=self.recv)
        thread.start()
        self.receveComplete.connect(self.vc.showImage)

    def recv(self):
        HOST, PORT = "localhost", 8003
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((HOST, PORT))
        print('Binding on port {0}. Begin to accept connection...'.format(PORT))
        threads = []
        while True:
            tcp_server.listen(10)
            (conn, (ip, port)) = tcp_server.accept()
            new_thread = recvThread(ip, port, conn, 64, self.receveComplete)
            new_thread.start()
            threads.append(new_thread)
            print('Client {0}:{1} connected!'.format(ip, port))
        for t in threads:
            t.join()

    def getVideo(self):
        return self.vc

app = QApplication(sys.argv)
if __name__ == '__main__':
    c = Video()
    # c = VedioCanvas()
