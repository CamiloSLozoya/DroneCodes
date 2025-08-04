import tkinter as tk
from tkinter import *
from tkinter import ttk
import serial
import threading
import matplotlib.pyplot as plt
import time
import csv
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw
import random
import os

esp32 = None  # Declarar globalmente antes del try

# ----------- CONFIGURA TU PUERTO SERIAL AQUÍ -------------
SERIAL_PORT = "COM10"
BAUD_RATE = 115200
# ----------------------------------------------------------

file_name = "historial_datos.csv"

class DatosJetson:
    def _init_(self, temperatura, humedad, fertilidad, altitud, altLidar, latitud, longitud, verde, verdor ):
        self.temperatura = temperatura
        self.humedad = humedad
        self.fertil = fertilidad
        self.altura = altitud
        self.altitudLidar = altLidar
        self.latitud = latitud
        self.longitud = longitud
        self.verde = verde
        self.verdor = verdor

    def guardadoCSV(self):
        escribir_encabezados = not os.path.exists(file_name) or os.path.getsize(file_name) == 0
        f1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            if escribir_encabezados:
                writer.writerow([
                    "Fecha y hora",
                    "Temperatura (°C)",
                    "Humedad (%)",
                    "Fertilidad",
                    "Altura GPS (m)",
                    "Altura Lidar (m)",
                    "Altitud (mm)",
                    "Latitud (°)",
                    "Longitud (°)"
                ])

            writer.writerow([
                f1,
                f"{self.temperatura:.2f}",
                f"{self.humedad:.2f}",
                f"{self.latitud:.6f}",   
                f"{self.longitud:.6f}",  
                f"{self.altura:.2f}", 
                f"{self.altitudLidar:.2f}",   
                f"{self.verde:.6f}",
                f"{self.verdor:.6f}",       
                "Fértil" if self.fertil else "Infértil",
            ])

try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE)
    esp32.flush()
    esp32.reset_input_buffer()   # limpia lo que ha recibido y aún no has leído
    esp32.reset_output_buffer()  # limpia lo que está por enviar escrito pero no transmitido
    print("Se abrió el puerto serie exitosamente")
except serial.SerialException as w:
    print(f"Error abriendo el puerto serial: {w}")

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
fertil = 0.0
temperatura_historial=[]
humedad_historial=[]
verde_historial=[]
verdor_historial = []

# Tkinter root window
root = tk.Tk()
root.title("Flight Monitor")
root.geometry("1100x720")
root.configure(bg="#f6f6f6")

# Fondo semitransparente
bg_image = Image.open(r"C:/Users/bruce/Downloads/FOTITOS/Nueva carpeta/dronsito.jpg").resize((1100, 720)).convert("RGBA")
for y in range(bg_image.height):
    for x in range(bg_image.width):
        r, g, b = bg_image.getpixel((x, y))[:3]
        bg_image.putpixel((x, y), (r, g, b, 120))
bg_tk = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_tk)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.lower()

# Estilos
style = ttk.Style()
style.theme_use("clam")
style.configure("TProgressbar", troughcolor="#e0e0e0", thickness=20)
style.configure("Green.Vertical.TProgressbar", background="#66bb6a")
style.configure("Yellow.Vertical.TProgressbar", background="#fbc02d")
style.configure("Red.Vertical.TProgressbar", background="#e53935")
style.configure("Blue.Vertical.TProgressbar", background="#42a5f5")

# Header y footer
title_canvas = tk.Canvas(root, width=1100, height=50, highlightthickness=0)
title_canvas.place(x=0, y=0)
title_img = Image.new("RGBA", (1100, 50), (0, 0, 0, 204))
title_img_tk = ImageTk.PhotoImage(title_img)
title_canvas.create_image(0, 0, anchor="nw", image=title_img_tk)
title_canvas.create_text(550, 25, text="✈ FLIGHT // MONITOR ✈", fill="white", font=("Segoe UI", 20, "bold"))

footer_canvas = tk.Canvas(root, width=1100, height=50, highlightthickness=0)
footer_canvas.place(x=0, y=670)
footer_img = Image.new("RGBA", (1100, 50), (0, 0, 0, 204))
footer_img_tk = ImageTk.PhotoImage(footer_img)
footer_canvas.create_image(0, 0, anchor="nw", image=footer_img_tk)
footer_canvas.create_text(550, 25, text="© 2025 DroneO2 · v1.0", fill="white", font=("Segoe UI", 12, "italic"))

