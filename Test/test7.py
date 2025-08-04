import tkinter as tk
from tkinter import *
from tkinter import ttk
import serial
import threading
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw
import random


esp32 = None  # Declarar globalmente antes del try

# ----------- CONFIGURA TU PUERTO SERIAL AQUÍ -------------
SERIAL_PORT = "COM9"
BAUD_RATE = 115200
# ----------------------------------------------------------

try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE)
    esp32.flush()
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
temperatura_historial=[]
# Tkinter root window
root = tk.Tk()
root.title("Flight Monitor")
root.geometry("1100x720")
root.configure(bg="#f6f6f6")

# Fondo semitransparente
bg_image = Image.open(r"C:/Users/camil/Downloads/dronsito.jpg").resize((1100, 720)).convert("RGBA")
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
shadow_card = ImageTk.PhotoImage(Image.open(r"C:/Users/camil/Downloads/shadow_card.jpg"))
tk.Label(root, image=shadow_card, bg="#f6f6f6").place(x=395, y=95)
tk.Label(root, image=shadow_card, bg="#f6f6f6").place(x=395, y=345)

# Imagenes que cambian dependiendo del verdor :D
semilla_feliz = ImageTk.PhotoImage(Image.open(r"C:/Users/camil/Downloads/semilla_feli.jpg").resize((80, 80)).convert("RGBA"))
semilla_tite  = ImageTk.PhotoImage(Image.open(r"C:/Users/camil/Downloads/semilla_tite.jpg").resize((80, 80)).convert("RGBA"))

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
fig1, ax1 = plt.subplots()
ax1.set_ylim(0, 60)
ax1.set_facecolor("#ffffff")
data1 = [temperatura]
line1, = ax1.plot(data1, marker="o", color="#1976d2", label="Temperatura")
ax1.legend()
canvas1 = FigureCanvasTkAgg(fig1, master=root)
canvas1.get_tk_widget().place(x=400, y=100, width=300, height=200)

fig2, ax2 = plt.subplots()
ax2.set_ylim(0, 100)
ax2.set_facecolor("#ffffff")
data2 = [humedad]
line2, = ax2.plot(data2, marker="s", color="#00897b", label="Humedad")
ax2.legend()
canvas2 = FigureCanvasTkAgg(fig2, master=root)
canvas2.get_tk_widget().place(x=400, y=350, width=300, height=200)


#------------------ Verdor o Verde -------------------------------
fig3, ax3 = plt.subplots()
ax3.set_ylim(0, 100)
ax3.set_facecolor("#ffffff")
data3 = [verde]
line3, = ax3.plot(data3, marker="s", color="#008000", label="Verde")
ax3.legend()
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
    alt_label.config(text=f"Altura: {altitud} m")

    #Update latitud, longitud y fertilidad (VERDE//Corrijanme)
    lat_label.config(text=f"Latitud: {latitud}")
    lon_label.config(text=f"Longitud: {longitud}")

    if verde > 50:
        fertilidad_label.config(text=f"Porcentaje de verde: {verde}% // \n DISTRIBUYA SEMILLAS", bg="#059414", fg="#FFFFFF")
    else:
        fertilidad_label.config(text=f"Porcentaje de verde: {verde}% // \n BUSQUE OTRA UBICACION", bg="#90021F", fg="#FFFFFF")

    #Imagen semilla (verdor)
    if verdor == .1:
        semilla_emocion_label.config(image=semilla_feliz)
    else:
        semilla_emocion_label.config(image=semilla_tite)

    #Para las graficas historicas
    data1.pop(0)
    data1.append(temperatura)
    line1.set_ydata(data1)
    ax1.set_xlim(0, len(data1) - 1)
    canvas1.draw()

    data2.pop(0)
    data2.append(humedad)
    line2.set_ydata(data2)
    ax2.set_xlim(0, len(data2) - 1)
    canvas2.draw()

    data3.pop(0)
    data3.append(verde)
    line3.set_ydata(data3)
    ax3.set_xlim(0, len(data3) - 1)
    canvas3.draw()

    root.after(1000, update_data)

def leer_serial():
    global temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor
    if not esp32:
        print("No se puede leer serial: ESP32 no disponible.")
        return

    while True:
        try:
            line = esp32.readline().decode('utf-8').strip()
            print(line)
            if line:
                print("línea leída")
                temperatura, humedad, latitud, longitud, altitud, altLidar, verde, verdor  = [float(x) for x in line.split(";")]
                print(f"Temperatura: {temperatura:.2f} °C")
                print(f"Humedad {humedad:.2f}%")
                print(f"Latitud {latitud:.2f}°")
                print(f"Longitud {longitud:.2f}°")
                print(f"Altitud {altitud:.2f} m")
                print(f"AltLidar {altLidar:.2f} m")
                print(f"Verde {verde:.2f} %")
                print(f"Verdor {verdor:.2f} m")
                root.after(0, update_data)
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