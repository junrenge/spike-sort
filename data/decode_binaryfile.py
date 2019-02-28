import re
import time
import queue
q = queue.Queue()

import ctypes
import os
import numpy as np

CUR_PATH = os.path.dirname(__file__)
dllPath = os.path.join(CUR_PATH, "Dlltest.dll")
print(dllPath)
pDll = ctypes.WinDLL(dllPath)
print(pDll)

class Rearray(ctypes.Structure):
    _fields_ = [("arr", ctypes.c_int * 640)]
pDll.getdata.restype = ctypes.POINTER(Rearray)


def read_dataSource(filename):
    with open(filename, 'rb') as f1:
        read_time, parse_time = 0, 0
        while True:
            try:
                i = 0
                s = time.time()
                data = f1.read(840)
                read_time = read_time + (time.time() - s)
                if len(data) < 840:
                    print("文件解析完", i)
                    break
                s = time.time()
                carray = (ctypes.c_char * len(data))(*data) #耗时很多
                result = pDll.getdata(carray)
                # print(len(result.contents.arr))
                parse_time = parse_time + (time.time() - s)
                i = i + 1
            except Exception as e:
                print('exception:', e)
        print("read:", read_time, "parse:", parse_time)
start = time.time()
read_dataSource('test2.bin') #120s300M用时120s 去掉append78s,c一次读5字节需要248s,c一次读84字节需要76s，840要68s
# read_dataSource('test.bin') #180s1G用时453s 去掉append306s
end = time.time()

print("time", end - start)