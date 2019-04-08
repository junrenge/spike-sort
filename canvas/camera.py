# -*- coding: utf-8 -*-

try:
    import cv2
except Exception:
    raise ImportError("You need OpenCV for this example.")

import numpy as np
from vispy import app
from vispy import gloo
import matplotlib.image as mpimg

vertex = """
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_texcoord = texcoord;
    }
"""

fragment = """
    uniform sampler2D texture;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(texture, v_texcoord);

        // HACK: the image is in BGR instead of RGB.
        //float temp = gl_FragColor.r;
        //gl_FragColor.r = gl_FragColor.b;
        //gl_FragColor.b = temp;
    }
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(640, 480), keys='interactive')
        self.program = gloo.Program(vertex, fragment, count=4)
        self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.program['texcoord'] = [(1, 1), (1, 0), (0, 1), (0, 0)]
        self.program['texture'] = np.zeros((480, 640, 3)).astype(np.uint8)

        width, height = self.physical_size
        gloo.set_viewport(0, 0, width, height)
        self._timer = app.Timer(1, connect=self.on_timer, start=True)
        self.show()
        self.n = 0

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear('black')
        self.program.draw('triangle_strip')

    def on_timer(self, event):
        s = 'D:/online-sorting-2/canvas/'+str(self.n+1)+'.jpg'
        img = mpimg.imread(s)
        img = cv2.resize(img, (640, 480))
        img = img.reshape((480, 640, -1))
        self.program['texture'] = img
        self.n = (self.n+1) % 3
        self.update()

if __name__ == '__main__':
    c = Canvas()
    app.run()
