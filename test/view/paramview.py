from pyqtgraph.parametertree import Parameter, ParameterTree
from utils.onechanel_controller import OnechannelDataprocessor
# from pyqtgraph.Qt import QtGui
# app2 = QtGui.QApplication([])

class ParamView(ParameterTree):

    def __init__(self):
        super(ParamView, self).__init__()
        self.dict = {
            'thresh_hold' : 0.9,
            'wave_number' : 3,
            'method' : 'kmeans'
        }

        self.params = [
            {'name': 'waveformview params', 'type': 'group', 'children': [
                {'name': 'thresh_hold', 'type': 'float', 'value': 0.9, 'step': 0.1},
                {'name': 'wave_number', 'type': 'int', 'value': 3},
                {'name': 'method', 'type': 'list', 'values': ['kmeans', 'dbscan'], 'value': 'kmeans'},
            ]},
            {'name': 'Save data', 'type': 'group', 'children': [
                {'name': 'Save State', 'type': 'action'},
            ]},
        ]
        self.p = Parameter.create(name='params', type='group', children=self.params)
        self.setParameters(self.p, showTop=False)

        # p.param('Save data', 'Save State').sigActivated.connect(save)#测试用

