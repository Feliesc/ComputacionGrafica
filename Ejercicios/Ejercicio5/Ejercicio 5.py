import glfw
import os
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm
import grafica.scene_graph as sg
from shapes import *
from model import *


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4

IMG_PATH = f"{os.path.dirname(__file__)}/sprites"


# Clase controlador con variables para manejar el estado de ciertos botones
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.is_w_pressed = False
        self.is_s_pressed = False
        self.is_a_pressed = False
        self.is_d_pressed = False


# we will use the global controller as communication with the callback function
controller = Controller()

# This function will be executed whenever a key is pressed or released
def on_key(window, key, scancode, action, mods):
    
    global controller
    
    # Caso de detectar la tecla [W], actualiza estado de variable
    if key == glfw.KEY_W:
        if action ==glfw.PRESS:
            controller.is_w_pressed = True
        elif action == glfw.RELEASE:
            controller.is_w_pressed = False

    # Caso de detectar la tecla [S], actualiza estado de variable
    if key == glfw.KEY_S:
        if action ==glfw.PRESS:
            controller.is_s_pressed = True
        elif action == glfw.RELEASE:
            controller.is_s_pressed = False

    # Caso de detectar la tecla [A], actualiza estado de variable
    if key == glfw.KEY_A:
        if action ==glfw.PRESS:
            controller.is_a_pressed = True
        elif action == glfw.RELEASE:
            controller.is_a_pressed = False

    # Caso de detectar la tecla [D], actualiza estado de variable
    if key == glfw.KEY_D:
        if action ==glfw.PRESS:
            controller.is_d_pressed = True
        elif action == glfw.RELEASE:
            controller.is_d_pressed = False

    # Caso de detecar la barra espaciadora, se cambia el metodo de dibujo
    if key == glfw.KEY_SPACE and action ==glfw.PRESS:
        controller.fillPolygon = not controller.fillPolygon

    # Caso en que se cierra la ventana
    elif key == glfw.KEY_ESCAPE and action ==glfw.PRESS:
        glfw.set_window_should_close(window, True)



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creating a glfw window
    width = 800
    height = 800
    title = "Ejercicio 5 - Felipe Escárate"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Pipeline para dibujar shapes con colores interpolados
    pipeline = es.SimpleTransformShaderProgram()
    # Pipeline para dibujar shapes con texturas
    tex_pipeline = es.SimpleTextureTransformShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Grafo de escena del auto
    car = createCar(pipeline) 
    # Grafo de escena del background
    mainScene = createScene(pipeline)
    # Se añade el auto a la escena principal
    mainScene.childs += [car]

    # Se instancia el modelo del auto
    player = Player(0.3)
    # Se indican las referencias del nodo y el controller al modelo
    player.set_model(car)
    player.set_controller(controller)

    background = Background(1)
    backGround = sg.findNode(mainScene, "background")
    background.set_model(backGround)
    background.set_controller(controller)

    # Shape con textura de la carga
    garbage = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, f"{IMG_PATH}/bag.png")
    # Se crean el grafo de escena con textura
    tex_scene = sg.SceneGraphNode("textureScene")

    baseGarbage = "garbage" #se crea el nombre base para el nodo garbage
    cargas = [] #esta lista irá aumentando a medida que avanza el auto
    


    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    n=0
    x=0
    maxposx = 0
    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1

        posx = player.pos[0]
        #se establece la posición máxima a la que ha llegado el auto para crear basuras hasta ahí
        if posx > maxposx:
            maxposx = posx

        #x aumenta al apretar la d y si la posición del auto es la máxima posición hasta ese momento
        if controller.is_d_pressed == True and maxposx == posx:
            x += 10*delta                   #x es un contador que aumenta a medida que el auto llega más lejos


        n0 = n      #se crea n0 para saber si aumentó n 
        n = int(x)  #es el x truncado y se usa para crear basuras
        
        #si n aumentó se crea una nueva basura
        if n>n0:
            garbageNode = sg.SceneGraphNode(baseGarbage + str(n)) #se le pone el indice al nombre del nodo ej: garbage0, garbage 1
            garbageNode.childs = [garbage]                         #se le da como hijo la textura
            tex_scene.childs += [garbageNode]                      #a la escena de textura se le asigna como hijo la basura
            carga = Carga(0.5 + 0.5*n, -0.65+(0.1)*(-1)**n, 0.1)     #se crea una carga
            carga.set_model(garbageNode)                           #se le asigna el modelo a la carga
            carga.set_controller(controller)                       #se le da el controlador para poder conocer su posición
            cargas += [carga]                                      #se agrega la carga a la lista de cargas
        #print(cargas)

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))
        # Using GLFW to check for input events
        glfw.poll_events()
        
        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Se llama al metodo del player para detectar colisiones
        player.collision(cargas)
        # Se llama al metodo del player para actualizar su posicion
        player.update(delta)
        # Se llama al metodo del fondo para actualizar su posicion
        background.update(delta)
        for i in range(n):
            cargas[i].update(delta)

        # Se crea el movimiento de giro del rotor
        rotor = sg.findNode(mainScene, "rtRotor")
        rotor.transform = tr.rotationZ(t1)

        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(mainScene, pipeline, "transform")

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    mainScene.clear()
    tex_scene.clear()
    
    glfw.terminate()