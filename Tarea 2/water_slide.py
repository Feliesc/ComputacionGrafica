# coding=utf-8
"""
Ejercicio 9 - Felipe Escárate
Recorriendo una isosuperficie
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys

import grafica.transformations as tr
import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.text_renderer as tx
import MJ as mj
from meshesYmodelos import *
from shaders import *
from collision import *
from curves import *

if len(sys.argv)==3:
    datosIngresados = True
    N = int(sys.argv[1])
    V = int(sys.argv[2])
    speed = V
    speed0= V
else:
    datosIngresados = False
    N = 8
    V = 4
    speed = V
    speed0= V

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 850
    height = 850

    window = glfw.create_window(width, height, "Water Slide - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    tobogan0Pipeline = es.SimpleModelViewProjectionShaderProgram()
    toboganPipeline = toboganShaderProgram()
    riverPipeline = water3DShaderProgram()
    seaPipeline = seaShaderProgram()
    gouraudPipeline = MultipleGouraudShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.7, 0.9, 0.9, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Se crea el Tobogan0 (el que está hecho con una curva de Hermite y otra de Bezier)
    gpuTobogan0 = gpuTobogan0(tobogan0Pipeline)
    # Se crea el Tobogan
    gpuTobogan = gpuTobogan(toboganPipeline)
    # Se crea el rio
    gpuRiver = gpuRiver(riverPipeline)
    #creamos el mar 
    gpuSea = gpuSea(seaPipeline)
    # Se crea el bote
    boatNode = mj.createBoatNode(gouraudPipeline, [0,0,0])
    #creamos el obstaculo
    gpuTire = gpuObstaculo(gouraudPipeline)
    #creamos un nodo que contendrá los obstaculos
    obstaclesNode = sg.SceneGraphNode("Obstaculos")
    #ahora agregamos los obstaculos
    cargas = []
    for i in range(len(posicionesObstaculos)):
        posObstaculo = posicionesObstaculos[i]
        px,py,pz = posObstaculo[0],posObstaculo[1],posObstaculo[2]
        obsNode = sg.SceneGraphNode("obstaculo" + str(i)) #se le pone el indice al nombre del nodo ej: obstaculo5
        obsNode.transform = tr.matmul([tr.translate(px, py, pz),tr.uniformScale(0.1),tr.rotationX(np.random.rand()*np.pi/8)])
        obsNode.childs = [gpuTire]                      #se le da como hijo la gpuShape del obstaculo
        obstaclesNode.childs += [obsNode]               #al grafo de obstaculos se le asigna como hijo ese obstaculo    
        carga = Carga([px,py,pz], 0.05)
        cargas += [carga]

    player = Player([0,0,0], 0.05)

    #también, se hace el mensaje de Retry:
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    messageCharSize = 0.1
    messageShape = tx.textToShape("Press R to Retry", messageCharSize, messageCharSize)
    gpuMessage = GPUShape().initBuffers()
    textPipeline.setupVAO(gpuMessage)
    gpuMessage.fillBuffers(messageShape.vertices, messageShape.indices, GL_STATIC_DRAW)
    gpuMessage.texture = gpuText3DTexture

    t0 = glfw.get_time()
    dx = 0

    #creamos listas con las posiciones de la cámara y el bote (hechas con curvas)
    ListaPosicionesCamara = CameraSpline
    ListaPosicionesBote = BoatSpline
    ListaTangentes = SplineTan[1:len(SplineTan)]
    t = 0
    tan1 = ListaTangentes[t]
    tan2 = ListaTangentes[t+1]
    ListaNormales = SplineNormal[1:len(SplineNormal)]
    normal1 = ListaNormales[t]
    normal2 = ListaNormales[t+1]
    movHorizontal = normal1*dx
    ListaPuntos = puntos.copy()[1:len(puntos)]
    z1 = ListaPuntos[t][2]
    z2 = ListaPuntos[t+1][2]


    #definimos un contador que sirve para ver las caras
    i = 0
    j=0
    cameraPos = ListaPosicionesCamara[i]    #posición inicial cámara
    boatPos = ListaPosicionesBote[i+2]        #posición inicial bote
    delta = 0   #toma valores entre 0 y 1
    deltaAlpha = 0 #toma valores entre 0 y 7
    danguloBrazo =0
    anguloAumenta = True
    while not glfw.window_should_close(window):
        #se printea esto en el loop porque si se hace antes, al importar este archivo en el de curvas, se printea 2 veces
        if datosIngresados == True:
            print("Se escribieron los parametros correctamente")
            datosIngresados = None  #se pone None para que no se vuelva a printear
        elif datosIngresados == False:
            print("no se escribieron los parametros correspondientes N V")
            print("Se utilizará la configuración por defecto: N=8; V=4")
            datosIngresados = None

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        ###################################################################################################################
        # Antes de llegar al final del tunel, pasa esto
        if i+3<118:
            #Vemos que si delta es mayor a uno lo hacemos 0 y tomamos a la siguiente cara como "posición inicial"
            if delta>=1:
                delta = 0
                i +=1
                #vemos cuando se debe cambiar de tangente
                #como cada curva de la spline está hecha por 7 puntos, debemos dividir por 7
                if (i+2)/7 == int((i+2)/7):
                    deltaAlpha = 0
                    t+=1
                    tan1 = ListaTangentes[t]
                    tan2 = ListaTangentes[t+1]
                    normal1 = ListaNormales[t]
                    normal2 = ListaNormales[t+1]
                    z1 = ListaPuntos[t][2]
                    z2 = ListaPuntos[t+1][2]
                cameraPos = ListaPosicionesCamara[i]
                boatPos = ListaPosicionesBote[i+2]
            #si no, seguimos aumentando delta para que la cámara se desplace al siguiente punto
            else:
                delta += speed*dt
                deltaAlpha += speed*dt


            if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS) and dx>-0.4:
                dx -= 2 * dt
            if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS) and dx<0.25:
                dx += 2* dt
            
            #calculamos la posición de la cámara y del bote
            CameraPosition = [cameraPos[0]*(1-delta) + ListaPosicionesCamara[i+1][0]*delta, cameraPos[1]*(1-delta) + ListaPosicionesCamara[i+1][1]*delta,
                    cameraPos[2]*(1-delta) + ListaPosicionesCamara[i+1][2]*+delta]
            
            BoatPosition = [boatPos[0]*(1-delta) + ListaPosicionesBote[i+3][0]*delta, boatPos[1]*(1-delta) + ListaPosicionesBote[i+3][1]*delta,
                    boatPos[2]*(1-delta) + ListaPosicionesBote[i+3][2]*+delta]

            BoatPosition = np.array(BoatPosition)+movHorizontal
            
            #luego, se calcula la tangente para obtener el angulo de rotación del bote (el sentido en el cual apunta)
            tan = [tan1[0]*(7-deltaAlpha)/7 + tan2[0]*deltaAlpha/7,
                    tan1[1]*(7-deltaAlpha)/7 + tan2[1]*deltaAlpha/7,
                    tan1[2]*(7-deltaAlpha)/7 + tan2[2]*+deltaAlpha/7]
            normalizedTan = np.array(tan)/np.linalg.norm(tan)

            #también se calcula la normal, para saber como se debería mover hacia los lados
            normal = [normal1[0]*(7-deltaAlpha)/7 + normal2[0]*deltaAlpha/7,
                    normal1[1]*(7-deltaAlpha)/7 + normal2[1]*deltaAlpha/7,
                    normal1[2]*(7-deltaAlpha)/7 + normal2[2]*deltaAlpha/7]
            

            #sacamos el angulo de rotación del bote usando producto punto
            productoPunto = np.dot(xtongo, normalizedTan)
            if normalizedTan[1]>=0:
                alpha = np.arccos(productoPunto)
            else:
                alpha = -np.arccos(productoPunto)
            
            movHorizontal = np.array(normal)*dx
        
        #cuando se llega al final del tunel, para lo siguiente
        elif delta <= 1:
            delta += speed*dt/15
            posFinal = [7.5,15,1.75]
            posFinalCamara = [5,13,2.25]

            #calculamos la posición de la cámara y del bote
            CameraPosition = [cameraPos[0]*(1-delta) + posFinalCamara[0]*delta, cameraPos[1]*(1-delta) + posFinalCamara[1]*delta,
                    cameraPos[2]*(1-delta) + posFinalCamara[2]*+delta]
            
            BoatPosition = [boatPos[0]*(1-delta) + posFinal[0]*delta, boatPos[1]*(1-delta) + posFinal[1]*delta,
                    boatPos[2]*(1-delta) + posFinal[2]*+delta]
            if deltaAlpha <=7:
                deltaAlpha += delta/7
                #luego, se calcula la tangente para obtener el angulo de rotación del bote (el sentido en el cual apunta)
                tan = [tan1[0]*(7-deltaAlpha)/7 + tan2[0]*deltaAlpha/7,
                        tan1[1]*(7-deltaAlpha)/7 + tan2[1]*deltaAlpha/7,
                        tan1[2]*(7-deltaAlpha)/7 + tan2[2]*+deltaAlpha/7]
                normalizedTan = np.array(tan)/np.linalg.norm(tan)

        #cuando delta = 1 (se llega a la posición final) el agua deja de moverse
        else:
            speed = 0

        
        ###################################################################################################################

        if (glfw.get_key(window, glfw.KEY_F) == glfw.PRESS) and anguloAumenta == True:
            danguloBrazo += 2* dt
        if anguloAumenta == False:
            danguloBrazo -= 2* dt
        
        if danguloBrazo>=np.pi/8:
            anguloAumenta = False
        if danguloBrazo<0:
            anguloAumenta = True

        rotorBrazoIzq = sg.findNode(boatNode,"LrotorBrazo")
        rotorBrazoIzq.transform = tr.rotationX((3*np.pi/2)+danguloBrazo)

        rotorBrazoDer = sg.findNode(boatNode,"RrotorBrazo")
        rotorBrazoDer.transform = tr.rotationX((-3*np.pi/2)-danguloBrazo)

        #cuando termina el nivel, el jugador puede presionar R para volver al inicio
        if i==115 and (glfw.get_key(window, glfw.KEY_R) == glfw.PRESS):
            print("Se vuelve a las condiciones iniciales")
            i = 0
            t = 0
            tan1 = ListaTangentes[t]
            tan2 = ListaTangentes[t+1]
            ListaNormales = SplineNormal[1:len(SplineNormal)]
            normal1 = ListaNormales[t]
            normal2 = ListaNormales[t+1]
            movHorizontal = normal1*dx
            ListaPuntos = puntos.copy()[1:len(puntos)]
            z1 = ListaPuntos[t][2]
            z2 = ListaPuntos[t+1][2]
            cameraPos = ListaPosicionesCamara[i]    #posición inicial cámara
            boatPos = ListaPosicionesBote[i+2]        #posición inicial bote
            delta = 0   #toma valores entre 0 y 1
            deltaAlpha = 0 #toma valores entre 0 y 7
            speed = speed0

        
                
        #############################
        bx = BoatPosition[0]
        by = BoatPosition[1]
        bz = BoatPosition[2]
        boatNode.transform = tr.matmul([tr.translate(bx, by, bz),tr.uniformScale(0.06),tr.rotationZ(alpha)])
        #############################

        #si se presiona V se usa la vista en primera persona
        if (glfw.get_key(window, glfw.KEY_V) == glfw.PRESS):
            viewPos = np.array(BoatPosition+np.array([0,0,0.15]))
            at = at =  np.array(BoatPosition+normalizedTan)
        else:
            viewPos = np.array(CameraPosition)
            at =  np.array(BoatPosition)

        #eye, at, up
        view = tr.lookAt(
            viewPos,
            at,
            np.array([0,0,1])
        )

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        #definimos las posiciones de las luces 2,3 y 4
        L1 = ListaPosicionesCamara[50]
        L2 = ListaPosicionesCamara[80]
        L3 = ListaPosicionesCamara[110]

        ####
        #Detectamos las colisiones
        player.pos = [bx,by,bz]
        if player.collision(cargas) == True:
            #el jugador pierde, por lo que se vuelve a las condiciones iniciales:
            print("Se vuelve a las condiciones iniciales")
            i = 0
            t = 0
            tan1 = ListaTangentes[t]
            tan2 = ListaTangentes[t+1]
            ListaNormales = SplineNormal[1:len(SplineNormal)]
            normal1 = ListaNormales[t]
            normal2 = ListaNormales[t+1]
            movHorizontal = normal1*dx
            ListaPuntos = puntos.copy()[1:len(puntos)]
            z1 = ListaPuntos[t][2]
            z2 = ListaPuntos[t+1][2]
            cameraPos = ListaPosicionesCamara[i]    #posición inicial cámara
            boatPos = ListaPosicionesBote[i+2]        #posición inicial bote
            delta = 0   #toma valores entre 0 y 1
            deltaAlpha = 0 #toma valores entre 0 y 7
            speed = speed0

        projection = tr.perspective(70, float(width)/float(height), 0.1, 100)

        ##################### Ahora le decimos a Open-GL que use los Shaders #######################################

        glUseProgram(toboganPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(toboganPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform
        glUniformMatrix4fv(glGetUniformLocation(toboganPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        # Drawing shapes with different model transformations
        glUniformMatrix4fv(glGetUniformLocation(toboganPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "La"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "Ld"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "Ls"), 0.6, 0.6, 0.6)

        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "Ka"), 0.0, 0.0, 0.0)
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "Kd"), 0.4, 0.4, 0.4)
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "Ks"), 0.2, 0.2, 0.2)

        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "lightPosition1"), bx, by, bz)
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "lightPosition2"), L1[0], L1[1], L1[2])
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "lightPosition3"), L2[0], L2[1], L2[2])
        glUniform3f(glGetUniformLocation(toboganPipeline.shaderProgram, "lightPosition4"), L3[0], L3[1], L3[2])

    
        glUniform1ui(glGetUniformLocation(toboganPipeline.shaderProgram, "shininess"), 1)
        glUniform1f(glGetUniformLocation(toboganPipeline.shaderProgram, "constantAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(toboganPipeline.shaderProgram, "linearAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(toboganPipeline.shaderProgram, "quadraticAttenuation"), 0.1)

        toboganPipeline.drawCall(gpuTobogan)
        
        glUseProgram(riverPipeline.shaderProgram)

        SPEED = 10*speed
        dt = glfw.get_time()
        #va desde 0 a 20
        dy = (SPEED*dt)%20
        #y va de -1/2 a 1/2
        y = -0.5+dy/20
        #va desde 0 a 1
        texIndex = dy/20
        #deformación del agua (movimiento del displacement map)
        deformationX = (10/2*dt)%20/20
        deformationY = y

        #los uniforms que se le pasan al vertex shader
        glUniformMatrix4fv(glGetUniformLocation(riverPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(riverPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(riverPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "texIndex"), texIndex)
        
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "Ld"), 1.0, 0.0, 0.0)
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "Ls"), 1.0, 0.0, 0.0)

        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "lightPosition1"), bx, by, bz)
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "lightPosition2"), L1[0], L1[1], L1[2])
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "lightPosition3"), L2[0], L2[1], L2[2])
        glUniform3f(glGetUniformLocation(riverPipeline.shaderProgram, "lightPosition4"), L3[0], L3[1], L3[2])

        glUniform1ui(glGetUniformLocation(riverPipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "constantAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "linearAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "quadraticAttenuation"), 0.1)

        #los uniforms que se pasan al fragment shader
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "posIndex"), y)
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "deformationX"), deformationX)
        glUniform1f(glGetUniformLocation(riverPipeline.shaderProgram, "deformationY"), deformationY)
        glUniform1i(glGetUniformLocation(riverPipeline.shaderProgram, "samplerTex"), 1)
        glUniform1i(glGetUniformLocation(riverPipeline.shaderProgram, "displacement"), 2)
        
        #Drawcall
        riverPipeline.drawCall(gpuRiver)
        
        glUseProgram(seaPipeline.shaderProgram)

        glUseProgram(gouraudPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "Ld"), 1.0, 0.0, 0.0)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "Ls"), 1.0, 0.0, 0.0)

        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "lightPosition1"), bx, by, bz)
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "lightPosition2"), L1[0], L1[1], L1[2])
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "lightPosition3"), L2[0], L2[1], L2[2])
        glUniform3f(glGetUniformLocation(gouraudPipeline.shaderProgram, "lightPosition4"), L3[0], L3[1], L3[2])
    
        glUniform1ui(glGetUniformLocation(gouraudPipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(gouraudPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(gouraudPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(gouraudPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
        glUniformMatrix4fv(glGetUniformLocation(gouraudPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(gouraudPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(gouraudPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))

        sg.drawSceneGraphNode(boatNode, gouraudPipeline, "model")
        sg.drawSceneGraphNode(obstaclesNode, gouraudPipeline, "model")

        #si se llega al final del nivel, se llama al shader:
        if i == 115:
            color = [np.random.rand(), np.random.rand(), np.random.rand()]
            glUseProgram(textPipeline.shaderProgram)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,0)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,1)
            gpuMessage.fillBuffers(messageShape.vertices, messageShape.indices, GL_DYNAMIC_DRAW)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), color[0], color[1], color[2], 1)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 1-color[0], 1-color[1], 1-color[2],0.5)
            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
                tr.translate(-0.9, 0.6, 0))
            textPipeline.drawCall(gpuMessage)
        
        #lo siguiente se dibuja solo si está a punto de llegar al final del tunel
        if i>= 100:

            glUseProgram(tobogan0Pipeline.shaderProgram)
            movTob0 = tr.matmul([tr.translate(30, 30, 0),tr.rotationZ(np.pi)])
            glUniformMatrix4fv(glGetUniformLocation(tobogan0Pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(tobogan0Pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(tobogan0Pipeline.shaderProgram, "model"), 1, GL_TRUE, movTob0)
            tobogan0Pipeline.drawCall(gpuTobogan0)

            dy2 = (SPEED*dt/10)%20
            #y va de -1/2 a 1/2
            y2 = -0.5+dy2/20
            #va desde 0 a 1
            texIndex2 = dy2/20
            #deformación del agua (movimiento del displacement map)
            deformationY2 = y2
            glUseProgram(seaPipeline.shaderProgram)
            #los uniforms que se le pasan al vertex shader
            glUniformMatrix4fv(glGetUniformLocation(seaPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(seaPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(seaPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
            glUniform1f(glGetUniformLocation(seaPipeline.shaderProgram, "texIndex"), texIndex2)

            #los uniforms que se pasan al fragment shader
            glUniform1f(glGetUniformLocation(seaPipeline.shaderProgram, "posIndex"), y2)
            glUniform1f(glGetUniformLocation(seaPipeline.shaderProgram, "deformationX"), deformationX)
            glUniform1f(glGetUniformLocation(seaPipeline.shaderProgram, "deformationY"), deformationY2)
            glUniform1i(glGetUniformLocation(seaPipeline.shaderProgram, "samplerTex"), 1)
            glUniform1i(glGetUniformLocation(seaPipeline.shaderProgram, "displacement"), 2)
            
            #Drawcall
            seaPipeline.drawCall(gpuSea,gpuRiver)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuSea.clear()
    gpuTire.clear()
    gpuTobogan0.clear()
    gpuTobogan.clear()
    gpuMessage.clear()
    glfw.terminate()