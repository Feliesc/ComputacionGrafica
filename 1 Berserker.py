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

def create_pared(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                    colors
        -1.0, y0, 0.0,              0.2, 0.2, 0.2,
        1.0, y0, 0.0,               0.2, 0.2, 0.2,
        1.0, y1*0.7, 0.0,           0.5, 0.5, 0.5,
        1.0, y1*0.8, 0.0,           0.5, 0.5, 0.5,
        0.3, y1*0.8, 0.0,           0.5, 0.5, 0.5,
        0.3, y1, 0.0,               0.7, 0.7, 0.7,
        0.0, y1, 0.0,               0.7, 0.7, 0.7,
        0.0, y1*0.8, 0.0,           0.5, 0.5, 0.5,
        0.0, y1*0.7, 0.0,           0.5, 0.5, 0.5,
        -0.3, y1*0.7, 0.0,          0.5, 0.5, 0.5,
        -0.3, y1*0.8, 0.0,          0.5, 0.5, 0.5,
        -1.0, y1*0.8, 0.0,          0.5, 0.5, 0.5,
        -1.0, y1*0.7, 0.0,          0.5, 0.5, 0.5]
    
    indices = [0,1,2,2,12,0,
                2,3,8,8,3,7,
                4,5,6,6,7,4,
                9,10,11,11,12,9]

    return Shape(vertices, indices)

#Se crea un Enderman(personaje de Minecraft que se teletransporta)
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

    pared_shape = create_pared(y0=-0.2, y1=0.45)
    gpu_pared = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_pared)
    vertexPipeline.setupVAO(gpu_pared)
    nochePipeline.setupVAO(gpu_pared)
    gpu_pared.fillBuffers(pared_shape.vertices, pared_shape.indices, GL_STATIC_DRAW)

    enderman_shape = create_enderman(x0=-0.3, y0=-0.22, width=0.2, height=0.9)
    gpu_enderman = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_enderman)
    vertexPipeline.setupVAO(gpu_enderman)
    nochePipeline.setupVAO(gpu_enderman)
    gpu_enderman.fillBuffers(enderman_shape.vertices, enderman_shape.indices, GL_STATIC_DRAW)

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
            vertexPipeline.drawCall(gpu_enderman)
            
        elif (controller.effect2):
            glUseProgram(nochePipeline.shaderProgram)
            nochePipeline.drawCall(gpu_sky)
            nochePipeline.drawCall(gpu_grass)
            nochePipeline.drawCall(gpu_pared)
            nochePipeline.drawCall(gpu_enderman)
            nochePipeline.drawCall(gpu_cubito)
            nochePipeline.drawCall(gpu_cubito2)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_grass)
            simplePipeline.drawCall(gpu_pared)
            vertexPipeline.drawCall(gpu_enderman)
            simplePipeline.drawCall(gpu_cubito)
            simplePipeline.drawCall(gpu_cubito2)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_grass.clear()
    gpu_pared.clear()
    gpu_enderman.clear()
    gpu_cubito.clear()
    gpu_cubito2.clear()
    

    glfw.terminate()