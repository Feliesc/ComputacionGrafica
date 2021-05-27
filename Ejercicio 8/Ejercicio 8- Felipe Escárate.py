#Ejercicio 8 - Felipe Escárate Fernández
import glfw
from OpenGL.GL import *
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.performance_monitor as pm
import grafica.lighting_shaders as ls
import grafica.scene_graph as sg
import newLightShaders as nl
from Toroide import *

class PolarCamera:
    def __init__(self):
        self.center = np.array([0.0, 0.0, -0.5])
        self.theta = 0
        self.rho = 5
        self.eye = np.array([0.0, 0.0, 0.0])
        self.height = 0.5
        self.up = np.array([0, 0, 1])
        self.viewMatrix = None

    def set_theta(self, delta):
        self.theta = (self.theta + delta) % (np.pi * 2)

    def set_rho(self, delta):
        if ((self.rho + delta) > 0.1):
            self.rho += delta

    def update_view(self):
        self.eye[0] = self.rho * np.sin(self.theta) + self.center[0]
        self.eye[1] = self.rho * np.cos(self.theta) + self.center[1]
        self.eye[2] = self.height + self.center[2]

        viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
        )
        return viewMatrix

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True

        self.is_up_pressed = False
        self.is_down_pressed = False
        self.is_left_pressed = False
        self.is_right_pressed = False

        self.polar_camera = PolarCamera()

    def get_camera(self):
        return self.polar_camera

    def on_key(self, window, key, scancode, action, mods):

        if key == glfw.KEY_UP:
            if action == glfw.PRESS:
                self.is_up_pressed = True
            elif action == glfw.RELEASE:
                self.is_up_pressed = False

        if key == glfw.KEY_DOWN:
            if action == glfw.PRESS:
                self.is_down_pressed = True
            elif action == glfw.RELEASE:
                self.is_down_pressed = False

        if key == glfw.KEY_RIGHT:
            if action == glfw.PRESS:
                self.is_right_pressed = True
            elif action == glfw.RELEASE:
                self.is_right_pressed = False

        if key == glfw.KEY_LEFT:
            if action == glfw.PRESS:
                self.is_left_pressed = True
            elif action == glfw.RELEASE:
                self.is_left_pressed = False
        
        if key == glfw.KEY_SPACE:
            if action == glfw.PRESS:
                self.fillPolygon = not self.fillPolygon

        if key == glfw.KEY_ESCAPE:
            if action == glfw.PRESS:
                glfw.set_window_should_close(window, True)

        elif key == glfw.KEY_LEFT_CONTROL:
            if action == glfw.PRESS:
                self.showAxis = not self.showAxis


    #Funcion que recibe el input para manejar la camara
    def update_camera(self, delta):
        if self.is_left_pressed:
            self.polar_camera.set_theta(-2 * delta)

        if self.is_right_pressed:
            self.polar_camera.set_theta( 2 * delta)

        if self.is_up_pressed:
            self.polar_camera.set_rho(-5 * delta)

        if self.is_down_pressed:
            self.polar_camera.set_rho(5 * delta)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Ejercicio 8 - Felipe Escárate Fernández"

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    controller = Controller()
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

     # Different shader programs for different lighting strategies
    phongPipeline = nl.MultiplePhongShaderProgram()
    phongTexPipeline = nl.MultipleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(4))

    tex_toroid = createToroidNode(phongTexPipeline, "sprites/tex.jpg", 0,0,0.2 , 0.5)
    tex_toroid2 = createToroidNode(phongTexPipeline, "sprites/tex2.jpg", 0,0,-0.6, -0.2)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()
    r = 0.5
    g = 0
    b = 0.25

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()

        delta = t1 -t0
        t0 = t1

        # Using GLFW to check for input events
        glfw.poll_events()

        controller.update_camera(delta)
        camera = controller.get_camera()
        viewMatrix = camera.update_view()

        # Setting up the projection transform
        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        lightingPipeline = phongPipeline
        #lightposition = [1*np.cos(t1), 1*np.sin(t1), 2.3]
        lightposition = [0, 0, 2.3]

        #r = np.abs(((0.5*t1+0.00) % 2)-1)
        #g = np.abs(((0.5*t1+0.33) % 2)-1)
        #b = np.abs(((0.5*t1+0.66) % 2)-1)
        
        #vamos alternando el """tipo""" de luz cada 1 segundo (son 3 """tipos""" de luz)
        if int(t1)%3==0:
            La = [0.6, 0.6, 0.7]
            Ld = [0.6, 0.6, 0.6]
            Ls = [0.85, 1.0, 1.0]
            Ks = [1.0, 1.0, 1.0]
            LightDirection = [0, -1, -1]
        elif int(t1)%3==1:
            La = [0.4, 0.6, 0.4]
            Ld = [0.3, 0.4, 0.2]
            Ls = [0.7, 0.7, 0.7]
            Ks = [0.5, 0.4, 0.2]
            LightDirection = [-1, -0.3, 0.3]
        elif int(t1)%3==2:
            La = [0.9, 0.7, 0.7]
            Ld = [0.1, 0.1, 0.1]
            Ls = [0.5, 0.5, 0.5]
            Ks = [0.6, 0.4, 0.2]
            LightDirection = [1, 0, 0]
        
        # Setting all uniform shader variables
        glUseProgram(phongTexPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "La"), La[0], La[1], La[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ld"), Ld[0], Ld[1], Ld[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ls"), Ls[0], Ls[1], Ls[2])

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ka"), 0.7, 0.7, 0.7)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Kd"), 0.7, 0.7, 0.7)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ks"), Ks[0], Ks[1], Ks[2])

        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram,  "lightDirection"), LightDirection[0], LightDirection[1], LightDirection[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(phongTexPipeline.shaderProgram, "shininess"), 100)
        
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "constantAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        sg.drawSceneGraphNode(tex_toroid, phongTexPipeline, "model")
        sg.drawSceneGraphNode(tex_toroid2, phongTexPipeline, "model")
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuAxis.clear()

    glfw.terminate()
