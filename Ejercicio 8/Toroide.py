import numpy as np
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

#Función que crea un toroide de color
def createColorToroid(N, r, g, b):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    R = 0.4
    radio = 0.1
    c = 0

    for i in range(N):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [(R+radio*np.cos(phi))*np.cos(theta), (R+radio*np.cos(phi))*np.sin(theta), radio*np.sin(phi)]
            v1 = [(R+radio*np.cos(phi1))*np.cos(theta), (R+radio*np.cos(phi1))*np.sin(theta), radio*np.sin(phi1)]
            v2 = [(R+radio*np.cos(phi1))*np.cos(theta1), (R+radio*np.cos(phi1))*np.sin(theta1), radio*np.sin(phi1)]
            v3 = [(R+radio*np.cos(phi))*np.cos(theta1), (R+radio*np.cos(phi))*np.sin(theta1), radio*np.sin(phi)]
            n0 = [-np.sin(phi)*np.cos(theta), -np.sin(phi)*np.sin(theta), np.cos(phi)]
            n1 = [-np.sin(phi1)*np.cos(theta), -np.sin(phi1)*np.sin(theta), np.cos(phi1)]
            n2 = [-np.sin(phi1)*np.cos(theta1), -np.sin(phi1)*np.sin(theta1), np.cos(phi1)]
            n3 = [-np.sin(phi)*np.cos(theta1), -np.sin(phi)*np.sin(theta1), np.cos(phi)]


            vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    return bs.Shape(vertices, indices)

#Función que crea un toroide de color
def createTexToroid(N):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    R = 0.4
    radio = 0.1
    c = 0

    for i in range(N):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [(R+radio*np.cos(phi))*np.cos(theta), (R+radio*np.cos(phi))*np.sin(theta), radio*np.sin(phi)]
            v1 = [(R+radio*np.cos(phi1))*np.cos(theta), (R+radio*np.cos(phi1))*np.sin(theta), radio*np.sin(phi1)]
            v2 = [(R+radio*np.cos(phi1))*np.cos(theta1), (R+radio*np.cos(phi1))*np.sin(theta1), radio*np.sin(phi1)]
            v3 = [(R+radio*np.cos(phi))*np.cos(theta1), (R+radio*np.cos(phi))*np.sin(theta1), radio*np.sin(phi)]
            n0 = [-np.sin(phi)*np.cos(theta), -np.sin(phi)*np.sin(theta), np.cos(phi)]
            n1 = [-np.sin(phi1)*np.cos(theta), -np.sin(phi1)*np.sin(theta), np.cos(phi1)]
            n2 = [-np.sin(phi1)*np.cos(theta1), -np.sin(phi1)*np.sin(theta1), np.cos(phi1)]
            n3 = [-np.sin(phi)*np.cos(theta1), -np.sin(phi)*np.sin(theta1), np.cos(phi)]


            vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], 1, 0, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4
    return bs.Shape(vertices, indices)

def createToroidNode(pipeline, path, x, y ,z, r):
    toroid = createTextureGPUShape(createTexToroid(20), pipeline, path)

    toroidNode = sg.SceneGraphNode("toroid")
    toroidNode.transform =tr.matmul([
        tr.translate(x,y,z), tr.rotationX(r)])
    toroidNode.childs = [toroid]

    scaledToroid = sg.SceneGraphNode("sc_toroid")
    scaledToroid.transform = tr.scale(3, 3, 3)
    scaledToroid.childs = [toroidNode]

    return scaledToroid