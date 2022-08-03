import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import os
from OpenGL.GL import *

IMG_PATH = f"{os.path.dirname(__file__)}"

def createTextureQuad(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions        texture     normales
        -0.5, -0.5, 0.0,  0, ny,    0,0,1,
         0.5, -0.5, 0.0, nx, ny,    0,0,1,
         0.5,  0.5, 0.0, nx, 0,     0,0,1,
        -0.5,  0.5, 0.0,  0, 0,     0,0,1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

#Creamos el piso
def create_floor(pipeline):
    shapeFloor = createTextureQuad(10, 10)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(
        f"{IMG_PATH}/madera.jpg", GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)
    return gpuFloor