from data.decode_data import recv,offline_decode
import threading
import os

# send, recv = Pipe()

def receiver(recv):
    while True:
        d= recv.recv()
        print(d[:, 0:3])
        print('#######################')

if __name__=="__main__":
    thread = threading.Thread(target=receiver,args=(recv,))
    thread.start()
    offline_decode(64, '', 'D:\\pyws\\online-sorting-2\\data\\test300M.bin')
