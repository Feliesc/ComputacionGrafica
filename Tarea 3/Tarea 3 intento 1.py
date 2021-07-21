# coding=utf-8
"""
Ejercicio 9 - Felipe Escárate
Recorriendo una isosuperficie
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys

import grafica.transformations as tr
import grafica.easy_shaders as es
import shaders as sh
from modelosOBJ import *
import figuras as fig
import bolas


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.right = False
        self.left = False
        self.X = False
        self.ballIndex = 0


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
        
    elif (glfw.get_key(window, glfw.KEY_X) == glfw.PRESS):
        controller.ballIndex += 1
        if controller.ballIndex == 16:
            controller.ballIndex = 0

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Tarea 3 - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    texPhongPipeline = sh.SimpleTexturePhongShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    #creamos la mesa de pool
    gpuTable = gpuTable(texPhongPipeline)
    #creamos el palo
    gpuCue = gpuPalo(texPhongPipeline)
    #luego las bolas
    posicionesIniciales = [[0,-4,0.475],
                        [0,3.96,0.475],
                        [-0.15,4.22,0.475],[0.15,4.22,0.475],
                        [-0.3,4.48,0.475],[0,4.48,0.475],[0.3,4.48,0.475],
                        [-0.45,4.74,0.475],[-0.15,4.74,0.475],[0.15,4.74,0.475],[0.45,4.74,0.475],
                        [-0.6,5,0.475],[-0.3,5,0.475],[0,5,0.475],[0.3,5,0.475],[0.6,5,0.475]]
    listaBolas = []
    for i in range(16):
        shape = fig.createGPUball(texPhongPipeline, i)
        bola = bolas.bola(posicionesIniciales[i], 0, shape)
        listaBolas += [bola]

    t0 = glfw.get_time()
    camera_theta = -np.pi/2

    i = 0 #contador para ver a qué bola apunta la cámara
    bolaActual = listaBolas[i]
    at = np.array([bolaActual.pos[0], bolaActual.pos[1], bolaActual.pos[2]])

    while not glfw.window_should_close(window):
        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
    

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        elif (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt
        
        bolaActual = listaBolas[controller.ballIndex]
        at = np.array([bolaActual.pos[0], bolaActual.pos[1], bolaActual.pos[2]])

        camX = at[0] + 5* np.sin(camera_theta)
        camY = at[1] + 5* np.cos(camera_theta)

        viewPos = np.array([camX, camY, 2])

        view = tr.lookAt(
            viewPos,
            at,
            np.array([0,0,1])
        )


        # Telling OpenGL to use our shader program
        glUseProgram(texPhongPipeline.shaderProgram)

        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "La"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ld"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ls"), 1, 1, 1)

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ka"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Kd"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ks"), 1, 1, 1)

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "lightPosition"), 0, 0, 3)
    
        glUniform1ui(glGetUniformLocation(texPhongPipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "constantAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "quadraticAttenuation"), 0.1)

        texPhongPipeline.drawCall(gpuTable)

        for i in range(len(listaBolas)):
            BOLA = listaBolas[i]
            bolaShape = BOLA.shape
            POS = BOLA.pos
            transform = tr.matmul([tr.translate(POS[0],POS[1],POS[2]),tr.uniformScale(0.3)])
            glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
            texPhongPipeline.drawCall(bolaShape)
        
        cueTransform = tr.matmul([tr.translate(at[0],at[1],at[2]),tr.rotationZ(-camera_theta+np.pi),
                                    tr.translate(0,-0.3,0),tr.rotationY(np.pi/32)])
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, cueTransform)
        texPhongPipeline.drawCall(gpuCue)


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()