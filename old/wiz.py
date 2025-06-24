import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import dialog
from tkinter import ttk
from modules.wizard import *

base = Tk()
base.geometry('50x50+1500+100')
StartWizard(base)
base.mainloop()
