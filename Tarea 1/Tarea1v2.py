""" P3 [Drive simulator] """

import glfw
import OpenGL.GL.shaders
import numpy as np
import grafica.basic_shapes as bs
import shaders as s
import grafica.transformations as tr
import grafica.performance_monitor as pm
import grafica.scene_graph as sg
from shapes import *
from model import *
import sys



if len(sys.argv)==5:
    print("Se escribieron los parametros correctamente")
    Z = int(sys.argv[1])
    H = int(sys.argv[2])
    T = int(sys.argv[3])
    P = int(sys.argv[4])
else:
    print("no se escribieron los parametros correspondientes Z H T P")


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


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
    title = "Tarea 1 - Felipe Escárate"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Pipeline para dibujar shapes con colores interpolados
    pipeline = s.SimpleTransformShaderProgram()
    # Pipeline para dibujar shapes con texturas
    tex_pipeline = s.SimpleTextureTransformShaderProgram()
    #Pipeline para animar npc
    anim_pipeline = s.AnimationShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.1, 0.9, 0.1, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Grafo de escena del auto
    car = createCar(pipeline)
    hinata = createTextureGPUShape(bs.createTextureQuad(), tex_pipeline, "sprites/hinata.png") 
    # Grafo de escena del background
    mainScene = createScene(pipeline)
    # Se añade el auto a la escena principaly

    # Se instancia el modelo del auto
    player = Player(0.3)
    # Se indican las referencias del nodo y el controller al modelo
    player.set_model(hinata)
    player.set_controller(controller)

    background = Background(1)
    backGround = sg.findNode(mainScene, "background")
    background.set_model(backGround)
    background.set_controller(controller)


    # Se crean el grafo de escena con textura
    tex_scene = sg.SceneGraphNode("textureScene")

    cargas = [] #esta lista irá aumentando a medida que avanza el auto


    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    n=0
    contador = 0
    contadorAcumulado = 0
    # Application loop
    while not glfw.window_should_close(window):
        # Shape con textura de la carga
        zombie = createTextureGPUShape(bs.createTextureQuad(), anim_pipeline, "sprites/zombie.png")
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1
        texture_time = int(9*glfw.get_time())

        n0 = n      #se crea n0 para saber si aumentó n 
        n = int(t1//T)
        n = n + contadorAcumulado
        
        #si n aumentó se crean nuevos Zombies
        if n>n0:
            #print(nmax)
            zombieNode = sg.SceneGraphNode("zombie" + str(n)) #se le pone el indice al nombre del nodo ej: zombie32
            zombieNode.childs = [zombie]                      #se le da como hijo la textura
            tex_scene.childs += [zombieNode]                  #a la escena de textura se le asigna como hijo la basura
            carga = Carga(((n%6)*(0.12)*(-1)**n)+0.05, 1.0, 0.15)  #se crea una carga
            carga.set_model(zombieNode)                       #se le asigna el modelo a la carga
            carga.set_controller(controller)                  #se le da el controlador para poder conocer su posición
            cargas += [carga]                                 #se agrega la carga a la lista de cargas
            #print(len(cargas))
            #Como hay que crear Z zombies, sumamos 1 a n (Z-1) veces
            if contador < Z-1:
                contador += 1
                contadorAcumulado += 1      #este contador nunca se hace 0 y es para sumarselo a n y que de el largo de la lista
            else:
                contador = 0
            

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
        for i in range(len(cargas)):
            cargas[i].update(delta)


        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(mainScene, pipeline, "transform")

        glUseProgram(tex_pipeline.shaderProgram)
        tex_pipeline.drawCall(hinata)

        # Se dibuja el grafo de escena con texturas
        glUseProgram(anim_pipeline.shaderProgram)
        glUniform1f(glGetUniformLocation(anim_pipeline.shaderProgram, "texture_index"), texture_time%8)
        sg.drawSceneGraphNode(tex_scene, anim_pipeline, "transform")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    mainScene.clear()
    tex_scene.clear()
    
    glfw.terminate()
