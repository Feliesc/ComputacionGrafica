import grafica.scene_graph as sg
import grafica.transformations as tr
from meshesYmodelos import gpuBoat, gpuCilinder, gpuSphere
import numpy as np


def createBoatNode(pipeline):
    gpuboat = gpuBoat(pipeline)
    gpuBodyOrArm = gpuCilinder(pipeline, 200/255, 80/255, 0)
    gpuHead = gpuSphere(pipeline)

    BoatNode = sg.SceneGraphNode("Bote")
    BoatNode.transform = tr.matmul([tr.translate(0,0.75,0),tr.rotationX(np.pi/2)])
    BoatNode.childs = [gpuboat]

    armNode = sg.SceneGraphNode("brazo")
    armNode.transform = tr.scale(0.25,0.25,1.25)
    armNode.childs = [gpuBodyOrArm]

    leftArmNode = sg.SceneGraphNode("brazoIzquierdo")
    leftArmNode.transform = tr.translate(0,1,0.5)
    leftArmNode.childs = [armNode]

    rightArmNode = sg.SceneGraphNode("brazoDerecho")
    rightArmNode.transform = tr.translate(0,-1,0.5)
    rightArmNode.childs = [armNode]

    LarmRotationNode = sg.SceneGraphNode("LrotorBrazo")
    LarmRotationNode.transform = tr.rotationX(3*np.pi/2)
    LarmRotationNode.childs =[leftArmNode]

    RarmRotationNode = sg.SceneGraphNode("RrotorBrazo")
    RarmRotationNode.transform = tr.rotationX(-3*np.pi/2)
    RarmRotationNode.childs =[rightArmNode]

    brazosNode = sg.SceneGraphNode("Brazos")
    brazosNode.transform = tr.translate(0,0,1.5)
    brazosNode.childs = [LarmRotationNode, RarmRotationNode]

    bodyNode = sg.SceneGraphNode("cuerpo")
    bodyNode.transform = tr.matmul([tr.scale(1,1,1.2)])
    bodyNode.childs = [gpuBodyOrArm]

    headNode = sg.SceneGraphNode("cabeza")
    headNode.transform = tr.matmul([tr.translate(0,0,1),tr.scale(0.75,0.75,0.75)])
    headNode.childs = [gpuHead]

    personNode = sg.SceneGraphNode("persona")
    personNode.transform = tr.matmul([tr.translate(0,0,0.5)])
    personNode.childs = [brazosNode,bodyNode,headNode]

    boatNode = sg.SceneGraphNode("bote")
    boatNode.childs = [BoatNode, personNode]
    return boatNode