import tkinter as tk
from tkinter import *
from modules.configurator import *

class Pour(ttk.Frame):
    def __init__(self,container,num):
        self.num=num
        self.AvailableInputs=GetAllSyringeInputs()
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()        
        self.Label1=ttk.Label(self.Line1, text="Put")
        self.Label1.pack(side="left")
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
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.Delete)
        self.Delete.pack(side="left")
        self.SyringeLabel=tk.Label(self.Line2,text="---")
        self.SyringeLabel.pack(side="left")
        self.AlertButtonMaxVol=tk.Button(self.Line2,text="Vmax!",state="normal",bg="red",command=self.MaxVolumeAlert)
        self.AlertButtonMinVol=tk.Button(self.Line2,text="Vmin!",state="normal",bg="yellow",command=self.MinVolumeAlert)
        self.AlertButtonWaste=tk.Button(self.Line2,text="W",state="normal",bg="green",command=self.WasteVolumeAlert)

      
    def Delete(self):
        DeletePourObject(self.num)

    def CheckValues(self):
        Input=self.Source.get()
        Output=self.Destination.get()
        Quantity=self.Amount.get()
        Unit=self.Units.get()
        if Input=="" or Output=="" or Quantity=="" or Unit=="":
            self.SyringeLabel.config(text="---")
            self.AlertButtonMinVol.pack_forget()        
            self.AlertButtonMaxVol.pack_forget()
            self.AlertButtonWaste.pack_forget()
            return
        try:
            Quantity=float(Quantity)
        except:
            self.SyringeLabel.config(text="Check quantity error")
            return
        syrnums=WhichSiringeIsConnectedTo(Input)
        AvailableSyringes=[]
        for syringe in syrnums:
            Outputs=GetAllOutputsOfSyringe(int(syringe))
            for connection in Outputs:
             if Output in connection:
                AvailableSyringes.append(syringe)
                break
        if len(AvailableSyringes)==0:
            self.SyringeLabel.config(text="Internal Error Check")
            return
        if Unit=="L": Quantity=Quantity*1000
        elif Unit=="mol" or Unit=="mmol":
            if Unit=="mmol": Quantity=Quantity/1000        
            try:
                M=GetMolarityOfInput(Input)
                if M>0:
                    Quantity=Quantity/M*1000
                else:
                    self.SyringeLabel.config(text="Check error molarity")
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
                    self.SyringeLabel.config(text="check error mass")
                    return
            except:
                return
        Quantity=round(Quantity,2)
        if Quantity<0.1:
            self.AlertButtonMinVol.pack(side="left")
        else:
            self.AlertButtonMinVol.pack_forget()
        if Output=="Air/Waste":
            self.AlertButtonWaste.pack(side="left")
        else:
            self.AlertButtonWaste.pack_forget()    
        self.SyringeLabel.config(text="Syringe "+'or'.join(AvailableSyringes)+" "+str(Quantity)+" mL")
        MaxVol=GetMaxVolumeApparatus(Output)
        if MaxVol>0 and Quantity>MaxVol:
            self.AlertButtonMaxVol.pack(side="left")
        else:
            self.AlertButtonMaxVol.pack_forget()
    
    def MaxVolumeAlert(self):
        messagebox.showerror("ERROR", "Volume exceeds the maximum capacity of reactor")

    def MinVolumeAlert(self):
        messagebox.showerror("Warning", "Volume exceedingly small")    

    def WasteVolumeAlert(self):
        messagebox.showerror("Warning", "Liquid poured into waste exit")
    
    def UnitTypecallback(self,event):
        Unit=self.Units.get()
        if Unit=="ALL":
            MaxVol=GetMaxVolumeApparatus(self.Source.get())
            if MaxVol>0:
                self.Amount.delete(0,tk.END)
                self.Amount.insert(0,str(MaxVol))
                self.Units.set("mL")
            else:
                self.Units.set("")

    def MaxCharsInList(self,list):
     return max([len(list[i]) for i in range(len(list))])
    
    def InputTypecallback(self,event):
        Input=self.Source.get()
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
        self.Units.config(values=PossibleUnits, state="readonly",width=self.MaxCharsInList(PossibleUnits)+2)
        if not self.Units.get() in PossibleUnits:
            self.Units.set("")
        if "Apparatus" in Input:
            self.Label1.config(text="Take")
            self.Label2.config(text="from")
            self.Label3.config(text="to")
        else:
            self.Label1.config(text="Put")        
            self.Label2.config(text="of")
            self.Label3.config(text="in")        
        SyrNums=WhichSiringeIsConnectedTo(Input)
        OutputsList=[]
        for SyringeNum in SyrNums:
            AvailableOutputs=GetAllOutputsOfSyringe(int(SyringeNum))
            for Output in AvailableOutputs:
                if Output not in OutputsList:
                    OutputsList.append(Output)
        PossibleOutputs=[OutputsList[i][0] for i in range(len(OutputsList))]
        PossibleOutputs.sort()
        self.Destination.config(values = PossibleOutputs,state="readonly",width=self.MaxCharsInList(PossibleOutputs))
        if not self.Destination.get() in PossibleOutputs:
            self.Destination.set("")

