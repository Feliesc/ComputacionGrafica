from OpenGL.GL import *
import OpenGL.GL.shaders
from grafica.gpu_shape import GPUShape
from PIL import Image
import numpy as np

#hacemos el GPU Shape que soporta 2 texturas
class TexGPUShape(GPUShape):
    def __init__(self):
        """VAO, VBO, EBO and texture handlers to GPU memory"""
        super().__init__()
        self.texture2 = None

    def __str__(self):
        return super().__str__() + "  tex=" + str(self.texture2)

    def clear(self):
        """Freeing GPU memory"""

        super().clear()
        if self.texture2 != None:
            glDeleteTextures(1, [self.texture2])

#Se crea el shader para las texturas del agua
class waterShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;
            uniform float texIndex;

            in vec2 position;
            out vec2 outTexCoords;
            out vec2 outTexCoords2;
            out vec3 fragPosition;

            void main()
            {
                gl_Position = transform * vec4(position, 0, 1.0f);
                //se utilizan dos cuadrados y se van moviendo para dar el efecto de que el agua no termina

                //vemos el primero de los cuadrados
                if(position.x>0 && position.y>0){
                    outTexCoords = vec2(1, texIndex-1); 
                }
                else if(position.x<0 && position.y>0){
                    outTexCoords = vec2(0, texIndex-1);
                }
                else if(position.x>0 && position.y<0){
                    outTexCoords = vec2(1, texIndex);
                }
                else{
                    outTexCoords = vec2(0, texIndex);
                } 

                //ahora vemos el segundo cuadrado
                if(position.x>0 && position.y>0){
                    outTexCoords2 = vec2(1, texIndex); 
                }
                else if(position.x<0 && position.y>0){
                    outTexCoords2 = vec2(0, texIndex);
                }
                else if(position.x>0 && position.y<0){
                    outTexCoords2 = vec2(1, 1+texIndex);
                }
                else{
                    outTexCoords2 = vec2(0, 1+texIndex);
                } 
                
                fragPosition = vec3(transform * vec4(position, 0.0, 1.0));
                    
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;
            in vec2 outTexCoords2;
            in vec3 fragPosition;

            out vec4 outColor;

            uniform sampler2D samplerTex;
            uniform sampler2D displacement;
            uniform float posIndex;
            uniform float deformationX;
            uniform float deformationY;

            void main()
            {   
                //le aplicamos las coordenadas de textura del primer cuadrado a la textura de ruido
                vec4 colorDisplacement1 = texture(displacement, vec2(outTexCoords.x+deformationX,outTexCoords.y+deformationY));
                //calculamos el promedio de los colores
                float promedioColores1 = (colorDisplacement1.r+colorDisplacement1.g+colorDisplacement1.b+colorDisplacement1.a)/4;
                //ahora usamos este promedio dar el efecto de deformación a la textura que se dibuja
                vec2 displacementCoords1 = vec2(4*(outTexCoords.x+promedioColores1*0.25)/5,outTexCoords.y);
                
                //hacemos lo mismo para el segundo quad
                vec4 colorDisplacement2 = texture(displacement, vec2(outTexCoords2.x+deformationX,outTexCoords2.y+deformationY));
                float promedioColores2 = (colorDisplacement2.r+colorDisplacement2.g+colorDisplacement2.b+colorDisplacement2.a)/4;
                vec2 displacementCoords2 = vec2(4*(outTexCoords2.x+promedioColores2*0.25)/5,outTexCoords2.y);

                if(fragPosition.y<posIndex){
                    outColor = texture(samplerTex, displacementCoords1);
                }
                else{
                    outColor = texture(samplerTex, displacementCoords2);
                }
                
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 2d vertices => 2*4 = 8 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)

#hacemos el mismo shader pero en 3D (para ponerlo en el tobogán)
#Además, le agregamos iluminación local
class water3DShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 projection;
            uniform mat4 view;
            uniform mat4 model;

            uniform float texIndex;
            
            uniform vec3 lightPosition1;
            uniform vec3 lightPosition2;
            uniform vec3 lightPosition3;
            uniform vec3 lightPosition4;
            
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            in vec3 position;
            //Son como las coordenadas de textura, pero en realidad se usan para hacer el paso entre el shader en 2D y en 3D
            in vec2 Coords2D;
            in vec3 normal;

            out vec2 outTexCoords;
            out vec2 outTexCoords2;
            out float quadsLimit;
            out vec3 vertexLightColor;

            void main()
            {
                gl_Position = projection * view * model * vec4(position, 1.0f);
                //se utilizan dos cuadrados y se van moviendo para dar el efecto de que el agua no termina

                //vemos el primero de los cuadrados(el de abajo)
                if(Coords2D.x>0 && Coords2D.y>0){
                    outTexCoords = vec2(2, texIndex-1); 
                }
                else if(Coords2D.x<0 && Coords2D.y>0){
                    outTexCoords = vec2(0, texIndex-1);
                }
                else if(Coords2D.x>0 && Coords2D.y<0){
                    outTexCoords = vec2(2, texIndex);
                }
                else{
                    outTexCoords = vec2(0, texIndex);
                } 

                //ahora vemos el segundo cuadrado
                if(Coords2D.x>0 && Coords2D.y>0){
                    outTexCoords2 = vec2(2, texIndex); 
                }
                else if(Coords2D.x<0 && Coords2D.y>0){
                    outTexCoords2 = vec2(0, texIndex);
                }
                else if(Coords2D.x>0 && Coords2D.y<0){
                    outTexCoords2 = vec2(2, 1+texIndex);
                }
                else{
                    outTexCoords2 = vec2(0, 1+texIndex);
                } 
                
                quadsLimit = Coords2D.y;


                //Hecho esto, agregamos la iluminación local:
                vec3 vertexPos = vec3(model * vec4(position, 1.0));

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);

                //Como hay 4 fuentes de luz, y debemos considerarlas todas, usamos una lista para las ultimas 3
                vec3 lights[3] = vec3[](lightPosition2, lightPosition3, lightPosition4);

                //vector donde se suman todas las fuentes de luz
                vec3 total = vec3(0.0f, 0.0f, 0.0f);

                //partimos por la primera luz
                vec3 toLight = lightPosition1 - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.001);
                vec3 diffuse = vec3(0.4, 0.4, 0.4) * vec3(1.0, 1.0, 1.0) * diff;
                    
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = vec3(0.2, 0.2, 0.2) * vec3(1.0, 1.0, 1.0) * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;

                total += (diffuse + specular) / attenuation;

                //luego, iteramos las otras fuentes de luz (usando la lista)
                //Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < 3; i++)
                {
                    vec3 toLight = lights[i] - vertexPos;
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(norm, lightDir), 0.001);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - vertexPos);
                    vec3 reflectDir = reflect(-lightDir, norm);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;

                    //se suma la contribución de la luz i al total
                    total += (diffuse + specular) / attenuation;
                } 



                
                vertexLightColor = ambient + total;
                    
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;
            in vec2 outTexCoords2;
            in float quadsLimit;
            in vec3 vertexLightColor;

            out vec4 outColor;

            uniform sampler2D samplerTex;
            uniform sampler2D displacement;
            uniform float posIndex;
            uniform float deformationX;
            uniform float deformationY;

            void main()
            {   
                //le aplicamos las coordenadas de textura del primer cuadrado a la textura de ruido
                vec4 colorDisplacement1 = texture(displacement, vec2(outTexCoords.x+deformationX,outTexCoords.y+deformationY));
                //calculamos el promedio de los colores
                float promedioColores1 = (colorDisplacement1.r+colorDisplacement1.g+colorDisplacement1.b+colorDisplacement1.a)/4;
                //ahora usamos este promedio dar el efecto de deformación a la textura que se dibuja
                vec2 displacementCoords1 = vec2(4*(outTexCoords.x+promedioColores1*0.25)/5,outTexCoords.y);
                
                //hacemos lo mismo para el segundo quad
                vec4 colorDisplacement2 = texture(displacement, vec2(outTexCoords2.x+deformationX,outTexCoords2.y+deformationY));
                float promedioColores2 = (colorDisplacement2.r+colorDisplacement2.g+colorDisplacement2.b+colorDisplacement2.a)/4;
                vec2 displacementCoords2 = vec2(4*(outTexCoords2.x+promedioColores2*0.25)/5,outTexCoords2.y);

                if(quadsLimit<posIndex){
                    vec4 color = texture(samplerTex, displacementCoords1);
                    outColor = vec4(vertexLightColor, 1.0) * color;
                }
                else{
                    vec4 color = texture(samplerTex, displacementCoords2);
                    outColor = vec4(vertexLightColor, 1.0) * color;
                }
                
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d coords => 3*4 + 2*4 + 3*4= 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        #Son como las coordenadas de textura, pero en realidad se usan para hacer el paso entre el shader en 2D y en 3D
        Coords2D = glGetAttribLocation(self.shaderProgram, "Coords2D")
        glVertexAttribPointer(Coords2D, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(Coords2D)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)
    
    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, TexGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

#ahora creamos un pipeline para el mar
#este usa una luz direccional (sol)
#no recibe fuentes de luz
class seaShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 projection;
            uniform mat4 view;
            uniform mat4 model;

            uniform float texIndex;
            
            uniform vec3 lightPosition;
            
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            in vec3 position;
            //Son como las coordenadas de textura, pero en realidad se usan para hacer el paso entre el shader en 2D y en 3D
            in vec2 Coords2D;
            in vec3 normal;

            out vec2 outTexCoords;
            out vec2 outTexCoords2;
            out float quadsLimit;
            out vec3 vertexLightColor;

            void main()
            {
                gl_Position = projection * view * model * vec4(position, 1.0f);
                //se utilizan dos cuadrados y se van moviendo para dar el efecto de que el agua no termina

                //vemos el primero de los cuadrados(el de abajo)
                if(Coords2D.x>0 && Coords2D.y>0){
                    outTexCoords = vec2(5, (texIndex-1)*5); 
                }
                else if(Coords2D.x<0 && Coords2D.y>0){
                    outTexCoords = vec2(0, (texIndex-1)*5);
                }
                else if(Coords2D.x>0 && Coords2D.y<0){
                    outTexCoords = vec2(5, texIndex*5);
                }
                else{
                    outTexCoords = vec2(0, texIndex*5);
                } 

                //ahora vemos el segundo cuadrado
                if(Coords2D.x>0 && Coords2D.y>0){
                    outTexCoords2 = vec2(5, (texIndex)*5); 
                }
                else if(Coords2D.x<0 && Coords2D.y>0){
                    outTexCoords2 = vec2(0, texIndex*5);
                }
                else if(Coords2D.x>0 && Coords2D.y<0){
                    outTexCoords2 = vec2(5, (1+texIndex)*5);
                }
                else{
                    outTexCoords2 = vec2(0, (1+texIndex)*5);
                } 
                
                quadsLimit = Coords2D.y;

                //Hecho esto, agregamos la iluminación local:
                vec3 vertexPos = vec3(model * vec4(position, 1.0));

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 lightDir = vec3(0,0,20);
                float diff = max(dot(norm, lightDir), 0);
                vec3 diffuse = vec3(0.05, 0.05, 0.05) * diff;
                    
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = vec3(0.05, 0.05, 0.05) * spec;

                vertexLightColor = ambient + (diffuse + specular);
                    
            }
            """

        fragment_shader = """
            #version 130

            in vec2 outTexCoords;
            in vec2 outTexCoords2;
            in float quadsLimit;
            in vec3 vertexLightColor;

            out vec4 outColor;

            uniform sampler2D samplerTex;
            uniform sampler2D displacement;
            uniform float posIndex;
            uniform float deformationX;
            uniform float deformationY;

            void main()
            {   
                //le aplicamos las coordenadas de textura del primer cuadrado a la textura de ruido
                vec4 colorDisplacement1 = texture(displacement, vec2(outTexCoords.x+deformationX,outTexCoords.y+deformationY));
                //calculamos el promedio de los colores
                float promedioColores1 = (colorDisplacement1.r+colorDisplacement1.g+colorDisplacement1.b+colorDisplacement1.a)/4;
                //ahora usamos este promedio dar el efecto de deformación a la textura que se dibuja
                vec2 displacementCoords1 = vec2(4*(outTexCoords.x+promedioColores1*0.25)/5,outTexCoords.y);
                
                //hacemos lo mismo para el segundo quad
                vec4 colorDisplacement2 = texture(displacement, vec2(outTexCoords2.x+deformationX,outTexCoords2.y+deformationY));
                float promedioColores2 = (colorDisplacement2.r+colorDisplacement2.g+colorDisplacement2.b+colorDisplacement2.a)/4;
                vec2 displacementCoords2 = vec2(4*(outTexCoords2.x+promedioColores2*0.25)/5,outTexCoords2.y);

                if(quadsLimit<posIndex){
                    vec4 color = texture(samplerTex, displacementCoords1);
                    outColor = vec4(vertexLightColor, 1.0) * color;
                }
                else{
                    vec4 color = texture(samplerTex, displacementCoords2);
                    outColor = vec4(vertexLightColor, 1.0) * color;
                }
                
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d coords => 3*4 + 2*4 + 3*4= 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        #Son como las coordenadas de textura, pero en realidad se usan para hacer el paso entre el shader en 2D y en 3D
        Coords2D = glGetAttribLocation(self.shaderProgram, "Coords2D")
        glVertexAttribPointer(Coords2D, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(Coords2D)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)

    def drawCall(self, gpuShape, gpuShape2, mode=GL_TRIANGLES):
        assert isinstance(gpuShape2, TexGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape2.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, gpuShape2.texture2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


#también debemos hacer un shader para el tobogán (hecho de roca)
class toboganShaderProgram():

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec2 fragTexCoords;
            out vec3 vertexLightColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition1;
            uniform vec3 lightPosition2;
            uniform vec3 lightPosition3;
            uniform vec3 lightPosition4;

            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                fragTexCoords = texCoords;

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);

                //Como hay 4 fuentes de luz, y debemos considerarlas todas, usamos una lista para las ultimas 3
                vec3 lights[3] = vec3[](lightPosition2, lightPosition3, lightPosition4);

                //vector donde se suman todas las fuentes de luz
                vec3 total = vec3(0.0f, 0.0f, 0.0f);

                //partimos por la primera luz
                vec3 toLight = lightPosition1 - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.001);
                vec3 diffuse = vec3(0.4, 0.4, 0.4) * vec3(1.0, 1.0, 1.0) * diff;
                    
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = vec3(0.2, 0.2, 0.2) * vec3(1.0, 1.0, 1.0) * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;

                total += (diffuse + specular) / attenuation;

                //luego, iteramos las otras fuentes de luz (usando la lista)
                //Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < 3; i++)
                {
                    vec3 toLight = lights[i] - vertexPos;
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(norm, lightDir), 0.001);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - vertexPos);
                    vec3 reflectDir = reflect(-lightDir, norm);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;

                    //se suma la contribución de la luz i al total
                    total += (diffuse + specular) / attenuation;
                } 
                
                vertexLightColor = ambient + total;
            }
            """

        fragment_shader = """
            #version 130

            in vec3 vertexLightColor;
            in vec2 fragTexCoords;

            out vec4 fragColor;

            uniform sampler2D samplerTex;

            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = vec4(vertexLightColor, 1.0) * textureColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2texCoords + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

