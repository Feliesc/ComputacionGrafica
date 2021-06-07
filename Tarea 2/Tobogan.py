import numpy as np
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def CatmullRomMatrix(P1, P2, P3, P4):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, P3, P4), axis=1)
    
    # Catmull-Rom base matrix is a constant
    Mcr = np.array([[0, -0.5, 1, -0.5], [1, 0, -2.5, 1.5], [0, 0.5, 2, -1.5], [0, 0, -0.5, 0.5]])    
    
    return np.matmul(G, Mcr)

def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=np.float32)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

P0 = [1, -0.3, 13]
P1 = [1, 0, 13]
P2 = [4, 2, 12]
P3 = [6, 4, 11]
P4 = [6, 6, 11]
P5 = [4, 8, 10]
P6 = [3, 8, 10]
P7 = [1, 6, 9]
P8 = [1, 5, 9]
P9 = [3, 3, 8]
P10 =[7, 3, 8]
P11 =[9, 5, 7]
P12 = [9, 8, 7]
P13 = [11, 10, 6]
P14 = [13, 8, 5]
P15 = [11, 6, 4]
P16 = [10, 6, 4]
P17 = [8, 8, 3]
P18 = [8, 11, 2]
P19 = [8, 13, 2]
    

puntos = [P0,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18,P19]

R=0.3
xtongo = [1,0,0]
ztongo = [0,0,1]
# Number of samples to plot 
N = 8
#cantidad de curvas que se hacen)
M = 8
theta = 2*np.pi/M
Splines = []
    
#creamos las M curvas
for m in range(M):
    dtheta = m*theta
    Puntos = puntos.copy()
    for p in range(len(Puntos)):
        punto = Puntos[p]
        if punto != Puntos[0] and punto != Puntos[len(Puntos)-1]:
            tangente = [Puntos[p+1][0]-Puntos[p-1][0], Puntos[p+1][1]-Puntos[p-1][1], Puntos[p+1][2]-Puntos[p-1][2]]
        else:
            tangente = [0,1,0]
        normal = np.cross(ztongo,tangente)
        NormalizedNormal = normal/np.linalg.norm(normal)

        productoPunto = np.dot(xtongo, NormalizedNormal)
        if NormalizedNormal[1]>=0:
            phi = np.arccos(productoPunto)
        else:
            phi = -np.arccos(productoPunto)

        punto[0] = punto[0] +R*np.sin(dtheta)*np.cos(phi)
        punto[1] = punto[1] +R*np.sin(dtheta)*np.sin(phi)
        punto[2] = punto[2] +R*np.cos(dtheta)
        
    Spline = []
    for p in range(len(puntos)-3):
        i = np.array([[*Puntos[p]]]).T
        ii = np.array([[*Puntos[p+1]]]).T
        iii = np.array([[*Puntos[p+2]]]).T
        iv = np.array([[*Puntos[p+3]]]).T
        GMcr = CatmullRomMatrix(i, ii, iii, iv)
        CatmullRomcurve = evalCurve(GMcr, N)
        Spline += [CatmullRomcurve]
    Splines += [Spline]
    
CatmullRomSplines = []
for Spline in Splines:
    crSpline = np.concatenate((Spline[0],Spline[1],Spline[2],Spline[3],Spline[4],Spline[5],Spline[6],Spline[7],Spline[8],Spline[9],Spline[10],Spline[11],Spline[12],Spline[13],Spline[14],Spline[15],Spline[16]), axis=0)
    CatmullRomSplines += [crSpline]


def Tobogan(curvas,N=8,R=0.2):
    vertices =[]
    indices =[]

    listaDesfase = [0]
    for curva in curvas:
        desfase = listaDesfase[len(listaDesfase)-1]
        for point in curva:
            vertices +=[point[0], point[1], point[2],   0, np.random.rand(), np.random.rand()]
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

def gpuTobogan(pipeline):
    shape = Tobogan(CatmullRomSplines,N=8,R=0.2)
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape