import numpy as np
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import openmesh as om
import os.path
from shaders import textureMIPMAPSetup, TexGPUShape, GPUShape
import obj_reader as oreader
from curves import ztongo, CurvasHB, CatmullRomSplines, CatmullRomRiverSplines

#Se crea un modelo geometrico del tobogán (esta función no se utiliza, ya que se usa una malla de poligonos)
def Tobogan(curvas,N=8,R=0.5):
    vertices =[]
    indices =[]

    listaDesfase = [0]
    for curva in curvas:
        desfase = listaDesfase[len(listaDesfase)-1]
        for point in curva:
            vertices +=[point[0], point[1], point[2],   np.random.rand(), np.random.rand(), 0]
            desfase +=1
        listaDesfase += [desfase]
    
    for i in range(len(listaDesfase)-2):
        j=listaDesfase[i]
        while listaDesfase[i] <= j < listaDesfase[i+1]-1:
            desfase = listaDesfase[i+1]-listaDesfase[i]
            indices += [j, j+1, j+desfase]
            indices += [j+1, j+desfase, j+1+desfase]
            j+=1
    
    #el ultimo pedazo de tobogán se hace diferente
    j=listaDesfase[len(listaDesfase)-2]
    k = 0
    while listaDesfase[len(listaDesfase)-2] <= j < listaDesfase[len(listaDesfase)-1]-1:
        indices += [j, j+1, k]
        indices += [j+1, k, k+1]
        j+=1
        k+=1

    return bs.Shape(vertices,indices)


def ToboganMesh(curvas):
    tobogan_mesh = om.TriMesh()
    listaDesfase = [0]#lista que indica el entre qué intervalos están los puntos de cada curva

    for curva in curvas:
        desfase = listaDesfase[len(listaDesfase)-1]
        for point in curva:
            #agregamos cada punto de cada curva a la lista de vértices
            tobogan_mesh.add_vertex(point)
            desfase +=1
        listaDesfase += [desfase]
    
    #ahora creamos las caras con los vertices agregados
    #para eso necesitamos los intervalos que se pusieron en la listaDesfase
    for i in range(len(listaDesfase)-1):
        j=0
        #tomamos en cuenta los vertices de una curva1 y una curva2
        #la curva1 corresponde a la que tiene los vértices en el intervalo [listaDesfase[i],listaDesfase[i+1][
        vertexsCurve1 = list(tobogan_mesh.vertices())[listaDesfase[i]:listaDesfase[i+1]]
        #la curva2 es la que tiene los vértices en el siguiente intervalo (a no ser que la curva 1 sea la ultima curva)
        if i != len(listaDesfase)-2:
            vertexsCurve2 = list(tobogan_mesh.vertices())[listaDesfase[i+1]:listaDesfase[i+2]]
        else:
            #en el caso de que la curva1 sea la ultima curva, se debe conectar esta con la primera curva
            vertexsCurve2 = list(tobogan_mesh.vertices())[listaDesfase[0]:listaDesfase[1]]

        #usando estos vértices, creamos las caras
        while j<listaDesfase[i+1]-listaDesfase[i]-1:
            tobogan_mesh.add_face(vertexsCurve1[j], vertexsCurve2[j], vertexsCurve2[j+1])
            tobogan_mesh.add_face(vertexsCurve2[j+1], vertexsCurve1[j+1], vertexsCurve1[j])
            j+=1
            
    return tobogan_mesh

def RiverMesh(curvas):
    river_mesh = om.TriMesh()
    listaDesfase = [0]#lista que indica el entre qué intervalos están los puntos de cada curva

    for c in range(len(curvas)):
        curva = curvas[c]
        otraCurva = curvas[c-1]
        desfase = listaDesfase[len(listaDesfase)-1]
        for p in range(len(curva)):
            point = curva[p]
            otraCurvaPoint = otraCurva[p]
            #agregamos cada punto de cada curva a la lista de vértices
            diferenciaYmitad = [(point[0]-otraCurvaPoint[0])*0.5,(point[1]-otraCurvaPoint[1])*0.5,
                                (point[2]-otraCurvaPoint[2])*0.5]
            punto = point+diferenciaYmitad

            #agregamos los vértices duplicados, para algo que se hará más adelante
            river_mesh.add_vertex(punto+[0,0,0.2])
            river_mesh.add_vertex(punto+[0,0,0.2])
            desfase +=2
        listaDesfase += [desfase]
    
    #ahora creamos las caras con los vertices agregados
    #para eso necesitamos los intervalos que se pusieron en la listaDesfase
    j=0
    vertexsCurve1 = list(river_mesh.vertices())[listaDesfase[0]:listaDesfase[1]]
    vertexsCurve2 = list(river_mesh.vertices())[listaDesfase[1]:listaDesfase[2]]
    #usando estos vértices, creamos las caras
    while j<listaDesfase[1]-1:
        river_mesh.add_face(vertexsCurve1[j], vertexsCurve2[j], vertexsCurve2[j+1])
        river_mesh.add_face(vertexsCurve2[j+1], vertexsCurve1[j+1], vertexsCurve1[j])
        j+=1
            
    return river_mesh

####################################################################
def get_vertexs_and_indexes(mesh,largoCurva=136):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    # Creamos una lista para los vertices e indices
    vertexs = []
    # Obtenemos los vertices y los recorremos
    x = 0
    j=1
    puntoInicial = list(mesh.points()[0])
    puntoFinal = list(mesh.points()[len(mesh.points())-1])

    for i in range(len(mesh.points())):
        vertex = mesh.points()[i]
        vertexs += vertex.tolist()
        # Agregamos las coordenadas de textura
        if i%2 == 0:
            y = 1
        else:
            y = 0
        vertexs += [x, y]
        if i ==largoCurva*j and x == 0:
            x = 1
            j+=1
        if i ==largoCurva*j and x == 1:
            x = 0
            j+=1

        #también agregamos las normales
        #calculamos la tangente de cada punto
        if list(vertex) != puntoInicial and list(vertex) != puntoFinal:
            vertex0 = mesh.points()[i-1]
            vertex2 = mesh.points()[i+1]
            tangente = [vertex2[0]-vertex0[0], vertex2[1]-vertex0[1], vertex2[2]-vertex0[2]]
        else:
            tangente = [0,1,0]

        #usamos la tangente para obtener la normal a la curva
        normal = np.cross(ztongo,tangente)
        #normalizamos la normal
        NormalizedNormal = normal/np.linalg.norm(normal)
        vertexs += [*list(NormalizedNormal)]    

    indexes = []

    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]

    return vertexs, indexes

#esta función se usa para obtener la info de los vértices del río
def getVertexsandIndexand2DCoords(mesh,largoCurva=136):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    # Creamos una lista para los vertices e indices
    vertexs = []
    # Obtenemos los vertices y los recorremos
    x = -0.5
    j=1
    for i in range(len(mesh.points())):
        vertex = mesh.points()[i]
        vertexs += vertex.tolist()
        # Agregamos las coordenadas 2D
        #como puse los vertices duplicados, no va a haber error al pasarle las coordenadas 2D al shader
        if i%2 == 0:
            y = 0.5
        else:
            y = -0.5
        vertexs += [x, y]
        if i ==2*largoCurva*j and x == -0.5:
            x = 0.5
            j+=1
        if i ==2*largoCurva*j and x == 0.5:
            x = -0.5
            j+=1
        
        vertexs += [0,0,1]

    indexes = []

    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]

    return vertexs, indexes

####################################################################
#ponemos la ruta de las texturas y OBJ
thisFilePath = os.path.abspath(__file__)
thisFolderPath = os.path.dirname(thisFilePath)
assetsDirectory = os.path.join(thisFolderPath, "assets")
assets2Directory = os.path.join(thisFolderPath, "grafica")

def gpuTobogan0(pipeline):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    toboganShape = Tobogan(CurvasHB)
    gpuShape.fillBuffers(toboganShape.vertices, toboganShape.indices, GL_STATIC_DRAW)
    return gpuShape

def gpuTobogan(pipeline):
    cobblestonePath = os.path.join(assetsDirectory, "cobblestone2.jpg")

    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.texture = textureMIPMAPSetup(
        cobblestonePath, GL_REPEAT, GL_REPEAT, GL_NEAREST_MIPMAP_LINEAR, GL_LINEAR)
    tobogan_mesh = ToboganMesh(CatmullRomSplines)
    vertices, indices = get_vertexs_and_indexes(tobogan_mesh)
    gpuShape.fillBuffers(vertices, indices, GL_STATIC_DRAW)
    return gpuShape