#ahora creamos un shader de iluminación local (Gouraud) pero con que reciba varias luces

class MultipleGouraudShaderProgram():

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;
            in vec3 normal;

            out vec4 vertexColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition1;
            uniform vec3 lightPosition2;
            uniform vec3 lightPosition3;
            uniform vec3 lightPosition4;

            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);

                //Como hay 4 fuentes de luz, y debemos considerarlas todas, usamos una lista para las ultimas 3
                vec3 lights[3] = vec3[](lightPosition2, lightPosition3, lightPosition4);

                //vector donde se suman todas las fuentes de luz
                vec3 total = vec3(0.0f, 0.0f, 0.0f);

                //partimos por la primera luz
                vec3 toLight = lightPosition1 - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.001);
                vec3 diffuse = vec3(0.01, 0.01, 0.01) * vec3(0.1, 0.1, 0.2) * diff;
                    
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), 50);
                vec3 specular = vec3(0.2, 0.2, 0.2) * vec3(0.2, 0.2, 0.2) * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;

                total += (diffuse + specular) / attenuation;

                //luego, iteramos las otras fuentes de luz (usando la lista)
                //Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < 3; i++)
                {
                    vec3 toLight = lights[i] - vertexPos;
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(norm, lightDir), 0.001);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - vertexPos);
                    vec3 reflectDir = reflect(-lightDir, norm);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;

                    //se suma la contribución de la luz i al total
                    total += (diffuse + specular) / attenuation;
                }
                
                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * color;
                vertexColor = vec4(result, 1.0);
            }
            """

        fragment_shader = """
            #version 130

            in vec4 vertexColor;
            out vec4 fragColor;

            void main()
            {
                fragColor = vertexColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def textureMIPMAPSetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)
    
    image = Image.open(imgName)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, image.size[0], image.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture