import minimalmodbus
import serial

# Configuración del sensor
instrument = minimalmodbus.Instrument('COM14', 1)
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.05
instrument.mode = minimalmodbus.MODE_RTU

def leer_distancia():
    try:
        distancia = instrument.read_register(24, 3, 4, False)
        return distancia
    except Exception as e:
        print(f"⚠  Error al leer distancia: {e}")
        return None
