import numpy

from pyqtgraph import GraphicsWindow


class SelectWaveformView(GraphicsWindow):

    def __init__(self):
        super(SelectWaveformView, self).__init__()

    def getPlot(self):
        self.plot = self.addPlot()
        self.plot.showAxis('bottom', False)
        self.plot.showAxis('left', False)
        self.plot.plot(numpy.zeros(50))
        return self.plot