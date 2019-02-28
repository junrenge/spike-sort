from pyqtgraph import GraphicsWindow


class TraceView(GraphicsWindow):

    def __init__(self):
        super(TraceView, self).__init__()

    def getCurves(self, num):
        self.curves = []
        for i in range(num):
            # if i % int(math.sqrt(num)) == 0:
            self.nextRow()
            self.plot = self.addPlot()
            # self.plot.setRange(xRange=[0, 2000], yRange=[-10, 10])
            self.plot.setRange(xRange=[0, 40000])
            self.plot.showAxis('bottom', False)
            self.plot.showAxis('left', False)
            self.plot.label = i
            self.curve = self.plot.plot()
            self.curve.setData([1,2,3])
            self.curves.append(self.curve)
        return self.curves