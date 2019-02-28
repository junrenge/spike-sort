import math
import numpy

from test.view.click_window import ClickWindow


class WaveformView(ClickWindow):

    def __init__(self):
        super(WaveformView, self).__init__()

    def getPlots(self, num):
        self.plots = []
        for i in range(num):
            if i % int(math.sqrt(num)) == 0:
                self.nextRow()
            self.plot = self.addPlot1()
            self.plot.showAxis('bottom', False)
            self.plot.showAxis('left', False)
            self.plot.lable = i
            self.plot.plot(numpy.zeros(50))
            self.plots.append(self.plot)
        return self.plots