def gpuRiver(pipeline):
    waterPath = os.path.join(assetsDirectory, "awa.png")
    displacementPath = os.path.join(assetsDirectory, "displacement2Map.png")

    gpuWater = TexGPUShape().initBuffers()
    pipeline.setupVAO(gpuWater)
    gpuWater.texture = es.textureSimpleSetup(
        waterPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    gpuWater.texture2 = es.textureSimpleSetup(
        displacementPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    river_mesh = RiverMesh(CatmullRomRiverSplines)
    vertices, indices = getVertexsandIndexand2DCoords(river_mesh)
    gpuWater.fillBuffers(vertices, indices, GL_STATIC_DRAW)
    return gpuWater

def gpuBoat(pipeline):
    boatPath = os.path.join(assetsDirectory, "boat.obj")
    shapeBoat = oreader.readOBJ(boatPath, (80/255, 50/255, 15/255))

    gpuBoat = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBoat)
    gpuBoat.fillBuffers(shapeBoat.vertices, shapeBoat.indices, GL_STATIC_DRAW)
    return gpuBoat

def create_sphere():
    N = 20
    vertices = []           # lista para almacenar los verices
    indices = []            # lista para almacenar los indices
    dTheta = 2 * np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    dPhi = 2 * np.pi /N     # angulo que hay entre cada iteracion de la coordenada phi
    rho = 0.5               # radio de la esfera
    c = 0                   # contador de vertices, para ayudar a indicar los indices

    # Se recorre la coordenada theta
    for i in range(N - 1):
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

            if i == 0:
                #           vertices                    color           normales
                vertices += [v0[0], v0[1], v0[2], 0.9, 0.7, 0.55, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.9, 0.7, 0.55, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 0.9, 0.7, 0.55, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3

           
            elif i == (N-2):
                #           vertices                    color           normales
                vertices += [v0[0], v0[1], v0[2], 0.9, 0.7, 0.55, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.9, 0.7, 0.55, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], 0.9, 0.7, 0.55, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            else: 
                #           vertices                    color    normales
                vertices += [v0[0], v0[1], v0[2], 0.9, 0.7, 0.55, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.9, 0.7, 0.55, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 0.9, 0.7, 0.55, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], 0.9, 0.7, 0.55, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)


def create_cilinder(r=200/255 ,g=30/255, b= 30/255):
    N = 20
    z = 0.5
    vertices = [0, 0, -z, r, g, b, 1,0,0]           
    indices = []           
    dTheta = 2 * np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    rho = 0.5               # radio de la esfera
    c = 1                   # contador de vertices, para ayudar a indicar los indices

    # primero creamos el circulo de abajo
    for i in range(N):
        theta = i * dTheta
                        #posición                                 #color        #normal
        vertices += [rho * np.cos(theta), rho * np.sin(theta), -z, r, g, b, np.cos(theta), np.sin(theta), 0]
        c+=1
        indices += [0, i, i+1]
    indices += [0, N, 1]

    vertices += [0, 0, z, r, g, b, 1,0,0]
    
    # Luego creamos el de arriba
    for i in range(N):
        theta = i * dTheta

                        #posición                                 #color        #normal
        vertices += [rho * np.cos(theta), rho * np.sin(theta), z, r, g, b, np.cos(theta), np.sin(theta), 0]

        indices += [c, c+i, c+i+1]
    indices += [c, 2*N+1, c+1]
    #ahora hacemos los rectangulo entre las dos bases
    for i in range(c-1):
        indices += [i,i+1,i+c+1]
        indices += [i+c,i+1+c,i]
    #y agregamos el ultimo rectangulo
    indices += [2*N+1, c+1, 1]
    indices += [2*N+1, c-1, 1]
        
    return bs.Shape(vertices, indices)

def gpuSphere(pipeline):
    shape = create_sphere()
    gpuSphere = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSphere)
    gpuSphere.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuSphere

def gpuCilinder(pipeline,r,g,b):
    shape = create_cilinder(r,g,b)
    gpuCilinder = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCilinder)
    gpuCilinder.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuCilinder

def createBigTexNormalQuad():
    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions        coordsCentradasEn0       normals
        0, 11, 1.75,           -0.5, -0.5,           0,0,1,
        15, 11, 1.75,          0.5, -0.5,            0,0,1,
        15, 21, 1.75,          0.5, 0.5,             0,0,1,
        0, 21, 1.75,           -0.5, 0.5,            0,0,1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

def gpuSea(pipeline):
    gpuWater = GPUShape().initBuffers()
    pipeline.setupVAO(gpuWater)
    seaShape = createBigTexNormalQuad()
    gpuWater.fillBuffers(seaShape.vertices, seaShape.indices, GL_STATIC_DRAW)
    return gpuWater

#hacemos un toroide para simular los neumáticos  
def createColorToroid(N, r, g, b):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    R = 0.4
    radio = 0.2
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


def gpuObstaculo(pipeline):
    shapeToroid = createColorToroid(8, 0.1,0.1,0.1)
    gpuObstaculo = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuObstaculo)
    gpuObstaculo.fillBuffers(shapeToroid.vertices, shapeToroid.indices, GL_DYNAMIC_DRAW)
    return gpuObstaculo
