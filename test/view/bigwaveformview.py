from test.view import ClickGraphicsWindow


class BigWaveformView(ClickGraphicsWindow):

    def __init__(self):
        super(BigWaveformView, self).__init__()

    def getPlot(self):
        self.plot = self.addPlot()
        self.plot.showAxis('bottom', False)
        self.plot.showAxis('left', False)
        self.plot.plot([1,2,3])
        return self.plot