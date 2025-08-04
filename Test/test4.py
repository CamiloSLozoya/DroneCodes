from tkinter import *
from tkinter import ttk
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables globales
MAX_PUNTOS=30

temperatura=0.0
humedad = 0.0
latitud = 0.0
longitud = 0.0
altitud = 0.0
altLidar = 0.0
verde = 0.0
verdor = 0.0
temperatura_historial=[]

# ----------- CONFIGURA TU PUERTO SERIAL AQUÍ -------------
SERIAL_PORT = "COM9"      # <- Cambia esto al puerto correcto
BAUD_RATE = 115200
# ----------------------------------------------------------

try: 
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE)  # Ajusta 'COM3' al puerto de tu Arduino
    esp32.flush
    print("Se abrio el puerto serie exitosamente")
except serial.SerialException as w:
        print(f"Error abriendo el puerto serial: {w}")

def actualizar_valores():
    global temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor
    temperatura_label.config(text=f"Temperatura: {temperatura:.2f}°C")
    humedad_label.config(text=f"Humedad: {humedad:.2f}%")
    latitud_label.config(text=f"Latitud: {latitud:.6f}")
    longitud_label.config(text=f"Longitud: {longitud:.6f}")
    altitud_label.config(text=f"Altitud: {altitud:.2f} m")
    altLidar_label.config(text=f"Altitud LIDAR: {altLidar:.2f} m")
    verde_label.config(text=f"Verde: {verde:.2f}")
    verdor_label.config(text=f"Verdor: {verdor:.2f}")
    actualizar_grafica()


def leer_serial():
    global temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor
    while True:
        line = esp32.readline().decode('utf-8').strip()
        if line:
            print("linea leida")
            try:
                temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor  = [float(x) for x in line.split(";")]
                print(f"Temperatura: {temperatura:.2f} °C")
                print(f"Humedad {humedad:.2f}%")
                print(f"Latitud {latitud:.2f}°")
                print(f"Longitud {longitud:.2f}°")
                print(f"Altutud {altitud:.2f} m")
                root.after(0, actualizar_valores)
            except ValueError:
                print(f"No se pudo convertir '{line}' a float.")
        time.sleep(0.1)


def actualizar_grafica():
    #Agregar nuevos datos
    temperatura_historial.append(temperatura)
    if len(temperatura_historial) > MAX_PUNTOS:
        temperatura_historial.pop(0)

    #Calcular eje x
    eje_x = list(range(-len(temperatura_historial)+1, 1))

    #Refrescar grafica en y
    linea_y.set_data(eje_x, temperatura_historial)
    ax_y.relim()
    ax_y.autoscale_view()

    canvas.draw()

# --- GUI principal ---
root = Tk() #Inicializas la librería 
frm = ttk.Frame(root, padding=200) #Creas el frame
frm.grid(row=0, column=0) #creas el grid del frame 

#Creas los lables de las diferentes señales
temperatura_label = ttk.Label(frm, text=f'Temperatura: {temperatura:.2f}°C')
temperatura_label.grid(column=0, row=0)

humedad_label = ttk.Label(frm, text=f'Humedad: {humedad:.2f}%')
humedad_label.grid(column=0, row=1)

latitud_label = ttk.Label(frm, text=f'Latitud: {latitud:.6f}')
latitud_label.grid(column=0, row=2)

longitud_label = ttk.Label(frm, text=f'Longitud: {longitud:.6f}')
longitud_label.grid(column=0, row=3)

altitud_label = ttk.Label(frm, text=f'Altitud: {altitud:.2f} m')
altitud_label.grid(column=0, row=4)

altLidar_label = ttk.Label(frm, text=f'Altitud LIDAR: {altLidar:.2f} m')
altLidar_label.grid(column=0, row=5)

verde_label = ttk.Label(frm, text=f'Verde: {verde:.2f}')
verde_label.grid(column=0, row=6)

verdor_label = ttk.Label(frm, text=f'Verdor: {verdor:.2f}')
verdor_label.grid(column=0, row=7)


ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=3) #Boton quit

# --- Gráfica matplotlib en Tkinter ---
#Grafica de y

fig, (ax_y, ax_u, ax_e)= plt.subplots(3, figsize=(9, 4), sharex=True)
linea_y, = ax_y.plot([], [], label='y (entrada)')
ax_y.set_title("Historial de y")
ax_y.set_ylabel("y")
ax_y.grid(True)
linea_u, = ax_u.plot([], [], label='u (salida)')
ax_u.set_title("Historial de u")
ax_u.set_ylabel("u")
ax_u.grid(True)
linea_e, = ax_e.plot([], [], label='e (error)')
ax_e.set_title("Historial de e")
ax_e.set_xlabel("Tiempo")
ax_e.set_ylabel("e")
ax_e.grid(True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

# Hilo para lectura serial
serial_thread = threading.Thread(target=leer_serial, daemon=True)
serial_thread.start()

root.mainloop()