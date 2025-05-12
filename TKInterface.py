import tkinter as tk

root = tk.Tk()

root.geometry("500x500")
root.title("Flight Monitor")

label = tk.label(root,text="Altura",font=('Comic Sans',18))
label.pack(padx=20,pady=20)

root.mainloop()