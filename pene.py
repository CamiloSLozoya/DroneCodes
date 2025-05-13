import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create main window
root = tk.Tk()
root.geometry("500x400")

# Create a label
label = tk.Label(root, text="Sales Data", font=("Arial", 14), bg="lightblue")
label.pack(pady=10)

# Create a Matplotlib figure for the chart
fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)
ax.plot([1, 2, 3, 4, 5], [10, 20, 15, 25, 30], marker="o", linestyle="-", color="blue")

# Embedding the chart in Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

root.mainloop()