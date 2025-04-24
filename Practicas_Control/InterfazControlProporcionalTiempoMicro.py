from tkinter import *
from tkinter import ttk
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------- CONFIGURA TU PUERTO SERIAL AQUÍ -------------
SERIAL_PORT = "COM4"      # <- Cambia esto al puerto correcto
BAUD_RATE = 115200
# ----------------------------------------------------------

# Variables globales
r = 0.0
y = 0.0
e = 0.0
u = 0.0
y_historial = []
e_historial = []
u_historial = []
start_loop = False
kp=1
u_min=0
u_max=1023

MAX_PUNTOS = 50  # Número de puntos a mostrar en la gráfica
try: 
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)  # Ajusta 'COM3' al puerto de tu Arduino
    arduino.flush
except serial.SerialException as w:
        print(f"Error abriendo el puerto serial: {w}")

def actualizar_valores():
    global r, y, e, u
    try:
        r = float(entrada_var.get())
        e = ((r - y)/r)*100

        #-----------------------Control-----------------------------
        u=kp*(r - y)
        if (u>u_max):
            u=u_max
        if (u<u_min):
            u=u_min
        #------------------------------------------------------------

        salida_label.config(text=f"Salida (u): {u:.2f}")
        error_label.config(text=f"Error (e): {e:.2f}")
        entrada_label.config(text=f"Entrada (y): {y:.2f}")
        actualizar_grafica()
        enviar_serial()

    except ValueError:
        salida_label.config(text="Salida (u): ---")
        error_label.config(text="Error (e): ---")

def enviar_serial():
    global u
    if arduino and arduino.is_open:
        mensaje = f"{u:.2f}\n"  # Formato a 2 decimales y salto de línea
        arduino.write(mensaje.encode('utf-8'))

def leer_serial():
    global y, start_loop
    while True:
        while start_loop:
            line = arduino.readline().decode('utf-8').strip()
            if line:
                try:
                    y = float(line)
                    root.after(0, actualizar_valores)
                except ValueError:
                    print(f"No se pudo convertir '{line}' a float.")
            time.sleep(0.1)


def actualizar_grafica():
    #Agregar nuevos datos
    y_historial.append(y)
    if len(y_historial) > MAX_PUNTOS:
        y_historial.pop(0)

    #Calcular eje x
    eje_x = list(range(-len(y_historial)+1, 1))

    #Refrescar grafica en y
    linea_y.set_data(eje_x, y_historial)
    ax_y.relim()
    ax_y.autoscale_view()
    
    #Refrescar grafica en u
    u_historial.append(u)
    if len(u_historial) > MAX_PUNTOS:
        u_historial.pop(0)
    linea_u.set_data(eje_x, u_historial)
    ax_u.relim()
    ax_u.autoscale_view()

    #Refrescar grafica en e
    e_historial.append(e)
    if len(e_historial) > MAX_PUNTOS:
        e_historial.pop(0)
    linea_e.set_data(eje_x, e_historial)
    ax_e.relim()
    ax_e.autoscale_view()

    canvas.draw()

def actualizar_referencia():
    global start_loop
    start_loop=True
    try:
        r = float(entrada_var.get())
        referencia_label.config(text=f"Referencia (r): {r:.2f}")
    except ValueError:
        referencia_label.config(text="Referencia (r): Valor inválido")


# --- GUI principal ---
root = Tk() #Inicializas la librería 
frm = ttk.Frame(root, padding=200) #Creas el frame
frm.grid(row=0, column=0) #creas el grid del frame 

entrada_var = StringVar() #Creas la variable "entrada_var" en formato string

entrada_entry = ttk.Entry(frm, textvariable=entrada_var) #Creas la entrada llamada "entrada_entry" en forma de entrada
entrada_entry.grid(column=1, row=0) #defines la posición en el grid

ttk.Button(frm, text="Actualizar", command=actualizar_referencia).grid(column=2, row=0) #Creas el boton de actualizar

#Creas los lables de las diferentes señales
referencia_label = ttk.Label(frm, text=f'Referencia (r): {r:.2f}')
referencia_label.grid(column=0, row=0)

entrada_label = ttk.Label(frm, text=f'Entrada (y): {y:.2f}')
entrada_label.grid(column=0, row=1)

salida_label = ttk.Label(frm, text=f'Salida (u): {u:.2f}')
salida_label.grid(column=0, row=2)

error_label = ttk.Label(frm, text=f'Error (e): {e:.2f}')
error_label.grid(column=0, row=3)

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