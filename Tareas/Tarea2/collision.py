class Player():
    # Clase que contiene al modelo del player
    def __init__(self, pos, radio):
        self.pos = pos 
        self.radio = radio # distancia para realizar los calculos de colision

    def collision(self, cargas):
        # Funcion para detectar las colisiones con las cargas
        # Se recorren las cargas 
        for carga in cargas:
            # si la distancia a la carga es menor que la suma de los radios ha ocurrido en la colision y la carga está infectada
            if (self.radio+carga.radio)**2 > ((self.pos[0]-carga.pos[0])**2 + (self.pos[1]-carga.pos[1])**2+ (self.pos[2]-carga.pos[2])**2):
                return True

class Carga():
    # Clase para contener las caracteristicas de un objeto que representa una carga 
    def __init__(self, pos, radio):
        self.pos = pos
        self.radio = radio