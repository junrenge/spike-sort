import pyqtgraph


class myplot(pyqtgraph.PlotItem):
    def __init__(self):
        super(myplot, self).__init__()

    sigClicked = pyqtgraph.QtCore.Signal(object)
    lable = -1
    def mouseClickEvent(self, ev):
        # print(self.lable)
        self.sigClicked.emit(self)