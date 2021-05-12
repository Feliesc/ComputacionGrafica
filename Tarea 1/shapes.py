"""Funciones para crear distintas figuras y escenas """

import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import shaders as s
import grafica.transformations as tr
import grafica.scene_graph as sg

def createGPUShape(shape, pipeline):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = s.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = s.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = s.textureSimpleSetup(
        path, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createGrassGPUShape(shape, pipeline):
    # Funcion para facilitar la inicializacion del GPUShape del pasto
    grassShape = s.GPUShape().initBuffers()
    pipeline.setupVAO(grassShape)
    grassShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    #Se usa un Mipmap para acomodar la textura (grande) del pasto en el cuadro chico
    grassShape.texture = s.textureMIPMAPSetup(
        "sprites/grass.jpg", GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR)
    return grassShape

def createGrassTextureQuad(x, y, t1, t2):

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions       #texture
        -x, -y,     0.0, t2,
         x, -y,     t1, t2,
         x,  y,     t1, 0.0,
        -x,  y,     0.0, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

def createColorTriangle(r, g, b):
    # Funcion para crear un triangulo con un color personalizado

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  r, g, b,
         0.5, -0.5, 0.0,  r, g, b,
         0.0,  0.5, 0.0,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return bs.Shape(vertices, indices)

def createUkaiEye():
    vertices = [
        0, 0, 0,    1, 1, 1,
        0, 0.3,0,   1, 1, 1,
        0.4, 0, 0,  1, 1, 1,
        0.75, 0.4,0, 1, 1, 1]
    
    indices =[0, 1, 2,
                2, 1, 3]
    return bs.Shape(vertices, indices)

def createUkaiFace():
    vertices = [
        0, 0.05, 0,    0.9, 0.7, 0.55,
        -0.23, 0.2,0,   0.9, 0.7, 0.55,
        0.23, 0.2, 0,  0.9, 0.7, 0.55,
        0.3, 0.62, 0,  0.9, 0.7, 0.55,
        -0.3, 0.62, 0,  0.9, 0.7, 0.55,
        0.0, 0.76, 0,  0.9, 0.7, 0.55]
    
    indices =[0, 1, 2,
              3, 2, 1,
              4, 3, 1,
              5, 4, 3]
    return bs.Shape(vertices, indices)

def createUkaiBody():
    vertices = [
        0, 0.425, 0,        0.9, 0.41, 0.0,
        0.5, 0.425,0,       0.9, 0.41, 0.0,
        0.0, 0.8,0,     0.9, 0.41, 0.0,
        0.5, 0.8, 0,    0.9, 0.41, 0.0,
        0.2, 1.0, 0,    0.9, 0.41, 0.0,
        0.3, 1.0, 0,    0.9, 0.41, 0.0]
    indices = [0,1,2,
              1,2,3,
              2,3,4,
              5,4,3]

    return bs.Shape(vertices, indices)

def createUkaiHair(N):
    # Funcion para crear el pelo del entrenador Ukai

    vertices = []
    indices = []

    dtheta = math.pi / N
    i=0
    while i <N:
        theta = i * dtheta
        phi = (i+0.5)* dtheta   #este ángulo es para los vértices que están más lejos del centro

        vertices += [
            # coords del vértice                                    # color amarillo (pelo ukai)
            0.25 * math.cos(theta), 0.25 * math.sin(theta), 0,        0.9, 0.75, 0.02,
            0.5 * math.cos(phi), 0.5 * math.sin(phi), 0,        0.85, 0.65, 0.02]

        # A triangle is created using the center, this and the next vertex
        indices += [i, i+1, i+2]
        i += 2

    # Al ultimo triángulo le falta un vértice, por lo que se lo agregamos
    vertices += [0.25 * math.cos(math.pi), 0.25 * math.sin(math.pi), 0,        0.9, 0.75, 0.02]

    return bs.Shape(vertices, indices)

def createUkaiRectangle(r, g, b):
    vertices = [
        -1.0, 0.9 , 0.0,        r, g, b,
        0, 0.9 , 0.0,        r, g, b,
        0, 0.75 , 0.0,        r, g, b,
        -1.0, 0.75 , 0.0,        r, g, b]
    indices = [0, 1, 2,
                2, 3, 0]
    return bs.Shape(vertices, indices)

def createColorCircle(N, r, g, b):
    # Funcion para crear un circulo con un color personalizado
    # Poligono de N lados 

    # First vertex at the center, white color
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  r, g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return bs.Shape(vertices, indices)

def create__glasses(N=20):
    vertices = [-0.1, 0 , 0 ,0.1, 0.2, 1]
    indices = []

    dtheta = 2 * math.pi / N

    #Creamos un circulo a la izquierda otro a la derecha y un rectangulo al centro:
    for i in range(N+1):
        theta = i * dtheta
        phi = (i+0.5) * dtheta
        
        vertices += [
            # vertex coordinates                                    colors
            0.2 * math.cos(theta)-0.4, 0.2 * math.sin(theta), 0,        0.1, 0.2, 1, 
            0.3 * math.cos(phi)-0.4, 0.3 * math.sin(phi), 0,        0.1, 0.2, 1]

    #Ahora hacemos los vértices del rectángulo del centro
    vertices += [-0.2, 0.08 , 0 ,   0.1, 0.2, 1,
                -0.2, -0.02 , 0 ,   0.1, 0.2, 1,
                0.2, 0.08 , 0,      0.8, 0.1, 0.1,
                0.2, -0.02 , 0,     0.8, 0.1, 0.1]
    
    #se hacen los indices del circulo izquierdo y el rectángulo del centro
    for i in range(2*N+5):
        indices += [i, i+1, i+2]

    #Finalmente agregamos los vértices e índices del lente derecho
    i = 2*N-1
    while i <= 4*N+6:
        theta = i * dtheta
        phi = (i+0.5) * dtheta
        
        vertices += [
            # vertex coordinates                                    colors
            0.2 * (-math.cos(theta))+0.4, 0.2 * math.sin(theta), 0,        0.8, 0.1, 0.1, 
            0.3 * (-math.cos(phi))+0.4, 0.3 * math.sin(phi), 0,        0.8, 0.1, 0.1]

        indices += [i, i+1, i+2]
        i+=1

    return bs.Shape(vertices, indices)

def createCurveBar(N,L):
    # First vertex at the center, white color
    vertices = []
    indices = []
    dtheta = 2 * math.pi / N
    for i in range(int(N*L)):
        theta = i * dtheta
        vertices += [
            # vertex coordinates                                        colors
            (0.2*math.sin(3*theta)+0.05*(-1)**i), (i/N), 0,        1, 0.6, 0.6]
        indices += [i,i+1,i+2]
    vertices += [0,L, 0,  1, 0.6, 0.6,
                 0,L, 0,  1, 0.6, 0.6]

    return bs.Shape(vertices, indices)


def createWhiteWall():
    vertices = [
        -1.0, 0.0 , 0.0,        0.9,0.9,0.9,
        1.0, 0.0 , 0.0,        0.9,0.9,0.9,
        1.0, 1.0 , 0.0,        0.9,0.9,0.9,
        -1.0, 1.0 , 0.0,        0.9,0.9,0.9]
    indices = [0, 1, 2,
                2, 3, 0]
    return bs.Shape(vertices, indices)

def createDoor():
    vertices = [
        -0.8, 0.0 , 0.0,        0.54,0.27,0.01,
        -0.5, 0.0 , 0.0,        0.54,0.27,0.01,
        -0.5, 0.7 , 0.0,        0.54,0.27,0.01,
        -0.8, 0.7 , 0.0,        0.54,0.27,0.01]
    indices = [0, 1, 2,
                2, 3, 0]
    return bs.Shape(vertices, indices)

def createRectangle(r, g, b):
    vertices = [
        -1.0, 0.9 , 0.0,        r, g, b,
        1.0, 0.9 , 0.0,        r, g, b,
        1.0, 0.75 , 0.0,        r, g, b,
        -1.0, 0.75 , 0.0,        r, g, b]
    indices = [0, 1, 2,
                2, 3, 0]
    return bs.Shape(vertices, indices)

def createWindow():
    vertices = [
        -0.2, 0.25 , 0.0,        0.0,1.0,1.0,
        0.8, 0.25 , 0.0,        0.0,1.0,1.0,
        0.8, 0.7 , 0.0,        0.0,1.0,1.0,
        -0.2, 0.7 , 0.0,        0.0,1.0,1.0]
    indices = [0, 1, 2,
                2, 3, 0]
    return bs.Shape(vertices, indices)