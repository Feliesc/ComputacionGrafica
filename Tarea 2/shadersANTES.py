from OpenGL.GL import *
import OpenGL.GL.shaders
from grafica.gpu_shape import GPUShape
from PIL import Image
import numpy as np

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
            uniform float dx;
            uniform float dyIndex;

            void main()
            {   
                vec4 color1a = texture(samplerTex, outTexCoords2);
                vec4 color2a = texture(displacement, vec2(0.5*outTexCoords2.x+dx,dyIndex+outTexCoords2.y));

                vec4 color1b = texture(samplerTex, outTexCoords);
                vec4 color2b = texture(displacement, vec2(0.5*outTexCoords.x+dx,dyIndex+outTexCoords.y));
                if(fragPosition.y>posIndex){
                    outColor = mix(color1a, color2a, 0.1);
                }
                else{
                    outColor = mix(color1b, color2b, 0.1);
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


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)



def textureSetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = Image.open(imgName)
    img_data = np.array(list(image.getdata()), np.uint8)

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

    return texture1

def displacementSetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = Image.open(imgName)
    img_data = np.array(list(image.getdata()), np.uint8)

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

    return texture1