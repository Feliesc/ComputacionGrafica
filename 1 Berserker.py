import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES

# A class to store the application control
class Controller:
    fillPolygon = True
    effect1 = False
    effect2 = False


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

    elif key == glfw.KEY_Q:
        controller.effect1 = not controller.effect1

    elif key == glfw.KEY_W:
        controller.effect2 = not controller.effect2

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

class GreenShaderProgram:

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
                float grayColor = (newColor.r + newColor.g + newColor.b) / 3.0;
                vec3 finalColor = newColor;
                if (newColor.g < newColor.r +0.1|| newColor.g < newColor.b +0.1)
                {
                    finalColor = vec3(grayColor, grayColor, grayColor);
                }
                outColor = vec4(finalColor, 1.0f);
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

class SunsetShaderProgram:

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
                vec3 finalColor = vec3((newColor.r + 0.4) , newColor.g + 0.2, newColor.b * 0.1 );
                outColor = vec4(finalColor, 1.0f);
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

def create_grass(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.2, 0.7, 0.3,
         1.0, y0, 0.0,  0.2, 0.7, 0.3,
         1.0, y1, 0.0,  0.2, 0.7, 0.3,
        -1.0, y1, 0.0,  0.2, 0.7, 0.3]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)


def create_enderman(x0, y0, width, height):
    vertices = [
        #Se hacen las piernas
        x0, y0, 0.0,                                       0.0, 0.0, 0.0,
        x0 + width*0.17, y0, 0.0,                          0.0, 0.0, 0.0,
        x0 + width*0.17, y0 + height*0.52, 0.0,            0.0, 0.0, 0.0,
        x0, y0 + height*0.52, 0.0,                         0.0, 0.0, 0.0,
        
        x0 + width*0.33, y0, 0.0,                          0.0, 0.0, 0.0,
        x0 + width*0.50, y0, 0.0,                          0.0, 0.0, 0.0,
        x0 + width*0.50, y0 + height*0.52, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.33, y0 + height*0.52, 0.0,            0.0, 0.0, 0.0,
        #Haciendo el cuerpo
        x0 - width*0.15, y0 + height*0.52, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.65, y0 + height*0.52, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.65, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 - width*0.15, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        #Haciendo los brazos
        x0 - width*0.15, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 - width*0.30, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 - width*0.34, y0 + height*0.20, 0.0,            0.0, 0.0, 0.0,
        x0 - width*0.19, y0 + height*0.20, 0.0,            0.0, 0.0, 0.0,
        
        x0 + width*0.65, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.80, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.84, y0 + height*0.20, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.69, y0 + height*0.20, 0.0,            0.0, 0.0, 0.0,
        #Creando la cabeza
        x0 - width*0.19, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.69, y0 + height*0.78, 0.0,            0.0, 0.0, 0.0,
        x0 + width*0.69, y0 + height*0.96, 0.0,            0.0, 0.0, 0.0,
        x0 - width*0.19, y0 + height*0.96, 0.0,            0.0, 0.0, 0.0,
        #Haciendo los ojos
        x0 - width*0.19, y0 + height*0.87, 0.0,            1.0, 1.0, 1.0,
        x0 - width*0.19, y0 + height*0.85, 0.0,            1.0, 1.0, 1.0,
        x0 + width*0.10, y0 + height*0.85, 0.0,            1.0, 0.0, 1.0,
        x0 + width*0.10, y0 + height*0.87, 0.0,            1.0, 0.0, 1.0,

        x0 + width*0.69, y0 + height*0.87, 0.0,            1.0, 1.0, 1.0,
        x0 + width*0.40, y0 + height*0.87, 0.0,            1.0, 0.0, 1.0,
        x0 + width*0.40, y0 + height*0.85, 0.0,            1.0, 0.0, 1.0,
        x0 + width*0.69, y0 + height*0.85, 0.0,            1.0, 1.0, 1.0]

    indices =[0,1,2,2,3,0,
                4,5,6,6,7,4,
                8,9,10,10,11,8,
                12,13,14,14,15,12,
                16,17,18,18,19,16,
                20,21,22,22,23,20,
                24,25,26,26,27,24,
                28,29,30,30,31,28]
    return Shape(vertices,indices)

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

    window = glfw.create_window(width, height, "P5: Efectos con shaders", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    simplePipeline = SimpleShaderProgram()
    greenPipeline = GreenShaderProgram()
    sunsetPipeline = SunsetShaderProgram()

    # Creating shapes on GPU memory
    sky_shape = create_sky(y0=-0.2, y1=1.0)
    gpu_sky = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_sky)
    greenPipeline.setupVAO(gpu_sky)
    sunsetPipeline.setupVAO(gpu_sky)
    gpu_sky.fillBuffers(sky_shape.vertices, sky_shape.indices, GL_STATIC_DRAW)

    grass_shape = create_grass(y0=-1.0, y1=-0.2)
    gpu_grass = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_grass)
    greenPipeline.setupVAO(gpu_grass)
    sunsetPipeline.setupVAO(gpu_grass)
    gpu_grass.fillBuffers(grass_shape.vertices, grass_shape.indices, GL_STATIC_DRAW)

    enderman_shape = create_enderman(x0=-0.3, y0=-0.22, width=0.2, height=0.9)
    gpu_enderman = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_enderman)
    greenPipeline.setupVAO(gpu_enderman)
    sunsetPipeline.setupVAO(gpu_enderman)
    gpu_enderman.fillBuffers(enderman_shape.vertices, enderman_shape.indices, GL_STATIC_DRAW)

    volcano_shape = create_volcano(x0=0.1, y0=-0.22, width=0.6, height=0.4)
    gpu_volcano = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_volcano)
    greenPipeline.setupVAO(gpu_volcano)
    sunsetPipeline.setupVAO(gpu_volcano)
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

        if (controller.effect1):
            glUseProgram(greenPipeline.shaderProgram)
            greenPipeline.drawCall(gpu_sky)
            greenPipeline.drawCall(gpu_grass)
            greenPipeline.drawCall(gpu_enderman)
            greenPipeline.drawCall(gpu_volcano)
        elif (controller.effect2):
            glUseProgram(sunsetPipeline.shaderProgram)
            sunsetPipeline.drawCall(gpu_sky)
            sunsetPipeline.drawCall(gpu_grass)
            greenPipeline.drawCall(gpu_enderman)
            sunsetPipeline.drawCall(gpu_volcano)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_grass)
            greenPipeline.drawCall(gpu_enderman)
            simplePipeline.drawCall(gpu_volcano)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_grass.clear()
    gpu_enderman.clear()
    gpu_volcano.clear()

    glfw.terminate()