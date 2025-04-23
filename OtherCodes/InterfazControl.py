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
y_historial = []

MAX_PUNTOS = 50  # Número de puntos a mostrar en la gráfica

def actualizar_valores():
    global r, y
    try:
        r = float(entrada_var.get())

        e = r - y
        if (e<0.0):
            u = 1.0
        else:
            u = 0.0

        referencia_label.config(text=f"Referencia (r): {r:.2f}")
        salida_label.config(text=f"Salida (u): {u:.2f}")
        error_label.config(text=f"Error (e): {e:.2f}")
    except ValueError:
        referencia_label.config(text="Referencia (r): Valor inválido")
        salida_label.config(text="Salida (u): ---")
        error_label.config(text="Error (e): ---")

def leer_serial():
    global y
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    try:
                        y = float(line)
                        root.after(0, actualizar_y_en_gui)
                    except ValueError:
                        print(f"No se pudo convertir '{line}' a float.")
                time.sleep(0.1)
    except serial.SerialException as e:
        print(f"Error abriendo el puerto serial: {e}")

def actualizar_grafica():
    y_historial.append(y)
    if len(y_historial) > MAX_PUNTOS:
        y_historial.pop(0)

    eje_x = list(range(-len(y_historial)+1, 1))
    linea.set_data(eje_x, y_historial)
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

def actualizar_y_en_gui():
    entrada_label.config(text=f"Entrada (y): {y:.2f}")
    actualizar_valores()
    actualizar_grafica()



# --- GUI principal ---
root = Tk()
frm = ttk.Frame(root, padding=20)
frm.grid(row=0, column=0)

entrada_var = StringVar()

entrada_entry = ttk.Entry(frm, textvariable=entrada_var)
entrada_entry.grid(column=1, row=0)

ttk.Button(frm, text="Actualizar", command=actualizar_valores).grid(column=2, row=0)

referencia_label = ttk.Label(frm, text=f'Referencia (r): {r:.2f}')
referencia_label.grid(column=0, row=0)

entrada_label = ttk.Label(frm, text=f'Entrada (y): {y:.2f}')
entrada_label.grid(column=0, row=1)

salida_label = ttk.Label(frm, text=f'Salida (u): {r - y:.2f}')
salida_label.grid(column=0, row=2)

error_label = ttk.Label(frm, text=f'Error (e): {r - y:.2f}')
error_label.grid(column=0, row=3)

ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=3)

# --- Gráfica matplotlib en Tkinter ---
fig, ax = plt.subplots(figsize=(5, 3))
linea, = ax.plot([], [], label='y (entrada)')
ax.set_title("Historial de y")
ax.set_xlabel("Tiempo")
ax.set_ylabel("y")
ax.grid(True)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

# Hilo para lectura serial
serial_thread = threading.Thread(target=leer_serial, daemon=True)
serial_thread.start()

root.mainloop()
