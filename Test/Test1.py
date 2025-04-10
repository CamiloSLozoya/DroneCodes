import cv2
import numpy as np
import matplotlib.pyplot as plt
import time 

# Toma de video con cámara
captura = cv2.VideoCapture(0)

# Rangos del color a detectar (verde en HSV)
VerdeBajo1 = np.array([36, 50, 70], np.uint8)
VerdeAlto1 = np.array([89, 255, 255], np.uint8)

# Valores de ExG mínimo y máximo
EXG_MIN = 21  
EXG_MAX = 137   

while True:
    ret, frame = captura.read()
    if ret:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        maskVerde = cv2.inRange(frameHSV, VerdeBajo1, VerdeAlto1)
        maskVerdeRGB=cv2.cvtColor(maskVerde, cv2.COLOR_HSV2BGR)
        contornos, _ = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i in contornos:
            area = cv2.contourArea(i)
            if area > 2000:
                nuevoContorno = cv2.convexHull(i)
                cv2.drawContours(frame, [nuevoContorno], 0, (0, 255, 0), 3)

        # -------------------------------
        # Cálculo de índice ExG (similar a NDVI)
        # -------------------------------
        b, g, r = cv2.split(frame.astype("float"))
        exg = 2 * g - r - b  # Fórmula del ExG

        # Aplicar la máscara para ExG solo en las zonas verdes
        exg_mascarado = cv2.bitwise_and(exg, exg, mask=maskVerdeRGB)
        valores_validos = exg_mascarado[maskVerde > 0]

        if len(valores_validos) > 0:
            promedio_exg = np.mean(valores_validos)
            porcentaje_verdor = (promedio_exg - EXG_MIN) / (EXG_MAX - EXG_MIN) * 100
            print(f"Porcentaje de verdor: {porcentaje_verdor: }%")
        else:
            porcentaje_verdor = 0
            print("No se detectó zona verde")

        cv2.imshow("Suavizado", frame)

        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

captura.release()
cv2.destroyAllWindows()

#meterle for