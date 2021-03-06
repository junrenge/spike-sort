from vispy import gloo
from vispy import app
import numpy as np
import math


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

wavenum_per_channel = 50
wave_len = 50
pointnum_per_channel = wave_len * wavenum_per_channel
y = np.random.randint(0, 1, size=[50, 50]).astype(np.float32)
color = 1 + np.zeros((pointnum_per_channel, 3)).astype(np.float32)
t=[]
for wavenum in range(wavenum_per_channel):
    for point in range(wave_len):
        t.append([0, 0, point, wavenum])
index = np.array(t).astype(np.float32)
print(1)

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive')
        self.shape = (1, 1)
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = self.shape
        self.program['u_n'] = wave_len
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.set_state(preset='additive', clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        gloo.set_clear_depth(10)
        self.show()

    def on_mouse_wheel(self, event):
        dx = np.sign(event.delta[1]) * .05
        scale_x, scale_y = self.program['u_scale']
        scale_x_new, scale_y_new = (scale_x * math.exp(.0 * dx),
                                    scale_y * math.exp(2.5 * dx))
        self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
        self.update()

    def on_mouse_press(self, event):
        print("mouse pressed", self.physical_size, event.pos)

    def recv(self, x, c):
        self.program['a_position'].set_data(x.ravel().astype(np.float32))
        self.program['a_color'].set_data(c.reshape(-1, 3).astype(np.float32))
        self.update()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        gloo.set_viewport(0, 0, *self.physical_size)
        self.program.draw('line_strip')
