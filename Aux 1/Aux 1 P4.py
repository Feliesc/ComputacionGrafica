"""P4) [Creando una escena] Cree funciones para crear polígonos que representen elementos de un paisaje 
donde se aprecia una isla. Luego junte estas funciones para crear una bonita escena."""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES

# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')
    
# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

class SimpleShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def create_sky(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y1, 0.0,  0.8, 1.0, 1.0,
        -1.0, y1, 0.0,  0.8, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_ocean(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.0, 0.0, 0.5,
         1.0, y0, 0.0,  0.0, 0.0, 0.5,
         1.0, y1, 0.0,  0.2, 0.4, 1.0,
        -1.0, y1, 0.0,  0.2, 0.4, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_island(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                           colors
         x0,         y0,               0.0,  0.63, 0.25, 0.0,
         x0 + width/2,  y0 - height,      0.0,  0.63, 0.25, 0.0,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.63, 0.25, 0.0,

         x0 + width/2,  y0 - height,      0.0,  0.9, 0.49, 0.13,
         x0 + width, y0,               0.0,  0.9, 0.49, 0.13,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.9, 0.49, 0.13,

         x0,         y0,               0.0,  0.0, 0.7, 0.0,
         x0 + width/2,  y0 - height *0.4, 0.0,  0.1, 1.0, 0.0,
         x0 + width, y0,               0.0,  0.0, 0.7, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices =  [0, 1, 2,
                3, 4, 5,
                6, 7, 8]

    return Shape(vertices, indices)

def create_volcano(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
         x0, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.8, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.4, y0 + height, 0.0,  0.6, 0.31, 0.17,

         x0 + width*0.2, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.6, y0 + height, 0.0, 0.6, 0.31, 0.17]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                3, 4, 5]

    return Shape(vertices, indices)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800

    window = glfw.create_window(width, height, "P4: Creando una escena", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    pipeline = SimpleShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Creating shapes on GPU memory
    sky_shape = create_sky(y0=-0.2, y1=1.0)
    gpu_sky = GPUShape().initBuffers()
    pipeline.setupVAO(gpu_sky)
    gpu_sky.fillBuffers(sky_shape.vertices, sky_shape.indices, GL_STATIC_DRAW)

    ocean_shape = create_ocean(y0=-1.0, y1=-0.2)
    gpu_ocean = GPUShape().initBuffers()
    pipeline.setupVAO(gpu_ocean)
    gpu_ocean.fillBuffers(ocean_shape.vertices, ocean_shape.indices, GL_STATIC_DRAW)

    island_shape = create_island(x0=-0.8, y0=-0.2, width=1.6, height=0.4)
    gpu_island = GPUShape().initBuffers()
    pipeline.setupVAO(gpu_island)
    gpu_island.fillBuffers(island_shape.vertices, island_shape.indices, GL_STATIC_DRAW)

    volcano_shape = create_volcano(x0=-0.3, y0=-0.22, width=0.6, height=0.4)
    gpu_volcano = GPUShape().initBuffers()
    pipeline.setupVAO(gpu_volcano)
    gpu_volcano.fillBuffers(volcano_shape.vertices, volcano_shape.indices, GL_STATIC_DRAW)


    # Setting up the clear screen color
    glClearColor(0.2, 0.2, 0.2, 1.0)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the Quad as specified in the VAO with the active shader program
        pipeline.drawCall(gpu_sky)
        pipeline.drawCall(gpu_ocean)
        pipeline.drawCall(gpu_island)
        pipeline.drawCall(gpu_volcano)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_ocean.clear()
    gpu_island.clear()
    gpu_volcano.clear()

    glfw.terminate()