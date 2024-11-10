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
        Label1.config(text="Take")
        Label2.config(text="from")
        Label3.config(text="to")
    else:
        Label1.config(text="Put")        
        Label2.config(text="of")
        Label3.config(text="in")        
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
        AlertButtonMinVol.pack_forget()        
        AlertButtonMaxVol.pack_forget()
        AlertButtonWaste.pack_forget()
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
    Quantity=round(Quantity,2)
    if Quantity<0.1:
        AlertButtonMinVol.pack(side="left")
    else:
        AlertButtonMinVol.pack_forget()
    if Output=="Air/Waste":
        AlertButtonWaste.pack(side="left")
    else:
        AlertButtonWaste.pack_forget()    
    SyringeLabel.config(text="Syringe "+'or'.join(AvailableSyringes)+" "+str(Quantity)+" mL")
    MaxVol=GetMaxVolumeApparatus(Output)
    if MaxVol>0 and Quantity>MaxVol:
        AlertButtonMaxVol.pack(side="left")
    else:
        AlertButtonMaxVol.pack_forget()
        
def MaxVolumeAlert():
    messagebox.showerror("ERROR", "Volume exceeds the maximum capacity of reactor")

def MinVolumeAlert():
    messagebox.showerror("Warning", "Volume exceedingly small")    

def WasteVolumeAlert():
    messagebox.showerror("Warning", "Liquid poured into waste exit")    

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
Label1=tk.Label(Line1,text="Put")
Label1.pack(side="left")
Amount=tk.Entry(Line1,state="normal",width=10)
Amount.pack(side="left")
Units=ttk.Combobox(Line1, values = ('mL','L'), state = 'readonly',width=3)
Units.bind("<<ComboboxSelected>>", UnitTypecallback)
Units.pack(side="left")
Label2=tk.Label(Line1,text="of")
Label2.pack(side="left")
Source=ttk.Combobox(Line1, values = AvailableInputs, state = 'readonly',width=MaxCharsInList(AvailableInputs))
Source.bind("<<ComboboxSelected>>", InputTypecallback)
Source.pack(side="left")
Label3=tk.Label(Line1,text="in")
Label3.pack(side="left")
Destination=ttk.Combobox(Line1, state = 'disabled')
Destination.pack(side="left")
Check=tk.Button(Line1,text="check",command=CheckValues)
Check.pack(side="left")
SyringeLabel=tk.Label(Line2,text="---")
SyringeLabel.pack(side="left")
AlertButtonMaxVol=tk.Button(Line2,text="Vmax!",state="normal",bg="red",command=MaxVolumeAlert)
AlertButtonMinVol=tk.Button(Line2,text="Vmin!",state="normal",bg="yellow",command=MinVolumeAlert)
AlertButtonWaste=tk.Button(Line2,text="W",state="normal",bg="green",command=WasteVolumeAlert)


