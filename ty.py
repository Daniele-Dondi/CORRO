import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import dialog
from tkinter import ttk
from modules.configurator import *

base = Tk()
Button(base, text="OK",command=lambda: StartConfigurator(base)).pack()
base.mainloop()
