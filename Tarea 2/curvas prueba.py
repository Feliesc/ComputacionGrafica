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

    #for point in catmullRomSpline:
        #se desplazan todos los puntos de la curva en 0.5 en el eje y
        #point[1] = point[1]+0.5
        #print(point[1])

    NN=8
    theta = 2*np.pi/NN
    curvas =[]

    for j in range(NN):
        dtheta = j*theta
        curvas.append(catmullRomSpline.copy())
        for point in curvas[j]:
            point[0] = point[0]+0.2*np.cos(dtheta)
            point[2] = point[2]+0.2*np.sin(dtheta)

    print(curvas[1])
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    plotCurve(ax, catmullRomSpline, "Catmull-Rom spline", (0,1,1))
    for i in range(len(curvas)):
        plotCurve(ax, curvas[i], "Catmull-Rom"+str(i), (0.1*i,0,1))

    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()