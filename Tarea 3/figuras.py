import numpy as np
from PIL import Image
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
    rho = 0.15               # radio de la esfera
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


#ahora hacemos los rectángulos para la barra de fuerza
def createBackgroundRectangle():
    vertices = [
    #   positions        colors
        -0.5, -1, 0.0,  0.2, 0.2, 1.0,
         0.5, -1, 0.0,  0.2, 0.2, 1.0,
         0.5,  1, 0.0,  0.2, 0.2, 1.0,
        -0.5,  1, 0.0,  0.2, 0.2, 1.0]
    indices = [
        0, 1, 2,
        2, 3, 0]
    return bs.Shape(vertices, indices)

def createBarRectangle():
    vertices = [
    #   positions        colors
        -0.45, -0.95, 0.0,  0.2, 1.0, 0.2,
         0.45, -0.95, 0.0,  0.2, 1.0, 0.2,
         0.45,  0.95, 0.0,  0.2, 1.0, 0.2,
        -0.45,  0.95, 0.0,  0.2, 1.0, 0.2]
    indices = [
        0, 1, 2,
        2, 3, 0]
    return bs.Shape(vertices, indices)

def createGPURectangles(pipeline):
    backShape = createBackgroundRectangle()
    gpuBack = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBack)
    gpuBack.fillBuffers(backShape.vertices, backShape.indices, GL_STATIC_DRAW)

    barShape = createBarRectangle()
    gpuBar = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBar)
    gpuBar.fillBuffers(barShape.vertices, barShape.indices, GL_STATIC_DRAW)
    return [gpuBack, gpuBar]

def createShadowQuad():
    vertices = [
    #   positions     texCoords
        -0.15, -0.15,  0, 1, 
         0.15, -0.15,  1, 1,
         0.15,  0.15,  1, 0,
        -0.15,  0.15,  0, 0]
    indices = [
        0, 1, 2,
        2, 3, 0]
    return bs.Shape(vertices, indices)

def createGPUshadowQuad(pipeline):
    shadowPath = os.path.join(texturesDirectory, "sombraBola.png")
    quadShape = createShadowQuad()
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)

    gpuQuad.texture = es.textureSimpleSetup(
        shadowPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuQuad.fillBuffers(quadShape.vertices, quadShape.indices, GL_STATIC_DRAW)
    return gpuQuad



def createBigTextureSphere(N):
    # Funcion para crear una esfera con normales y texturizada

    vertices = []           # lista para almacenar los verices
    indices = []            # lista para almacenar los indices
    dTheta = 2*np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    dPhi = 2 * np.pi /N     # angulo que hay entre cada iteracion de la coordenada phi
    rho = 50               # radio de la esfera
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
            n0 = [-np.sin(theta)*np.cos(phi), -np.sin(theta)*np.sin(phi), -np.cos(theta)]
            n1 = [-np.sin(theta1)*np.cos(phi), -np.sin(theta1)*np.sin(phi), -np.cos(theta1)]
            n2 = [-np.sin(theta1)*np.cos(phi1), -np.sin(theta1)*np.sin(phi1), -np.cos(theta1)]
            n3 = [-np.sin(theta)*np.cos(phi1), -np.sin(theta)*np.sin(phi1), -np.cos(theta)]

                #           vertices           UV coord                      normales
            vertices += [v0[0], v0[1], v0[2], phi/(2*np.pi), theta/(np.pi), n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], phi/(2*np.pi), theta1/(np.pi), n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], phi1/(2*np.pi), theta1/(np.pi), n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], phi1/(2*np.pi), theta/(np.pi), n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 2, c + 3, c + 0 ]
            c += 4

    return bs.Shape(vertices, indices)

def createGPUbigSphere(pipeline):
    texPath = os.path.join(texturesDirectory, "fondo3.png")
    ballShape = createBigTextureSphere(40)

    gpuBall = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBall)
    gpuBall.texture = es.textureSimpleSetup(
        texPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuBall.fillBuffers(ballShape.vertices, ballShape.indices, GL_STATIC_DRAW)
    return gpuBall




def textureRGBASetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = Image.open(imgName)
    img_data = np.array(list(image.getdata()), np.uint8)

    internalFormat = GL_RGBA
    format = GL_RGBA

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, image.size[0], image.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)

    return texture

#ahora hacemos la linea de la trayectoria
def createLineaPunteada(puntoInicio, tan, N):
    normal = np.cross(tan,[0,0,1])
    largo = 12  #largo de la mesa
    dx = largo/N
    vertices = []
    indices = []
    p0 = np.array([puntoInicio[0], puntoInicio[1]])

    vertice = lambda i: p0+ dx*i*tan

    i=1
    #se crean cuadrados y triángulos para marcar la trayectoria
    while i <= N:
        p1 = vertice(i)
        #si el cuadrado estaría fuera de la mesa, se rompe el ciclo
        if p1[0]>3 or p1[0]<-3 or p1[1]>6 or p1[1]<-6:
            break
        p2 = vertice(i+1)
        vertices += [p1[0]+normal[0]*0.025, p1[1]+normal[1]*0.025, 1, 1, 1]
        vertices += [p1[0]-normal[0]*0.025, p1[1]-normal[1]*0.025, 1, 1, 1]
        vertices += [p2[0]+normal[0]*0.025, p2[1]+normal[1]*0.025, 1, 1, 1]
        vertices += [p2[0]-normal[0]*0.025, p2[1]-normal[1]*0.025, 1, 1, 1]
        #ahora hacemos la punta de la flecha
        vertices += [p2[0], p2[1], 1, 1, 1]
        vertices += [vertice(i+2)[0], vertice(i+2)[1], 1, 1, 1]
        vertices += [p2[0]+normal[0]*0.05, p2[1]+normal[1]*0.05, 1, 1, 1]
        vertices += [p2[0]-normal[0]*0.05, p2[1]-normal[1]*0.05, 1, 1, 1]

        indices += [8*i, 8*i+1, 8*i+3,
                    8*i+3, 8*i+2, 8*i]
        
        indices += [8*i+4, 8*i+5, 8*i+6,
                    8*i+4, 8*i+5, 8*i+7]

        
        i+=2

    return bs.Shape(vertices, indices)

def createGPULine(pipeline, puntoInicio, tan, N):
    lineShape = createLineaPunteada(puntoInicio, tan, N)
    gpuLine = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuLine)
    gpuLine.fillBuffers(lineShape.vertices, lineShape.indices, GL_DYNAMIC_DRAW)
    return gpuLine



