import numpy as np
from edo import *

class bola:
    def __init__(self, ballIndex, pos, vel, shape, coefRoce, C ,mass=0.1, radio=0.15):
        self.pos = np.array(pos)
        self.vel = np.array(vel)
        self.speed = np.linalg.norm(self.vel)
        self.signosVelocidad = [0,0]
        self.mass = mass
        self.shape = shape
        self.radio = radio
        self.ballIndex = ballIndex
        self.coefRoce = coefRoce
        self.C = C #es el coeficiente de restitución
        self.theta = 0
        self.velAngular = self.speed/self.radio
        self.anguloRotacion = 0
        self.ejeRotacion = np.array([1,1,1])
        
    #metodo que revisa la colisión entre la bola y el palo
    def cueCollision(self, cuePos, Force, focusedBall, theta, dt):
        if cuePos>-0.1 and focusedBall==self.ballIndex:
            #como sabemos: Impulso = Δp = F*Δt
            #entonces: pf - pi = pf = F*Δt = F*dt
            #con lo cual: m*vf = F*dt -> vf = F*dt/m
            magnitudVelocidad = Force*dt/self.mass
            self.vel = np.array([-magnitudVelocidad*np.sin(theta), -magnitudVelocidad*np.cos(theta),0])
            self.speed = np.linalg.norm(self.vel)
            self.theta = theta
    
    def ballCollision(self, listaBolas):
        otrasBolas = listaBolas[0:self.ballIndex] + listaBolas[self.ballIndex+1:len(listaBolas)] 
        for bola in otrasBolas:
            restaPos = [self.pos[0]-bola.pos[0], self.pos[1]-bola.pos[1], self.pos[2]-bola.pos[2]]
            if np.linalg.norm(restaPos)<bola.radio+self.radio:
                #como las bolas tienen la misma masa, se intercambian las rapideces
                self.speed, bola.speed = bola.speed, self.speed
                rapidezInicial1 = self.speed
                rapidezInicial2 = bola.speed

                self.speed = ((1-self.C)*rapidezInicial1 + (1+self.C)*rapidezInicial2)/2
                bola.speed = ((1-self.C)*rapidezInicial1 + (1+self.C)*rapidezInicial2)/2

                #la dirección de la velocidad está dada por el lugar donde se golpearon las bolas
                restaPosNormalizado = np.array(restaPos)/np.linalg.norm(restaPos)
                self.vel = self.speed*restaPosNormalizado
                bola.vel = bola.speed*(-restaPosNormalizado)

                self.velAngular = self.speed/self.radio
                bola.velAngular = bola.speed/bola.radio
                
    
    def borderCollision(self):
        if self.pos[0]+self.radio>3 or self.pos[0]-self.radio<-3:
            self.vel[0] = -self.vel[0]
            self.velAngular = self.speed/self.radio
            if self.pos[0]+self.radio>3:
                self.pos[0]=3-self.radio
            else:
                self.pos[0]=self.radio-3
        if self.pos[1]+self.radio>6 or self.pos[1]-self.radio<-6:
            self.vel[1] = -self.vel[1]
            self.velAngular = self.speed/self.radio
            if self.pos[1]+self.radio>6:
                self.pos[1]=6-self.radio
            else:
                self.pos[1]=self.radio-6
    
    def actualPos(self, dt):
        self.pos[0] = self.pos[0] + self.vel[0]*dt
        self.pos[1] = self.pos[1] + self.vel[1]*dt
    
    #función que se aproxima mediante métodos numéricos
    def F(self, t, Z):
        gravedad = 10
        magnitudAceleracion = gravedad*self.coefRoce
        aceleracion = np.array([0,0,0])
        if self.signosVelocidad[0]*self.vel[0]<0:
            aceleracion[0] = -magnitudAceleracion*np.sin(self.theta)
        if self.signosVelocidad[1]*self.vel[1]<0:
            aceleracion[1] = -magnitudAceleracion*np.cos(self.theta)

        return np.array([Z[1], aceleracion])
    
    def update(self, cuePos, Force, listaBolas, t ,dt, focusedBall, theta):
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
            self.vel = self.vel+self.coefRoce*dt*10*np.array([np.sin(self.theta),np.cos(self.theta),0])
        #imponemos que la bola se quede quieta cuando la rapidez ya se hizo negativa
        else:
            self.vel = np.array([0,0,0])
            self.speed = 0
        
        self.actualPos(dt)
        self.cueCollision(cuePos, Force, focusedBall, theta, dt)
        self.ballCollision(listaBolas)
        self.borderCollision()
        

        

