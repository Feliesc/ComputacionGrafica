"""Funciones para crear distintas figuras y escenas """

import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import shaders as s
import grafica.transformations as tr
import grafica.ex_curves as cv
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
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

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

def evalMixCurve(N):
    # Funcion para generar N puntos entre 0 y 1 de una curva personalizada
    # Hermite + Bezier para modelar la superficie de un auto

    # Puntos de Control
    P0 = np.array([[0.07, 0.14, 0]]).T
    P1 = np.array([[0.27, -0.04, 0]]).T
    P2 = np.array([[0.42, 0.06, 0]]).T
    P3 = np.array([[0.5, -0.06, 0]]).T
    P4 = np.array([[-0.5, -0.06, 0]]).T
    T0 = np.array([[-0.13, 0.35, 0]]).T
    alpha = 1
    T1 = 3 * alpha * (P1 - P0)
    # Matrices de Hermite y Beziers
    H_M = cv.hermiteMatrix(P4, P0, T0, T1)
    B_M = cv.bezierMatrix(P0, P1, P2, P3)

    # Arreglo de numeros entre 0 y 1
    ts = np.linspace(0.0, 1.0, N//2)
    offset = N//2 
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(len(ts) * 2, 3), dtype=float)
    
    # Se llenan los puntos de la curva
    for i in range(len(ts)):
        T = cv.generateT(ts[i])
        curve[i, 0:3] = np.matmul(H_M, T).T
        curve[i + offset, 0:3] = np.matmul(B_M, T).T
        
    return curve

def createColorChasis(r, g, b):
    # Crea un shape del chasis de un auto a partir de una curva personalizada
    vertices = []
    indices = []
    curve = evalMixCurve(64) # Se obtienen los puntos de la curva
    delta = 1 / len(curve) # distancia del step /paso
    x_0 = -0.5 # Posicion x inicial de la recta inferior
    y_0 = -0.2 # Posicion y inicial de la recta inferior
    counter = 0 # Contador de vertices, para indicar los indices

    # Se generan los vertices
    for i in range(len(curve)-1):
        c_0 = curve[i] # punto i de la curva
        r_0 = [x_0 + i*delta, y_0] # punto i de la recta
        c_1 = curve[i + 1] # punto i + 1 de la curva
        r_1 = [x_0 + (i+1)*delta, y_0] # punto i + 1 de la recta
        vertices += [c_0[0], c_0[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_0[0], r_0[1], 0, r, g, b]
        vertices += [c_1[0], c_1[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_1[0], r_1[1], 0, r, g, b]
        indices += [counter + 0, counter +1, counter + 2]
        indices += [counter + 2, counter + 3, counter + 1]
        counter += 4

    return bs.Shape(vertices, indices)


def createCar(pipeline):
    # Se crea la escena del auto de la pregunta 1

    # Se crean las shapes en GPU
    gpuChasis = createGPUShape(createColorChasis(0.7, 0, 0), pipeline) # Shape del chasis 
    gpuGrayCircle =  createGPUShape(createColorCircle(20, 0.4, 0.4, 0.4), pipeline) # Shape del circulo gris
    gpuBlackCircle =  createGPUShape(createColorCircle(20, 0, 0, 0), pipeline) # Shape del circulo negro
    gpuBlueQuad = createGPUShape(bs.createColorQuad(0.2, 0.2, 1), pipeline) # Shape de quad azul

    # Nodo del chasis rojo
    redChasisNode = sg.SceneGraphNode("redChasis")
    redChasisNode.childs = [gpuChasis]

    # Nodo del circulo gris
    grayCircleNode = sg.SceneGraphNode("grayCircleNode")
    grayCircleNode.childs = [gpuGrayCircle]
    
    # Nodo del circulo negro
    blackCircleNode = sg.SceneGraphNode("blackCircle")
    blackCircleNode.childs = [gpuBlackCircle]

    # Nodo del quad celeste
    blueQuadNode = sg.SceneGraphNode("blueQuad")
    blueQuadNode.childs = [gpuBlueQuad]

    # Nodo del circulo gris escalado
    scaledGrayCircleNode = sg.SceneGraphNode("slGrayCircle")
    scaledGrayCircleNode.transform = tr.scale(0.6, 0.6, 0.6)
    scaledGrayCircleNode.childs = [grayCircleNode]

    # Nodo de una rueda, escalado
    wheelNode = sg.SceneGraphNode("wheel")
    wheelNode.transform = tr.scale(0.22, 0.22, 0.22)
    wheelNode.childs = [blackCircleNode, scaledGrayCircleNode]

    # Nodo de la ventana, quad celeste escalado
    windowNode = sg.SceneGraphNode("window")
    windowNode.transform = tr.scale(0.22, 0.15, 1)
    windowNode.childs = [blueQuadNode]
     
    # Rueda izquierda posicionada
    leftWheel = sg.SceneGraphNode("lWheel")
    leftWheel.transform = tr.translate(-0.3, -0.2, 0)
    leftWheel.childs = [wheelNode]

    # Rueda derecha posicionada
    rightWheel = sg.SceneGraphNode("rWheel")
    rightWheel.transform = tr.translate(0.26, -0.2, 0)
    rightWheel.childs = [wheelNode]

    # Ventana posicionada
    translateWindow = sg.SceneGraphNode("tlWindow")
    translateWindow.transform = tr.translate(-0.08, 0.06, 0.0)
    translateWindow.childs = [windowNode]

    # Nodo padre auto
    carNode = sg.SceneGraphNode("car")
    carNode.childs = [redChasisNode, translateWindow, leftWheel, rightWheel]

    return carNode

def createScene(pipeline):
    # Funcion que crea la escena de la pregunta 2

    # Se crean las shapes en GPU
    gpuGreenTriangle = createGPUShape(createColorTriangle(0.1, 0.7, 0.1), pipeline) # Shape del triangulo verde
    gpuBrownQuad = createGPUShape(bs.createColorQuad(0.6, 0.3, 0.1), pipeline) # Shape del cuadrado café
    gpuGrayQuad = createGPUShape(bs.createColorQuad(0.5, 0.5, 0.5), pipeline) # Shape del quad gris
    gpuWhiteQuad =  createGPUShape(bs.createColorQuad(1, 1, 1), pipeline) # Shape del quad azul

 ###############CREAR NODOS ARBOLEEES 

    #se crea el tronco de un arbol
    logNode = sg.SceneGraphNode("log")
    logNode.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(0.03, 0.1, 1)])
    logNode.childs = [gpuBrownQuad]
    #Se crean las hojas del arbol
    leafNode = sg.SceneGraphNode("leafs")
    leafNode.transform = tr.matmul([tr.translate(0, 0.1, 0), tr.scale(0.1, 0.2, 1)])
    leafNode.childs = [gpuGreenTriangle]
    #Se crea el primer arbol
    treeNode = sg.SceneGraphNode("tree")
    treeNode.childs = [logNode, leafNode]
    #Se crea un arbol parecido pero más delgado
    thinTreeNode = sg.SceneGraphNode("thintree")
    thinTreeNode.transform = tr.matmul([tr.scale(0.4, 1.3, 0),tr.translate(-0.08, 0.3, 0)])
    thinTreeNode.childs = [treeNode]
    #Se crea un arbol alto
    tallerTreeNode = sg.SceneGraphNode("tallertree")
    tallerTreeNode.transform = tr.matmul([tr.scale(0.6, 2.0, 0),tr.translate(0.4, 0, 0)])
    tallerTreeNode.childs = [treeNode]
    #Se crea un arbol grueso
    heavyTreeNode = sg.SceneGraphNode("heavytree")
    heavyTreeNode.transform = tr.matmul([tr.translate(0.13, 0.3, 0),tr.scale(1.6, 0.7, 0)])
    heavyTreeNode.childs = [treeNode]
    #Arbol chueco
    fallingTreeNode = sg.SceneGraphNode("fallingtree")
    fallingTreeNode.transform = tr.matmul([tr.translate(0.2, 0.55, 0),tr.scale(0.6, 2.0, 0),tr.shearing(-0.3,0,0,0,0,0)])
    fallingTreeNode.childs = [treeNode]
    #Árbol chueco 2 
    fallingTree2Node = sg.SceneGraphNode("fallingtree2")
    fallingTree2Node.transform = tr.matmul([tr.translate(0.07, 0.7, 0),tr.scale(0.8, 1.1, 0),tr.shearing(0.3,0,0,0,0,0)])
    fallingTree2Node.childs = [treeNode]


    #Se crea un nodo con un grupo de todos los tipos de arboles
    treesNode = sg.SceneGraphNode("trees")
    treesNode.transform = tr.matmul([tr.translate(-0.9, 0, 0)])
    treesNode.childs = [treeNode, fallingTreeNode, fallingTree2Node, heavyTreeNode, thinTreeNode, tallerTreeNode]

    #Se copia el grupo de árboles pero se traslada hacia arriba
    trees2Node = sg.SceneGraphNode("trees2")
    trees2Node.transform = tr.matmul([tr.translate(0, 1.0, 0)])
    trees2Node.childs = [treesNode]

    #Se copia el grupo de árboles pero se traslada hacia abajo
    trees0Node = sg.SceneGraphNode("trees0")
    trees0Node.transform = tr.matmul([tr.translate(0, -1.0, 0)])
    trees0Node.childs = [treesNode]

    #Se crea un nodo los dos grupos de árboles (para que se genere el efecto de continuidad al mover la cámara)
    parkNode = sg.SceneGraphNode("park")
    parkNode.childs = [treesNode, trees0Node, trees2Node]

    #Se crea un nodo como el anterior, pero para generar árboles en la derecha
    park2Node = sg.SceneGraphNode("park")
    park2Node.transform = tr.matmul([tr.translate(1.6, 0, 0)])
    park2Node.childs = [parkNode]


    # Nodo de la carretera, quad gris escalado y posicionado
    streetNode = sg.SceneGraphNode("highway")
    streetNode.transform = tr.matmul([tr.scale(1.2, 2.0, 1)])
    streetNode.childs = [gpuGrayQuad]
    
    # nodo de la linea de pista, quad blanco escalado y posicionado
    lineNode = sg.SceneGraphNode("line")
    lineNode.transform = tr.matmul([tr.translate(0, -0.5, 0), tr.scale(0.02, 0.5, 1)])
    lineNode.childs = [gpuWhiteQuad]

    line2Node = sg.SceneGraphNode("line2")
    line2Node.transform = tr.matmul([tr.translate(0, 0.5, 0), tr.scale(0.02, 0.5, 1)])
    line2Node.childs = [gpuWhiteQuad]

    linesNode = sg.SceneGraphNode("lines")
    linesNode.childs = [lineNode, line2Node]

    backGroundNode1 = sg.SceneGraphNode("background1")
    backGroundNode1.transform = tr.matmul([tr.translate(0, 1.0, 0)])
    backGroundNode1.childs = [streetNode,linesNode, parkNode, park2Node]

    backGroundNode2 = sg.SceneGraphNode("background2")
    backGroundNode2.transform = tr.matmul([tr.translate(0, -2.0, 0)])
    backGroundNode2.childs = [backGroundNode1]


    # Nodo del background con todos los nodos anteriores
    backGroundNode = sg.SceneGraphNode("background")
    backGroundNode.childs = [backGroundNode1, backGroundNode2]

    # Nodo padre de la escena
    sceneNode = sg.SceneGraphNode("world")
    sceneNode.childs = [backGroundNode]

    return sceneNode