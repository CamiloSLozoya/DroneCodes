import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class RealTimeChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiple Real-Time Charts")

        # Create first chart directly in the main window
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_ylim(0, 100)
        self.data1 = [random.randint(0, 100) for _ in range(10)]
        self.line1, = self.ax1.plot(self.data1, marker="o", label="Chart 1")
        self.ax1.legend()
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.root)
        self.canvas1.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10)

        # Create second chart directly in the main window
        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_ylim(0, 100)
        self.data2 = [random.randint(0, 100) for _ in range(10)]
        self.line2, = self.ax2.plot(self.data2, marker="s", color="red", label="Chart 2")
        self.ax2.legend()
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.root)
        self.canvas2.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)

        # Start updating both charts
        self.update_chart1()
        self.update_chart2()

    def update_chart1(self):
        self.data1.pop(0)
        self.data1.append(random.randint(0, 100))
        self.line1.set_ydata(self.data1)
        self.ax1.set_xlim(0, len(self.data1) - 1)
        self.canvas1.draw()
        self.root.after(500, self.update_chart1)

    def update_chart2(self):
        self.data2.pop(0)
        self.data2.append(random.randint(0, 100))
        self.line2.set_ydata(self.data2)
        self.ax2.set_xlim(0, len(self.data2) - 1)
        self.canvas2.draw()
        self.root.after(500, self.update_chart2)

# Run the application
root = tk.Tk()
app = RealTimeChartApp(root)
root.mainloop()