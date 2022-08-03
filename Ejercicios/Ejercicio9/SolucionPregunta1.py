import openmesh as om
import numpy as np
import math
import random

def create_quad():
    # Creamos una malla de triangulos
    mesh = om.TriMesh()

    #  2 ==== 1
    #  |\   0 |
    #  | \    |
    #  |   \  |
    #  |    \ |
    #  | 1   \|
    #  3 ==== 0

    # Agregamos algunos vertices a la malla
    vh0 = mesh.add_vertex([0.5, -0.5, 0])
    vh1 = mesh.add_vertex([0.5, 0.5, 0])
    vh2 = mesh.add_vertex([-0.5, 0.5, 0])
    vh3 = mesh.add_vertex([-0.5, -0.5, 0])

    # Agregamos algunas caras a la malla
    fh0 = mesh.add_face(vh0, vh1, vh2)
    fh1 = mesh.add_face(vh0, vh2, vh3)

    return mesh

def create_gaussiana(N, a):

    # Definimos la función de la gaussiana
    def gaussiana(x, y, a):
        return a * math.exp(-.5*x**2 + -.5*y**2)

    # Creamos arreglos entre -5 y 5, de tamaño N
    xs = np.linspace(-5, 5, N)
    ys = np.linspace(-5, 5, N)

    # Creamos una malla de triangulos
    gaussiana_mesh = om.TriMesh()

    # Generamos un vertice para cada x,y,z
    for i in range(len(xs)):
        for j in range(len(ys)):
            x = xs[i]
            y = ys[j]
            z = gaussiana(x, y, a)
            
            # Agregamos el vertice a la malla
            gaussiana_mesh.add_vertex([x, y, z])

    # Podemos calcular el indice de cada punto (i,j) de la siguiente manera
    index = lambda i, j: i*len(ys) + j 
    
    # Creamos caras para cada cuadrado de la malla
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):

            # Conseguimos los indices por cada cuadrado
            isw = index(i,j)
            ise = index(i+1,j)
            ine = index(i+1,j+1)
            inw = index(i,j+1)

            # Obtenemos los vertices, y agregamos las caras
            vertexs = list(gaussiana_mesh.vertices())

            gaussiana_mesh.add_face(vertexs[isw], vertexs[ise], vertexs[ine])
            gaussiana_mesh.add_face(vertexs[ine], vertexs[inw], vertexs[isw])

    return gaussiana_mesh

def get_vertexs_and_indexes(mesh):
    # Obtenemos las caras de la malla
    faces = mesh.faces()

    # Creamos una lista para los vertices e indices
    vertexs = []

    # Obtenemos los vertices y los recorremos
    for vertex in mesh.points():
        vertexs += vertex.tolist()
        # Agregamos un color al azar
        vertexs += [random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)]

    indexes = []

    for face in faces:
        # Obtenemos los vertices de la cara
        face_indexes = mesh.fv(face)
        for vertex in face_indexes:
            # Obtenemos el numero de indice y lo agregamos a la lista
            indexes += [vertex.idx()]

    return vertexs, indexes

####################################################################################################
# Funciones para conseguir la isosuperficie
####################################################################################################

def get_isosurface_triangle(mesh, min_value, max_value):
    # Obtenemos las caras de la malla
    mesh_faces = mesh.faces()

    # Recorremos las caras
    for face in mesh_faces:
        # Si encontramos una que este en el rango buscado la devolvemos
        if face_in_range(mesh, face, min_value, max_value):
            return face
    
    # Si no encontramos cara, no devolvemos nada
    return

def face_in_range(mesh, face, min_value, max_value):
    # Obtenemos los vertices de la cara
    face_vertexes = list(mesh.fv(face))

    # Obtenemos las posiciones de los 3 vertices
    first_vertex = mesh.point(face_vertexes[0]).tolist()
    second_vertex = mesh.point(face_vertexes[1]).tolist()
    third_vertex = mesh.point(face_vertexes[2]).tolist()

    # Revisamos si alguno de los vertices esta en el rango buscado, devolvemos true si esta dentro del rango
    if (min_value <= first_vertex[2] <= max_value) or (min_value <= second_vertex[2] <= max_value) or (
            min_value <= third_vertex[2] <= max_value):
            return True
    
    return False

def get_in_range_faces(mesh, face, min_value, max_value, in_range_faces):
    # Si la cara no esta en el rango, o si ya pasamos por ella, terminamos de revisar
    # Darse cuenta que si la cara no esta en rango, entonces no seguiremos revisando las caras que siguen de aquella, ya que las caras de la isosuperficie estarán conectadas
    if not face_in_range(mesh, face, min_value, max_value) or face in in_range_faces:
        return in_range_faces

    # En otro caso agregamos la cara a una lista que contiene las caras que estan en rango
    in_range_faces += [face]

    # Obtenemos las caras adjacentes de la cara entregada
    adjacent_faces = mesh.ff(face)

    # Por cada cara adjacente recorremos recursivamente buscando las caras en rango
    # Darse cuenta que la linea 134 es para que no se quede infinitamente revisando todas las caras.
    for adjacent_face in adjacent_faces:
        in_range_faces = get_in_range_faces(mesh, adjacent_face, min_value, max_value, in_range_faces)

    # Devolvemos la lista de caras en rango
    return in_range_faces


def create_new_mesh(faces_list, old_mesh):
    # Creamos una malla nueva
    mesh = om.TriMesh()

    # Recorremos las caras
    for face in faces_list:
        # Obtenemos los vertices de la cara y sus posiciones
        vertexs = list(old_mesh.fv(face))
        vertex1 = list(old_mesh.point(vertexs[0]))
        vertex2 = list(old_mesh.point(vertexs[1]))
        vertex3 = list(old_mesh.point(vertexs[2]))

        # Añadimos los vertices a la malla nueva
        v1 = mesh.add_vertex(vertex1)
        v2 = mesh.add_vertex(vertex2)
        v3 = mesh.add_vertex(vertex3)

        # Añadimos la cara a la malla nueva
        mesh.add_face(v1, v2, v3)

    return mesh

def faces_positions(mesh):
    #creamos una variable con todas las caras de la malla
    mesh_faces = mesh.faces()
    positions =[]
    #recorremos cada cara en la malla
    for face in mesh_faces:
        #obtenemos una lista con los vertices de cada cara
        face_vertexes = list(mesh.fv(face))

        # Obtenemos las posiciones de los 3 vertices
        first_vertex = mesh.point(face_vertexes[0]).tolist()
        positions += [first_vertex]
        
    return positions

