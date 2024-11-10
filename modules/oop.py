import tkinter as tk
from tkinter import ttk
from configurator import *

class Pour(ttk.Frame):
    def __init__(self, container):
        self.AvailableInputs=GetAllSyringeInputs()
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()        
        self.label = ttk.Label(self.Line1, text="Put")
        self.label.pack(side="left")
        self.Amount=tk.Entry(self.Line1,state="normal",width=10)
        self.Amount.pack(side="left")
        self.Units=ttk.Combobox(self.Line1, values = ('mL','L'), state = 'readonly',width=3)
        self.Units.bind("<<ComboboxSelected>>", self.UnitTypecallback)
        self.Units.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="of")
        self.Label2.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableInputs, state = 'readonly')
        self.Source.bind("<<ComboboxSelected>>", self.InputTypecallback)
        self.Source.pack(side="left")
        self.Label3=tk.Label(self.Line1,text="in")
        self.Label3.pack(side="left")
        self.Destination=ttk.Combobox(self.Line1, state = 'disabled')
        self.Destination.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.SyringeLabel=tk.Label(self.Line2,text="---")
        self.SyringeLabel.pack(side="left")
        self.AlertButtonMaxVol=tk.Button(self.Line2,text="Vmax!",state="normal",bg="red",command=self.MaxVolumeAlert)
        self.AlertButtonMinVol=tk.Button(self.Line2,text="Vmin!",state="normal",bg="yellow",command=self.MinVolumeAlert)
        self.AlertButtonWaste=tk.Button(self.Line2,text="W",state="normal",bg="green",command=self.WasteVolumeAlert)
        

    def CheckValues(self):
        return
    
    def MaxVolumeAlert():
        return
    
    def MinVolumeAlert():
        return

    def WasteVolumeAlert():
        return
        
    def UnitTypecallback(self,event):
        return
    
    def InputTypecallback(self,event):
        return    

def make_draggable(widget):
    widget.bind("<Button-1>", on_drag_start)
    widget.bind("<B1-Motion>", on_drag_motion)

def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

main = tk.Tk()
main.geometry('800x620+500+150')
LoadConnFile('../test.conn')
frame=Pour(main)
frame.place(x=10,y=10)
make_draggable(frame)

frame2=Pour(main)
frame2.place(x=10,y=10)
make_draggable(frame2)



