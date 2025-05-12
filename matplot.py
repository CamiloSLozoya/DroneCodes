import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

arduino.inWaiting != 0


def plot():
    ax.clear()
    x= np.random.randint(0,10,10)
    y= np.random.randint(0,10,10)
    ax.plot(x, y)
    canvas.draw()

#Initialize Tkinter
root = tk.Tk()
fig, ax = plt.subplots()



#Tkinter app
frame = tk.Frame(root)
label = tk.Label(text = "Matplotlib")
label.config(font=("Courier", 32))
label.pack()


canvas = FigureCanvasTkAgg(fig, master = frame)
canvas.get_tk_widget().pack()

frame.pack()
tk.Button(frame, text= "Plot graph", command = plot).pack(pady=10)
root.mainloop()