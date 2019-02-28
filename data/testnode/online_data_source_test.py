from data.testnode.online_data_source import OnlineDataSource
from data.testnode.traceview import FakeReceiver

if __name__ == '__main__':
    # app = pg.mkQApp()

    sender = OnlineDataSource()
    stream_spec = dict(protocol='tcp', interface='127.0.0.1', port='*',
                       transfermode='plaindata', streamtype='analogsignal',
                       dtype='float32', shape=(-1, 64), compression='',
                       scale=None, offset=None, units='')
    sender.configure(egg_host='localhost',egg_port=8001,nb_channel=64,sample_rate=40000.)
    sender.outputs['signals'].configure(**stream_spec)
    sender.initialize()

    receiver = FakeReceiver()
    receiver.inputs['signals'].connect(sender.outputs['signals'])
    print("finish connect")
    sender.start_decode()
    receiver.start_receive()
    print("receiver.start_receive over")


