# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import glfw
import math
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr

# Un entero tiene 4 bytes
SIZE_IN_BYTES = 4

# Se crea el controlador
class Controller:
    fillPolygon = True

# we will use the global controller as communication with the callback function
controller = Controller()

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

def drawCallL(self, gpuShape, mode=GL_LINE):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

#definimos una función para crear un circulo (similar a la de basic_shapes)
def createCircle(N,Radio,r,g,b):
    # Primer vértice en el centro
    vertices = [0, 0, 0, r, g, b]
    indices = []
    dtheta = 2 * math.pi / N
    for i in range(N):
        theta = i * dtheta
        vertices += [
            # Se le agregan vertices
            Radio * math.cos(theta), Radio * math.sin(theta), 0,
            # colores
            r,g,b]
        # Se agregan los indices
        indices += [0, i, i+1]
    # The final triangle connects back to the second vertex
    indices += [0, N, 1]
    return Shape(vertices, indices)

def createCircunferencia(N,Radio):
    vertices = []
    indices = []
    dtheta = 2 * math.pi / N
    for i in range(N):
        theta = i * dtheta
        vertices += [
            # Se le agregan vertices
            Radio * math.cos(theta), Radio * math.sin(theta), 0,
            # colores
            1.0,1.0,1.0]
        # Se agregan los indices
        indices += [0, i, i+1]
    # The final triangle connects back to the second vertex
    indices += [0, N, 1]
    return Shape(vertices, indices)



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Sistema Solar", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Creating shapes on GPU memory
    shapeTierra = createCircle(30,0.5,0.1,1.0,0.1)
    gpuTierra = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTierra)
    gpuTierra.fillBuffers(shapeTierra.vertices, shapeTierra.indices, GL_STATIC_DRAW)

    shapeQuad = bs.createRainbowQuad()
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Using the time as the theta parameter
        theta = glfw.get_time()

        # Tierra
        tierraTransform = tr.matmul([
            tr.translate(0.5, 0.5, 0),
            tr.rotationZ(2 * theta),
            tr.uniformScale(0.5)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tierraTransform)

        # drawing function
        pipeline.drawCall(gpuTierra)

        # Another instance of the triangle
        triangleTransform2 = tr.matmul([
            tr.translate(-0.5, 0.5, 0),
            tr.scale(
                0.5 + 0.2 * np.cos(1.5 * theta),
                0.5 + 0.2 * np.sin(2 * theta),
                0)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, triangleTransform2)
        pipeline.drawCall(gpuTierra)

        # Quad
        quadTransform = tr.matmul([
            tr.translate(-0.5, -0.5, 0),
            tr.rotationZ(-theta),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, quadTransform)
        pipeline.drawCall(gpuQuad)

        # Another instance of the Quad
        quadTransform2 = tr.matmul([
            tr.translate(0.5, -0.5, 0),
            tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, quadTransform2)
        pipeline.drawCall(gpuQuad)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTierra.clear()
    gpuQuad.clear()
    
    glfw.terminate()