class Heat(ttk.Frame):
    def __init__(self,container,num):
        self.num=num
        self.AvailableApparatus=GetAllHeatingApparatus()
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Line3=tk.Frame(self)
        self.Line3.pack()        
        self.Label1=ttk.Label(self.Line1, text="Heat")
        self.Label1.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableApparatus, state = 'readonly')
        self.Source.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="at")
        self.Label2.pack(side="left")
        self.Temperature=tk.Entry(self.Line1,state="normal",width=10)
        self.Temperature.pack(side="left")
        self.Label3=ttk.Label(self.Line1, text="°C for")
        self.Label3.pack(side="left")
        self.Time=tk.Entry(self.Line1,state="normal",width=10)
        self.Time.pack(side="left")
        self.Label4=tk.Label(self.Line1,text="min")
        self.Label4.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.Delete)
        self.Delete.pack(side="left")
        self.Wait=tk.Checkbutton(self.Line2,text="wait for cooling")
        self.Wait.select()
        self.Wait.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")
        self.AlertButtonMaxVol=tk.Button(self.Line2,text="Vmax!",state="normal",bg="red",command=self.MaxVolumeAlert)
        self.AlertButtonMinVol=tk.Button(self.Line2,text="Vmin!",state="normal",bg="yellow",command=self.MinVolumeAlert)
        self.AlertButtonWaste=tk.Button(self.Line2,text="W",state="normal",bg="green",command=self.WasteVolumeAlert)

      
    def Delete(self):
        DeleteHeatObject(self.num)

    def CheckValues(self):
        Input=self.Source.get()
        Temperature=self.Temperature.get()
        Time=self.Time.get()
        if Input=="" or Temperature=="":
            self.StatusLabel.config(text="Non valid values")
            return
        if Time=="": Time=0
        try:
            Temperature=float(Temperature)
            Time=float(Time)
            if Time<0: Time/=0
        except:
            self.StatusLabel.config(text="Non valid values")
            return
        else:
            self.StatusLabel.config(text="Valid values")
    
    def MaxVolumeAlert(self):
        messagebox.showerror("ERROR", "Volume exceeds the maximum capacity of reactor")

    def MinVolumeAlert(self):
        messagebox.showerror("Warning", "Volume exceedingly small")    

    def WasteVolumeAlert(self):
        messagebox.showerror("Warning", "Liquid poured into waste exit")
    
    def UnitTypecallback(self,event):
        Unit=self.Units.get()
        if Unit=="ALL":
            MaxVol=GetMaxVolumeApparatus(self.Source.get())
            if MaxVol>0:
                self.Amount.delete(0,tk.END)
                self.Amount.insert(0,str(MaxVol))
                self.Units.set("mL")
            else:
                self.Units.set("")

    def MaxCharsInList(self,list):
     return max([len(list[i]) for i in range(len(list))])
    
    def InputTypecallback(self,event):
        Input=self.Source.get()
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
        self.Units.config(values=PossibleUnits, state="readonly",width=self.MaxCharsInList(PossibleUnits)+2)
        if not self.Units.get() in PossibleUnits:
            self.Units.set("")
        if "Apparatus" in Input:
            self.Label1.config(text="Take")
            self.Label2.config(text="from")
            self.Label3.config(text="to")
        else:
            self.Label1.config(text="Put")        
            self.Label2.config(text="of")
            self.Label3.config(text="in")        
        SyrNums=WhichSiringeIsConnectedTo(Input)
        OutputsList=[]
        for SyringeNum in SyrNums:
            AvailableOutputs=GetAllOutputsOfSyringe(int(SyringeNum))
            for Output in AvailableOutputs:
                if Output not in OutputsList:
                    OutputsList.append(Output)
        PossibleOutputs=[OutputsList[i][0] for i in range(len(OutputsList))]
        PossibleOutputs.sort()
        self.Destination.config(values = PossibleOutputs,state="readonly",width=self.MaxCharsInList(PossibleOutputs))
        if not self.Destination.get() in PossibleOutputs:
            self.Destination.set("")

