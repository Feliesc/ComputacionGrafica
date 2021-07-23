import obj_reader as oread
import os.path
from OpenGL.GL import *
import grafica.easy_shaders as es

#ponemos la ruta de las texturas y OBJ
thisFilePath = os.path.abspath(__file__)
thisFolderPath = os.path.dirname(thisFilePath)
texturesDirectory = os.path.join(thisFolderPath, "texturas")
meshesDirectory = os.path.join(thisFolderPath, "obj")
graficaDirectory = os.path.join(thisFolderPath, "grafica")


def gpuTable(pipeline):
    tablePath = os.path.join(meshesDirectory, "4.obj")
    tableTexPath = os.path.join(texturesDirectory, "texMesa6.png")
    shapeTable = oread.readOBJ(tablePath)

    gpuTable = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTable)
    gpuTable.texture = es.textureSimpleSetup(
        tableTexPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuTable.fillBuffers(shapeTable.vertices, shapeTable.indices, GL_STATIC_DRAW)
    return gpuTable

def gpuPalo(pipeline):
    cuePath = os.path.join(meshesDirectory, "palo1.obj")
    cueTexPath = os.path.join(texturesDirectory, "palo1.png")
    shapeCue = oread.readOBJ(cuePath)

    gpuCue = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCue)
    gpuCue.texture = es.textureSimpleSetup(
        cueTexPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuCue.fillBuffers(shapeCue.vertices, shapeCue.indices, GL_STATIC_DRAW)
    return gpuCue
