import numpy as np
import os.path
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es


def createTextureNormalSphere(N):
    # Funcion para crear una esfera con normales y texturizada

    vertices = []           # lista para almacenar los verices
    indices = []            # lista para almacenar los indices
    dTheta = 2*np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    dPhi = 2 * np.pi /N     # angulo que hay entre cada iteracion de la coordenada phi
    rho = 0.5               # radio de la esfera
    c = 0                   # contador de vertices, para ayudar a indicar los indices

    # Se recorre la coordenada theta
    for i in range(int(N/2)):
        theta = i * dTheta # angulo theta en esta iteracion
        theta1 = (i + 1) * dTheta # angulo theta en la iteracion siguiente
         # Se recorre la coordenada phi
        for j in range(N):
            phi = j*dPhi # angulo phi en esta iteracion
            phi1 = (j+1)*dPhi # angulo phi en la iteracion siguiente

            # Se crean los vertices necesarios son coordenadas esfericas para cada iteracion

            # Vertice para las iteraciones actuales de theta (i) y phi (j) 
            v0 = [rho*np.sin(theta)*np.cos(phi), rho*np.sin(theta)*np.sin(phi), rho*np.cos(theta)]
            # Vertice para las iteraciones siguiente de theta (i + 1) y actual de phi (j) 
            v1 = [rho*np.sin(theta1)*np.cos(phi), rho*np.sin(theta1)*np.sin(phi), rho*np.cos(theta1)]
            # Vertice para las iteraciones actual de theta (i) y siguiente de phi (j + 1) 
            v2 = [rho*np.sin(theta1)*np.cos(phi1), rho*np.sin(theta1)*np.sin(phi1), rho*np.cos(theta1)]
            # Vertice para las iteraciones siguientes de theta (i + 1) y phi (j + 1) 
            v3 = [rho*np.sin(theta)*np.cos(phi1), rho*np.sin(theta)*np.sin(phi1), rho*np.cos(theta)]

            # Se crean los vectores normales para cada vertice segun los valores de rho tongo 
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]

                #           vertices           UV coord                      normales
            vertices += [v0[0], v0[1], v0[2], phi/(2*np.pi), theta/(np.pi), n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], phi/(2*np.pi), theta1/(np.pi), n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], phi1/(2*np.pi), theta1/(np.pi), n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], phi1/(2*np.pi), theta/(np.pi), n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4

    return bs.Shape(vertices, indices)

#ponemos la ruta de las texturas y OBJ
thisFilePath = os.path.abspath(__file__)
thisFolderPath = os.path.dirname(thisFilePath)
texturesDirectory = os.path.join(thisFolderPath, "texturas")

def createGPUball(pipeline, num):
    texPath = os.path.join(texturesDirectory, "Ball"+str(num)+".jpg")
    ballShape = createTextureNormalSphere(20)

    gpuBall = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBall)
    gpuBall.texture = es.textureSimpleSetup(
        texPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuBall.fillBuffers(ballShape.vertices, ballShape.indices, GL_STATIC_DRAW)
    return gpuBall