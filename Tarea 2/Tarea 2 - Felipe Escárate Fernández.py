# coding=utf-8
"""
Ejercicio 9 - Felipe Escárate
Recorriendo una isosuperficie
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import grafica.transformations as tr
import grafica.easy_shaders as es
import SolucionPregunta1 as p1
from Tobogan import *


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Ejercicio 9 - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    #######################################################################
    # Crear gpu gaussiana
    #######################################################################

    # Creamos la malla de la gaussiana
    mesh = p1.create_gaussiana(50, 5)

    # Definimos los valores del rango que queremos nuestra isosuperficie
    MIN_VALUE = 1
    MAX_VALUE = 3

    # Obtenemos la primera cara que se encuentra en el rango buscado
    first_face_in_range = p1.get_isosurface_triangle(mesh, MIN_VALUE, MAX_VALUE)

    # Recorremos la malla desde la cara anterior, obteniendo todas las caras que se encuentran en rango
    faces_in_range = p1.get_in_range_faces(mesh, first_face_in_range, MIN_VALUE, MAX_VALUE, [])

    # Con las caras en rango, creamos una nueva malla
    new_mesh = p1.create_new_mesh(faces_in_range, mesh)

    # Obtenemos los vertices e indices de la nueva malla
    isosurface_vertices, isosurface_indices = p1.get_vertexs_and_indexes(new_mesh)

    # Creamos la GPU shape y la inicializamos
    gpuMalla = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuMalla)
    gpuMalla.fillBuffers(isosurface_vertices, isosurface_indices, GL_STATIC_DRAW)


    # Se crea el Tobogan
    gpuToroid = gpuTobogan(pipeline)

    t0 = glfw.get_time()
    camera_theta = -np.pi/2

    #creamos una lista con las posiciones de un vertice corrrespondiente a cada cara (de la isosuperficie)
    ListaPosiciones = p1.faces_positions(new_mesh)
    #definimos un contador que sirve para ver las caras
    i = 0
    pos = ListaPosiciones[i]    #posición inicial
    delta = 0   #toma valores entre 0 y 1
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        ###################################################################################################################
        #Vemos que si delta es mayor a uno lo hacemos 0 y tomamos a la siguiente cara como "posición inicial"
        if delta>1:
            delta = 0
            i +=1
            pos = ListaPosiciones[i]
        #si no, seguimos aumentando delta para que el objeto se desplace a la siguiente cara
        else:
            delta += 3*dt
        ###################################################################################################################
    

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        # Setting up the view transform

        camX = 20 * np.sin(camera_theta)
        camY = 20 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 15])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform
        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes with different model transformations
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        pipeline.drawCall(gpuToroid)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()