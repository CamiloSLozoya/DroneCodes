import serial
import keyboard  # Necesitas instalarlo con: pip install keyboard
import time
arduino = serial.Serial('COM4', 115200)  # Ajusta 'COM3' al puerto de tu Arduino
arduino.flush

while True:
    tecla=keyboard.read_key()
    arduino.write(tecla.encode())  # Envía la tecla por Serial
    print("enviado", tecla)
    tecla=0
    while arduino.in_waiting==0:
        linea=0
    while arduino.in_waiting!=0:
        linea=arduino.read()
        print("Recibido:", linea.decode('utf-8')) 
    linea=0
    
