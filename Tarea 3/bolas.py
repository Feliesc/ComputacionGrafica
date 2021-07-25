import numpy as np
from numpy.linalg.linalg import _eigvalsh_dispatcher
from edo import *

class bola:
    def __init__(self, ballIndex, pos, vel, shape, coefRoce, C ,mass=0.1, radio=0.15):
        self.pos = np.array(pos)
        self.vel = np.array(vel)
        self.speed = np.linalg.norm(self.vel)
        self.signosVelocidad = [0,0]#BORRAR SI NO USO F
        self.mass = mass
        self.shape = shape
        self.radio = radio
        self.ballIndex = ballIndex
        self.coefRoce = coefRoce
        self.C = C #es el coeficiente de restitución
        self.theta = 0
        self.velAngular = self.speed/self.radio #(esta es la rapidez angular; no velocidad)
        self.anguloRotacion = 0
        self.ejeRotacion = np.array([1,1,1])
        self.enHoyo = False #variable para saber cuando la pelota entra al hoyo
        self.enJuego = True #variable para ver el transcurso de la pelota desde que entra al hoyo hasta que deja de estar en el juego
        self.hermiteCurve = None #cada bola tiene una curva que descrive su trayectoria al caer al hoyo
        self.deltaHermite = 0
        self.indexHermite = 0

    #metodo que revisa la colisión entre la bola y el palo
    def cueCollision(self, cuePos, Energy, focusedBall, theta, dt):
        if cuePos>-0.1 and focusedBall==self.ballIndex:
            #como sabemos: Ec = (1/2)*m*(v)^2
            #entonces: 2Ec/m = v^2
            #con lo cual: v = sqrt(2Ec/m)
            magnitudVelocidad = (2*Energy/self.mass)**(1/2)
            self.vel = np.array([-magnitudVelocidad*np.sin(theta), -magnitudVelocidad*np.cos(theta),0])
            self.speed = np.linalg.norm(self.vel)
            self.theta = theta
    
    def ballCollision(self, listaBolas):
        otrasBolas = listaBolas[0:self.ballIndex] + listaBolas[self.ballIndex+1:len(listaBolas)] 
        for bola in otrasBolas:
            restaPos = [self.pos[0]-bola.pos[0], self.pos[1]-bola.pos[1], self.pos[2]-bola.pos[2]]
            if np.linalg.norm(restaPos)<bola.radio+self.radio:
                #como las bolas tienen la misma masa, se intercambian las rapideces usando el coef de restitución
                rapidezInicial1 = self.speed
                rapidezInicial2 = bola.speed

                self.speed = ((1-self.C)*rapidezInicial1 + (1+self.C)*rapidezInicial2)/1.65
                bola.speed = ((1-self.C)*rapidezInicial2 + (1+self.C)*rapidezInicial1)/1.65

                #la dirección de la velocidad está dada por el lugar donde se golpearon las bolas
                restaPosNormalizado = np.array(restaPos)/np.linalg.norm(restaPos)
                self.vel = self.speed*restaPosNormalizado
                bola.vel = bola.speed*(-restaPosNormalizado)
                
    
    #al chocar con el borde, invertimos el sentido de la velocidad y reducimos su magnitud
    def borderCollision(self):
        if self.pos[0]+self.radio>3 or self.pos[0]-self.radio<-3:
            self.vel[0] = -self.vel[0]
            if self.pos[0]+self.radio>3:
                self.pos[0]=3-self.radio
            else:
                self.pos[0]=self.radio-3
            #una vez que se cambió el sentido, se procede a reducir la velocidad
            self.vel = 0.75*self.vel
            self.speed = 0.75*self.speed
            self.velAngular = self.speed/self.radio

        if self.pos[1]+self.radio>6 or self.pos[1]-self.radio<-6:
            self.vel[1] = -self.vel[1]
            if self.pos[1]+self.radio>6:
                self.pos[1]=6-self.radio
            else:
                self.pos[1]=self.radio-6
            #una vez que se cambió el sentido, se procede a reducir la velocidad
            self.vel = 0.75*self.vel
            self.speed = 0.75*self.speed
            self.velAngular = self.speed/self.radio

    
    def colHole(self):
        #los puntos claves son (-3,6) (3,6) (-3,0) (3,0) (-3,-6) (3,-6)
        #hacemos una comparación para cada uno de los 6 hoyos
        if np.linalg.norm(self.pos-np.array([-3,6.2,0]))<0.6+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([-3,6.2,0]))/np.linalg.norm(self.pos-np.array([-3,6.2,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([-3,6.2,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
        elif np.linalg.norm(self.pos-np.array([3,6.2,0]))<0.6+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([3,6.2,0]))/np.linalg.norm(self.pos-np.array([3,6.2,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([3,6.2,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
        elif np.linalg.norm(self.pos-np.array([-3.25,0,0]))<0.4+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([-3.25,0,0]))/np.linalg.norm(self.pos-np.array([-3,0,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([-3.25,0,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
        elif np.linalg.norm(self.pos-np.array([3.25,0,0]))<0.4+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([3.25,0,0]))/np.linalg.norm(self.pos-np.array([3,0,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([3.25,0,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
        elif np.linalg.norm(self.pos-np.array([-3,-6.2,0]))<0.6+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([-3,-6.2,0]))/np.linalg.norm(self.pos-np.array([-3,-6.2,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([-3,-6.2,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
        elif np.linalg.norm(self.pos-np.array([3,-6.2,0]))<0.6+self.radio:
            self.enHoyo = True
            T1 = (self.pos-np.array([3,-6.2,0]))/np.linalg.norm(self.pos-np.array([3,-6.2,0]))
            T2 = np.array([0,0,-1])
            P1 = self.pos
            P2 = np.array([3,-6.2,-0.75])
            GMh = hermiteMatrix(P1, P2, T1, T2)
            self.hermiteCurve = evalCurve(GMh, 5)
    
    def actualPos(self, dt):
        self.pos[0] = self.pos[0] + self.vel[0]*dt
        self.pos[1] = self.pos[1] + self.vel[1]*dt
    
    
    def update(self, cuePos, Energy, listaBolas, dt, focusedBall, theta):
        if self.enHoyo == False:
            self.colHole()#vemos si la pelota está en el hoyo
        #si la pelota no está en el hoyo, se hace lo siguiente
        if self.enHoyo == False:
            #si la bola se está moviendo
            if self.speed>0:
                #se calcula la velocidad angular y angulo de rotación
                self.velAngular = self.speed/self.radio
                self.anguloRotacion -= self.velAngular*dt
                #se calcula el eje de rotación en función de la velocidad
                ejeRotacionSinNormalizar = np.cross(self.vel,[0,0,1])
                self.ejeRotacion = ejeRotacionSinNormalizar/np.linalg.norm(ejeRotacionSinNormalizar)
                #disminuimos su velocidad y rapidez producto del roce
                self.speed -= self.coefRoce*dt*10
                direccionVelocidad = self.vel/np.linalg.norm(self.vel)
                self.vel = self.vel-self.coefRoce*dt*10*direccionVelocidad
            #imponemos que la bola se quede quieta cuando la rapidez ya se hizo negativa
            else:
                self.vel = np.array([0,0,0])
                self.speed = 0
            
            self.actualPos(dt)
            self.cueCollision(cuePos, Energy, focusedBall, theta, dt)
            self.ballCollision(listaBolas)
            self.borderCollision()

        elif self.enJuego == True:
            #si está en el hoyo pero sigue en juego, se hace la caida de la bola según la curva de Hermite
            if self.deltaHermite<1:
                self.deltaHermite += 0.1
                self.pos[0] = self.hermiteCurve[self.indexHermite][0]*(1-self.deltaHermite) + self.hermiteCurve[self.indexHermite+1][0]*self.deltaHermite
                self.pos[1] = self.hermiteCurve[self.indexHermite][1]*(1-self.deltaHermite) + self.hermiteCurve[self.indexHermite+1][1]*self.deltaHermite
                self.pos[2] = self.hermiteCurve[self.indexHermite][2]*(1-self.deltaHermite) + self.hermiteCurve[self.indexHermite+1][2]*self.deltaHermite
            else:
                if self.indexHermite == 3:
                    self.enJuego = False

                self.deltaHermite = 0
                self.indexHermite += 1
    

    #hacemos algo parecido al método update pero se activa cuando G_Alta = True
    def updateG_Alta(self, t, deltaTime, listaBolas):
        if self.enJuego == True:

            self.ballCollisionGravity(listaBolas)
            self.borderCollision()
            # RK4 integration
            pos1 = self.pos
            vel1 = self.vel
            centroDeMasa, MASA = self.centroDeMasaYMASA(listaBolas)
            k1 = self.velocity(0, pos1, listaBolas)
            k2 = self.velocity(0+deltaTime/2, pos1+(deltaTime/2)*k1, listaBolas)
            k3 = self.velocity(0+deltaTime/2, pos1+(deltaTime/2)*k2, listaBolas)
            k4 = self.velocity(0+deltaTime, pos1+deltaTime*k3, listaBolas)

            self.pos = pos1 + (deltaTime/6)*(k1+2*k2+2*k3+k4)
            self.vel = vel1 + deltaTime*aceleracionGravedad(self.pos, MASA, centroDeMasa)
            


    def velocity(self, deltaTime, pos, listaBolas):
        centroDeMasa, MASA = self.centroDeMasaYMASA(listaBolas)
        #ahora sacamos el potencial al que está sometido esta bola

        vel1 = self.vel
        K1 = aceleracionGravedad(pos, MASA, centroDeMasa)
        K2 = aceleracionGravedad(pos+(deltaTime/2)*K1, MASA, centroDeMasa)
        K3 = aceleracionGravedad(pos+(deltaTime/2)*K2, MASA, centroDeMasa)
        K4 = aceleracionGravedad(pos+deltaTime*K3, MASA, centroDeMasa)

        return vel1 + (deltaTime/6)*(K1+2*K2+2*K3+K4)

    def centroDeMasaYMASA(self, listaBolas):
        otrasBolas = listaBolas[0:self.ballIndex] + listaBolas[self.ballIndex+1:len(listaBolas)]
        
        if len(otrasBolas)>0:
            centroDeMasa = np.array([0.0,0.0,0.0])
            bolasEnJuego = 0
            for bola in otrasBolas:
                if bola.enJuego==True:
                    centroDeMasa += bola.pos
                    bolasEnJuego +=1
            centroDeMasa /= bolasEnJuego
                
            MASA = bolasEnJuego*self.mass #la suma de las masas de las otras bolas
        else:
            centroDeMasa = self.pos
            MASA = 0
        return centroDeMasa, MASA

    def ballCollisionGravity(self, listaBolas):
        otrasBolas = listaBolas[0:self.ballIndex] + listaBolas[self.ballIndex+1:len(listaBolas)] 
        for bola in otrasBolas:
            restaPos = [self.pos[0]-bola.pos[0], self.pos[1]-bola.pos[1], 0]
            norma = np.linalg.norm(restaPos)
            epsilon = bola.radio+self.radio-norma
            if epsilon>0:
                #como las bolas tienen la misma masa, se intercambian las rapideces usando el coef de restitución
                rapidezInicial1 = self.speed
                rapidezInicial2 = bola.speed

                self.speed = ((1-self.C)*rapidezInicial1 + (1+self.C)*rapidezInicial2)/2
                bola.speed = ((1-self.C)*rapidezInicial2 + (1+self.C)*rapidezInicial1)/2

                #la dirección de la velocidad está dada por el lugar donde se golpearon las bolas
                restaPosNormalizado = np.array(restaPos)/np.linalg.norm(restaPos)
                self.vel = self.speed*restaPosNormalizado
                bola.vel = bola.speed*(-restaPosNormalizado)
                
                direccion = np.array(restaPos)/norma
                self.pos = self.pos + (epsilon/2)*direccion
                bola.pos = bola.pos - (epsilon/2)*direccion


############################ FUNCIONES ÚTILES ###########################################################

def aceleracionGravedad(posCuerpo, masa, POS):
    restaVectores = POS-posCuerpo
    r = np.linalg.norm(restaVectores)
    magnitud = 10*masa/(r**2)
    if magnitud>200:
            magnitud = 0.0001
    direccionNormalizada = restaVectores/r
    return magnitud*direccionNormalizada






def hermiteMatrix(P1, P2, T1, T2):
    p1 = np.array([P1]).T
    p2 = np.array([P2]).T
    t1 = np.array([T1]).T
    t2 = np.array([T2]).T
    # Generate a matrix concatenating the columns
    G = np.concatenate((p1, p2, t1, t2), axis=1)
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])    
    return np.matmul(G, Mh)

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=np.float32)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve



        

