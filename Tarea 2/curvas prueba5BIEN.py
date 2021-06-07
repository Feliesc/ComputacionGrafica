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
    P0 = [1, -0.3, 13]
    P1 = [1, 0, 13]
    P2 = [4, 2, 12]
    P3 = [6, 4, 11]
    P4 = [6, 6, 11]
    P5 = [4, 8, 10]
    P6 = [1.5, 7.5, 9.5]
    P7 = [0.75, 6, 9]
    P8 = [1, 4.5, 8.5]
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
            
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    for i in range(len(CatmullRomSplines)):
        plotCurve(ax, CatmullRomSplines[i], "Catmull-Rom"+str(i), (0.1*i,0,1))

    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()