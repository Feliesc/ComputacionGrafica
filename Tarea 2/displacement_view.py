# coding=utf-8
"""Textures and transformations in 2D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path

from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from shaders import *
from PIL import Image


def createTextureQuad():

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions
        -0.5, -0.5,
         0.5, -0.5,
         0.5,  0.5,
        -0.5,  0.5,]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return bs.Shape(vertices, indices)

if __name__ == "__main__":
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displacement View - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

#####################################################################################################

    pipeline = waterShaderProgram()

#####################################################################################################
    
    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

######################################################################################################
    # Definimos donde se encuentran las texturas
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "assets")
    waterPath = os.path.join(spritesDirectory, "awa.png")
    displacementPath = os.path.join(spritesDirectory, "displacement2Map.png")

    # Creating shapes on GPU memory
    ##################PARA LA LLUVIA#########################################################
    shapeWater = createTextureQuad()
    gpuWater = GPUShape().initBuffers()
    pipeline.setupVAO(gpuWater)
    gpuWater.texture = textureSetup(
        waterPath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    gpuWater.fillBuffers(shapeWater.vertices, shapeWater.indices, GL_STATIC_DRAW)

    gpuDisplacement = GPUShape().initBuffers()
    gpuDisplacement.texture = textureSetup(
        displacementPath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the shapes

        speed = 10
        dt = glfw.get_time()
        #va desde 0 a 20
        dy = (speed*dt)%20
        #y va de -1/2 a 1/2
        y = -0.5+dy/20
        #va desde 0 a 1
        texIndex = dy/20
        #movimiento del agua en el eje x (movimiento del displacement map)
        dx = np.sin(dt)/5+0.5
##############################################################################################################
        # Telling OpenGL to use our shader program
        glUseProgram(pipeline.shaderProgram)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "posIndex"), y)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texIndex"), texIndex)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "dx"), dx)
        
        
        glBindVertexArray(gpuWater.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gpuWater.texture)
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "samplerTex"), 0)
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, gpuDisplacement.texture)
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "displacement"), 1)
        glDrawElements(GL_TRIANGLES, gpuWater.size, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        

        
        
##############################################################################################################

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuWater.clear()

    glfw.terminate()
