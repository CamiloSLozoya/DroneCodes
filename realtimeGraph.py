import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class RealTimeChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Chart with Tkinter")
        self.root.geometry("800x500")

        # Create figure and axis for the chart
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(0, 100)  # Set y-axis limits
        self.data = [random.randint(0, 100) for _ in range(10)]
        self.line, = self.ax.plot(self.data, marker="o")

        # Embed the matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().place(x=10, y=100, width=300, height=200)

        # Start updating the chart
        self.update_chart()
        

    def update_chart(self):
        # Shift data and append a new random value
        self.data.pop(0)
        self.data.append(random.randint(0, 100))

        # Update plot data
        self.line.set_ydata(self.data)
        self.ax.set_xlim(0, len(self.data)-1)
        self.canvas.draw()

        # Schedule next update
        self.root.after(500, self.update_chart)  # Updates every 500ms

# Create the application window and start the main loop
root = tk.Tk()
app = RealTimeChartApp(root)
root.mainloop()