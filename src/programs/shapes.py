# shapes.py
import ctypes
import numpy as np

from OpenGL.GL import *


class Triangle:
    def __init__(self, size):
        self.size = size
        self.vertices = np.array([
            -0.75, -0.75,0.0,1.0, 0.0, 0.0,
            0.0,  0.75,0.0, 0.0, 1.0,  0.0,
            0.75,  -0.75, 0.0, 0.0,  0.0, 1.0,
            ],dtype=np.float32)

        self._create_triangle(size)

    def change_size(self, size):
        self.size = size
        self._create_triangle(size)

    def _create_triangle(self, change:float=0):
        # Scale the vertex positions by the specified size
        self.vertices[0:3] = self.vertices[0:3] * change
        self.vertices[6:9] = self.vertices[6:9] * change
        self.vertices[12:15] = self.vertices[12:15] * change
        
        # fmt: off | on ?
        # allocate a VertexArray
        self.vao_id = glGenVertexArrays(1)
        # now bind a vertex array object for our verts
        glBindVertexArray(self.vao_id)

        vbo_id = glGenBuffers(1)
        #  now bind this to the VBO buffer
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
        #  allocate the buffer data
        # Use .nbytes for numpy arrays to get the total byte size. OpenGL can sometimes struggle on MacOS with this.
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #  now fix this to the attribute buffer 0
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(0))
        #  enable and bind this attribute (will be inPosition in the shader)
        glEnableVertexAttribArray(0)
        #  now fix this to the attribute buffer 0
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(self.vertices.itemsize * 3))
        #  enable and bind this attribute (will be inPosition in the shader)
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)