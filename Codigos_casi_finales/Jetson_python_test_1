import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import serial
import minimalmodbus

#--------------------------------------------------------------------------------------------------------------
#Este es el setup, aqui se definen las variables y constantes utilizandas
#--------------------------------------------------------------------------------------------------------------

#Toma de fotos con camara
captura=cv2.VideoCapture(1) #Cambiar en jetson a 0
d=0
#Dimensiones de la imagen
captura.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
captura.set(cv2.CAP_PROP_FRAME_HEIGHT,1440)
# Rangos del color a detectar (verde en HSV)
VerdeBajo1 = np.array([36, 50, 70], np.uint8)
VerdeAlto1 = np.array([89, 255, 255], np.uint8) 

#Conectar el serial con el ESP32
ESP32 = serial.Serial('COM5', 115200)  # Ajusta el puerto al de la jetson
ESP32.flush

#Toma de desición de cuando activar servo
Verde_min=35 #porcentaje
Verdor_min=50 #porcentaje

# Configuración del sensor
instrument = minimalmodbus.Instrument('COM6', 1)
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.05
instrument.mode = minimalmodbus.MODE_RTU

#Variables de tiempo
measureTime=2000 #Cantidad de milisegundos que espera para realizar la acción
t_start=time.perf_counter()

#--------------------------------------------------------------------------------------------------------------
#Tomar foto obtener verde y verdor
#--------------------------------------------------------------------------------------------------------------
def obtenerVerde ():
        ret,img= captura.read()
        if ret == True:
                #Preparar imagen
                frameHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #Convertir imagen a escala HSV
                maskVerde = cv2.inRange(frameHSV, VerdeBajo1, VerdeAlto1)#Usar mascara para deterctr los pixeles verdes
                contornos,_ = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #detectar los contornos 
                b, g, r = cv2.split(img.astype("float")) #Separar la imagen en sus componentes RGB
                #dibujar los contornos
                for i in contornos:
                        area = cv2.contourArea(i)
                        if area > 2000:
                            nuevoContorno = cv2.convexHull(i)
                            cv2.drawContours(img, [nuevoContorno], 0, (0, 255, 0), 3)
                cv2.imshow("Contornos de verde", img) #Imprimir imagen con contornos
                # Cálculo de índice ExG (similar a NDVI)
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
                return [porcentaje_verde, porcentaje_verdor]
        
#--------------------------------------------------------------------------------------------------------------
#Obtener temperatura, humedad y GPS del ESP32
#--------------------------------------------------------------------------------------------------------------
def ObtenerDatosESP (altura,porcentaje_verde, porcentaje_verdor,fertil):
    mensaje="R"+str(altura)+";"+str(porcentaje_verde)+";"+str(porcentaje_verdor)+";"+str(fertil)
    ESP32.write(mensaje.encode())  # Envía la tecla por Serial
    print("Enviado: ", mensaje)
    while ESP32.in_waiting==0:
        linea=0
    try: 
        linea=ESP32.readline().decode('utf-8').strip()
        print(linea)
        if (linea):
            temperatura, humedad, latitud, longitud, altitud = [float(x) for x in linea.split(";")]
            print(f"Temperatura: {temperatura:.2f} °C")
            print(f"Humedad {humedad:.2f}%")
            print(f"Latitud {latitud:.2f}°")
            print(f"Longitud {longitud:.2f}°")
            print(f"Altutud {altitud:.2f} m")
            return [temperatura, humedad, latitud, longitud, altitud]
    except Exception as e:
        print(f"Error leyendo del puerto serial: {e}")
    time.sleep(0.1)

#--------------------------------------------------------------------------------------------------------------
#Tomar altura con el sensor LIDAR
#--------------------------------------------------------------------------------------------------------------
def leer_distancia():
    try:
        distancia = instrument.read_register(24, 3, 4, False)
        return distancia
    except Exception as e:
        print(f"Error al leer distancia: {e}")
        return None
#--------------------------------------------------------------------------------------------------------------
#Algoritmo para la toma de desiciones
#--------------------------------------------------------------------------------------------------------------
def isFertil (porcentaje_verde, porcentaje_verdor):
     if  (porcentaje_verde>=Verde_min) & (porcentaje_verdor>=Verdor_min):
          print ("Suelo fertil")
          return 1
     else: 
          print ("Suelo infertil")
          return 0 
     
#--------------------------------------------------------------------------------------------------------------
#Guardar imagen en la carpeta correcta
#--------------------------------------------------------------------------------------------------------------
def SaveImage(fertil,metadata): 
    global d
    ret, img =captura.read()
    filename = "file_"+str(d)+str(metadata)+".jpg"
    if fertil: 
        cv2.imwrite('Dron_Project_Code/fotosFertil' + filename,img)
    else: 
        cv2.imwrite('Dron_Project_Code/fotosFertil' + filename,img)
    d+=1

#--------------------------------------------------------------------------------------------------------------
#Activar Servomotor
#--------------------------------------------------------------------------------------------------------------
def ActivarServo(fertil, altura):
    #ecuación para control servo
    servo_control=int(altura*3+1) #Hay que cambiar esto
    if fertil:
        mensaje= "S"+ str(servo_control)
        ESP32.write(mensaje.encode())  # Envía la tecla por Serial
        print("Enviado control servo")
    else:
         print("No enviado")

#--------------------------------------------------------------------------------------------------------------
#Main Loop
#--------------------------------------------------------------------------------------------------------------
while True: 
    if captura.isOpened():
        t_next=time.perf_counter()
        if ((t_next-t_start)*1000>=measureTime):
            t_start=time.perf_counter()

            #--------------------------------------------------------------------------------------------------
            #Programa principal
            [porcentaje_verde, porcentaje_verdor]=obtenerVerde()
            altura=leer_distancia()
            print(f"El dron esta a {altura:.2f} m")
            fertil=isFertil (porcentaje_verde, porcentaje_verdor)
            [temperatura, humedad, latitud, longitud, altitud] = ObtenerDatosESP(altura,porcentaje_verde, porcentaje_verdor, fertil)
            
            print(f"Temperatura: {temperatura:.2f} °C")
            print(f"Humedad {humedad:.2f}%")
            print(f"Latitud {latitud:.2f}°")
            print(f"Longitud {longitud:.2f}°")
            print(f"Altutud {altitud:.2f} m")

            
            #SaveImage(fertil,latitud, longitud, altitud)

            ActivarServo(0,altura)
            #--------------------------------------------------------------------------------------------------

    #Salida al presionar s
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break
    else: 
        print("Error: no se pudo abrir la camara.")
        exit()