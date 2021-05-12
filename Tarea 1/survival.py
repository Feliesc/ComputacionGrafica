"""Tarea 1 - Felipe Escárate Fernández"""

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
from MJ import *
import sys
import grafica.text_renderer as tx



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
        self.is_space_pressed = False
        self.hasGlasses = False


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
    if key == glfw.KEY_F and action ==glfw.PRESS:
        controller.fillPolygon = not controller.fillPolygon
    
    if key == glfw.KEY_SPACE:
        if action ==glfw.PRESS:
            controller.is_space_pressed = True
        elif action == glfw.RELEASE:
            controller.is_space_pressed = False

    # Caso en que se cierra la ventana
    elif key == glfw.KEY_ESCAPE and action ==glfw.PRESS:
        glfw.set_window_should_close(window, True)



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creating a glfw window
    width = 900
    height = 900
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
    tex_pipeline = s.TextureShaderProgram()
    #Pipeline para animar npc
    anim_pipeline = s.AnimationShaderProgram()
    #Pipeline que usan los humanos contagiados (cuando el player lleva los lentes y presiona espacio se manda un uniform al shader)
    infected_pipeline = s.InfectedShaderProgram()
    #Pipeline para Hinata:
    hinata_pipeline = s.HinataShaderProgram()
    #Pipeline para texto
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.1, 0.9, 0.1, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Gpu Shape de Hinata
    hinata = createTextureGPUShape(bs.createSimpleTextureQuad(), hinata_pipeline, "sprites/hinataMove2.png")
     
    # Grafo de escena del background de figuras simples
    mainScene = createScene(pipeline)
    #Grafo de el fondo con texturas
    grass_scene = createGrassScene(tex_pipeline)

    # Se instancia el modelo del auto
    player = Player(0.15)
    # Se indican las referencias del nodo y el controller al modelo
    player.set_model(hinata)
    player.set_controller(controller)

    #Se crea el grafo de escena (solo las figuras simples)
    background = Background(1)
    backgroundModel = sg.findNode(mainScene, "background")
    background.set_model(backgroundModel)
    background.set_controller(controller)

    # Se crean el grafo de escena con textura
    grassBackground = Background(1)
    grassModel = sg.findNode(grass_scene, "grassScene")
    grassBackground.set_model(grassModel)
    grassBackground.set_controller(controller)


    #Se crea el grafo donde estarán zombies y humanos (con texturas animadas)
    anim_scene = sg.SceneGraphNode("animationScene")
    #se crea la escena donde estarán los humanos contagiados
    infected_scene = sg.SceneGraphNode("infectedHumansScene")

    #se crea una lista con zombies y otra con humanos
    zombies = [] #estas listas irán aumentando a medida que pasa el tiempo
    humanos = []

    #hacemos la GPU Shape del Zombie y la de Kageyama
    gpuZombie = createTextureGPUShape(bs.createSimpleTextureQuad(), anim_pipeline, "sprites/zombie.png")
    gpuKageyama = createTextureGPUShape(bs.createSimpleTextureQuad(), anim_pipeline, "sprites/kageyama4.png")

    #Ahora creamos una lista de 100 booleanos para ver en esa lista la probabilidad de que un humano esté infectado:
    ListaBooleanos = np.full((100), False, dtype=bool)
    ListaBooleanos[0:P+1] = True            #cambiamos los primeros P Falses por Trues
    #Más abajo se tomará un entero entre 0 y 99 para cada humano y de acuerdo a eso se le asignará una componente de la lista


    ####################################################################################################################
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    messageCharSize = 0.2
    uWin = "You Win!"
    game_over = "Game Over"
    message = None
    ####################################################################################################################


    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    ##########Definimos variables que se utilizarán al momento de correr el programa###################################

    n=0                     #los siguientes 3 contadores se usan para agregar Zombies a la escena
    contador = 0
    contadorAcumulado = 0
    m=0                     #los siguientes 3 contadores se usan para agregar Humanos(Kageyamas)
    contadorM = 0
    contadorMAcumulado = 0
    glasses = None          #Se crea la variable especifica si "hay lentes o no"
    color_index = 1         #este es un indice de color que se le pasa a los shaders para que vaya "anocheciendo"
    largoNivel = 10          #esta variable indica que tan largo es el nivel en términos de coordenadas en el eje Y
    theta = 0               #angulo de movimiento de los brazos de Ukai
    aumentando = True       #es verdadero si el angulo theta está aumentando
    color = []
    cantidadLetras=0        #es la cantidad de letras que salen en los mensajes ("Game Over" o "You Win")

    #####################################################################################################################

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()

        #Si aumenta un segundo, se escriben dos letras más en el mensaje final (Game Over/You Win)
        if int(t1) > int(t0):
            cantidadLetras+=2

        #Creamos una diferencia de tiempo para actualizar las texturas, posiciones, etc
        delta = t1 -t0
        t0 = t1
        texture_time = int(9*glfw.get_time())   #es un indice que se le pasa a los shaders para que actualicen las texturas

        if cantidadLetras>10:
            cantidadLetras=0

        #se genera un color random cada cierto tiempo (este color es el que está en el mensaje "You Win" o "Game Over")
        if int(t1) != int(t0-0.5):
            color = [np.random.rand(), np.random.rand(), np.random.rand()]

        color_index -= 0.03333*delta        #a los 30 segundos la pantalla se pone negra (anochece) (1/30 = 0.03333333)
        #si la pantalla se pone negra (se hace de noche) el jugador pierde
        if color_index<0 and player.youWin == False:
            player.gameOver=True
        
        #Ahora creamos oscilación del angulo theta (el que describe el movimiento de los brazos de Ukai)
        if aumentando == True:
            theta+= delta
        else:
            theta-= delta
        if theta >0:
            aumentando = False
        if theta < -0.225:
            aumentando = True


        ################################  SPAWNEO DE HUMANOS Y ZOMBIES  ########################################################

        n0 = n      #se crea n0 para saber si aumentó n 
        n = int((t1+0.7)//T)
        n = n + contadorAcumulado

        m0 = m      #se crea m0 para saber si aumentó m 
        m = int(t1//(T))
        m = m + contadorMAcumulado
        
        #si n aumentó se crean nuevos Zombies
        if n>n0 and player.contadorPosY<largoNivel and Z != 0:
            zombieNode = sg.SceneGraphNode("zombie" + str(n)) #se le pone el indice al nombre del nodo ej: zombie32
            zombieNode.childs = [gpuZombie]                      #se le da como hijo la gpuShape del Zombie
            anim_scene.childs += [zombieNode]                  #a la escena de animación se le asigna como hijo el nodo Zombie
            zombie = Zombie(((n%6)*(0.12)*(-1)**n)+0.05, 1.0, 0.15)  #se crea un zombie
            zombie.set_model(zombieNode)                       #se le asigna un modelo
            zombie.set_controller(controller)                  #se le da el controlador para poder conocer su posición
            zombies += [zombie]                                 #se agrega el Zombie a la lista de zombies
            #print(len(zombies))
            #Como hay que crear Z zombies, sumamos 1 a n (Z-1) veces
            if contador < Z-1:
                contador += 1
                contadorAcumulado += 1      #este contador nunca se hace 0 y es para sumarselo a n y que de el largo de la lista
            else:
                contador = 0
        
        #si m aumentó se crean nuevos Humanos
        if m>m0 and player.contadorPosY<largoNivel and H != 0:
            #para el humano, vemos la probabilidad de que esté contagiado y le asignamos valor de verdad a la variable "infected"
            indice = np.random.randint(100) #da un indice entre 0 y 100
            infected = ListaBooleanos[indice]   #se toma un booleano random de la lista
            kageyamaNode = sg.SceneGraphNode("kageyama" + str(m)) #se le pone el indice al nombre del nodo ej: kageyama23
            kageyamaNode.childs = [gpuKageyama]                      #se le da como hijo la gpuShape de Kageyama
            if infected == False:
                anim_scene.childs += [kageyamaNode]               #a la escena de animación se le asigna como hijo el nodo Kageyama
            else:                                                 #si el humano está infectado, se pone como hijo de la escena de infectados
                infected_scene.childs += [kageyamaNode]
            kageyama = Humano(((m%6)*(0.12)*(-1)**(m+1)-0.05), 1.0, 0.15, infected, gpuZombie)  #se crea un humano
            kageyama.set_model(kageyamaNode)                       #se le asigna el modelo a al humano
            kageyama.set_controller(controller)                  #se le da el controlador para poder conocer su posición
            humanos += [kageyama]                                 #se agrega a kageyama a la lista de humanos
            #Como hay que crear H kageyamas, sumamos 1 a m (H-1) veces
            if contadorM < H-1:
                contadorM += 1
                contadorMAcumulado += 1      #este contador nunca se hace 0 y es para sumarselo a m y que de el largo de la lista
            else:
                contadorM = 0
        
        #Si la cantidad de zombies es mayor a 20 se elimina el primero de la lista para vaciar memoria de la GPU
        if len(zombies)>20:
            zombieBasura = zombies.pop(0)
            gpuShapeBasura = (zombieBasura.model.childs)
            gpuShapeBasura.clear()
        
        #Si la cantidad de humanos es mayor a 20 se elimina el primero de la lista para vaciar memoria de la GPU
        if len(humanos)>20:
            humanoBasura = humanos.pop(0)
            gpuShapeBasura = (humanoBasura.model.childs)
            gpuShapeBasura.clear()

        #########################################################################################################################################

        """ahora vemos el contador de distancia en Y para ver que tan lejos
         llega el jugador y de acuerdo a eso activar ciertos eventos"""

        #Se generan lentes cada cierta distancia (solo si no hay otros lentes en la escena)
        if int(player.contadorPosY)%3 == 0 and glasses == None and player.contadorPosY < largoNivel-2:
            movEnPantalla = 0
            xglasses = -0.1
            yglasses = 1.0
            radioHit = 0.06
            glasses = createGlasses(pipeline, xglasses, yglasses)
        
        #Ahora vemos que pasa cuando hay lentes en la escena
        if glasses !=None:
            """si aún no ha agarrado los lentes se hace que estos se muevan en la posición 
                de la pantalla a medida que el personaje se mueve"""
            if controller.hasGlasses == False:
                if player.controller.is_w_pressed:
                    movEnPantalla -= delta
                if player.controller.is_s_pressed:
                    movEnPantalla += delta
                glasses.transform = tr.matmul([tr.translate(xglasses, yglasses+movEnPantalla, 0), tr.scale(0.08, 0.08, 0)])
                
                #Si no agarró los lentes y ya se alejó una distancia 10 se despawnean los lentes para poder crear otros
                if movEnPantalla<-3:
                    glasses.childs.clear()
                    glasses = None
    
            #Si el personaje chocha con los lentes
            if (player.radio+radioHit)**2 > ((player.pos[0]-xglasses)**2 + (-0.8-(yglasses+movEnPantalla))**2):
                controller.hasGlasses = True
            if controller.hasGlasses == True:
                glasses.transform = tr.matmul([tr.translate(player.pos[0], player.pos[1]-0.006, 0), tr.scale(0.06, 0.06, 0)])
            
        
        #si tiene los lentes equipados y se presiona la tecla espacio, se le pasa un uniform al shader de Humanos
        """el infected_index se multiplica con las componentes rojas y azul del color en el infected_pipeline, por lo que
        si vale 0 anula estas componentes y si vale uno, hace un efecto neutro"""
        if controller.hasGlasses == True and controller.is_space_pressed==True:
            infected_index = 0
        else:
            infected_index = 1


        #####Ahora, hacemos aparecer la tienda cuando el player está por terminar el juego
        if player.contadorPosY > largoNivel and player.storeIsPlaced == False:
            storeNode = createStore(pipeline)
            background2 = sg.findNode(mainScene, "background2")
            background2.childs += [storeNode]
            gpuBigGrass = createGrassGPUShape(createGrassTextureQuad(1, 0.25, 8, 2), tex_pipeline)
            #Se crea el nodo de la zona que tiene pasto
            bigGrassNode = sg.SceneGraphNode("bigGrass")
            bigGrassNode.transform = tr.matmul([tr.translate(0, 2.25, 0), tr.scale(1, 1, 1)])
            bigGrassNode.childs = [gpuBigGrass]
            grass_scene.childs += [bigGrassNode]

            player.storeIsPlaced = True
            background.storeIsPlaced = True
            grassBackground.storeIsPlaced = True
        
        ###Cuando la tienda ya está en pantalla, el fondo deja de moverse
        if player.contadorPosY > (largoNivel + 0.7) and background.backgroundMove == True:
            background.backgroundMove = False
            grassBackground.backgroundMove = False

        ####Ahora nos ponemos en el caso de que el jugador se devuelva, en este caso, revertimos las condiciones recién puestas
        if player.contadorPosY <= largoNivel and player.storeIsPlaced == True:
            storeNode.childs.clear()
            background.storeIsPlaced = False
            grassBackground.storeIsPlaced = False
            player.storeIsPlaced = False
        if player.contadorPosY <= (largoNivel + 0.7) and background.backgroundMove == False:
            background.backgroundMove = True
            grassBackground.backgroundMove = True

        #Luego hacemos rotaciones para los brazos de Ukai (esto se hace solo cuando la tienda ya entró en la escena)
        if player.storeIsPlaced == True:
            thetaAntebrazo = 2*theta
            #se hace una aproximación para que el antebrazo no se "despegue" del brazo
            deltaX = (math.cos(3*theta)-math.cos(theta))
            deltaY = (math.sin(3*theta)-math.sin(theta))
            #se busca el nodo del brazo izquierdo para rotarlo
            movimientoBrazos = sg.findNode(mainScene, "leftArm")
            movimientoBrazos.transform = tr.rotationZ(theta)
            #ahora se rota el antebrazo
            movimientoAntebrazos = sg.findNode(mainScene, "leftForearm")
            movimientoAntebrazos.transform = tr.matmul([tr.rotationZ(thetaAntebrazo), tr.translate(deltaX,deltaY,0)])
            #como el brazo derecho tiene como hijo al brazo izquierdo, repite los movimientos de este
        
        #Se genera el mensaje de victoria cuando el personaje llega a cierto punto del nivel.
        if player.contadorPosY > largoNivel+1.1 and player.youWin == False:
            player.youWin = True
            cantidadLetras=0

        """"============================================================================================================="""

        # Se llama al metodo del player para detectar colisiones
        player.collision(zombies)
        player.collision(humanos)
        # Como queremos que el player no se pueda mover después de ganar o perder, hacemos que solo se actualice si no ha ganado/perdido
        if player.gameOver ==False and player.youWin ==False:
            player.update(delta)
            # Se llama al metodo del fondo para actualizar su posicion
            background.update(delta)
            #Lo mismo para actualizar el pasto
            grassBackground.update(delta)

        #ahora para actualizar los zombies y humanos, debemos recorrer sus listas
        for i in range(len(zombies)):
            #si el fondo se está moviendo, los zombies se mueven junto con el fondo
            if background.backgroundMove == True:
                (zombies[i]).cargaMove = True
            else:
                (zombies[i]).cargaMove = False
            #se llama al metodo update de cada carga
            zombies[i].update(delta)
        
        for i in range(len(humanos)):
            #si el fondo se está moviendo, los humanos se mueven junto con el fondo
            if background.backgroundMove == True:
                (humanos[i]).cargaMove = True
            else:
                (humanos[i]).cargaMove = False
            #se llama al metodo update de cada carga
            humanos[i].update(delta)
            humanos[i].collision(zombies)
        
        ############################### Se genera la interfaz de victoria y derrota #############################################
        if player.gameOver == True:
            color_index = 0    #se oscurece la pantalla
            message = game_over[0:cantidadLetras]
        if player.youWin == True:
            message = uWin[0:cantidadLetras]

        # Ahora vemos hacemos las gpuShape del You Win y del Game Over
        if message !=None:  
            messageShape = tx.textToShape(message, messageCharSize, messageCharSize)
            gpuMessage = s.GPUShape().initBuffers()
            textPipeline.setupVAO(gpuMessage)
            gpuMessage.fillBuffers(messageShape.vertices, messageShape.indices, GL_STATIC_DRAW)
            gpuMessage.texture = gpuText3DTexture

        #########################################################################################################################

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

        ############################################# DIBUJANDO ##################################################

        #Primero se dibuja el pasto:
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(grass_scene, tex_pipeline, "transform")
        glUniform1f(glGetUniformLocation(tex_pipeline.shaderProgram, "color_index"), color_index)

        # Se dibuja el grafo de escena principal
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(mainScene, pipeline, "transform")
        if glasses !=None and controller.hasGlasses == False:
            sg.drawSceneGraphNode(glasses, pipeline, "transform")
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "color_index"), color_index)

        ################################ Se dibuja a Hinata #####################################################
        #vemos el valor que debe tomar texture_indexY:
        if controller.is_w_pressed == True:
            texture_indexY = 2
            #Como Hinata estaría de espaldas, los lentes deberían dibujarse antes:
            if controller.hasGlasses==True:
                glUseProgram(pipeline.shaderProgram)
                sg.drawSceneGraphNode(glasses, pipeline, "transform")
        elif controller.is_s_pressed == True:
            texture_indexY = 3
        elif controller.is_d_pressed == True:
            texture_indexY = 0
        elif controller.is_a_pressed == True:
            texture_indexY = 1
        else:
            texture_indexY = 4
        
        #Y con esto se dibuja a Hinata
        glUseProgram(hinata_pipeline.shaderProgram)
        glUniform1f(glGetUniformLocation(hinata_pipeline.shaderProgram, "texture_indexX"), texture_time%4)
        glUniform1f(glGetUniformLocation(hinata_pipeline.shaderProgram, "texture_indexY"), texture_indexY)
        glUniform1f(glGetUniformLocation(hinata_pipeline.shaderProgram, "color_index"), color_index)
        #Se mandan transformaciones a la GPU
        glUniformMatrix4fv(glGetUniformLocation(hinata_pipeline.shaderProgram, "transform"), 1, GL_TRUE, 
            tr.matmul([tr.translate(player.pos[0], player.pos[1], 0), tr.scale(player.size, player.size, 1)]))
        hinata_pipeline.drawCall(hinata)

        if controller.hasGlasses == True:
            glUseProgram(pipeline.shaderProgram)
            if (texture_indexY==3 or texture_indexY==4) :
                sg.drawSceneGraphNode(glasses, pipeline, "transform")
            if (texture_indexY==0):
                glasses.transform = tr.matmul([tr.translate(player.pos[0]+0.03, player.pos[1]-0.006, 0), tr.scale(0.02, 0.06, 0)])
                sg.drawSceneGraphNode(glasses, pipeline, "transform")
            if (texture_indexY==1):
                glasses.transform = tr.matmul([tr.translate(player.pos[0]-0.07, player.pos[1]-0.006, 0), tr.scale(0.02, 0.06, 0)])
                sg.drawSceneGraphNode(glasses, pipeline, "transform")

        ############################################################################################################

        # Se dibuja el grafo de escena con texturas animadas
        glUseProgram(anim_pipeline.shaderProgram)

        glUniform1f(glGetUniformLocation(anim_pipeline.shaderProgram, "color_index"), color_index)
        glUniform1f(glGetUniformLocation(anim_pipeline.shaderProgram, "texture_index"), texture_time%8)
        sg.drawSceneGraphNode(anim_scene, anim_pipeline, "transform")

        # Se dibuja el grafo de escena con humanos infectados
        glUseProgram(infected_pipeline.shaderProgram)

        glUniform1f(glGetUniformLocation(infected_pipeline.shaderProgram, "color_index"), color_index)
        glUniform1f(glGetUniformLocation(infected_pipeline.shaderProgram, "infected_index"), infected_index)
        glUniform1f(glGetUniformLocation(infected_pipeline.shaderProgram, "texture_index"), texture_time%8)
        sg.drawSceneGraphNode(infected_scene, infected_pipeline, "transform")

        #Dibujamos la barra de progreso:
        glUseProgram(pipeline.shaderProgram)
        NivelDeAvance = (player.contadorPosY+2)/(2*largoNivel+5)
        bar = createCurveBar(60,2*NivelDeAvance)
        gpuBar = s.GPUShape().initBuffers()
        pipeline.setupVAO(gpuBar)
        gpuBar.fillBuffers(bar.vertices, bar.indices, GL_DYNAMIC_DRAW)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, 
            tr.matmul([tr.translate(-1.025, 0.9, 0),tr.rotationZ(-math.pi/2) ,tr.scale(0.3, 2, 1)]))
        pipeline.drawCall(gpuBar)

        if player.youWin == True or player.gameOver == True:
            glUseProgram(textPipeline.shaderProgram)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,0)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,1)
            gpuMessage.fillBuffers(messageShape.vertices, messageShape.indices, GL_DYNAMIC_DRAW)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), color[0], color[1], color[2], 1)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 1-color[0], 1-color[1], 1-color[2],0.5)
            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
                tr.translate(-0.9, 0, 0))
            textPipeline.drawCall(gpuMessage)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    mainScene.clear()
    gpuBar.clear()
    hinata.clear()
    gpuMessage.clear()
    glasses.clear()
    grass_scene.clear()
    anim_scene.clear()
    
    glfw.terminate()
