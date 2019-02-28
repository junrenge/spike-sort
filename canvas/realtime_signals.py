#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Multiple real-time digital signals with GLSL-based clipping.
"""
import numpy
import threading
import time

from vispy import gloo
from vispy import app
import numpy as np
import math

#数据
# Number of cols and rows in the table.
nrows = 64
ncols = 1
i = 0
# Number of signals.
m = nrows*ncols
# Number of samples per signal.
n = 40000
# Various signal amplitudes.
amplitudes = .1 + .2 * np.random.rand(m, 1).astype(np.float32)
# Generate the signals as a (m, n) array.
y = 0 * np.random.randn(m, n).astype(np.float32)
k = 0
s = 1000
#颜色
# Color of each vertex (TODO: make it more efficient by using a GLSL-based
# color map and the index).
color = np.repeat(np.random.uniform(size=(m, 3), low=.5, high=.9),
                  n, axis=0).astype(np.float32)
# Signal 2D index of each vertex (row and col) and x-index (sample index
# within each signal).
index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
              np.repeat(np.tile(np.arange(nrows), ncols), n),
              np.tile(np.arange(n), m)].astype(np.float32)

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

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        self.program['u_n'] = n

        gloo.set_viewport(0, 0, *self.physical_size)
        self._timer = app.Timer('auto', connect=self.on_timer, start=True, )
        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.show()

        self.data = 0 * np.random.randn(m, 1).astype(np.float32)
        self.data_thread = threading.Thread(target=self.data_thread)
        self.data_thread.start()

    def data_thread(self):
        global i
        while True:
            if len(self.data[0]) > 100000:
                self.data = self.data[:,:1]
                i = 0
                print('存储，改变i值')
            self.data = numpy.hstack((self.data,(amplitudes * np.random.randn(m, 100))))

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_mouse_wheel(self, event):
        dx = np.sign(event.delta[1]) * .05
        scale_x, scale_y = self.program['u_scale']
        scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
                                    scale_y * math.exp(0.0*dx))
        self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
        self.update()

    def on_mouse_press(self, event):
        print("mouse pressed", self.physical_size, event.pos)

    def on_timer(self, event):
        global k, s, i
        if i*s+s < len(self.data[0]):
            self.program['a_position'].set_data(y.ravel().astype(np.float32))
            self.update()
            # y[:, k:(k+s)] = amplitudes * np.random.randn(m, s)
            y[:, k:(k + s)] = self.data[:, i*s:i*s+s]
            k = (k + s)%n#实现推进绘图的效果
            i += 1
            # y[:, :-k] = y[:, k:]
            # y[:, -k:] =  amplitudes * np.random.randn(m, k)
            # y[:, k%100:(k+10)%100] = amplitudes * np.random.randn(m, 10)

    def on_draw(self, event):
        gloo.clear(depth=10)
        self.program.draw('line_strip')

    def paramchange(self,p):
        print("canvas paramchanged!",p.props)

if __name__ == '__main__':
    c = Canvas()
    app.run()
