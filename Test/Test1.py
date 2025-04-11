import cv2
import numpy as np
import matplotlib.pyplot as plt
import time 

# Rangos del color a detectar (verde en HSV)
VerdeBajo1 = np.array([36, 50, 70], np.uint8)
VerdeAlto1 = np.array([89, 255, 255], np.uint8) 

#Cargar imagen
img = cv2.imread('Test\imagen.jpg')

#Mostrar imagen
if img is None:
    #Marcar error si no hay imagen
    print("Image not loaded. Check the path!")
    exit()
else:
    #Convertir imagen a escala HSV
    frameHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #Usar mascara para deterctr los pixeles verdes
    maskVerde = cv2.inRange(frameHSV, VerdeBajo1, VerdeAlto1)
    #detectar los contornos
    contornos, _ = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #Separar la imagen en sus componentes RGB
    b, g, r = cv2.split(img.astype("float"))
    #dibujar los contornos
    for i in contornos:
            area = cv2.contourArea(i)
            if area > 2000:
                nuevoContorno = cv2.convexHull(i)
                cv2.drawContours(img, [nuevoContorno], 0, (0, 255, 0), 3)
    #Imprimir imagen con contornos
    cv2.imshow("Contornos de verde", img)

    # -------------------------------
    # Cálculo de índice ExG (similar a NDVI)
    # -------------------------------
    exg = 2 * g - r - b  # Fórmula del ExG
    exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype("uint8") #Normalizar imagen
    exg_mascarado = cv2.bitwise_and(exg_norm, exg_norm, mask=maskVerde) #Eliminar pixeles que no sean verdes
    #Imprimir imagen verde
    cv2.imshow("Imagen ExG normalizada", exg_norm)

    #Calcular porcentaje de verdor
    pixeles_totales = maskVerde.shape[0] * maskVerde.shape[1]
    pixeles_verdes = cv2.countNonZero(maskVerde)
    porcentaje_verde = (pixeles_verdes / pixeles_totales) * 100 #porcentaje de pixeles verdes en la imagen
    porcentaje_verdor = (np.sum(exg_mascarado)/(pixeles_verdes*255))*100 #porcentaje de verdor de los pixeles verdes

    #Imprimir resultado
    print(f"Porcentaje de pixeles verdes: {porcentaje_verde:.2f}%")
    print(f"Porcentaje de verdor: {porcentaje_verdor:.2f}%")

#Espera a que preciones la letra s para cerrar y salir del código
while True:
    if cv2.waitKey(1) & 0xFF == ord("s"):
         break
    
cv2.destroyAllWindows()