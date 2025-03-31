import serial
import keyboard
import time

arduino = serial.Serial('COM4', 115200) 

def tecla_presionada(tecla):
    print(f"Presionaste: {tecla.name}")
keyboard.on_press()  # Detecta cualquier tecla presionada

keyboard.wait()  # Mantiene el programa corriendo

    
