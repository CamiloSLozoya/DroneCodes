import cv2
import numpy as np

#Toma de video con camara
captura=cv2.VideoCapture(0)

#Rangos del color a detectar
VerdeBajo1=np.array([36,50,70],np.uint8)
VerdeAlto1=np.array([89,255,255],np.uint8)

while True:
    ret,frame= captura.read()
    if ret == True:
        frameHSV=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) #Transformación de RGB a HSV
        maskVerde=cv2.inRange(frameHSV,VerdeBajo1,VerdeAlto1) #Encuentra rangos indicados en la imagen, guarda en máscara
        _,contornos,_=cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i in contornos:
            area=cv2.contourArea(i)
            if area > 2000:
                nuevoContorno=cv2.convexHull(i)
                cv2.drawContours(frame, [nuevoContorno], 0, (0,255,0),3 )
        
        cv2.imshow("Suavizado", frame)
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

captura.realease()
cv2.destroyAllWindows()

