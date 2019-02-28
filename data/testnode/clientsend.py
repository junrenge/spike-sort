import numpy
import socket
import struct
from threading import Thread

from data.decode_data import decode

packer = struct.Struct('f')

# from multiprocessing import Process, Pipe

class ClientThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_client.connect(("localhost", 8001))

    def run(self):
        with open('../../resource/test300M.bin', 'rb') as f1:
            i = 0
            while True:
                #每次发送一帧的大小
                test_data = f1.read(84)
                if len(test_data) == 84:
                    self.tcp_client.send(test_data)
                    i = i + 1
                    # if i == 4500:
                    #     print(decode(test_data, 64))
                    #     break
                    print(i)
                else:
                    print("data over")
                    break

if __name__ == '__main__':
    clientThread = ClientThread()
    clientThread.start()
    # time.sleep(10000)
    # clientThread.join()




