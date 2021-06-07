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

def CatmullRomMatrix(P1, P2, P3, P4):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, P3, P4), axis=1)
    
    # Catmull-Rom base matrix is a constant
    Mcr = np.array([[0, -0.5, 1, -0.5], [1, 0, -2.5, 1.5], [0, 0.5, 2, -1.5], [0, 0, -0.5, 0.5]])    
    
    return np.matmul(G, Mcr)


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
    curve = np.ndarray(shape=(N, 3), dtype=np.float32)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve
    

if __name__ == "__main__":
    
    """
    Example for Catmull Rom curve
    """
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
    P11 = np.array([[2.5, 1, 0.0]]).T#punto sin curva final

    P00 = [1, -0.3, 2]
    P0 = [1, 0, 2]
    P1 = [1.1, 0.3, 2]
    P2 = [2, 0.6, 2]
    P3 = [1.5, 1, 1.6]
    P4 = [1, 0.8, 1.4]
    P5 = [1.6, 0.5, 1.2]
    P6 = [2.8, 0.5, 1]
    P7 = [2.5, 0, 0.8]
    P8 = [2.1, 0.1, 0.4]
    P9 = [2, 0.5, 0.0]
    P10 =[2.2, 0.9, 0.0]
    P11 =[2.5, 1, 0.0]
    

    puntos = [P00,P0,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11]

    R=0.2
    xtongo = [1,0,0]
    ztongo = [0,0,1]
    # Number of samples to plot 
    N = 8
    #cantidad de curvas que se hacen)
    M = 8
    theta = 2*np.pi/M
    curvas =[]
    CRcurves = []
    for j in range(M):
        dtheta = j*theta
        PUNTOS = puntos.copy()
        POINTS = []
        for i in range(len(PUNTOS)-1):
            point = PUNTOS[i]
            if i == len(point):
                tangente = [point[0]-PUNTOS[i-1][0], point[1]-PUNTOS[i-1][1], point[2]-PUNTOS[i-1][2]]
            else:
                tangente = [PUNTOS[i+1][0]-point[0], PUNTOS[i+1][1]-point[1], PUNTOS[i+1][2]-point[2]]
            normal = np.cross(tangente,ztongo)
            VectorNormalizado = normal/np.linalg.norm(normal)
            productoPunto = np.dot(VectorNormalizado, xtongo)
            dalpha = np.arccos(productoPunto)

            deltaX = R*np.sin(dtheta)*np.cos(dalpha)
            deltaY = R*np.sin(dtheta)*np.sin(dalpha)
            deltaZ = R*np.cos(dtheta)

            x = point[0]+deltaX
            y = point[1]+deltaY
            z = point[2]+deltaZ

            POINTS += [np.array([[x, y, z]]).T]

        for i in range(len(POINTS)-3):
            GMc = CatmullRomMatrix(POINTS[i], POINTS[i+1], POINTS[i+2], POINTS[i+3])
            CRcurve = evalCurve(GMc, N)
            CRcurves += [CRcurve]
        curvas += [np.concatenate((CRcurves[0],CRcurves[1],CRcurves[2],CRcurves[3],CRcurves[4],CRcurves[5],CRcurves[6],CRcurves[7],CRcurves[8]), axis=0)]
    
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    for i in range(len(curvas)):
        plotCurve(ax, curvas[i], "Catmull-Rom"+str(i), (0.1*i,0,1))

    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()