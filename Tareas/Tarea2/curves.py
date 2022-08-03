import numpy as np
from water_slide import N


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

def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=np.float32)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

#Ponemos los puntos para la curva de Hermite
H1 = np.array([[1, 2, 13]]).T
H2 = np.array([[6, 6, 7]]).T
HT1 = np.array([[20, 0, 1]]).T
HT2 = np.array([[-20, 1, 0]]).T

GMh = hermiteMatrix(H1, H2, HT1, HT2)
hermiteCurve = evalCurve(GMh, 10)

#ahora para la curva de Bezier

B0 = np.array([[6, 6, 7]]).T
B1 = np.array([[2, 7, 7]]).T
B2 = np.array([[2, 14, 1]]).T
B3 = np.array([[13, 13, 2]]).T
    
GMb = bezierMatrix(B0, B1, B2, B3)
bezierCurve = evalCurve(GMb, 10)

#concatenamos las dos curvas:

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

        #teniendo esto, podemos calcular el punto 
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


########################### AQUI EMPIEZA LO DE CATMULL-ROM #########################################################

def CatmullRomMatrix(P1, P2, P3, P4):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, P3, P4), axis=1)
    
    # Catmull-Rom base matrix is a constant
    Mcr = np.array([[0, -0.5, 1, -0.5], [1, 0, -2.5, 1.5], [0, 0.5, 2, -1.5], [0, 0, -0.5, 0.5]])    
    
    return np.matmul(G, Mcr)

#Ponemos los puntos de la Catmull-Rom Spline
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

R=0.5               #Radio del tobogán
xtongo = [1,0,0]
ztongo = [0,0,1]
# Number of samples to plot 
n = 8
#cantidad de curvas que se hacen)
M = 8
theta = 2*np.pi/M
Splines = []

ListaPuntosRio = []

#creamos las M curvas
for m in range(M):
    dtheta = m*theta
    Puntos = puntos.copy()
    for p in range(len(Puntos)):
        punto = Puntos[p]

        #calculamos la tangente de cada punto
        if punto != Puntos[0] and punto != Puntos[len(Puntos)-1]:
            tangente = [Puntos[p+1][0]-Puntos[p-1][0], Puntos[p+1][1]-Puntos[p-1][1], Puntos[p+1][2]-Puntos[p-1][2]]
        else:
            tangente = [0,1,0]
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

        ##############ESTO ES PARA ALGO QUE SE USA DESPUES#######################################
        #Se guardan los puntos de las curvas con m = 5 y m = 6
        if m==5 or m == 6:
            ListaPuntosRio += [np.array(punto)]
        #########################################################################################
        
    Spline = []
    for p in range(len(puntos)-3):
        i = np.array([[*Puntos[p]]]).T
        ii = np.array([[*Puntos[p+1]]]).T
        iii = np.array([[*Puntos[p+2]]]).T
        iv = np.array([[*Puntos[p+3]]]).T
        GMcr = CatmullRomMatrix(i, ii, iii, iv)
        CatmullRomcurve = evalCurve(GMcr, n)
        Spline += [CatmullRomcurve]
    Splines += [Spline]
    
CatmullRomSplines = []
#aquí se forman las splines que definen el tobogán
for Spline in Splines:
    crSpline = np.concatenate((Spline[0],Spline[1],Spline[2],Spline[3],Spline[4],Spline[5],Spline[6],Spline[7],Spline[8],Spline[9],Spline[10],Spline[11],Spline[12],Spline[13],Spline[14],Spline[15],Spline[16]), axis=0)
    CatmullRomSplines += [crSpline]

