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

P00 = np.array([[1, -0.3, 2]]).T#punto sin curva
P0 = np.array([[1, 0, 2]]).T
P1 = np.array([[1.1, 0.3, 2]]).T
P2 = np.array([[2, 0.6, 2]]).T
P3 = np.array([[1.5, 1, 1.6]]).T
P4 = np.array([[1, 0.8, 1.4]]).T
P5 = np.array([[1.6, 0.5, 1.2]]).T
P6 = np.array([[2.8, 0.5, 1]]).T
P7 = np.array([[2.5, 0, 0.8]]).T
P8 = np.array([[2.1, 0.1, 0.4]]).T
P9 = np.array([[2, 0.5, 0.0]]).T
P10 = np.array([[2.2, 0.9, 0.0]]).T
P11 = np.array([[2.5, 1, 0.0]]).T#punto sin curva finall

GMc0 = CatmullRomMatrix(P00, P0, P1, P2)    
GMc1 = CatmullRomMatrix(P0, P1, P2, P3)
GMc2 = CatmullRomMatrix(P1, P2, P3, P4)
GMc3 = CatmullRomMatrix(P2, P3, P4, P5)
GMc4 = CatmullRomMatrix(P3, P4, P5, P6)
GMc5 = CatmullRomMatrix(P4, P5, P6, P7)
GMc6 = CatmullRomMatrix(P5, P6, P7, P8)
GMc7 = CatmullRomMatrix(P6, P7, P8, P9)
GMc8 = CatmullRomMatrix(P7, P8, P9, P10)
GMc9 = CatmullRomMatrix(P8, P9, P10, P11)
    
# Number of samples to plot
N = 8

CRcurve0 = evalCurve(GMc0, N)  
CRcurve1 = evalCurve(GMc1, N)
CRcurve2 = evalCurve(GMc2, N)
CRcurve3 = evalCurve(GMc3, N)
CRcurve4 = evalCurve(GMc4, N)
CRcurve5 = evalCurve(GMc5, N)
CRcurve6 = evalCurve(GMc6, N)
CRcurve7 = evalCurve(GMc7, N)
CRcurve8 = evalCurve(GMc8, N)
CRcurve9 = evalCurve(GMc9, N)


catmullRomSpline = np.concatenate((CRcurve0,CRcurve1,CRcurve2,CRcurve3,CRcurve4,CRcurve5,CRcurve6,CRcurve7,CRcurve8,CRcurve9), axis=0)


def Tobogan(curva,N=8,R=0.2):
    vertices =[]
    indices =[]
    theta = 2*np.pi/N
    curvas =[]

    for j in range(N):
        dtheta = j*theta
        curvas.append(curva.copy())
        for point in curvas[j]:
            point[0] = point[0]+0.2*np.cos(dtheta)
            point[2] = point[2]+0.2*np.sin(dtheta)

    j=0
    curve = curvas[j]
    curve2 = curvas[j+1]

    i = 0
    vertices += [curve[i][0], curve[i][1], curve[i][2],     0, 1, 1]
    vertices += [curve2[i][0], curve2[i][1], curve2[i][2],     0, 1, 1]
    while i < len(curve)-1:
        vertices += [curve[i+1][0], curve[i+1][1], curve[i+1][2],     0, 1, 1]
        vertices += [curve2[i+1][0], curve2[i+1][1], curve2[i+1][2],     0, 1, 1]

        indices += [i, i+1, i+2]
        indices += [i+1, i+2, i+3]

        i+=1


    j = 1
    curve = curvas[j]
    desfase = len(vertices)-1
    while j < N-1:
        if j%2 ==0:
            curve2 = curvas[j+1]
        else:
            curve2= (curvas[j+1])[::-1]
        i = 0
        vertices += [curve[i][0], curve[i][1], curve[i][2],     0, 1, 1]
        vertices += [curve2[i][0], curve2[i][1], curve2[i][2],     0, 1, 1]
        while i < len(curve)-1:
            vertices += [curve[i+1][0], curve[i+1][1], curve[i+1][2],     0, 1, 1]
            vertices += [curve2[i+1][0], curve2[i+1][1], curve2[i+1][2],     0, 1, 1]

            indices += [i+desfase, i+1+desfase, i+2+desfase]
            indices += [i+1+desfase, i+2+desfase, i+3+desfase]

            i+=1
        desfase = len(vertices)-1
        curve = curve2[::-1]
        j+=1



    return bs.Shape(vertices,indices)

def gpuTobogan(pipeline):
    shape = Tobogan(catmullRomSpline,N=8,R=0.2)
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape