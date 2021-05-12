""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import grafica.transformations as tr

class Player():
    # Clase que contiene al modelo del player
    def __init__(self, size):
        self.pos = [0,-0.8] # Posicion actual (cambia a medida que avanza Hinata)
        self.contadorPosY= -0.8  #Posición en la pantalla en el eje Y (no se va a cambiar hasta que aparezca la tienda en la escena)
        self.vel = [1,1] # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.075 # distancia para realiozar los calculos de colision
        self.storeIsPlaced = False
        self.gameOver = False
        self.youWin = False

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):
        # Se actualiza la posicion de Hinata

        #### Se usa la posición en el eje Y solo como método para ver cuando spawnear lentes o dibujar el modelo de la tienda
        #Si se presiona la W el contador de posición del personaje aumenta en el eje Y
        if self.controller.is_w_pressed:
            self.contadorPosY += self.vel[1] * delta
        #Si se presiona la S el contador de posición del personaje disminuye en el eje Y
        if self.controller.is_s_pressed:
            self.contadorPosY -= self.vel[1] * delta
        ##############################################################################################
        # Si detecta la tecla [D] presionada y no se ha salido de la calle se mueve hacia la derecha
        if self.controller.is_d_pressed and self.pos[0]<0.5:
            self.pos[0] += self.vel[0] * delta
        # Si detecta la tecla [A] presionada se mueve hacia la izquierda
        if self.controller.is_a_pressed and self.pos[0]>-0.5:
            self.pos[0] -= self.vel[0] * delta

        # Se le aplica la transformacion de traslado segun la posicion actual
        # La traslación depende si ya llegó la tienda a la escena o no

        # ahora vemos lo que sucede cuando aparece la tienda
        #Si se presiona la W la posición del personaje aumenta en el eje Y
        if self.storeIsPlaced ==True:
            if self.controller.is_w_pressed:
                self.pos[1] += self.vel[1] * delta
            #Si se presiona la S el contador de posición del personaje disminuye en el eje Y
            if self.controller.is_s_pressed:
                self.pos[1] -= self.vel[1] * delta

        

    def collision(self, cargas):
        # Funcion para detectar las colisiones con las cargas

        # Se recorren las cargas 
        for carga in cargas:
            # si la distancia a la carga es menor que la suma de los radios ha ocurrido en la colision y la carga está infectada
            if (self.radio+carga.radio)**2 > ((self.pos[0]-carga.move[0])**2 + (self.pos[1]-carga.move[1])**2) and carga.infected == True:
                self.gameOver = True
                return


class Background():
    # Clase que contiene al modelo del player / auro
    def __init__(self, size):
        self.pos = 0 # Posicion en el escenario
        self.vel = 1 # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.1 # distancia para realiozar los calculos de colision
        self.storeIsPlaced = False
        self.backgroundMove = True


    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):
        # Se actualiza la posicion del fondo
        #si la posición se sale del rango, traslada la escena para generar un efecto infinito
        if self.storeIsPlaced == False:
            if (self.pos <= -1.0 or self.pos >= 1.0):
                self.pos = 0

        if self.backgroundMove == True:
            # Si detecta la tecla [W] presionada se mueve hacia la arriba
            if self.controller.is_w_pressed:
                self.pos -= self.vel * delta
            # Si detecta la tecla [S] presionada y no se ha salido de la pista se mueve hacia abajo
            if self.controller.is_s_pressed:
                self.pos += self.vel * delta
                #print(self.pos[0])


        # Se le aplica la transformacion de traslado segun la posicion actual
        self.model.transform = tr.matmul([tr.translate(0, self.pos, 0), tr.scale(self.size, self.size, 1)])

        
class Zombie():
    # Clase para contener las caracteristicas de un objeto que representa una carga 
    def __init__(self, posx, posy, size):
        self.move = [posx, posy]
        self.vel = [1,1] # Velocidad de desplazamiento
        self.radio = size/4
        self.size = size
        self.model = None
        self.cargaMove = True
        self.infected = True
    
    def set_model(self, new_model):
        self.model = new_model
    
    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):

        self.move[1] -= 0.3 * delta
        if self.cargaMove == True:
            if self.controller.is_w_pressed:
                self.move[1] -= self.vel[1] * delta

            if self.controller.is_s_pressed:
                self.move[1] += self.vel[1] * delta
            #print("carga", self.move[0], self.move[1])

        # Se posiciona el nodo referenciado
        self.model.transform = tr.matmul([tr.translate(self.move[0], self.move[1], 0), tr.scale(self.size, self.size, 1)])

class Humano():
    # Clase para contener las caracteristicas de un objeto que representa una carga 
    def __init__(self, posx, posy, size, infected, zombieGpuShape):
        self.move = [posx, posy]
        self.vel = [1,1] # Velocidad de desplazamiento
        self.radio = size/4
        self.size = size
        self.model = None
        self.cargaMove = True
        self.infected = infected
        self.zombieGpuShape = zombieGpuShape
    
    def set_model(self, new_model):
        self.model = new_model
    
    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):

        self.move[1] -= 1 * delta
        if self.cargaMove == True:
            if self.controller.is_w_pressed:
                self.move[1] -= self.vel[1] * delta

            if self.controller.is_s_pressed:
                self.move[1] += self.vel[1] * delta
            #print("carga", self.move[0], self.move[1])

        # Se posiciona el nodo referenciado
        self.model.transform = tr.matmul([tr.translate(self.move[0], self.move[1], 0), tr.scale(self.size, self.size, 1)])
    
    def collision(self, zombies):
        # Se recorrela lista de zombies
        for zombie in zombies:
            # Si choca con un zombie pasa a estado "infectado" y cambia su gpuShape
            if (self.radio+zombie.radio)**2 > ((self.move[0]-zombie.move[0])**2 + (self.move[1]-zombie.move[1])**2):
                self.model.childs.clear()
                self.model.childs += [self.zombieGpuShape]
                self.infected = True
                return