"""P3) [Primer Shader] Realice un Shader en que se programe el Fragment Shader de manera que pinte las figuras dependiendo 
de la posición vertical en pantalla, solo especificando las coordenadas en los vértices y declarando los colores a 
interpolar en el shader correspondiente"""

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


class ColorShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
            }
            """

        fragment_shader = """
            #version 130
            in vec4 gl_FragCoord;
            vec3 color1 = vec3(1.0f, 0.0f, 0.0f);
            vec3 color2 = vec3(0.0f, 0.0f, 1.0f);
            int height = 600;

            out vec4 outColor;

            void main()
            {   
                float t = gl_FragCoord[1] / height;
                float cr = color1[0] * (1-t) + color2[0] * t;
                float cg = color1[1] * (1-t) + color2[1] * t;
                float cb = color1[2] * (1-t) + color2[2] * t;
                outColor = vec4(cr, cg, cb, 1.0f);
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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


def createTriangle():

    # Defining the location of  each vertex  of the shape
    vertices = [
    #   positions        
        -1.0, -1.0, 0.0,
         1.0, -1.0, 0.0,
         0.0,  1.0, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return Shape(vertices, indices)

def createQuads():

    # Defining the location of  each vertex  of the shape
    vertices = [
    #   positions        
        -1.0, -0.75, 0.0,
         -0.5, -1.0, 0.0,
         0.0,  1.0, 0.0,
         -0.75, 0.75, 0.0,

         0.3, 0.1, 0.0,
        0.7, 0.1, 0.0, 
        0.5, 1.0, 0.0,
        
        0.1, -0.9, 0.0,
        0.9, -0.3, 0.0,
        0.3, -0.15, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices =  [0, 1, 2,
                2, 3, 0,
                4, 5, 6,
                7, 8, 9]

    return Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "P3: Primer Shader", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    pipeline = ColorShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Creating shapes on GPU memory
    shapeTriangle = createTriangle()
    gpuTriangle = GPUShape().initBuffers()
    pipeline.setupVAO(gpuTriangle)
    gpuTriangle.fillBuffers(shapeTriangle.vertices, shapeTriangle.indices, GL_STATIC_DRAW)
    
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
        pipeline.drawCall(gpuTriangle)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTriangle.clear()

    glfw.terminate()