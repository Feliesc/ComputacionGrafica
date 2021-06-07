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

def CatmullRomMatrix(P1, P2, T1, T2):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    
    # Catmull-Rom base matrix is a constant
    Mh = np.array([[0, -0.5, 1, -0.5], [1, 0, -2.5, 1.5], [0, 0.5, 2, -1.5], [0, 0, -0.5, 0.5]])    
    
    return np.matmul(G, Mh)


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

P0 = np.array([[-0.3, -0.2, 0.001]]).T#punto sin curva
P1 = np.array([[0, 0, 0.001]]).T
P2 = np.array([[0.4, 0.2, 0.001]]).T
P3 = np.array([[0.6, 0.05, 0.001]]).T
P4 = np.array([[0.9, 0.05, 0.001]]).T
P5 = np.array([[1.1, 0.2, 0.001]]).T
P6 = np.array([[1.5, -0.2, 0.001]]).T
P7 = np.array([[1.9, 0, 0.001]]).T
P8 = np.array([[2, 0.2, 0.001]]).T#punto sin curva final
    
GMc1 = CatmullRomMatrix(P0, P1, P2, P3)
GMc2 = CatmullRomMatrix(P1, P2, P3, P4)
GMc3 = CatmullRomMatrix(P2, P3, P4, P5)
GMc4 = CatmullRomMatrix(P3, P4, P5, P6)
GMc5 = CatmullRomMatrix(P4, P5, P6, P7)
GMc6 = CatmullRomMatrix(P5, P6, P7, P8)
    
# Number of samples to plot
N = 8
    
catmullRomCurve1 = evalCurve(GMc1, N)
catmullRomCurve2 = evalCurve(GMc2, N)
catmullRomCurve3 = evalCurve(GMc3, N)
catmullRomCurve4 = evalCurve(GMc4, N)
catmullRomCurve5 = evalCurve(GMc5, N)
catmullRomCurve6 = evalCurve(GMc6, N)

catmullRomSpline = np.concatenate((catmullRomCurve1,catmullRomCurve2,catmullRomCurve3,catmullRomCurve4,catmullRomCurve5,catmullRomCurve6), axis=0)

catmullRomSpline2 = np.concatenate((catmullRomCurve1,catmullRomCurve2,catmullRomCurve3,catmullRomCurve4,catmullRomCurve5,catmullRomCurve6), axis=0)
for point in catmullRomSpline2:
        #se desplazan todos los puntos de la curva en 0.2 en el eje y
        point[1] = point[1]-0.4

catmullRomSplineBoat = np.concatenate((catmullRomCurve1,catmullRomCurve2,catmullRomCurve3,catmullRomCurve4,catmullRomCurve5,catmullRomCurve6), axis=0)
for point in catmullRomSplineBoat:
        #se desplazan todos los puntos de la curva en 0.2 en el eje y
        point[1] = point[1]-0.2