# shapes.py
import ctypes
import numpy as np
import math
import time

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


class GenSphere:
    def run_test(self, num):
        st = time.time()
        for _ in range(num):
            sphere = self.generate_sphere_vertices_manual()
        et = time.time()
        return (et - st) / num, sphere

    @staticmethod
    def graph(particles):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_box_aspect([1, 1, 1])
        ax.scatter(particles[0::3], particles[1::3], particles[2::3], s=1)
        plt.show()
    
    @staticmethod
    def generate_sphere_vertices_manual(r=0.05, stacks=10, sectors=10):
        vertices_size = stacks * sectors * 6
        vertices = np.zeros((vertices_size, 3), dtype=np.float32)
        # List version: vertices = []

        counter = 0
        for i in range(stacks):
            t1 = i / stacks * math.pi
            t2 = (i+1) / stacks * math.pi
            for j in range(sectors):
                p1 = j / sectors * 2 * math.pi
                p2 = (j+1) / sectors * 2 * math.pi

                def getPos(t, p):
                    return [
                        r * math.sin(t) * math.cos(p),
                        r * math.cos(t),
                        r * math.sin(t) * math.sin(p)]

                v1, v2, v3, v4 = getPos(t1, p1), getPos(t2, p1), getPos(t2, p2), getPos(t1, p2)
                vertices[counter:counter+6] = [v1, v2, v3, v2, v4, v3]
                counter += 6
                # For list version: generally slower than a preallocated numpy array
                # vertices.extend(v1 + v2 + v3)
                # vertices.extend(v2 + v4 + v3)
        
        return vertices.flatten()
