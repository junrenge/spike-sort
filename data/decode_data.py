#coding=utf-8
#在jit装饰器装饰的函数中，不可以有第三方的package
import time
from numba import jit
import numpy as np
import time
from multiprocessing import Pipe


buffer=[]

send, recv = Pipe()

@jit
def decode(bin,channel_num):
    ch=np.array([0.]*channel_num)
    ch_idx=0
    decode_num=channel_num/4#每轮解析次数
    for i in range(decode_num):#5字节（40位）一个完整解析，80/5=16次解析
        d_idx=i*5
        ch[ch_idx] = (bin[d_idx] << 2) + (bin[d_idx + 1] >> 6)
        # print(ch[ch_idx])
        ch_idx+=1
        ch[ch_idx] = ((bin[d_idx + 1] & 0x3F) << 4) + (bin[d_idx + 2] >> 4)
        # print(ch[ch_idx])
        ch_idx += 1
        ch[ch_idx] = ((bin[d_idx + 2] & 0x0F) << 6) + (bin[d_idx + 3] >> 2)
        # print(ch[ch_idx])
        ch_idx += 1
        ch[ch_idx] = ((bin[d_idx + 3] & 0x03) << 8) + (bin[d_idx + 4])
        # print(ch[ch_idx])
        ch_idx += 1
    return ch

def offline_decode(channel_num,file_path,file_name):
    global buffer,out
    #判断路径
    file=file_path+file_name
    print(file)
    try:
        f1 = open(file, 'rb')
        ch = np.array([0.] * channel_num)
        n = 0
        t1 = time.time()
        bin_length = int(10 * channel_num / 8)  # 一帧数据的长度
        while True:
            bin = f1.read(bin_length)  # 读一帧数据
            if len(bin) == bin_length:
                ch = decode(bin, channel_num)
                # print("解析后的一帧数据：",ch)
                if len(buffer)>=1024:
                    # print('缓冲区满了')
                    #拿走数据
                    send.send(np.array(buffer))
                    #清空buffer
                    buffer=[]
                else:
                    buffer.append(ch)
                    # print(len(buffer))
            else:
                print("解析完成")
                break
        f1.close()
        t = time.time() - t1
        print(t)
    except Exception as e:
        print("File is not found.")



import socket
import struct
from threading import Thread
import numpy as np
packer = struct.Struct('f')


class recvThread(Thread):  # 接收数据-->解码-->发送到buffer

    def __init__(self, ip, port,conn, channel_num):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn=conn
        self.channel_num = channel_num
        print("[+] New server socket thread started for " + ip + ':' + str(port))

    def run(self):
        try:
            i = 0  # 接收帧的数量
            while True:
                data = self.conn.recv(84)  # 接收数据
                if len(data) == 84:
                    ch = [0] * self.channel_num
                    ch = decode(data)
                    if len(buffer) >= 1024:
                        # print('缓冲区满了')
                        # 拿走数据
                        send.send(np.array(buffer))
                        # 清空buffer
                        buffer = []
                    else:
                        buffer.append(ch)
                        # print(len(buffer))
        except Exception as e:
            print('exception:', e)
# HOST, PORT = "192.168.1.209", 7
def online_decode(HOST,PORT,channel_num):

    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((HOST, PORT))
    print('Binding on port {0}. Begin to accept connection...'.format(PORT))
    threads = []
    while True:
        tcp_server.listen(10)
        (conn, (ip, port)) = tcp_server.accept()#收到客户端的连接
        recvthread = recvThread(ip, port,conn,channel_num)#接收客户端的数据进行处理
        recvthread.start()
        print('Client {0}:{1} connected!'.format(ip, port))
        threads.append(recvthread)
    for t in threads:
        t.join()
