Para gran parte de los aspectos realizados en la tarea se hizo uso del programa Blender, partiendo por algunas mallas geométricas, como lo son la mesa de pool,
el palo, y los focos que se ven en el fondo. La creación de la mesa de pool se hizo deformando un cubo, agregándole caras y realizando distintas operaciones disponibles
en el programa. Para crear los orificios de la mesa de pool, fue necesario importar el add-on “Bool Tools” con la finalidad de usar la operación binaria de “diferencia”
entre unos cilindros y la mesa anteriormente modelada.


La iluminación global, fue realizada utilizando el Blender. Para esto se colocaron algunos de los objetos anteriormente mencionados, y se utilizó el motor de renderizado
Cycles, el cual permite el uso de Path tracing. Utilizando la iluminación global obtenida, se generó una “High Dinamic Range Image” (HDRI) en formato .png. 
Para la renderización de esta imagen, se movió la cámara al centro de la escena y se configuró como se muestra a continuación:



Este archivo, se utilizaría posteriormente como textura, la cual, al ser mapeada al interior de una esfera, generaría una “skybox”. Por otro lado, las texturas
correspondientes al palo y a la mesa de pool, fueron creadas utilizando las herramientas de Blender para el mapeo de las coordenadas UV y el coloreado de texturas.
También, se le aplicó iluminación global a la textura de la mesa de pool, para que fuera consistente con la iluminación del entorno.

Observaciones:
• Tanto las texturas de las bolas de pool como las del escenario fueron descargadas de internet.
• En general, como todas las texturas utilizadas fueron hechas a medida, no fue necesario utilizar Mipmaps.

En cuanto a las vistas y proyecciones se crearon “dos cámaras”, para esto se variaban los vectores `at`, `eye` y `up`. La primera cámara, tenía como vector `at` a
la posición de la bola enfocada, por otro lado, su vector eye, correspondía a un desplazamiento desde el vector at una distancia R, esto, en coordenadas polares.
Con lo cual, si la bola se movía, la cámara perseguía a la bola, además al presionar las flechas, la cámara rotaba alrededor de la bola, esto porque el vector `eye`
estaba trasladado en coordenadas polares alrededor del vector `at`. Finalmente el vector up correspondía a $\hat{z}$ Para la segunda cámara, el vector `at` correspondía
origen, es decir (0,0,0), el vector eye se encontraba en (0,0,15) y el vector up estaba dado por $-\hat{x}$, de esta forma, se tenía una vista superior a la mesa de pool.


Para la implementación de las físicas y colisiones, se creó una clase “bola” a la cual pertenecían cada una de las bolas de billar. Esta clase tenía una serie de métodos
para verificar las colisiones:

* cueCollision, corresponde al método que detecta la colisión entre el palo y la bola a la cual se está 
enfocando. Esta colisión consiste simplemente, en detectar si la posición del palo (expresada 
como un número entero) llega a un valor en el cual toca a la bola. La velocidad con la que la esfera 
sale disparada depende de la energía con la que se “cargó el palo”, esta energía es visible en el 
programa y teniendo este valor se puede despejar la rapidez como sigue:

$$E_{c} = \frac{1}{2} m v^{2} \rightarrow \sqrt{\frac{2 E_{c}}{m}}$$

La dirección de la velocidad viene dada por el ángulo en que se encontraba el palo, el cual, 
coincide con el ángulo en el que se encontraba la cámara, por ende, se utiliza este valor.


* ballCollision, es el método que detecta la colisión de una bola con las demás, para esto se compara 
si la resta de las posiciones es menor a la suma de los radios. Si se tiene lo anterior, estamos ante 
una colisión, por lo cual, al tratarse de un choque inelástico, las rapideces resultantes se calculan 
como sigue:

$$v_{1}' = \frac{m(1-C)v_{1} + m (1+C)v_{2}}{m+m} = \frac{(1-C)v_{1} + (1+C)v_{2}}{2}$$

$$v_{2}' = \frac{(1-C)v_{2} + (1+C)v_{1}}{2}$$

Con C, el coeficiente de restitución
La dirección de las velocidades, viene dada por el vector que corresponde a la resta de las 
posiciones de las bolas (vector normalizado). 

* borderCollision, calcula las colisiones de la bola con el borde de la mesa, para lo cual, se 
comprueba si la posición actual de la esfera, está en los límites. Si sucede lo anterior, se considera 
un choque con el borde, por lo cual, se invierte la dirección de una componente de la velocidad 
dependiendo del borde en el cual chocó la bola. Además, se multiplica la rapidez por 0,75 para 
ralentizar la pelota.

* colHole, revisa si la pelota entra en alguno de los hoyos de la mesa, para 
esto se consideran los orificios como esferas y se compara de manera 
similar a ballCollision, con la diferencia que, en vez de cambiar la velocidad 
de la pelota, esta cambia su trayectoria a una descrita por una curva de 
Hermite (para entrar al agujero).

Durante la trayectoria de las bolas en la mesa de pool, estas son afectadas por el roce, por lo cual, se tiene 
que: $F_{roce} = \mu \cdot Normal$ y como la superficie es plana y paralela al suelo, $Normal = g$ (con $g>0$). 
Entonces, se tiene que la aceleración provocada por el roce estaría dada por: $\mu \cdot g$, de tal forma, que, en 
cada iteración, se le resta $\mu \cdot g \cdot dt$ a la rapidez (método de Euler).
Luego, para obtener la rotación de cada bola, se usa su rapidez angular, la cual es calculada como:


Por otro lado, se implementó un aumento en la constante de gravitación universal, lo cual se activa 
presionando la tecla “G”. Con este aumento, se toma 𝑐𝑜𝑛𝑠𝑡𝑎𝑛𝑡𝑒𝐷𝑒𝐺𝑟𝑎𝑣𝑖𝑡𝑎𝑐𝑖ó𝑛𝑈𝑛𝑖𝑣𝑒𝑟𝑠𝑎𝑙 = 10, de tal 
forma, que las bolas se atraen entre ellas. Esto se pudo hacer de la siguiente forma:
- Para cada bola, se calculó el centro de masa de las otras bolas.
- Teniendo esto, se pudo obtener la aceleración de gravedad a la cual la bola está sometida.
- Con la aceleración se calculó la velocidad actual utilizando el método de Runge-Kutta 4.
- Finalmente se calcula la posición usando Runge-Kutta 4.

Para observar esto de mejor manera, se creó una malla al nivel de la mesa, que estaba formada a partir 
de una grilla a la cual se le aplicó una triangulación de Delauney. En cada punto de la grilla se calculó el 
potencial gravitatorio ejercido por las pelotas, y se pasó esta información como color. Para esto se tomó 
la magnitud del potencial en cada punto de la grilla y se dividió para que tomara valores entre 0 y 1, de 
tal forma que si la magnitud del potencial era máxima el punto de la grilla tomaba un color rojo y si era 
mínima tomaba un color azulado. Con esto se podría observar el campo del potencial en tiempo real.

