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
    #Output=Destination.get()
    return

def UnitTypecallback(event):
    Unit=Units.get()
    if Unit=="ALL":
        MaxVol=GetMaxVolumeApparatus(Source.get())
        if MaxVol>0:
            Amount.delete(0,tk.END)
            Amount.insert(0,str(MaxVol))
            Units.set("mL")
        else:
            Units.set("")
    return
       
def InputTypecallback(event):
    global OutputsList
    Input=Source.get()
    PossibleUnits=["mL","L"]
    if "Reactant" in Input:
        M=GetMolarityOfInput(Input)
        if M>0:
            PossibleUnits.append("mmol")            
            PossibleUnits.append("mol")
            MM=GetMMOfInput(Input)
            if MM>0:
                PossibleUnits.append("mg")                
                PossibleUnits.append("g")
    elif "Apparatus" in Input:
        MaxVol=GetMaxVolumeApparatus(Input)
        if MaxVol>0:
         PossibleUnits.append("ALL")
    Units.config(values=PossibleUnits, state="readonly",width=MaxCharsInList(PossibleUnits)+2)
    if not Units.get() in PossibleUnits:
        Units.set("")
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
    Destination.config(values = PossibleOutputs,state="readonly",width=MaxCharsInList(PossibleOutputs))
    if not Destination.get() in PossibleOutputs:
        Destination.set("")
        
def MaxCharsInList(list):
    return max([len(list[i]) for i in range(len(list))])

def CheckValues():
    Input=Source.get()
    Output=Destination.get()
    Quantity=Amount.get()
    Unit=Units.get()
    if Input=="" or Output=="" or Quantity=="" or Unit=="":
        SyringeLabel.config(text="---")
        AlertButton.pack_forget()
        return
    try:
        Quantity=float(Quantity)
    except:
        print("Check quantity error")
        return
    syrnums=WhichSiringeIsConnectedTo(Input)
    #print(Input,Output,syrnums)
    AvailableSyringes=[]
    for syringe in syrnums:
        Outputs=GetAllOutputsOfSyringe(int(syringe))
        for connection in Outputs:
         if Output in connection:
            AvailableSyringes.append(syringe)
            break
    #print(AvailableSyringes)
    if len(AvailableSyringes)==0:
        print("Internal Error CHECK")
        return
    if Unit=="L": Quantity=Quantity*1000
    elif Unit=="mol" or Unit=="mmol":
        if Unit=="mmol": Quantity=Quantity/1000        
        try:
            M=GetMolarityOfInput(Input)
            if M>0:
                Quantity=Quantity/M*1000
            else:
                print("check error molarity")
                return
        except:
            return
    elif Unit=="g" or Unit=="mg":
        if Unit=="mg": Quantity=Quantity/1000
        try:
            M=GetMolarityOfInput(Input)
            MM=GetMMOfInput(Input)
            if M>0 and MM>0:
                Quantity=Quantity/MM/M*1000
            else:
                print("check error mass")
                return
        except:
            return
    SyringeLabel.config(text="Syringe "+'or'.join(AvailableSyringes)+" "+str(Quantity)+" mL")
    MaxVol=GetMaxVolumeApparatus(Output)
    if MaxVol>0 and Quantity>MaxVol:
        AlertButton.pack()
    else:
        AlertButton.pack_forget()
        

def VolumeAlert():
    messagebox.showerror("ERROR", "Inserted volume exceeds the maximum capacity of reactor")

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
Amount = tk.Entry(Line1,state="normal",width=10)
Amount.pack(side="left")
Units=ttk.Combobox(Line1, values = ('mL','L'), state = 'readonly',width=3)
Units.bind("<<ComboboxSelected>>", UnitTypecallback)
Units.pack(side="left")
frdame = tk.Label(Line1,text="of")
frdame.pack(side="left")
Source=ttk.Combobox(Line1, values = AvailableInputs, state = 'readonly',width=MaxCharsInList(AvailableInputs))
Source.bind("<<ComboboxSelected>>", InputTypecallback)
Source.pack(side="left")
yfrdame = tk.Label(Line1,text="in")
yfrdame.pack(side="left")
Destination=ttk.Combobox(Line1, state = 'disabled')
Destination.bind("<<ComboboxSelected>>", OutputTypecallback)
Destination.pack(side="left")
Check=tk.Button(Line1,text="check",command=CheckValues)
Check.pack(side="left")
SyringeLabel=tk.Label(Line2,text="---")
SyringeLabel.pack(side="left")
AlertButton=tk.Button(Line2,text="!",state="normal",bg="red",command=VolumeAlert)
#AlertButton.pack(side="left")

