# coding=utf-8
"""Hermite and Bezier curves using python, numpy and matplotlib"""

import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

__author__ = "Daniel Calderon"
__license__ = "MIT"


def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def hermiteMatrix(P1, P2, T1, T2):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])    
    
    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)


def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)
    

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

if __name__ == "__main__":
    
    """
    Example for Hermite curve
    """
    
    P1 = np.array([[3, 2, 13]]).T
    P2 = np.array([[6, 6, 7]]).T
    T1 = np.array([[15, 0, 1]]).T
    T2 = np.array([[-15, 1, 0]]).T
    
    GMh = hermiteMatrix(P1, P2, T1, T2)
    print(GMh)
    
    # Number of samples to plot
    N = 8
    
    hermiteCurve = evalCurve(GMh, N)
    
    # Setting up the matplotlib display for 3
    
    """
    Example for Bezier curve
    """
    
    R0 = np.array([[6, 6, 7]]).T
    R1 = np.array([[2, 7, 7]]).T
    R2 = np.array([[2, 14, 1]]).T
    R3 = np.array([[13, 13, 2]]).T
    
    GMb = bezierMatrix(R0, R1, R2, R3)
    bezierCurve = evalCurve(GMb, N)
    
    curvaHermiteBezier = np.concatenate((hermiteCurve,bezierCurve), axis=0)

    M = 8
    R =0.5
    theta = 2*np.pi/M
    CurvasHB = []
    xtongo = [1,0,0]
    ztongo = [0,0,1]

    ListaPuntosRio0 = []

    #creamos las M curvas
    for m in range(M):
        dtheta = m*theta
        Puntos = curvaHermiteBezier.copy()
        for p in range(len(Puntos)):
            punto = list(Puntos[p])

            #calculamos la tangente de cada punto
            if punto != list(Puntos[0]) and punto != list(Puntos[len(Puntos)-1]):
                tangente = [Puntos[p+1][0]-Puntos[p-1][0], Puntos[p+1][1]-Puntos[p-1][1], Puntos[p+1][2]-Puntos[p-1][2]]
            else:
                tangente = [1,0,0]
            #usamos la tangente para obtener la normal a la curva
            normal = np.cross(ztongo,tangente)
            #normalizamos la normal
            NormalizedNormal = normal/np.linalg.norm(normal)

            #ahora buscamos el ángulo entre la normal de la curva y xtongo
            productoPunto = np.dot(xtongo, NormalizedNormal)
            if NormalizedNormal[1]>=0:
                phi = np.arccos(productoPunto)
            else:
                phi = -np.arccos(productoPunto)

            #tediendo esto, podemos calcular el punto 
            punto[0] = punto[0] +R*np.sin(dtheta)*np.cos(phi)
            punto[1] = punto[1] +R*np.sin(dtheta)*np.sin(phi)
            punto[2] = punto[2] +R*np.cos(dtheta)

            Puntos[p] =np.array([punto[0],punto[1],punto[2]])

            ##############ESTO ES PARA ALGO QUE SE USA DESPUES#######################################
            #Se guardan los puntos de las curvas con m = 5 y m = 6
            if m==5 or m == 6:
                ListaPuntosRio0 += [np.array(punto)]
            #########################################################################################
            
        CurvasHB += [Puntos]
        

    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    for i in range(len(CurvasHB)):
        plotCurve(ax, CurvasHB[i], "s"+str(i), (0.13*i,0,1))


    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()