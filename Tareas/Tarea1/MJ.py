import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import shaders as s
import grafica.transformations as tr
import grafica.scene_graph as sg
from shapes import *

def createScene(pipeline):
    # Funcion que crea la escena de modelos geométricos
    # Se crean las shapes en GPU
    gpuGreenTriangle = createGPUShape(createColorTriangle(0, 0.8, 0.4), pipeline) # Shape del triangulo verde
    gpuBrownQuad = createGPUShape(bs.createColorQuad(0.6, 0.3, 0.1), pipeline) # Shape del cuadrado café
    gpuGrayQuad = createGPUShape(bs.createColorQuad(0.5, 0.5, 0.5), pipeline) # Shape del quad gris
    gpuWhiteQuad =  createGPUShape(bs.createColorQuad(1, 1, 1), pipeline) # Shape del quad azul

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

    largeWhiteQuad = sg.SceneGraphNode("limite")
    largeWhiteQuad.transform = tr.matmul([tr.translate(-0.6, 0, 0), tr.scale(0.02, 2, 1)])
    largeWhiteQuad.childs = [gpuWhiteQuad]

    largeWhiteQuad2 = sg.SceneGraphNode("limite2")
    largeWhiteQuad2.transform = tr.matmul([tr.translate(-1.0, 0, 0), tr.scale(0.02, 2, 1)])
    largeWhiteQuad2.childs = [gpuWhiteQuad]

    #Se crea un nodo los dos grupos de árboles (para que se genere el efecto de continuidad al mover la cámara)
    parkNode = sg.SceneGraphNode("park")
    parkNode.childs = [treesNode, trees0Node, trees2Node, largeWhiteQuad, largeWhiteQuad2]

    #Se crea un nodo como el anterior, pero para generar árboles en la derecha
    park2Node = sg.SceneGraphNode("park2")
    park2Node.transform = tr.translate(1.6, 0, 0)
    park2Node.childs = [parkNode]

    # Nodo de la carretera, quad gris escalado y posicionado
    streetNode = sg.SceneGraphNode("highway")
    streetNode.transform = tr.scale(1.2, 2.0, 1)
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
    backGroundNode1.transform = tr.matmul([tr.translate(0, -1.0, 0)])
    backGroundNode1.childs = [streetNode,linesNode, parkNode, park2Node]

    backGroundNode2 = sg.SceneGraphNode("background2")
    backGroundNode2.transform = tr.matmul([tr.translate(0, 2.0, 0)])
    backGroundNode2.childs = [backGroundNode1]

    # Nodo del background con todos los nodos anteriores
    backGroundNode = sg.SceneGraphNode("background")
    backGroundNode.childs = [backGroundNode1, backGroundNode2]

    # Nodo padre de la escena
    sceneNode = sg.SceneGraphNode("world")
    sceneNode.childs = [backGroundNode]

    return sceneNode

#Función que crea un nodo con los lentes
def createGlasses(pipeline, x, y):
    gpuGlasses = createGPUShape(create__glasses(), pipeline)

    glassesNode = sg.SceneGraphNode("lentes")
    glassesNode.transform = tr.matmul([tr.translate(x, y, 0)])
    glassesNode.childs = [gpuGlasses]
    return glassesNode

#Nodo Tienda
def createStore(pipeline):
    gpuWhiteWall = createGPUShape(createWhiteWall(), pipeline)
    gpuDoor = createGPUShape(createDoor(), pipeline)
    gpuBlackRectangle = createGPUShape(createRectangle(0, 0 ,0), pipeline)
    gpuWindow = createGPUShape(createWindow(), pipeline)

    wallNode = sg.SceneGraphNode("wall")
    wallNode.childs = [gpuWhiteWall]

    doorNode = sg.SceneGraphNode("door")
    doorNode.childs = [gpuDoor]

    blackNode = sg.SceneGraphNode("black")
    blackNode.childs = [gpuBlackRectangle]

    windowNode = sg.SceneGraphNode("window")
    windowNode.childs = [gpuWindow]

    ukaiNode = createUkai(pipeline)
    ukaiNode.transform = tr.matmul([tr.scale(0.4, 0.4, 0), tr.translate(0.4, 0.7, 0)])

    StoreNode = sg.SceneGraphNode("store")
    StoreNode.transform = tr.matmul([tr.scale(0.6, 0.6, 0), tr.translate(0, -0.4, 0)])
    StoreNode.childs = [wallNode, doorNode, blackNode, windowNode, ukaiNode]
    return StoreNode

#Función que crea el grafo que contiene el pasto
def createGrassScene(pipeline):
    #se crea la Shape del pasto
    gpuGrass = createGrassGPUShape(createGrassTextureQuad(0.5, 1, 4, 8), pipeline)
    #Se crea el nodo de la zona que tiene pasto
    grassNode1 = sg.SceneGraphNode("grass1")
    grassNode1.transform = tr.matmul([tr.translate(-0.8, -1.0, 0), tr.scale(1, 1, 1)])
    grassNode1.childs = [gpuGrass]

    grassNode2 = sg.SceneGraphNode("grass2")
    grassNode2.transform = tr.matmul([tr.translate(0.8, -1.0, 0), tr.scale(1, 1, 1)])
    grassNode2.childs = [gpuGrass]

    grassNode = sg.SceneGraphNode("grass")
    grassNode.transform = tr.matmul([tr.translate(0, 2.0, 0), tr.scale(1, 1, 1)])
    grassNode.childs = [grassNode1, grassNode2]

    # Se crean el grafo de escena con textura
    grass_scene = sg.SceneGraphNode("grassScene")
    grass_scene.childs = [grassNode1, grassNode2, grassNode]
    return grass_scene

