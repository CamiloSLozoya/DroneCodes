import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import serial
import minimalmodbus
import tensorflow as tf

#--------------------------------------------------------------------------------------------------------------
#Este es el setup, aqui se definen las variables y constantes utilizandas
#--------------------------------------------------------------------------------------------------------------

#Toma de fotos con camara
captura=cv2.VideoCapture(0) #Cambiar en jetson a 0
d=0

# Carga del modelo CNN
model = tf.keras.models.load_model('modeloajetson.h5')
down_size = (280, 280)  # Tamaño de entrada para el modelo

#Dimensiones de la imagen
captura.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
captura.set(cv2.CAP_PROP_FRAME_HEIGHT,1440)
# Rangos del color a detectar (verde en HSV)
VerdeBajo1 = np.array([36, 50, 70], np.uint8)
VerdeAlto1 = np.array([89, 255, 255], np.uint8) 

#Conectar el serial con el ESP32
ESP32 = serial.Serial('/dev/ttyUSB1', 115200)  # Ajusta el puerto al de la jetson
ESP32.reset_input_buffer()   # limpia lo que ha recibido y aún no has leído
ESP32.reset_output_buffer()  # limpia lo que está por enviar (escrito pero no transmitido)
ESP32.flush

#Toma de desición de cuando activar servo
Verde_min=35 #porcentaje
Verdor_min=50 #porcentaje

# Configuración del sensor
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.05
instrument.mode = minimalmodbus.MODE_RTU

#Variables de tiempo
measureTime=2500 #Cantidad de milisegundos que espera para realizar la acción
t_start=time.perf_counter()

#--------------------------------------------------------------------------------------------------------------
#Ajuste Gamma
#--------------------------------------------------------------------------------------------------------------
def adjust_gamma(image, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

#--------------------------------------------------------------------------------------------------------------
#Filtro de imagen para CNN
#--------------------------------------------------------------------------------------------------------------
def preparaciónImagen():
     ret, frame = captura.read()
     # 1. Ajuste de brillo/saturación
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     h, s, v = cv2.split(hsv)
     v = np.clip(v * 0.6, 0, 255).astype(np.uint8)  # reducir brillo
     s = np.clip(s * 1.7, 0, 255).astype(np.uint8)  # aumentar saturación
     hsv_adjusted = cv2.merge((h, s, v))
     frame = cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

     # 2. Ajuste dinámico de gamma según el brillo
     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
     mean_brightness = np.mean(gray)
     gamma = 1.5 if mean_brightness < 80 else 0.8
     frame_adjusted = adjust_gamma(frame, gamma=gamma)
     return frame_adjusted

#--------------------------------------------------------------------------------------------------------------
#CNN
#--------------------------------------------------------------------------------------------------------------
def isFertilCNN(frame_adjusted):
    # Preparar imagen para el modelo (redimensionar)
    resized = cv2.resize(frame_adjusted, down_size, interpolation=cv2.INTER_LINEAR)
    # Realizar predicción
    prediction = model.predict(np.array([resized]))[0]
    
    if  (prediction[0]>=0.7):
          print ("Suelo fertil")
          return 1
    else: 
          print ("Suelo infertil")
          return 0 

#--------------------------------------------------------------------------------------------------------------
#Tomar foto obtener verde y verdor
#--------------------------------------------------------------------------------------------------------------
def obtenerVerde ():
        ret,img= captura.read()
        if ret == True:
                #Preparar imagen
                frameHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #Convertir imagen a escala HSV
                maskVerde = cv2.inRange(frameHSV, VerdeBajo1, VerdeAlto1)#Usar mascara para deterctr los pixeles verdes
                ,contornos, = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #detectar los contornos 
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
    mensaje="R"+str(altura)+";"+str(porcentaje_verde)+";"+str(porcentaje_verdor)+";"+str(fertil)+"\n"
    ESP32.write(mensaje.encode())  # Envía la tecla por Serial
    print("Enviado: ", mensaje)
    flag=1
    t_start=time.perf_counter()
    while (ESP32.in_waiting==0) and (flag):
        t_next=time.perf_counter()
        if ((t_next-t_start)*1000<1000):
            linea=0
        else: 
             print("Fallo la comunicacion con el ESP32")
             flag=0
    if flag:
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
            return [0.0, 0.0, 0.0, 0.0, 0.0]
    else:
         return [0.0, 0.0, 0.0, 0.0, 0.0]
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
        return 0.0
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
    servo_control=int(altura*10+10) #Hay que cambiar esto
    if fertil:
        mensaje= "S"+ str(servo_control)+"\n"
        ESP32.write(mensaje.encode())  # Envía la tecla por Serial
        print(f"Servo activado con {servo_control} ciclos")
    else:
         print("Servo no activado")
         #._annotations_

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
            img=preparaciónImagen()
            fertil=isFertilCNN(img)
            #fertil=isFertil (porcentaje_verde, porcentaje_verdor)
            [temperatura, humedad, latitud, longitud, altitud] = ObtenerDatosESP(altura,porcentaje_verde, porcentaje_verdor, fertil)
            time.sleep(1)
            print(f"Temperatura: {temperatura:.2f} °C")
            print(f"Humedad {humedad:.2f}%")
            print(f"Latitud {latitud:.2f}°")
            print(f"Longitud {longitud:.2f}°")
            print(f"Altutud {altitud:.2f} m")
            #SaveImage(fertil,latitud, longitud, altitud)
            ActivarServo(fertil,altura)
            #--------------------------------------------------------------------------------------------------
    #Salida al presionar s
        if cv2.waitKey(1) & 0xFF == ord("s"):
            break
    else: 
        print("Error: no se pudo abrir la camara.")
        exit()