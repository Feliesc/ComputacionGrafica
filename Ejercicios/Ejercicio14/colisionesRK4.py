# coding=utf-8
"""Circles, collisions and gravity"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm


# Example parameters

NUMBER_OF_CIRCLES = 20
CIRCLE_DISCRETIZATION = 20
RADIUS = 0.03
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

class Circle:
    def __init__(self, pipeline, position, velocity, r, g, b):
        shape = bs.createColorCircle(CIRCLE_DISCRETIZATION, r, g, b)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 2 * RADIUS
        bs.scaleVertices(shape, 6, (scaleFactor, scaleFactor, 1.0))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        self.position = position
        self.radius = RADIUS
        self.velocity = velocity

    def action(self, t, deltaTime):
        # RK4 integration
        pos1 = self.position
        vel1 = self.velocity
        k1 = self.vel(0, pos1)
        k2 = self.vel(0+deltaTime/2, pos1+(deltaTime/2)*k1)
        k3 = self.vel(0+deltaTime/2, pos1+(deltaTime/2)*k2)
        k4 = self.vel(0+deltaTime, pos1+deltaTime*k3)

        self.position = pos1 + (deltaTime/6)*(k1+2*k2+2*k3+k4)

        K1 = self.gravity(self.position)
        K2 = self.gravity(self.position+(deltaTime/2)*K1)
        K3 = self.gravity(self.position+(deltaTime/2)*K2)
        K4 = self.gravity(self.position+deltaTime*K3)

        self.velocity = vel1 + (deltaTime/6)*(K1+2*K2+2*K3+K4)

    def vel(self, h, pos):
        return self.velocity + h*self.gravity(pos)
    
    def gravity(self, pos):
        g = 1/(np.linalg.norm(pos)**2)
        if g>200:
            g = 0.0001
        normalizado = pos/np.linalg.norm(pos)
        prodPunto = np.dot(normalizado, np.array([1,0]))
        if pos[1]>=0:
            phi = np.arccos(prodPunto)
        else:
            phi = -np.arccos(prodPunto)
        gx = -g*np.cos(phi)
        gy = -g*np.sin(phi)
        return np.array([gx,gy], dtype=np.float32)

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(self.position[0], self.position[1], 0.0)
        )
        self.pipeline.drawCall(self.gpuShape)
    

def rotate2D(vector, theta):
    """
    Direct application of a 2D rotation
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        cos_theta * vector[0] - sin_theta * vector[1],
        sin_theta * vector[0] + cos_theta * vector[1]
    ], dtype = np.float32)


def collide(circle1, circle2):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    
    assert isinstance(circle1, Circle)
    assert isinstance(circle2, Circle)

    normal = circle2.position - circle1.position
    normal /= np.linalg.norm(normal)

    circle1MovingToNormal = np.dot(circle2.velocity, normal) > 0.0
    circle2MovingToNormal = np.dot(circle1.velocity, normal) < 0.0

    if not (circle1MovingToNormal and circle2MovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both circles, 1 and 2.
        v1n = np.dot(circle1.velocity, normal) * normal
        v1t = np.dot(circle1.velocity, tangent) * tangent

        v2n = np.dot(circle2.velocity, normal) * normal
        v2t = np.dot(circle2.velocity, tangent) * tangent

        # swaping the normal components...
        # this means that we applying energy and momentum conservation
        circle1.velocity = v2n + v1t
        circle2.velocity = v1n + v2t


def areColliding(circle1, circle2):
    assert isinstance(circle1, Circle)
    assert isinstance(circle2, Circle)

    difference = circle2.position - circle1.position
    distance = np.linalg.norm(difference)
    collisionDistance = circle2.radius + circle1.radius
    return distance < collisionDistance


def collideWithBorder(circle):

    # Right
    if circle.position[0] + circle.radius > 1.0:
        circle.velocity[0] = -abs(circle.velocity[0])

    # Left
    if circle.position[0] < -1.0 + circle.radius:
        circle.velocity[0] = abs(circle.velocity[0])

    # Top
    if circle.position[1] > 1.0 - circle.radius:
        circle.velocity[1] = -abs(circle.velocity[1])

    # Bottom
    if circle.position[1] < -1.0 + circle.radius:
        circle.velocity[1] = abs(circle.velocity[1])


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.circleCollisions = False
        self.useGravity = False

# we will use the global controller as communication with the callback function
controller = Controller()


# This function will be executed whenever a key is pressed or released
def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
        print("Fill polygons?", controller.fillPolygon)

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_1:
        controller.circleCollisions = not controller.circleCollisions
        print("Collisions among circles?", controller.circleCollisions)

    elif key == glfw.KEY_2:
        controller.useGravity = not controller.useGravity
        print("Gravity?", controller.useGravity)

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    # Creating a glfw window
    title = "Circles, collisions and gravity"
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Creating shapes on GPU memory
    circles = []
    for i in range(NUMBER_OF_CIRCLES):
        position = np.array([
            random.uniform(-1.0 + RADIUS, 1.0 - RADIUS),
            random.uniform(-1.0 + RADIUS, 1.0 - RADIUS)
        ])
        velocity = np.array([
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5)
        ])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    noGravityAcceleration = np.array([0.0, 0.0], dtype=np.float32)
    gravityAcceleration = noGravityAcceleration
    t0 = glfw.get_time()

    # Application loop
    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Using the time as the theta parameter
        theta = glfw.get_time()
        deltaTime = theta-t0
        t0 = theta

        if controller.useGravity:
            acceleration = gravityAcceleration
        else:
            acceleration = noGravityAcceleration
        
        # Physics!
        for circle in circles:
            # moving each circle
            circle.action(theta, deltaTime)

            # checking and processing collisions against the border
            collideWithBorder(circle)

        # checking and processing collisions among circles
        if controller.circleCollisions:
            for i in range(len(circles)):
                for j in range(i+1, len(circles)):
                    if areColliding(circles[i], circles[j]):
                        collide(circles[i], circles[j])

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # drawing all the circles
        for circle in circles:
            circle.draw()

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    for circle in circles:
        circle.gpuShape.clear()
    
    glfw.terminate()
