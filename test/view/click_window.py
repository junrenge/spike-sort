import pyqtgraph as pg
from test.view.click_plot import myplot


class ClickWindow(pg.GraphicsWindow):
    def __init__(self):
        super(ClickWindow, self).__init__()

    def addPlot1(self, row=None, col=None, rowspan=1, colspan=1, **kargs):
        """
        Create a PlotItem and place it in the next available cell (or in the cell specified)
        All extra keyword arguments are passed to :func:`PlotItem.__init__ <pyqtgraph.PlotItem.__init__>`
        Returns the created item.
        """
        plot = myplot(**kargs)
        self.addItem(plot, row, col, rowspan, colspan)
        return plot

