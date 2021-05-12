import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES
import math

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

class vertexShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130
            in vec3 position;
            in vec3 color;
            out vec3 newColor;

            void main()
            {
                vec3 newPos = vec3((position[0]*2)+0.25, (position[1]*2)-1, position[2]);
                gl_Position = vec4(newPos, 1.0f);
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

class nocheShaderProgram:

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
                vec3 finalColor = vec3((newColor.r * 0.2) , newColor.g * 0.1, newColor.b * 0.2 );
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

#se crea el cielo
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

#se crea pasto
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
####


def create_pared(N, L=2):
    vertices = []
    indices = []
    dtheta = 2 * math.pi / N
    for i in range(int(N*L)):
        theta = i * dtheta
        vertices += [
            # vertex coordinates                                        colors
            (0.2*math.sin(3*theta)+0.05*(-1)**i), (i/N), 0,        1, 0.6, 0.6]
        indices += [i,i+1,i+2]
    vertices += [0,L, 0,  1, 0.6, 0.6,
                 0,L, 0,  1, 0.6, 0.6]

    return Shape(vertices, indices)

def createGlasses():
    vertices = [
        -1.0, 0.2, 0.0,         0.3,0.2,0.2,
        -0.4, 0.2, 0.0,         0.3,0.2,0.2,
        -0.2, 0.4, 0.0,         0.6,0.25,0.25,
        -1.0, 0.4, 0.0,         0.6,0.25,0.25,
        -0.7, 0.4, 0.0,         0.6,0.25,0.25,
        -1.0, 0.8, 0.0,         0.6,0.25,0.25,
        -0.85, 0.8, 0.0,         0.6,0.25,0.25,
        0.2, 0.4, 0.0,          0.6,0.25,0.25,
        0.85, 0.8, 0.0,          0.6,0.25,0.25,
        1.0, 0.2, 0.0,          0.3,0.2,0.2,
        0.4, 0.2, 0.0,          0.3,0.2,0.2,
        0.2, 0.4, 0.0,          0.6,0.25,0.25,
        1.0, 0.4, 0.0,          0.6,0.25,0.25,
        0.7, 0.4, 0.0,          0.6,0.25,0.25,
        1.0, 0.8, 0.0,          0.6,0.25,0.25,
        1.0, 0.9, 0.0,          0.6,0.5,0.5,
        -1.0, 0.9, 0.0,         0.6,0.5,0.5,
        0.0, 0.8, 0.0,         0.6,0.25,0.25]
    indices = [0, 1, 2,
                2, 3, 0,
                3, 4, 5,
                6, 5, 4,
                7, 2, 6,
                8, 7, 6,
                9, 10, 11,
                12,11,9,
                12,13,14,
                14, 13, 8,
                17,16, 5,
                17, 15, 14]

    return Shape(vertices, indices)

#Se crea un Enderman(personaje de Minecraft que se teletransporta)

#se crea un cubito de Minecraft
def create_cubito(x0, y0, tamanno):
    vertices = [
        #se hace la parte de tierra desde frente
        x0, y0, 0.0,                             0.65, 0.3, 0.16,
        x0 + tamanno, y0, 0.0,                   0.65, 0.3, 0.16,
        x0 + tamanno, y0 + tamanno*0.65, 0.0,    0.65, 0.3, 0.16,
        x0, y0 + tamanno*0.65, 0.0,              0.65, 0.3, 0.16,
        #se hace la parte que tiene pasto (de frente)
        x0, y0 + tamanno*0.65, 0.0,              0.65, 0.3, 0.16,
        x0, y0 + tamanno, 0.0,                   0.2, 0.7, 0.3,
        x0 + tamanno, y0 + tamanno, 0.0,         0.2, 0.7, 0.3,
        x0 + tamanno, y0 + tamanno*0.65, 0.0,    0.65, 0.3, 0.16,
        #Ahora se hace el relieve(partiendo por la parte con tierra)
        x0, y0, 0.0,                             0.5, 0.2, 0.2,
        x0-tamanno*0.15, y0+tamanno*0.15, 0.0,   0.5, 0.2, 0.2,
        x0-tamanno*0.15, y0+tamanno*0.85, 0.0,   0.5, 0.2, 0.2,
        x0, y0+tamanno*0.70, 0.0,                0.5, 0.2, 0.2,
        #Relieve con pasto
        x0, y0+tamanno*0.70, 0.0,                0.5, 0.2, 0.2,
        x0-tamanno*0.15, y0+tamanno*0.85, 0.0,   0.5, 0.2, 0.2,
        x0-tamanno*0.15, y0+tamanno*1.15, 0.0,   0.0, 0.7, 0.5,
        x0, y0+tamanno, 0.0,                     0.0, 0.7, 0.5,

        x0, y0+tamanno, 0.0,                     0.2, 0.7, 0.45,
        x0-tamanno*0.15, y0+tamanno*1.15, 0.0,   0.2, 0.7, 0.45,
        x0+tamanno*0.85, y0+tamanno*1.15, 0.0,   0.2, 0.7, 0.45,
        x0+tamanno, y0+tamanno, 0.0,             0.2, 0.7, 0.45]
    indices = [0,1,2,2,3,0,
                4,5,6,6,7,4,
                8,9,10,10,11,8,
                12,13,14,14,15,12,
                16,17,18,18,19,16]
    return Shape(vertices,indices)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Bono Berserker 1", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    simplePipeline = SimpleShaderProgram()
    vertexPipeline = vertexShaderProgram()
    nochePipeline = nocheShaderProgram()

    # Creating shapes on GPU memory
    sky_shape = create_sky(y0=-0.2, y1=1.0)
    gpu_sky = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_sky)
    vertexPipeline.setupVAO(gpu_sky)
    nochePipeline.setupVAO(gpu_sky)
    gpu_sky.fillBuffers(sky_shape.vertices, sky_shape.indices, GL_STATIC_DRAW)

    grass_shape = create_grass(y0=-1.0, y1=-0.2)
    gpu_grass = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_grass)
    vertexPipeline.setupVAO(gpu_grass)
    nochePipeline.setupVAO(gpu_grass)
    gpu_grass.fillBuffers(grass_shape.vertices, grass_shape.indices, GL_STATIC_DRAW)

    pared_shape = create_pared(60)
    gpu_pared = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_pared)
    vertexPipeline.setupVAO(gpu_pared)
    nochePipeline.setupVAO(gpu_pared)
    gpu_pared.fillBuffers(pared_shape.vertices, pared_shape.indices, GL_STATIC_DRAW)


    cubito_shape = create_cubito(x0=0.15, y0=-0.24, tamanno=0.25)
    gpu_cubito = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_cubito)
    vertexPipeline.setupVAO(gpu_cubito)
    nochePipeline.setupVAO(gpu_cubito)
    gpu_cubito.fillBuffers(cubito_shape.vertices, cubito_shape.indices, GL_STATIC_DRAW)

    cubito2_shape = create_cubito(x0=0.45, y0=-0.7, tamanno=0.40)
    gpu_cubito2 = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_cubito2)
    vertexPipeline.setupVAO(gpu_cubito2)
    nochePipeline.setupVAO(gpu_cubito2)
    gpu_cubito2.fillBuffers(cubito2_shape.vertices, cubito2_shape.indices, GL_STATIC_DRAW)


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
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_grass)
            simplePipeline.drawCall(gpu_pared)
            simplePipeline.drawCall(gpu_cubito)
            simplePipeline.drawCall(gpu_cubito2)
            glUseProgram(vertexPipeline.shaderProgram)
            
        elif (controller.effect2):
            glUseProgram(nochePipeline.shaderProgram)
            nochePipeline.drawCall(gpu_sky)
            nochePipeline.drawCall(gpu_grass)
            nochePipeline.drawCall(gpu_pared)
            nochePipeline.drawCall(gpu_cubito)
            nochePipeline.drawCall(gpu_cubito2)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            #simplePipeline.drawCall(gpu_sky)
            #simplePipeline.drawCall(gpu_grass)
            simplePipeline.drawCall(gpu_pared)
            #simplePipeline.drawCall(gpu_cubito)
            #simplePipeline.drawCall(gpu_cubito2)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_grass.clear()
    gpu_pared.clear()
    gpu_cubito.clear()
    gpu_cubito2.clear()
    

    glfw.terminate()