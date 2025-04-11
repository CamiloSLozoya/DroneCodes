import cv2
import numpy as np
import matplotlib.pyplot as plt
import time 

#--------------------------------------------------------------------------------------------------------------
#Este es el setup, aqui se definen las variables y constantes utilizandas
#--------------------------------------------------------------------------------------------------------------

#Toma de video con camara
captura=cv2.VideoCapture(1)

# Rangos del color a detectar (verde en HSV)
VerdeBajo1 = np.array([36, 50, 70], np.uint8)
VerdeAlto1 = np.array([89, 255, 255], np.uint8) 

#Toma de desición de cuando activar servo
Verde_min=35 #porcentaje
Verdor_min=50 #porcentaje

#Variables de tiempo
measureTime=2 #Cantidad de segundos que espera para realizar la acción
t_start=time.gmtime()
t_next=t_start.tm_sec+measureTime

#--------------------------------------------------------------------------------------------------------------
#Loop
#--------------------------------------------------------------------------------------------------------------
while True:
    if captura.isOpened():
        t=time.gmtime() #obtener tiempo actual
        if (t.tm_sec==(t_next)):
            #print(t.tm_sec) #Esto es opcional
            ret,img= captura.read()
            if ret == True:
                #Preparar imagen
                frameHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #Convertir imagen a escala HSV
                maskVerde = cv2.inRange(frameHSV, VerdeBajo1, VerdeAlto1)#Usar mascara para deterctr los pixeles verdes
                contornos, _ = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #detectar los contornos 
                b, g, r = cv2.split(img.astype("float")) #Separar la imagen en sus componentes RGB

                #dibujar los contornos
                for i in contornos:
                        area = cv2.contourArea(i)
                        if area > 2000:
                            nuevoContorno = cv2.convexHull(i)
                            cv2.drawContours(img, [nuevoContorno], 0, (0, 255, 0), 3)
                cv2.imshow("Contornos de verde", img) #Imprimir imagen con contornos

                # -------------------------------
                # Cálculo de índice ExG (similar a NDVI)
                # -------------------------------
                exg = 2 * g - r - b  # Fórmula del ExG
                exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype("uint8") #Normalizar imagen
                exg_mascarado = cv2.bitwise_and(exg_norm, exg_norm, mask=maskVerde) #Eliminar pixeles que no sean verdes
                cv2.imshow("Imagen ExG normalizada", exg_norm) #Imprimir imagen de escala de verdes

                #Calcular porcentaje de verdor
                pixeles_totales = maskVerde.shape[0] * maskVerde.shape[1]
                pixeles_verdes = cv2.countNonZero(maskVerde)
                porcentaje_verde = (pixeles_verdes / pixeles_totales) * 100 #porcentaje de pixeles verdes en la imagen
                porcentaje_verdor = (np.sum(exg_mascarado)/(pixeles_verdes*255))*100 #porcentaje de verdor de los pixeles verdes

                #Imprimir resultado
                print(f"Porcentaje de pixeles verdes: {porcentaje_verde:.2f}%")
                print(f"Porcentaje de verdor: {porcentaje_verdor:.2f}%")

                #Actuar con el servomotor
                if (porcentaje_verde>=Verde_min) & (porcentaje_verdor>=Verdor_min):
                    print("Activar Servo")
                    # -------------------------------
                    # Aqui va el codigo para activar el servo
                    # -------------------------------

                t_next=t.tm_sec+measureTime
                if (t_next>=60):
                    t_next=t_next%60

        #Salida al presionar s
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

    else: 
        print("Error: no se pudo abrir la camara.")
        exit()


    