###################### end of classes ######################
PourArray=[]
HeatArray=[]
WashArray=[]
FunctionArray=[]
CurrentY=2

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

def DeletePourObject(num):
    global PourArray
    print("Deleting Pour n.",num)
    PourArray[num].destroy()
    #PourArray.pop(num)
    return

def DeleteHeatObject(num):
    global HeatArray
    print("Deleting Heat n.",num)
    HeatArray[num].destroy()
    #PourArray.pop(num)
    return



def StartWizard(window):
    
    LoadConnFile('test.conn')

    def CreateNewPour():
        global PourArray,CurrentY
        num=len(PourArray)
        pour=Pour(frame2,num)
        pour.place(x=10,y=CurrentY)
        CurrentY+=50    
        make_draggable(pour)
        PourArray.append(pour)
        
    def CreateNewHeat():
        global HeatArray,CurrentY
        num=len(HeatArray)
        heat=Heat(frame2,num)
        heat.place(x=10,y=CurrentY)
        CurrentY+=50    
        make_draggable(heat)
        HeatArray.append(heat)
        
    def CreateNewWash():
        global WashArray,CurrentY
        num=len(WashArray)
        pour=Pour(frame2,num)#
        pour.place(x=10,y=CurrentY)
        CurrentY+=50    
        make_draggable(pour)
        WashArray.append(pour)

    def CreateNewFunction():
        global FunctionArray,CurrentY
        num=len(FunctionArray)
        pour=Pour(frame2,num)#
        pour.place(x=10,y=CurrentY)
        CurrentY+=50    
        make_draggable(pour)
        FunctionArray.append(pour)


    
    WizardWindow=tk.Toplevel(window)
    WizardWindow.title("CORRO WIZARD")
    WizardWindow.geometry('1000x800+500+150')
    WizardWindow.grab_set()
    frame1 = tk.Frame(WizardWindow)
    frame1.pack(side="top")
    tk.Button(frame1,text="Pour liquid",command=CreateNewPour).pack(side="left")
    tk.Button(frame1,text="Heat reactor",command=CreateNewHeat).pack(side="left")
    tk.Button(frame1,text="Wash reactor",command=CreateNewWash).pack(side="left")
    tk.Button(frame1,text="Device ON/OFF",command=CreateNewFunction).pack(side="left")    
    tk.Button(frame1,text="Titrate",command=CreateNewFunction).pack(side="left")    
    tk.Button(frame1,text="Function",command=CreateNewFunction).pack(side="left")    
    frame2 = tk.Frame(WizardWindow,bg="white",width=1000,height=800)
    frame2.pack()
    
    WizardWindow.mainloop()

##    root = tk.Tk()
##    root.geometry("1000x800")
##    frame1 = tk.Frame(root)
##    frame1.pack(side="top")
##    New1=tk.Button(frame1,text="Pour liquid",command=CreateNewPour)
##    New1.pack(side="left")
##    New2=tk.Button(frame1,text="Heat/activate reactor",command=CreateNewHeat)
##    New2.pack(side="left")
##    New2=tk.Button(frame1,text="Wash reactor",command=CreateNewWash)
##    New2.pack(side="left")
##    frame2 = tk.Frame(root,bg="white",width=1000,height=800)
##    frame2.pack()
##    root.mainloop()


