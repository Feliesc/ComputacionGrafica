# coding=utf-8
"""
Ejercicio 9 - Felipe Escárate
Recorriendo una isosuperficie
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys
import json

import grafica.transformations as tr
import grafica.easy_shaders as es
import shaders as sh
from modelosOBJ import *
import figuras as fig
import bolas

#DESCOMENTAR CUANDO HAYA TERMINADO
#archivo = str(sys.argv[1])
#abrir = open(archivo)

# se abre el archivo json
abrir = open('config.json')
# se carga (como diccionario)
config = json.load(abrir)

coefRoce=config['coeficienteDeRoce']
C=config['coeficienteDeRestitucion']
  
# cerrando el archivo
abrir.close()


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.right = False
        self.left = False
        self.X = False
        self.focusedBall = 0
        self.toggleCam = False


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
        
    elif (glfw.get_key(window, glfw.KEY_X) == glfw.PRESS):
        controller.focusedBall += 1
        if controller.focusedBall == 16:
            controller.focusedBall = 0
    
    elif (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and controller.toggleCam == False:
        controller.toggleCam = True

    elif (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) and controller.toggleCam == True:
        controller.toggleCam = False

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Tarea 3 - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipeline = sh.SimpleShaderProgram()
    texPhongPipeline = sh.SimpleTexturePhongShaderProgram()
    tex2Dpipeline = sh.tex2DShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    #creamos la mesa de pool
    gpuTable = gpuTable(texPhongPipeline)
    #creamos el palo
    gpuCue = gpuPalo(texPhongPipeline)
    #luego las bolas
    posicionesIniciales = [[0,-4,0.15],
                        [0,3.96,0.15],
                        [-0.15,4.22,0.15],[0.15,4.22,0.15],
                        [-0.3,4.48,0.15],[0,4.48,0.15],[0.3,4.48,0.15],
                        [-0.45,4.74,0.15],[-0.15,4.74,0.15],[0.15,4.74,0.15],[0.45,4.74,0.15],
                        [-0.6,5,0.15],[-0.3,5,0.15],[0,5,0.15],[0.3,5,0.15],[0.6,5,0.15]]
    listaBolas = []
    for i in range(16):
        shape = fig.createGPUball(texPhongPipeline, i)
        bola = bolas.bola(i, posicionesIniciales[i], [0,0,0] , shape, coefRoce, C)
        listaBolas += [bola]

    #creamos el cuadrado que corresponde a la sombra de las bolas
    gpuShadow = fig.createGPUshadowQuad(tex2Dpipeline)

    #creamos los gpuShape para los rectángulos que son la barra de fuerza
    gpuRectangles = fig.createGPURectangles(pipeline)
    #creamos la esfera que contiene el fondo
    gpuBackgroundShpere = fig.createGPUbigSphere(texPhongPipeline)

    t0 = glfw.get_time()
    camera_theta = np.pi

    i = 0 #contador para ver a qué bola apunta la cámara
    bolaActual = listaBolas[i]
    at = np.array([bolaActual.pos[0], bolaActual.pos[1], bolaActual.pos[2]])
    cuePos = -0.3
    cueCharging = False
    cueHitting = False
    Force = 0
    maxCuePos = -3

    while not glfw.window_should_close(window):
        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
    

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        elif (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt
        
        bolaActual = listaBolas[controller.focusedBall]
        at = np.array([bolaActual.pos[0], bolaActual.pos[1], bolaActual.pos[2]])
        AT = at

        camX = at[0] + 5* np.sin(camera_theta)
        camY = at[1] + 5* np.cos(camera_theta)

        viewPos = np.array([camX, camY, 2])
        eye = np.array([0,0,1])

        #si se presiona la cámara, cambia la transformación de vista según los siguientes vectores
        if controller.toggleCam == True:
            AT = np.array([0,0,0])
            viewPos = np.array([0,0,15])
            eye = np.array([-1,0,0])

        view = tr.lookAt(
            viewPos,
            AT,
            eye)
        
        #cuando se mantiene la Z, se carga el palo (mientras más tiempo se esté manteniendo, le pega a la pelota con más fuerza)
        if (glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS):
            if cuePos>maxCuePos:
                cuePos -= 2*dt
            cueCharging = True

            glUseProgram(pipeline.shaderProgram)
            
            barTransform = tr.matmul([tr.translate(0.6,-0.8+(cuePos/maxCuePos)/5,0),tr.scale(0.1,0.2*cuePos/maxCuePos,0.2)])
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, barTransform)
            pipeline.drawCall(gpuRectangles[1])
        
            backTransform = tr.matmul([tr.translate(0.6,-0.6,0),tr.scale(0.1,0.2,0.2)])
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, backTransform)
            pipeline.drawCall(gpuRectangles[0])
            
            print(cuePos)
        else:
            cueCharging = False
        #si se dejó de cargar, pasa al estado de "pegar"
        if cueCharging==False and cuePos !=-0.3 and cueHitting == False:
            cueHitting = True
            #se calcula la fuerza en función de qué tanto se cargó el palo
            Force = -cuePos*100
        #mientras está pegando, cambia la posición del palo para mostrar la animación (hasta que le pega a la esfera)
        if cueHitting == True:
            cuePos += 7*dt
            if cuePos >=0:
                cueHitting = False
                cuePos = -0.3
            
        for bola in listaBolas:
            bola.update(cuePos, Force, listaBolas, t0, dt, controller.focusedBall, camera_theta)

        # Telling OpenGL to use our shader program
        glUseProgram(texPhongPipeline.shaderProgram)

        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "La"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ld"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ls"), 0, 0, 0)

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ka"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Kd"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "Ks"), 0, 0, 0)

        glUniform3f(glGetUniformLocation(texPhongPipeline.shaderProgram, "lightPosition"), 0, 0, 3)
    
        glUniform1ui(glGetUniformLocation(texPhongPipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "constantAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(texPhongPipeline.shaderProgram, "quadraticAttenuation"), 0.1)

        texPhongPipeline.drawCall(gpuTable)
        texPhongPipeline.drawCall(gpuBackgroundShpere)

        for i in range(len(listaBolas)):
            BOLA = listaBolas[i]
            bolaShape = BOLA.shape
            POS = BOLA.pos
            transform = tr.matmul([tr.translate(POS[0],POS[1],POS[2]),tr.rotationA(BOLA.anguloRotacion,BOLA.ejeRotacion)])
            glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
            texPhongPipeline.drawCall(bolaShape)
        
        cueTransform = tr.matmul([tr.translate(at[0],at[1],at[2]),tr.rotationZ(-camera_theta+np.pi),
                                    tr.translate(0,cuePos,0.1),tr.rotationY(np.pi/24)])
        glUniformMatrix4fv(glGetUniformLocation(texPhongPipeline.shaderProgram, "model"), 1, GL_TRUE, cueTransform)
        texPhongPipeline.drawCall(gpuCue)

        #ahora dibujamos la sombra para cada bola
        glUseProgram(tex2Dpipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(tex2Dpipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(tex2Dpipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        for i in range(len(listaBolas)):
            BOLA = listaBolas[i]
            POS = BOLA.pos
            transform = tr.translate(POS[0],POS[1],0)
            glUniformMatrix4fv(glGetUniformLocation(tex2Dpipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
            tex2Dpipeline.drawCall(gpuShadow)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuShadow.clear()
    gpuCue.clear()
    gpuBackgroundShpere.clear()
    gpuTable.clear()

    glfw.terminate()