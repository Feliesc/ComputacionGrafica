### **Modelación Jerárquica:** 
Para la creación del videojuego se utilizaron 4 grafos principales, 2 de ellos corresponden a grafos de escena (uno con texturas y 
otro con modelos geométricos), los otros dos grafos corresponden a grafos que contienen a los NPC, es decir zombis y humanos. El grafo que contiene a los zombis
y humanos no infectados es dibujado utilizando un Shader que les asigna las coordenadas de textura, esto para no tener que crear varias Gpu Shapes.
Por otro lado, los humanos enfermos están en otro grafo, esto se debe a que para ellos se utiliza otro Shader, el cual recibe un uniform que hace a los humanos
cambiar de color cuando se activa la funcionalidad de los lentes. A continuación, se muestra el grafo de escena con modelos geométricos:

![imagen](https://user-images.githubusercontent.com/80856926/194462881-1e47a08c-e443-4a4f-add2-0c69da0dc222.png)

Además de los grafos ya mencionados, se crearon grafos para la tienda y para el personaje dentro de ella, los cuales se agregaron como hijos al “grafo de escena
con polígonos simples”.

### **Shaders:**

En total se utilizaron 6 shaders, los cuales estaban relacionados con los siguientes puntos:
- Los polígonos sin textura
- Las texturas del fondo (pasto)
- Los zombis y humanos no contagiados (asignación de coordenadas de textura)
- Los humanos contagiados (además de las coordenadas de textura se le daba un uniform al Shader para cambiar el color)
- Hinata (se animaba al jugador dependiendo de la dirección del movimiento)
- El shader para renderizar texto (se utiliza en las pantallas de “You Win” y “Game Over”)

A los primeros 5 shaders se les pasó un uniform (índice de color) que multiplicaba las componentes de color, esto con el fin de que al pasar el tiempo
se fuera oscureciendo la pantalla y así dar la impresión de que estaba anocheciendo. Luego, en el momento en que se hacía completamente de noche, el juego 
mostraba el mensaje de Game Over. Cabe destacar que, para los shaders que usaban texturas, se debió excluir la componente alfa al momento de multiplicar,
esto con el fin de no modificar la transparencia.

### **Transformaciones:**

En cuanto a transformaciones, se utilizaron: Traslaciones, Rotaciones, Reflexiones, Escalamientos y Shearing. Algunas fueron realizadas en la creación de los grafos
y otras fueron enviadas a los shaders. Como se dijo anteriormente, se utilizaron texturas para animar tanto a Hinata como a los NPC, para lo cual fue necesario crear
“índices de textura” que iban cambiando con el tiempo y al recibir ciertos inputs. Estos índices se enviaban a los respectivos shaders mediante uniforms.
Para el caso del pasto, como se utilizó una textura más grande que el espacio utilizado, se usó un Mipmap (se usó la opción GL_LINEAR_MIPMAP_NEAREST),
además para envolver la textura se usó GL_REPEAT en ambos ejes.

### **Imágenes:**

![imagen](https://user-images.githubusercontent.com/80856926/194466230-667b2831-145d-4b2c-b362-9f9d08b4d4db.png)
![imagen](https://user-images.githubusercontent.com/80856926/194466249-83571cae-3d49-4420-80b5-a9e1a9e8fcd6.png)
![imagen](https://user-images.githubusercontent.com/80856926/194466265-e9a56637-b004-4754-9892-b0d59ee81321.png)

### **Ejecución:**

``python survival.py Z H T P``
donde 
* Z: Cantidad de zombies que aparecen cada T segundos.
* H: Cantidad de humanos que entran a la escena cada T segundos.
* P: La probabilidad de que un humano esté contagiado.
