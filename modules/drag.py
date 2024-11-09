import tkinter as tk
from tkinter import ttk
from configurator import *

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

def OutputTypecallback(event):
    #Output=ysunit.get()
    return

def UnitTypecallback(event):
    Unit=unit.get()
    if Unit=="ALL":
        MaxVol=GetMaxVolumeApparatus(sunit.get())
        if MaxVol>0:
            rdame.delete(0,tk.END)
            rdame.insert(0,str(MaxVol))
            unit.set("mL")
        else:
            unit.set("")
    return
       
def InputTypecallback(event):
    global OutputsList
    Input=sunit.get()
    PossibleUnits=["mL","L"]
    if "Reactant" in Input:
        M=GetMolarityOfInput(Input)
        if M>0:
            PossibleUnits.append("mol")
            MM=GetMMOfInput(Input)
            if MM>0:
                PossibleUnits.append("g")
    elif "Apparatus" in Input:
        MaxVol=GetMaxVolumeApparatus(Input)
        if MaxVol>0:
         PossibleUnits.append("ALL")
    unit.config(values=PossibleUnits, state="readonly",width=MaxCharsInList(PossibleUnits)+1)
    if not unit.get() in PossibleUnits:
        unit.set("")
    if "Apparatus" in Input:
        afrdame.config(text="Take")
        frdame.config(text="from")
        yfrdame.config(text="to")
    else:
        afrdame.config(text="Put")        
        frdame.config(text="of")
        yfrdame.config(text="in")        
    SyrNums=WhichSiringeIsConnectedTo(Input)
    OutputsList=[]
    for SyringeNum in SyrNums:
        AvailableOutputs=GetAllOutputsOfSyringe(int(SyringeNum))
        for Output in AvailableOutputs:
            if Output not in OutputsList:
                OutputsList.append(Output)
    PossibleOutputs=[OutputsList[i][0] for i in range(len(OutputsList))]
    PossibleOutputs.sort()
    ysunit.config(values = PossibleOutputs,state="readonly",width=MaxCharsInList(PossibleOutputs))
    if not ysunit.get() in PossibleOutputs:
        ysunit.set("")
        
def MaxCharsInList(list):
    return max([len(list[i]) for i in range(len(list))])

LoadConnFile('../test.conn')
AvailableInputs=GetAllSyringeInputs()
OutputsList=[]


main = tk.Tk()
main.geometry('800x620+500+150')

F=tk.Frame(main, bd=1, bg="grey")
F.place(x=10,y=10)
make_draggable(F)
Line1=tk.Frame(F)
Line1.pack()
Line2=tk.Frame(F)
Line2.pack()
afrdame = tk.Label(Line1,text="Put")
afrdame.pack(side="left")
rdame = tk.Entry(Line1,state="normal",width=10)
rdame.pack(side="left")
unit=ttk.Combobox(Line1, values = ('mL','L'), state = 'readonly',width=3)
unit.bind("<<ComboboxSelected>>", UnitTypecallback)
unit.pack(side="left")
frdame = tk.Label(Line1,text="of")
frdame.pack(side="left")
sunit=ttk.Combobox(Line1, values = AvailableInputs, state = 'readonly',width=MaxCharsInList(AvailableInputs))
sunit.bind("<<ComboboxSelected>>", InputTypecallback)
sunit.pack(side="left")
yfrdame = tk.Label(Line1,text="in")
yfrdame.pack(side="left")
ysunit=ttk.Combobox(Line1, state = 'disabled')
ysunit.bind("<<ComboboxSelected>>", OutputTypecallback)
ysunit.pack(side="left")
SyringeLabel=tk.Label(Line2,text="---")
SyringeLabel.pack()
