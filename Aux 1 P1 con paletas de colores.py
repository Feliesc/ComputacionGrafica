import numpy as np
import sira

def draw_rectangle(matrix, x, y, width, height, index):
    matrix[x:x + width, y:y + height] = index

if __name__ == "__main__":
    
    S = 14
    W = 60
    H = 40
    windowSize = (W*S, H*S)

    # Se crea la matriz (esta vez no tiene la componente del rgb)
    imgData = np.zeros((W, H), dtype=np.uint8)

    # Se pinta la matriz completa con el color del fondo
    imgData[:, :] = 0

    #Al pintar las cosas, en vez de darle un color rgb, se les asigna un indice
    # Se pinta el suelo
    draw_rectangle(imgData, x=0, y=28, width=60, height=12, index=1)
    # Se pinta la primera parte de la carroceria
    draw_rectangle(imgData, x=12, y=25, width=37, height=8, index=2)
    # Se pinta la segunda parte de la carroceria
    draw_rectangle(imgData, x=20, y=17, width=21, height=8, index=2)
    # Se pinta la primera rueda
    draw_rectangle(imgData, x=18, y=30, width=7, height=7, index=3)
    # Se pinta la segunda rueda
    draw_rectangle(imgData, x=36, y=30, width=7, height=7, index=3)
    # Se pinta la primera ventana
    draw_rectangle(imgData, x=32, y=19, width=9, height=6, index=4)

    #se crean las paletas de colores
    colorPalette = np.ndarray((5,3), dtype=np.uint8)
    colorPalette[0] = np.array([0,255,255], dtype=np.uint8)
    colorPalette[1] = np.array([120,120,120], dtype=np.uint8)
    colorPalette[2] = np.array([255,0,0], dtype=np.uint8)
    colorPalette[3] = np.array([50,50,50], dtype=np.uint8)
    colorPalette[4] = np.array([0,150,255], dtype=np.uint8)

    colorPalette1 = np.ndarray((5,3), dtype=np.uint8)
    colorPalette1[0] = np.array([0,0,125], dtype=np.uint8)
    colorPalette1[1] = np.array([40,40,40], dtype=np.uint8)
    colorPalette1[2] = np.array([130,0,50], dtype=np.uint8)
    colorPalette1[3] = np.array([0,0,0], dtype=np.uint8)
    colorPalette1[4] = np.array([0,50,255], dtype=np.uint8)

    colorPalette2 = np.ndarray((5,3), dtype=np.uint8)
    colorPalette2[0] = np.array([255,145,50], dtype=np.uint8)
    colorPalette2[1] = np.array([200,170,140], dtype=np.uint8)
    colorPalette2[2] = np.array([225,80,50], dtype=np.uint8)
    colorPalette2[3] = np.array([50,70,50], dtype=np.uint8)
    colorPalette2[4] = np.array([0,150,255], dtype=np.uint8)
    
    #se genera el display usando la funcion para coloreado indirecto
    display = sira.IndirectRGBRasterDisplay(windowSize, imgData.shape, "Indirect RGB Raster Display")

    display.setColorPalette(colorPalette1)#se selecciona una paleta
    display.setMatrix(imgData)
    display.draw()
