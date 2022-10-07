### Instrucciones de ejecución
El primer programa se ejecuta utilizando `python displacement_view.py`

mientras que el segundo con `python water_slide.py N V` siendo N la cantidad de obstáculos generados y V la velocidad del bote (Se recomienda N = 8 y V = 4). 

Además, durante el segundo programa se utilizan las teclas: derecha 
e izquierda para moverse, espacio para ver los polígonos utilizados, F para mover los brazos de la persona 
y V para cambiar la vista de la cámara.


### Curvas: 
Para crear el tobogán pedido, se creó una spline de Catmull-Rom, hecha con 20 puntos de control, los cuales fueron copiados para crear otras 8 splines similares, 
que describieran la forma del tobogán. Para que las splines no se cruzaran entre ellas y estuvieran perfectamente separadas, se tuvo que realizar un cálculo de 
tangente en cada punto de la spline inicial, y hacer producto cruz de esta con el vector unitario ẑ, con el fin de poder obtener la normal de cada punto.
Con esta normal se puede ver la dirección en que deben estar los puntos las curvas hechas en base a la original. Además como se buscaba que la sección transversal
del tobogán fuera circular, se usaron coordenadas polares para obtener las diferentes posiciones de cada una de las 8 curvas.

![imagen](https://user-images.githubusercontent.com/80856926/194467603-d3280197-2954-4c85-8930-ce0458a83a70.png)
![imagen](https://user-images.githubusercontent.com/80856926/194467619-e277e701-3519-48f9-ad62-131a3584434f.png)

Además de estas 8 curvas, se crearon otras 2 bajo el mismo principio, con el fin de describir la trayectoria de la cámara y la del bote.
Por otro lado, se creó otro tobogán a partir de una curva de Hermite unida con una de Bezier, para usarlo como decoración. Usando las splines de Catmull-Rom,
se creo una malla poligonal del tobogán utilizando la librería openmesh. Además, para crear el río que va dentro del tobogán, se creó una malla de poligonos,
usando 2 de las 8 curvas que describen al tobogán, y acomodandolas para que se viera como se deseaba. 

### Texturas

Para el agua se utilizaron 2 texturas, una que se dibujaba, y otra para simular el desplazamiento. Para esto, se leyó el canal de color para la textura de
desplazamiento; luego se promediaron los valores de las componentes R, G, B y A, para agregarle este valor a las coordenadas de textura de la textura a dibujar.
Como las texturas del río y las del agua fuera del tobogán eran las mismas, al momento de enviarlas a dibujar, fueron reutilizadas para ahorrar memoria.

### Shaders:

En total, se utilizaron 7 shaders, los cuales se relacionan con los siguientes puntos:
- El desplazamiento del agua en el caso de 2 dimensiones.
- El desplazamiento del agua en el tobogán (usa iluminación local con 4 luces).
- El desplazamiento del agua fuera del tobogán (usa una luz direccional).
- El tobogán en sí (usa textura e iluminación local).
- El bote, persona y obstáculos (usa el modelo de Gouraud y recibe 4 fuentes de luz).
- El texto que se muestra al final.

De estos shaders, 6 fueron creados haciendo las modificaciones correspondientes a otros shaders usados en el curso. Notar que para los shaders relacionados con agua,
se debió mover la textura de desplazamiento, lo cual se hizo en el Vertex Shader, cambiando ahí las coordenadas de textura ahí. Para esto se le pasó un uniform (float)
que describía el “avance” de la textura. Además, al Fragment Shader, se le pasaron otros uniforms para crear efectos de deformación distintos.

La iluminación local se hizo siguiendo el modelo de iluminación de Gouraud, al cual, en vez de darle solo una fuente de luz, se le dieron 4. Una de las fuentes de luz,
correspondía a una luz blanca que sigue la posición del bote (como si fuera una linterna en el bote); en cambio, las otras 3 luces tienen posiciones fijas dentro del
tobogán y son de color rojo (esto hace que el agua parezca roja en ciertas zonas). Para el shader del agua fuera del tobogán, simplemente se usó una luz direccional,
esto con el fin de que se viera iluminado afuera. Para esta tarea, se crearon 3: modelos geométricos: un cilindro, el tobogán con curvas de Hermite y Bezier, y los
Toroides que se usaron para hacer los obstáculos.

### Modelos 

Por otro lado, el bote se creó usando Blender y se exportó como OBJ para leerlo en Python. Luego, al tobogán se le puso una textura de piedra, la cual, al ser
de una resolución más alta que la del espacio utilizado, fue necesario utilizar Mipmap (se usó la opción GL_NEAREST_MIPMAP_LINEAR), además para envolver la 
textura se usó GL_REPEAT en ambos ejes.

Además, se usó una esfera, la cual fue utilizada para crear a la persona encima del bote, utilizando modelación jerárquica de la siguiente forma.

![imagen](https://user-images.githubusercontent.com/80856926/194468234-62163d5d-b319-47fb-9038-d4368437fa2b.png)

[Notar que los brazos de la persona se pueden mover si se mantiene la tecla F en la ejecución del programa.]


También se creó un nodo aparte que contenía todos los obstáculos con el fin de dibujarlos más fácilmente. 

Notar que, en el grafo Bote-Persona, se usaron transformaciones de escalamiento, rotación y traslación. Por otro lado, también se hicieron transformaciones durante el
transcurso del programa, ya que, se iba aplicando una traslación a medida que el bote avanzaba, y se aplicaba una rotación con el fin de que el bote apuntara hacia
donde corre el agua del tobogán. Para obtener este ángulo de rotación se usaron las tangentes de la trayectoria del bote y se les hizo producto punto con el vector
unitario $\hat{x}$. Notar que para que el movimiento del bote se viera continuo se calculaba su posición actual como:

$$posiciónActual = posición_{i} * (1 - \delta) + posición_{i+1}* \delta$$

Siendo $posición_{i}$ un punto de la spline de Catmull-Rom que describe la trayectoria del bote (la que se nombró anteriormente) y la posición_{i+1} el punto 
siguiente en esa misma spline (delta va desde 0 hasta 1 y su valor vuelve a 0 cuando $posiciónActual = posición_{i+1}$, en ese caso, $i = i + 1$).
De esta misma forma se calculaba la tangente actual (para la rotación del bote) y la posición de la cámara actual.

Con respecto a la transformación de vista, esta tenía como vector eye la recién nombrada “posición actual de la cámara”, luego, su vector `at` era posición actual
del bote y su vector `up`, era el vector unitario $\hat{z}$, de esta forma, se tiene una vista en tercera persona del bote. Por otro lado, si se mantiene la tecla V
durante el transcurso del programa, se cambia el vector `at` por la tangente de la trayectoria y el vector `eye` por la posición del bote, con lo cual,
se tiene una vista en primera persona. Finalmente, cuando termina el nivel, la cámara se mueve de tal forma que deja ver el tobogán hecho con curvas de 
Hermite y Bezier.

![imagen](https://user-images.githubusercontent.com/80856926/194468976-555de3ae-ed82-42fb-9ba9-d437c0deae7d.png)





