# _*_ coding: utf-8 _*_
# @File: tcp_server.py
# @Author: Boss Xiao
# @Date: 2018/4/11
# @Desc: a tcp server demo

import socket
import struct
from threading import Thread
import numpy as np

packer = struct.Struct('f')

class ReadThread(Thread):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ':' + str(port))

    def run(self):
        try:
            with open('test.bin', 'wb') as fp:
                i = 0
                while True:
                  data = conn.recv(2048)
                  if not data:break
                  fp.write(data)
                  i += 1
                  print(i)
            print('exit')
        except Exception as e:
            print('exception:', e)

# HOST, PORT = "localhost", 7
HOST, PORT = "192.168.1.209", 7
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((HOST, PORT))
print('Binding on port {0}. Begin to accept connection...'.format(PORT))
threads = []
while True:
    tcp_server.listen(10)
    (conn, (ip, port)) = tcp_server.accept()
    readthread = ReadThread(ip, port)
    readthread.start()
    print('Client {0}:{1} connected!'.format(ip, port))
    threads.append(readthread)

for t in threads:
    t.join()