#ahora hacemos la spline que define la trayectoria de la cámara (además, guardamos las tangentes y normales normalizadas)
camSpline = []
SplineTan = []
Puntos = puntos.copy()
for p in range(len(Puntos)):
    punto = Puntos[p]
    #calculamos la tangente de cada punto
    if punto != Puntos[0] and punto != Puntos[len(Puntos)-1]:
        tangente = [Puntos[p+1][0]-Puntos[p-1][0], Puntos[p+1][1]-Puntos[p-1][1], Puntos[p+1][2]-Puntos[p-1][2]]
    else:
        tangente = [0,1,0]
    #guardamos la tangente normalizada en una lista
    XYtan = [tangente[0],tangente[1],0]
    normalizedTan = np.array(XYtan)/np.linalg.norm(XYtan)
    SplineTan += [normalizedTan]

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
    punto[0] = punto[0] +R*np.cos(phi)
    punto[1] = punto[1] +R*np.sin(phi)
    punto[2] = punto[2] + 0.1
        
for p in range(len(puntos)-3):
        i = np.array([[*Puntos[p]]]).T
        ii = np.array([[*Puntos[p+1]]]).T
        iii = np.array([[*Puntos[p+2]]]).T
        iv = np.array([[*Puntos[p+3]]]).T
        GMcr = CatmullRomMatrix(i, ii, iii, iv)
        CatmullRomcurve = evalCurve(GMcr, n)
        #no se toma en cuenta el último valor, para que no hayan duplicados
        camSpline += [CatmullRomcurve[0:len(CatmullRomcurve)-1]]

CameraSpline = np.concatenate((camSpline[0],camSpline[1],camSpline[2],camSpline[3],camSpline[4],camSpline[5],camSpline[6],
                                camSpline[7],camSpline[8],camSpline[9],camSpline[10],camSpline[11],camSpline[12],
                                camSpline[13],camSpline[14],camSpline[15],camSpline[16]), axis=0)

#y la spline que describe la trayectoria del bote
boatSpline = []
for p in range(len(puntos)-3):
        i = np.array([[Puntos[p][0],Puntos[p][1],Puntos[p][2]-0.23]]).T
        ii = np.array([[Puntos[p+1][0],Puntos[p+1][1],Puntos[p+1][2]-0.23]]).T
        iii = np.array([[Puntos[p+2][0],Puntos[p+2][1],Puntos[p+2][2]-0.23]]).T
        iv = np.array([[Puntos[p+3][0],Puntos[p+3][1],Puntos[p+3][2]-0.23]]).T
        GMcr = CatmullRomMatrix(i, ii, iii, iv)
        CatmullRomcurve = evalCurve(GMcr, n)#no se toma en cuenta el último valor, para que no hayan duplicados
        boatSpline += [CatmullRomcurve[0:len(CatmullRomcurve)-1]]

BoatSpline = np.concatenate((boatSpline[0],boatSpline[1],boatSpline[2],boatSpline[3],boatSpline[4],boatSpline[5],boatSpline[6],
                                boatSpline[7],boatSpline[8],boatSpline[9],boatSpline[10],boatSpline[11],boatSpline[12],
                                boatSpline[13],boatSpline[14],boatSpline[15],boatSpline[16]), axis=0)

#Ahora hacemos las 2 curvas que describen el río: 
CatmullRomRiverSplines = [CatmullRomSplines[5],CatmullRomSplines[6]]

#ahora guardamos las restas entre los puntos de las curvas que describen el rio, ya que coinciden con las normales
    #de la trayectoria del bote
SplineNormal = []
ListaDiferencias = []
for i in range(20):
    diferencia = ListaPuntosRio[i+20]-ListaPuntosRio[i]
    normal = diferencia/np.linalg.norm(diferencia)
    ListaDiferencias += [diferencia]
    SplineNormal += [normal]
#además, con esto se pueden crear las posiciones de los obstaculos
posicionesObstaculos = []
for k in range(N):
    u = np.random.randint(1,17)
    deltaX = np.random.rand()
    posObstaculo = ListaPuntosRio[u] + ListaDiferencias[u]*deltaX + np.array([0,0,0.2])
    posicionesObstaculos += [posObstaculo]
