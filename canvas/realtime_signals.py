#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import threading

from scipy import signal

from vispy import gloo
from vispy import app
import numpy as np

VERT_SHADER = """
#version 120

// y coordinate of the position.
attribute float a_position;

// row, col, and time index.
attribute vec3 a_index;
varying vec3 v_index;

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
varying vec3 v_index;

varying vec2 v_position;
varying vec4 v_ab;

void main() {
    gl_FragColor = v_color;

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;

    // Clipping test.
    vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
    if ((test.x > 1) || (test.y > 1))
        discard;
}
"""

nrows = 64
ncols = 1
data_array_point = 0
m = nrows*ncols
n = 40000
amplitudes = .1 + .2 * np.random.rand(m, 1).astype(np.float32)
y = 0 * np.random.randn(m, n).astype(np.float32)
k = 0
data_step = 400

color = .3+0*np.repeat(np.random.uniform(size=(m, 3), low=.5, high=.9),
                  n, axis=0).astype(np.float32)

index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
              np.repeat(np.tile(np.arange(nrows), ncols), n),
              np.tile(np.arange(n), m)].astype(np.float32)
index[:,1] = nrows - 1 -index[:,1]

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive', resizable=True)
        self.size = (400, 2500)
        self.position = (0, 0)
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        self.program['u_n'] = n

        gloo.set_viewport(0, 0, *self.physical_size)
        self._timer = app.Timer(1/100, connect=self.on_timer, start=True, )
        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.show()

        self.data = 0 * np.random.randn(m, 1).astype(np.float32)
        self.data_threa = threading.Thread(target=self.data_thread)
        # self.data_threa.start()

    def data_thread(self):
        global data_array_point
        while True:
            if len(self.data[0]) > 50000:
                self.data = self.data[:, 50000:]
                data_array_point = 0
                print('存储，改变i值')
            self.data = numpy.hstack((self.data, (amplitudes * np.random.randn(m, 100))))

    def recv(self, data):
        global data_array_point
        if len(self.data[0]) > 50000:
            self.data = self.data[:, 50000:]
            data_array_point = 0
            print('存储，改变i值')
        # self.data = numpy.hstack((self.data, data.transpose()))
        # print(len(self.data[0]))
        b, a = signal.iirfilter(5, 300 / 40000 * 2,
                                analog=False, btype='highpass',
                                ftype='butter', output='ba')
        filtedData = signal.filtfilt(b, a, data.T) * 10
        self.data = numpy.hstack((self.data, filtedData))

    # def on_resize(self, event):
    #     print('traceview resize')
    #     gloo.set_viewport(0, 0, *event.physical_size)

    # def on_mouse_wheel(self, event):
    #     dx = np.sign(event.delta[1]) * .05
    #     scale_x, scale_y = self.program['u_scale']
    #     scale_x_new, scale_y_new = (scale_x * math.exp(.0 * dx),
    #                                 scale_y * math.exp(2.5 * dx))
    #     self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
    #     self.update()

    def on_mouse_press(self, event):
        print("mouse pressed", self.physical_size, event.pos)

    def on_timer(self, event):
        global k, data_step, data_array_point, y
        # print('real_time timer')
        if data_array_point*data_step+data_step < len(self.data[0]):
            # print(y)
            self.program['a_position'].set_data(y.ravel().astype(np.float32))
            self.update()
            try:
                y[:, k:(k + data_step)] = self.data[:, data_array_point*data_step:(data_array_point+1)*data_step]
            except Exception as e:
                print(e.__traceback__)
                print(k, data_step, data_array_point)
            k = (k + data_step) % n
            data_array_point += 1

    def on_draw(self, event):
        gloo.clear(depth=10)
        gloo.set_viewport(0, 0, *self.physical_size)
        self.program.draw('line_strip')

    def color_change(self, i):
        global color
        print("real time", i)
        sub_color = np.repeat(np.array([[0, 0, 0.9]]), n, axis=0).astype(np.float32)
        color = .3 + 0 * color
        color[(i-1) * n:i * n, :] = sub_color
        self.program['a_color'] = color


if __name__ == '__main__':
    c = Canvas()
    print(c.native)
    app.run()
