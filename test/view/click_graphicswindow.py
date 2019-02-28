import pyqtgraph as pg
from test.view.click_plot import ClickPlot


class ClickGraphicsWindow(pg.GraphicsWindow):
    def __init__(self):
        super(ClickGraphicsWindow, self).__init__()

    def addPlot1(self, row=None, col=None, rowspan=1, colspan=1, **kargs):
        print(123)
        """
        Create a PlotItem and place it in the next available cell (or in the cell specified)
        All extra keyword arguments are passed to :func:`PlotItem.__init__ <pyqtgraph.PlotItem.__init__>`
        Returns the created item.
        """
        plot = ClickPlot(**kargs)
        self.addItem(plot, row, col, rowspan, colspan)
        return plot

