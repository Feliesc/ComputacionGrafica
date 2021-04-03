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

def createCircunferencia(N,Radio,r,g,b):
    # Primer vértice en el centro
    vertices = [Radio, 0, 0, r, g, b]
    indices = []
    dtheta = 2 * math.pi / (N-1)
    for i in range(N):
        theta = i * dtheta
        vertices += [
            # Se le agregan vertices
            Radio * math.cos(theta), Radio * math.sin(theta), 0,
            # colores
            r, g, b]
        # Se agregan los indices
        indices += [i, i+1]
    return Shape(vertices, indices)

def createTrayectoria(N,Radio):
    # Primer vértice en el centro
    vertices = [Radio, 0, 0, 1.0, 1.0, 1.0]
    indices = []
    dtheta = 2 * math.pi / (N-1)
    for i in range(N):
        theta = i * dtheta
        vertices += [
            # Se le agregan vertices
            Radio * math.cos(theta), Radio * math.sin(theta), 0,
            # colores
            1.0, 1.0, 1.0]
        # Se agregan los indices
        indices += [i+1]
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

    # Creando los 2 Shader Program
    simplePipeline = es.SimpleShaderProgram()
    pipeline = es.SimpleTransformShaderProgram()

    # Se pone color negro de fondo
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Creating shapes on GPU memory
    shapeSol = createCircle(30,0.25,1.0,1.0,0.0)
    gpuSol = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSol)
    gpuSol.fillBuffers(shapeSol.vertices, shapeSol.indices, GL_STATIC_DRAW)
    #Haciendo el contorno del Sol
    shapeConSol = createCircunferencia(30,0.25,1.0,0.0,0.0)
    gpuConSol = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuConSol)
    gpuConSol.fillBuffers(shapeConSol.vertices, shapeConSol.indices, GL_STATIC_DRAW)

    #Haciendo la Tierra
    shapeTierra = createCircle(30,0.25,0.1,0.6,0.1)
    gpuTierra = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTierra)
    gpuTierra.fillBuffers(shapeTierra.vertices, shapeTierra.indices, GL_STATIC_DRAW)
    #Creando el Contorno
    shapeConTierra = createCircunferencia(30,0.25,1.0,1.0,1.0)
    gpuConTierra = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuConTierra)
    gpuConTierra.fillBuffers(shapeConTierra.vertices, shapeConTierra.indices, GL_STATIC_DRAW)
    #Creamos la trayectoria de la Tierra al rededor del sol
    shapeTraTierra = createTrayectoria(200,0.73)
    gpuTraTierra = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTraTierra)
    gpuTraTierra.fillBuffers(shapeTraTierra.vertices, shapeTraTierra.indices, GL_STATIC_DRAW)
    #Creamos la trayectoria de la Luna al rededor de la Tierra
    shapeTraLuna = createTrayectoria(50,0.5)
    gpuTraLuna = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTraLuna)
    gpuTraLuna.fillBuffers(shapeTraLuna.vertices, shapeTraLuna.indices, GL_STATIC_DRAW)

    #Haciendo la Luna
    shapeLuna = createCircle(30,0.25,0.25,0.25,0.25)
    gpuLuna = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuLuna)
    gpuLuna.fillBuffers(shapeLuna.vertices, shapeLuna.indices, GL_STATIC_DRAW)
    #Creando el Contorno
    shapeConLuna = createCircunferencia(30,0.25,0.0,0.0,1.0)
    gpuConLuna = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuConLuna)
    gpuConLuna.fillBuffers(shapeConLuna.vertices, shapeConLuna.indices, GL_STATIC_DRAW)

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

        
        #Diciendole a Open-GL que use el shader "normal"
        glUseProgram(simplePipeline.shaderProgram)
        #Dibujando el Sol
        pipeline.drawCall(gpuSol)
        #Dibujando el contorno del Sol
        pipeline.drawCall(gpuConSol, mode=GL_LINES)
        #Dibujando la trayectoria
        pipeline.drawCall(gpuTraTierra, mode=GL_LINES)

        #Diciendole a Open-GL que use el shader de transformaciones
        glUseProgram(pipeline.shaderProgram)

        # Tierra
        tierraTransform = tr.matmul([
            tr.rotationZ(2 * theta),
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.5)
        ])
        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tierraTransform)

        # drawing function
        pipeline.drawCall(gpuTierra)
        pipeline.drawCall(gpuConTierra, mode=GL_LINES)
        pipeline.drawCall(gpuTraLuna, mode=GL_LINES)


        # Luna
        lunaTransform = tr.matmul([
            tr.rotationZ(2 * theta),
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.5),
            tr.rotationZ(2 * theta),
            tr.translate(0.35, 0.35, 0),
            tr.uniformScale(0.5)
        ])
        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, lunaTransform)
        pipeline.drawCall(gpuLuna)
        pipeline.drawCall(gpuConLuna, mode=GL_LINES)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTierra.clear()
    gpuConTierra.clear()
    gpuTraTierra.clear()
    
    glfw.terminate()