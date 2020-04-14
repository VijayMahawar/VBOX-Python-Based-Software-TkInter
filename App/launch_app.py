import tkinter as tk
from vbox_app_scripts.app import vbox_procesing
from tkinter import messagebox


root = tk.Tk()
b = vbox_procesing(root)
def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()
        root.destroy()
root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
root.mainloop()