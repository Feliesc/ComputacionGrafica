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
from PIL import Image

__author__ = "Daniel Calderon"
__license__ = "MIT"

###########################################################################
# Creamos nuestro vertex shader
class SimpleNewTextureTransformShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;
            uniform float texture_index;

            in vec2 position;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 0, 1.0f);

                if(position.x>0 && position.y>0){
                    outTexCoords = vec2((texture_index + 1)*1/10, 0); 
                }
                else if(position.x<0 && position.y>0){
                    outTexCoords = vec2(texture_index*1/10, 0);
                }
                else if(position.x>0 && position.y<0){
                    outTexCoords = vec2((texture_index + 1)*1/10, 1);
                }
                else{
                    outTexCoords = vec2(texture_index*1/10, 1);
                }
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 2d vertices => 2*4 = 8 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

#Se crea el shader para la lluvia
class RainShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;
            uniform float rain_index1;

            in vec2 position;
            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 0, 1.0f);
                if(position.x>0 && position.y>0){
                    outTexCoords = vec2(1, rain_index1); 
                }
                else if(position.x<0 && position.y>0){
                    outTexCoords = vec2(0, rain_index1);
                }
                else if(position.x>0 && position.y<0){
                    outTexCoords = vec2(1, 1);
                }
                else{
                    outTexCoords = vec2(0, 1);
                } 
                
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 2d vertices => 2*4 = 8 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

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

##################################################################################################

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
#####################################################################################################

        self.actual_sprite = 1
        self.x = 0.0
        self.rain_index = 1

#####################################################################################################


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

#####################################################################################################

    elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
        controller.actual_sprite = (controller.actual_sprite + 1)%10
        controller.x -=0.05
    
    elif key == glfw.KEY_LEFT or key == glfw.KEY_A:
        controller.actual_sprite = (controller.actual_sprite - 1)%10
        controller.x +=0.05

#####################################################################################################

    else:
        print('Unknown key')


if __name__ == "__main__":
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Ejercicio 4 - Felipe Escárate", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

#####################################################################################################

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = SimpleNewTextureTransformShaderProgram()
    pipelineRain = RainShaderProgram()

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
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath = os.path.join(spritesDirectory, "sprites.png")
    rainPath = os.path.join(spritesDirectory, "lluvia.png")

    # Creating shapes on GPU memory
    ##################PARA LA LLUVIA#########################################################
    shapeRain = createTextureQuad()
    gpuRain = GPUShape().initBuffers()
    pipelineRain.setupVAO(gpuRain)
    gpuRain.texture = es.textureSimpleSetup(
        rainPath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    gpuRain.fillBuffers(shapeRain.vertices, shapeRain.indices, GL_STATIC_DRAW)
    

    #######################PARA EL CABALLERO###################################################
    shapeKnight = createTextureQuad()
    gpuKnight = GPUShape().initBuffers()
    pipeline.setupVAO(gpuKnight)
    gpuKnight.texture = es.textureSimpleSetup(
        spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    gpuKnight.fillBuffers(shapeKnight.vertices, shapeKnight.indices, GL_STATIC_DRAW)

#######################################################################################################    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the shapes

        dy = (5*glfw.get_time())%40
        rain_index = 1-dy/20
##############################################################################################################
        # Telling OpenGL to use our shader program
        glUseProgram(pipelineRain.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipelineRain.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(controller.x, 1, 0),
            tr.scale(2, 0.1*dy, 1)
        ]))
        glUniform1f(glGetUniformLocation(pipelineRain.shaderProgram, "rain_index1"), rain_index)
        pipelineRain.drawCall(gpuRain)
        ################################
        glUseProgram(pipelineRain.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipelineRain.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(controller.x, 0-dy/20, 0),
            tr.scale(2, 2, 1)
        ]))
        glUniform1f(glGetUniformLocation(pipelineRain.shaderProgram, "rain_index1"), 0)
        pipelineRain.drawCall(gpuRain)
        ##############################

        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.uniformScale(0.5)
        ]))

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "texture_index"), controller.actual_sprite)

        pipeline.drawCall(gpuKnight)
        
##############################################################################################################

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuKnight.clear()
    gpuRain.clear()

    glfw.terminate()