#funcion que genera un grafo del entrenador Ukai
def createUkai(pipeline):
    gpuFace = createGPUShape(createUkaiFace(), pipeline)
    gpuEye = createGPUShape(createUkaiEye(), pipeline)
    gpuEyebrow = createGPUShape(createRectangle(0, 0 ,0), pipeline)
    gpuIris = createGPUShape(createColorCircle(20, 0, 0, 0), pipeline)
    gpuMouth = createGPUShape(createRectangle(0, 0 ,0), pipeline)
    gpuBody = createGPUShape(createUkaiBody(), pipeline)
    gpuHair = createGPUShape(createUkaiHair(10), pipeline)
    gpuHair = createGPUShape(createUkaiHair(10), pipeline)
    gpuBiceps = createGPUShape(createUkaiRectangle(0.9, 0.41, 0), pipeline)
    gpuForearm = createGPUShape(createUkaiRectangle(0.9, 0.7, 0.55), pipeline)

    irisNode= sg.SceneGraphNode("UkaiIris")
    irisNode.transform = tr.matmul([tr.translate(0.25, 0.15, 0), tr.scale(0.3, 0.3, 1)])
    irisNode.childs = [gpuIris]

    EyebrowNode = sg.SceneGraphNode("UkaiEyebrow")
    EyebrowNode.transform = tr.matmul([tr.translate(0.3, 0.0, 0), tr.scale(0.3, 0.5, 1), tr.rotationZ(0.1)])
    EyebrowNode.childs = [gpuEyebrow]

    eyeNode = sg.SceneGraphNode("UkaiEye")
    eyeNode.childs = [gpuEye]

    eyeNode1 = sg.SceneGraphNode("UkaiEye1")
    eyeNode1.transform = tr.matmul([tr.translate(0.12, 0.62, 0), tr.scale(0.15, 0.15, 1)])
    eyeNode1.childs = [eyeNode, irisNode, EyebrowNode]

    eyeNode2 = sg.SceneGraphNode("UkaiEye2")
    eyeNode2.transform = tr.matmul([tr.translate(0.02, 0.62, 0), tr.scale(-0.15, 0.15, 1)])
    eyeNode2.childs = [eyeNode, irisNode ,EyebrowNode]

    faceNode = sg.SceneGraphNode("UkaiFace")
    faceNode.transform = tr.matmul([tr.translate(0.073, 0.32, 0), tr.scale(0.7, 0.7, 1)])
    faceNode.childs = [gpuFace]

    mouthNode1 = sg.SceneGraphNode("UkaiMouth1")
    mouthNode1.transform = tr.matmul([tr.translate(0.07, 0.4, 0), tr.scale(0.05, 0.1, 1)])
    mouthNode1.childs = [gpuMouth]

    mouthNode2 = sg.SceneGraphNode("UkaiMouth2")
    mouthNode2.transform = tr.matmul([tr.translate(0.01, 0.41, 0), tr.scale(0.01, 0.1, 1), tr.rotationZ(-0.1)])
    mouthNode2.childs = [gpuMouth]

    mouthNode = sg.SceneGraphNode("UkaiMouth")
    mouthNode.childs = [mouthNode1, mouthNode2]

    HairNode = sg.SceneGraphNode("UkaiHair")
    HairNode.transform = tr.matmul([tr.translate(0.07, 0.7, 0), tr.scale(0.8, 0.5, 1)])
    HairNode.childs = [gpuHair]

    headNode = sg.SceneGraphNode("UkaiHead")
    headNode.childs = [faceNode, eyeNode1, eyeNode2, mouthNode, HairNode]

    torsoNode = sg.SceneGraphNode("UkaiTorso")
    torsoNode.transform = tr.matmul([tr.translate(-0.18, -0.5, 0), tr.scale(1, 1, 1)])
    torsoNode.childs = [gpuBody]

    forearmTranslateNode = sg.SceneGraphNode("UkaiForearm")
    forearmTranslateNode.transform = tr.matmul([tr.translate(-0.8, 0.35, 0), tr.scale(1.2, 0.6, 1)])
    forearmTranslateNode.childs = [gpuForearm]

    bicepsNode = sg.SceneGraphNode("UkaiArmShape")
    bicepsNode.childs = [gpuBiceps]

    forearmNode = sg.SceneGraphNode("leftForearm")
    forearmNode.childs = [forearmTranslateNode]

    armNode = sg.SceneGraphNode("UkaiArm")
    armNode.transform = tr.matmul([tr.translate(-0.1, -0.325, 0), tr.scale(0.3, 0.7, 1)])
    armNode.childs = [forearmNode, bicepsNode]

    leftArm = sg.SceneGraphNode("leftArm")
    leftArm.childs = [armNode]

    rightArm =sg.SceneGraphNode("rightArm")
    rightArm.transform = tr.matmul([tr.translate(0.1, 0, 0), tr.scale(-1, 1, 1)])
    rightArm.childs = [leftArm]

    bodyNode = sg.SceneGraphNode("UkaiBody")
    bodyNode.childs = [torsoNode, leftArm, rightArm]
    
    UkaiNode = sg.SceneGraphNode("UkaiNode")
    UkaiNode.childs = [bodyNode, headNode]

    return UkaiNode