# Sombra y etiquetas
shadow_card = ImageTk.PhotoImage(Image.open(r"C:/Users/bruce/Downloads/FOTITOS/Nueva carpeta/shadow_card.png"))
tk.Label(root, image=shadow_card, bg="#f6f6f6").place(x=395, y=95)
tk.Label(root, image=shadow_card, bg="#f6f6f6").place(x=395, y=345)

# Imagenes que cambian dependiendo del verdor :D
semilla_feliz = ImageTk.PhotoImage(Image.open(r"C:/Users/bruce/Downloads/FOTITOS/Nueva carpeta/happy_seed.jpg").resize((80, 80)).convert("RGBA"))
semilla_tite  = ImageTk.PhotoImage(Image.open(r"C:/Users/bruce/Downloads/FOTITOS/Nueva carpeta/sad_seed.jpg").resize((80, 80)).convert("RGBA"))

# Aquí se corrige: se separa la creación y el posicionamiento
semilla_emocion_label = tk.Label(root, image=semilla_tite, bg="#f6f6f6")
semilla_emocion_label.place(x=150, y=260)

##############################
lat_label = tk.Label(root, text="Latitud: 0.000000", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#333", bd=1, relief="solid")
lat_label.place(x=50, y=100, width=220)
lon_label = tk.Label(root, text="Longitud: 0.000000", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#333", bd=1, relief="solid")
lon_label.place(x=50, y=140, width=220)

fertilidad_label = tk.Label(root, text="Fertil", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#333", bd=1, relief="solid")
fertilidad_label.place(x=50, y=200, width=300)

#################### Gráficas ###################
fig1, ax_temp= plt.subplots()

ax_temp.set_ylim(0, 60)
ax_temp.set_facecolor("#ffffff")
temperatura_historial = [temperatura]
line_temp, = ax_temp.plot(temperatura_historial, marker="o", color="#1976d2", label="Temperatura")
ax_temp.legend()
canvas1 = FigureCanvasTkAgg(fig1, master=root)
canvas1.get_tk_widget().place(x=400, y=100, width=300, height=200)

fig2, ax_hum= plt.subplots()
ax_hum.set_ylim(0, 100)
ax_hum.set_facecolor("#ffffff")
humedad_historial = [humedad]
line_hum, = ax_hum.plot(humedad_historial, marker="s", color="#00897b", label="Humedad")
ax_hum.legend()
canvas2 = FigureCanvasTkAgg(fig2, master=root)
canvas2.get_tk_widget().place(x=400, y=350, width=300, height=200)


#------------------ Verdor o Verde -------------------------------
fig3, ax_verde = plt.subplots()
ax_verde.set_ylim(0, 100)
ax_verde.set_facecolor("#ffffff")

verde_historial = [verde]
verdor_historial = [verdor]

line_verde, = ax_verde.plot(verde_historial, marker="s", color="#008000", label="Verde")
line_verdor, = ax_verde.plot(verdor_historial, marker="o", color="#012D04", label="Verdor")

ax_verde.legend()

canvas3 = FigureCanvasTkAgg(fig3, master=root)
canvas3.get_tk_widget().place(x=50, y=350, width=300, height=200)

############## Barras ##############

#Barra de Temperatura
temp_label = tk.Label(root, text="Temperatura: 0°C", font=("Segoe UI", 16), bg="#f6f6f6", fg="#444")
temp_label.place(x=770, y=90)
progress_bar = ttk.Progressbar(root, orient="vertical", length=150, mode="determinate", maximum=60)
progress_bar.place(x=830, y=140)

#Barra de altura GPS
alt_label = tk.Label(root, text="Altura: 0 m", font=("Segoe UI", 16), bg="#f6f6f6", fg="#444")
alt_label.place(x=770, y=420)
alt_bar = ttk.Progressbar(root, orient="vertical", length=150, mode="determinate", maximum=40, style="Blue.Vertical.TProgressbar")
alt_bar.place(x=830, y=470)

#Barra de altura LIDAR
altLid_label = tk.Label(root, text="Altura (Lidar): 0 m", font=("Segoe UI", 16), bg="#f6f6f6", fg="#444")
altLid_label.place(x=820, y=300)
altLid_bar = ttk.Progressbar(root, orient="vertical", length=150, mode="determinate", maximum=25, style="Blue.Vertical.TProgressbar")
altLid_bar.place(x=950, y=350)

# Función de actualización
def update_data():
    global temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor

    #Checar si las round arruinan el dato.  POSIBLE FUENTE DE ERROR
    #lat = round(latitud, 6)
    #lon = round(longitud, 6)
    
    #Update de la barra de temperatura
    progress_bar["value"] = temperatura
    temp_label.config(text=f"Temperatura: {temperatura}°C")
    if temperatura < 20:
        progress_bar.configure(style="Green.Vertical.TProgressbar")
    elif temperatura < 35:
        progress_bar.configure(style="Yellow.Vertical.TProgressbar")
    else:
        progress_bar.configure(style="Red.Vertical.TProgressbar")

    #Update de la barra de altura LIDAR
    altLid_bar["value"] = altLidar
    altLid_label.config(text=f"Altura actual LIDAR: {altLidar} m")
    if altLidar < 5:
        altLid_bar.configure(style="Red.Vertical.TProgressbar")
    elif altLidar < 15:
        altLid_bar.configure(style="Yellow.Vertical.TProgressbar")
    else:
        altLid_bar.configure(style="Green.Vertical.TProgressbar")

    #Update de altura por GPS (probs sobre el nivel del mar)
    alt_bar["value"] = altitud
    alt_label.config(text=f"Altura: {(altitud/1000)} m")

    #Update latitud, longitud y fertilidad (VERDE//Corrijanme)
    lat_label.config(text=f"Latitud: {round((latitud/10000000),3)}")
    lon_label.config(text=f"Longitud: {round((longitud/10000000),3)}")

    if fertil:
        fertilidad_label.config(text=f"Porcentaje de verde: {round(verde,2)}% // \n DISTRIBUYA SEMILLAS", bg="#059414", fg="#FFFFFF")
        semilla_emocion_label.config(image=semilla_feliz)
    else:
        fertilidad_label.config(text=f"Porcentaje de verde: {round(verde,2)}% // \n BUSQUE OTRA UBICACION", bg="#90021F", fg="#FFFFFF")
        semilla_emocion_label.config(image=semilla_tite)

    root.after(100, actualizar_grafica)

def actualizar_grafica():
    #Agregar nuevos datos
    temperatura_historial.append(temperatura)
    if len(temperatura_historial) > MAX_PUNTOS:
        temperatura_historial.pop(0)

    #Calcular eje x
    eje_x = list(range(-len(temperatura_historial)+1, 1))

    #Refrescar grafica temp
    line_temp.set_data(eje_x, temperatura_historial)
    ax_temp.relim()
    ax_temp.autoscale_view()
    canvas1.draw()
    
    #Refrescar grafica humedad
    humedad_historial.append(humedad)
    if len(humedad_historial) > MAX_PUNTOS:
        humedad_historial.pop(0)
    line_hum.set_data(eje_x, humedad_historial)
    ax_hum.relim()
    ax_hum.autoscale_view()
    canvas2.draw()

    #Refrescar grafica verde
    verde_historial.append(verde)
    if len(verde_historial) > MAX_PUNTOS:
        verde_historial.pop(0)
    line_verde.set_data(eje_x, verde_historial)
    ax_verde.relim()
    ax_verde.autoscale_view()
    canvas3.draw()

    #Refrescar grafica verdor
    verdor_historial.append(verdor)
    if len(verdor_historial) > MAX_PUNTOS:
        verdor_historial.pop(0)
    line_verdor.set_data(eje_x, verdor_historial)
    ax_verde.relim()
    ax_verde.autoscale_view()
    canvas3.draw()

def leer_serial():
    global temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor, fertil
    if not esp32:
        print("No se puede leer serial: ESP32 no disponible.")
        return

    while True:
        try:
            line = esp32.readline().decode('utf-8').strip()
            print(line)
            if line:
                print("línea leída")
                temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor, fertil  = [float(x) for x in line.split(";")]
                datos = DatosJetson(
                temperatura=temperatura,
                humedad=humedad,
                latitud=latitud/10000000,
                longitud=longitud/10000000,
                altitud=altitud,
                altLidar=altLidar,
                verde = verde,
                verdor = verdor,
                fertilidad=fertil
                )
                print(f"Temperatura: {temperatura:.2f} °C")
                print(f"Humedad {humedad:.2f}%")
                print(f"Latitud {latitud:.2f}°")
                print(f"Longitud {longitud:.2f}°")
                print(f"Altitud {altitud:.2f} m")
                print(f"AltLidar {altLidar:.2f} m")
                print(f"Verde {verde:.2f} %")
                print(f"Verdor {verdor:.2f} %")
                print(f"Fertil {fertil:.2f} ")
                root.after(0, update_data)
                datos.guardadoCSV()
        except Exception as e:
            print(f"Error leyendo del puerto serial: {e}")
        time.sleep(0.1)

# Hilo para lectura serial
serial_thread = threading.Thread(target=leer_serial, daemon=True)
serial_thread.start()

# Iniciar bucle de actualización
#update_data()

# Ejecutar GUI
root.mainloop()