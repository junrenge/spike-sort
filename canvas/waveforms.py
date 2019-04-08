import threading
import numpy
from pyacq import register_node_type, Node
from utils.get_waves import get_waves, get_waves_2
from vispy import gloo
from vispy import app
import numpy as np
import math
from scipy import signal
from canvas.selected_waveforms import Canvas as SelectedWaveCanvas

VERT_SHADER = """
#version 120

// y coordinate of the position.
attribute float a_position;

// row, col, and time index.
attribute vec4 a_index;
varying vec4 v_index;

// 2D scaling factor (zooming).
uniform vec2 u_scale;

// Size of the table.
uniform vec2 u_size;

// Number of samples per signal.
uniform float u_n;

// Color.
attribute vec3 a_color;
varying vec4 v_color;

// Varying variables used for clipping in the fragment shader.
varying vec2 v_position;
varying vec4 v_ab;

void main() {
    float nrows = u_size.x;
    float ncols = u_size.y;

    // Compute the x coordinate from the time index.
    float x = -1 + 2*a_index.z / (u_n-1);
    vec2 position = vec2(x - (1 - 1 / u_scale.x), a_position);

    // Find the affine transformation for the subplots.
    vec2 a = vec2(1./ncols, 1./nrows)*.9;
    vec2 b = vec2(-1 + 2*(a_index.x+.5) / ncols,
                  -1 + 2*(a_index.y+.5) / nrows);
    // Apply the static subplot transformation + scaling.
    gl_Position = vec4(a*u_scale*position+b, 0.0, 1.0);

    v_color = vec4(a_color, 1.);
    v_index = a_index;

    // For clipping test in the fragment shader.
    v_position = gl_Position.xy;
    v_ab = vec4(a, b);
}
"""
FRAG_SHADER = """
#version 120

varying vec4 v_color;
varying vec4 v_index;

varying vec2 v_position;
varying vec4 v_ab;

void main() {
    gl_FragColor = v_color;

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;

    if ((fract(v_index.w) > 0.) || (fract(v_index.y) > 0.))
        discard;

    // Clipping test.
    vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
    if ((test.x > 1) || (test.y > 1))
        discard;
}
"""

nrows = 8
ncols = 8
wavenum_per_channel = 50
channel_num = nrows * ncols
wave_len = 50
pointnum_per_channel = wave_len * wavenum_per_channel
data_step = 400
data_array_point = 0

amplitudes = .1 + .2 * np.random.rand(channel_num, 1).astype(np.float32)

y = np.random.randint(0, 1, size=[channel_num, 50, 50]).astype(np.float32)
ylist = y.tolist()


color = 1 + np.zeros((channel_num, pointnum_per_channel, 3)).astype(np.float32)#将color改成和y的维度一样的。
color = color.tolist()

t=[]
for i in range(nrows):
    for j in range(ncols):
        for wavenum in range(wavenum_per_channel):
            for point in range(wave_len):
                t.append([j, nrows - 1 - i, point, wavenum])

index = np.array(t).astype(np.float32)
print(1)

class WaveCanvas(app.Canvas, Node):
    _output_specs = {'test': {}}

    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive')

        self.shape = (nrows, ncols)
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        # self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_position'] = ylist
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = self.shape
        self.program['u_n'] = wave_len

        gloo.set_viewport(0, 0, *self.physical_size)
        self._timer = app.Timer(1/100, connect=self.on_timer, start=True, )
        gloo.set_state(preset='additive', clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        gloo.set_clear_depth(10)
        self.show()
        self.data = 0 * np.random.randn(channel_num, 1).astype(np.float32)
        self.data_threa = threading.Thread(target=self.datathread)
        # self.data_threa.start()
        self.head = 0
        self.num = 1

        self.sub_view = SelectedWaveCanvas()

    def get_sub_view(self):
        return self.sub_view

    def datathread(self):
        global data_array_point
        while True:
            if len(self.data[0]) > 50000:
                self.data = self.data[:, 50000:]
                data_array_point = 0
                print('存储，改变i值')
                gloo.clear(color=True, depth=True)
            b, a = signal.butter(8, [0.06, 0.6], 'bandpass')
            filtedData = signal.filtfilt(b, a, amplitudes * np.random.randn(channel_num, 100))
            self.data = numpy.hstack((self.data, filtedData))

    def recv(self, data):
        global data_array_point
        if len(self.data[0]) > 50000:
            self.data = self.data[:, 50000:]
            data_array_point = 0
            print('存储，改变i值')
        # b, a = signal.butter(8, [0.06, 0.6], 'bandpass')
        # filtedData = signal.filtfilt(b, a, data.transpose())
        b, a = signal.iirfilter(5, 300 / 40000 * 2,
                                analog=False, btype='highpass',
                                ftype='butter',output='ba')
        filtedData = signal.filtfilt(b, a, data.T) * 10
        self.data = numpy.hstack((self.data, filtedData))

    def on_timer(self, event):
        # global data_step, data_array_point, k, ylist,color
        global data_step, data_array_point, k
        if data_array_point * data_step + data_step < len(self.data[0]):
            self.temp = self.data[:, data_array_point * data_step: data_array_point * data_step + data_step]
            y,col = get_waves_2(self.temp, channel_num, ylist, color)
            self.program['a_position'].set_data(y)
            self.program['a_color'] = col
            self.update()
            self.sub_view.recv(y[(self.num-1)*50: self.num*50],col[(self.num-1)*50*50: self.num*50*50])

            data_array_point += 1

    def on_mouse_wheel(self, event):
        dx = np.sign(event.delta[1]) * .05
        scale_x, scale_y = self.program['u_scale']
        scale_x_new, scale_y_new = (scale_x * math.exp(.0 * dx),
                                    scale_y * math.exp(2.5 * dx))
        self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
        self.update()

    def on_mouse_press(self, event):
        global color
        i = int(event.pos[0]/(int(self.physical_size[0])/nrows))+1
        j = int(event.pos[1]/(int(self.physical_size[1])/ncols))
        num = j * ncols + i
        self.num = num
        print(num)

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        gloo.set_viewport(0, 0, *self.physical_size)
        self.program.draw('line_strip')

register_node_type(WaveCanvas)
if __name__ == '__main__':
    c = WaveCanvas()
    app.run()