import tkinter as tk
from tkinter import *
from tkinter.tix import *
from modules.configurator import *

class Pour(ttk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.AvailableInputs=GetAllSyringeInputs()
        self.Height=50
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
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableInputs, width=self.MaxCharsInList(self.AvailableInputs), state = 'readonly')
        self.Source.bind("<<ComboboxSelected>>", self.InputTypecallback)
        self.Source.pack(side="left")
        self.Label3=tk.Label(self.Line1,text="in")
        self.Label3.pack(side="left")
        self.Destination=ttk.Combobox(self.Line1, state = 'disabled')
        self.Destination.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")
        self.AlertButtonMaxVol=tk.Button(self.Line2,text="Vmax!",state="normal",bg="red",command=self.MaxVolumeAlert)
        self.AlertButtonMinVol=tk.Button(self.Line2,text="Vmin!",state="normal",bg="yellow",command=self.MinVolumeAlert)
        self.AlertButtonWaste=tk.Button(self.Line2,text="W",state="normal",bg="green",command=self.WasteVolumeAlert)
      
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action
        
    def CheckValues(self):
        Input=self.Source.get()
        Output=self.Destination.get()
        Quantity=self.Amount.get()
        Amount=Quantity #we keep amount with the current units, Quantity will be transformed in mL
        Unit=self.Units.get()
        self.Action=[]
        if Input=="" or Output=="" or Quantity=="" or Unit=="":
            self.StatusLabel.config(text="---")
            self.AlertButtonMinVol.pack_forget()        
            self.AlertButtonMaxVol.pack_forget()
            self.AlertButtonWaste.pack_forget()
            return
        try:
            Quantity=float(Quantity)
        except:
            self.StatusLabel.config(text="Check quantity error")
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
            self.StatusLabel.config(text="Internal Error Check")
            return
        if Unit=="L": Quantity=Quantity*1000
        elif Unit=="mol" or Unit=="mmol":
            if Unit=="mmol": Quantity=Quantity/1000        
            try:
                M=GetMolarityOfInput(Input)
                if M>0:
                    Quantity=Quantity/M*1000
                else:
                    self.StatusLabel.config(text="Check error molarity")
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
                    self.StatusLabel.config(text="check error mass")
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
        self.StatusLabel.config(text="Syringe "+'or'.join(AvailableSyringes)+" "+str(Quantity)+" mL")
        self.Action=[AvailableSyringes,Quantity,Amount,Unit,Input,Output] #Quantity=mL, Amount measured in Unit
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

    def MaxCharsInList(self,List):
     return max([len(List[i]) for i in range(len(List))])
    
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
    def __init__(self,container):
        self.Action=[]
        self.AvailableApparatus=GetAllHeatingApparatus()
        self.Height=75
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
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly')
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
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.Checked=tk.IntVar()
        self.Wait=tk.Checkbutton(self.Line2,text="wait for cooling",variable=self.Checked)
        self.Wait.select()
        self.Wait.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")
        self.HighTempAlertButton=tk.Button(self.Line2,text="Hot!",state="normal",bg="red",command=self.HighTempAlert)
      
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def CheckValues(self):
        Apparatus=self.Source.get()
        Temperature=self.Temperature.get()
        Time=self.Time.get()
        Wait4Cooling=self.Checked.get()
        self.Action=[]        
        if Apparatus=="" or Temperature=="":
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
            self.Action=[Apparatus,Temperature,Time,Wait4Cooling]
            if Wait4Cooling==0:
                self.HighTempAlertButton.pack(side="left")
            else:
                self.HighTempAlertButton.pack_forget()            
    
    def HighTempAlert(self):
        messagebox.showerror("Warning", "The reactor will be hot after this step")
    
    def MaxCharsInList(self,List):
     return max([len(List[i]) for i in range(len(List))])


class Wash(ttk.Frame):
    def __init__(self,container):
        #self.AvailableApparatus=GetAllVesselApparatus()
        self.AvailableApparatus=GetAllSyringeOutputs()
        self.AvailableInputs=GetAllSyringeInputs()
        self.Action=[]
        self.Height=70
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Line3=tk.Frame(self)
        self.Line3.pack()        
        self.Label1=ttk.Label(self.Line1, text="Wash")
        self.Label1.pack(side="left")
        self.Destination=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly')
        self.Destination.bind("<<ComboboxSelected>>", self.InputTypecallback)
        self.Destination.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="with")
        self.Label2.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = [], state = 'disabled') 
        self.Source.pack(side="left")
        self.Label3=ttk.Label(self.Line2, text="Number of cycles:")
        self.Label3.pack(side="left")
        self.Cycles=tk.Spinbox(self.Line2, from_=1, to=10, repeatdelay=500, repeatinterval=200);
        self.Cycles.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")

    def InputTypecallback(self,event):
        Vessel=self.Destination.get()
        SyrNums=WhichSiringeIsConnectedTo(Vessel)
        InputsList=[]
        for SyringeNum in SyrNums:
            AvailableInputs=GetAllInputsOfSyringe(int(SyringeNum))
            for Input in AvailableInputs:
                if Input not in InputsList:
                    InputsList.append(Input)
        PossibleInputs=[InputsList[i][0] for i in range(len(InputsList))]
        PossibleInputs.sort()
        self.Source.config(values = PossibleInputs,state="readonly",width=self.MaxCharsInList(PossibleInputs))
        if not self.Source.get() in PossibleInputs:
            self.Source.set("")    
    
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action        

    def CheckValues(self):
        Destination=self.Destination.get()
        Source=self.Source.get()
        Cycles=self.Cycles.get()
        self.Action=[]
        self.StatusLabel.config(text="---")
        if not Destination=="" and not Source=="":
         self.Action=[Destination,Source,Cycles]
         self.StatusLabel.config(text="Ok")
    
    def HighTempAlert(self):
        messagebox.showerror("Warning", "The reactor will be hot after this step")
    
    def MaxCharsInList(self,List):
     return max([len(List[i]) for i in range(len(List))])

    

###################### end of classes ######################
ActionsArray=[]    
CurrentY=2

def ReorderObjects():
    global CurrentY
    CurrentY=2
    Sorted=GetYStack()
    for element in Sorted:
        Item=element[1]
        Item.place(x=10, y=CurrentY)
        CurrentY+=int(Item.Height)
            
def GetYStack():
    global ActionsArray
    Result=[]
    for item in ActionsArray:
        Result.append([item.winfo_y(),item])
    Result.sort() #now we have the array of objects ordered w. respect to Y pos            
    return Result

def DeleteObjByIdentifier(ObjIdentifier):
    global ActionsArray
    num=ActionsArray.index(ObjIdentifier)
    ActionsArray.pop(num)
    ObjIdentifier.destroy()
    ReorderObjects()

def StartWizard(window):
    
    LoadConnFile('test.conn')

    def make_draggable(widget):
        widget.bind("<Button-1>", on_drag_start)
        widget.bind("<B1-Motion>", on_drag_motion)
        widget.bind("<ButtonRelease-1>", on_mouse_up)

    def on_drag_start(event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
        widget.lift()

    def on_drag_motion(event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)

    def on_mouse_up(event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        ReorderObjects()


    def CreateNewObject(ObjType):
        global ActionsArray,CurrentY
        if ObjType=="Pour":
            Obj=Pour(frame2)
        elif ObjType=="Heat":
            Obj=Heat(frame2)
        elif ObjType=="Wash":
            Obj=Wash(frame2)
        else:
            messagebox.showerror("ERROR", "Object "+ObjType+" Unknown")
            return
        YSize=Obj.Height
        Obj.place(x=10,y=CurrentY)
        CurrentY+=YSize
        make_draggable(Obj)
        ActionsArray.append(Obj)

    def CheckProcedure():
        Sorted=GetYStack()
        print(len(Sorted)," Actions")
        for Action in Sorted:
            Object=Action[1]
            print(str(Object.__class__.__name__))
            Object.CheckValues()
            print(Object.GetAction())

    
    WizardWindow=tk.Toplevel(window)
    WizardWindow.title("CORRO WIZARD")
    WizardWindow.geometry('1000x600+200+10')
    WizardWindow.grab_set()
    frame1 = tk.Frame(WizardWindow)
    frame1.pack(side="top")
    frame2 = tk.Frame(WizardWindow,bg="white",width=1000,height=500)
    frame2.pack()
##    swin = ScrolledWindow(frame2, width=1000, height=400)
##    swin.pack()
##    win = swin.window
    frame3 = tk.Frame(WizardWindow,bg="gray",width=1000,height=30)
    frame3.pack(side="bottom")    
    tk.Button(frame1,text="Pour liquid",command=lambda: CreateNewObject("Pour")).pack(side="left")
    tk.Button(frame1,text="Heat reactor",command=lambda: CreateNewObject("Heat")).pack(side="left")
    tk.Button(frame1,text="Wash reactor",command=lambda: CreateNewObject("Wash")).pack(side="left")
    tk.Button(frame1,text="L/L separation",command=lambda: CreateNewObject("Liq")).pack(side="left")
    tk.Button(frame1,text="Evaporate solvent",command=lambda: CreateNewObject("Evap")).pack(side="left")
    tk.Button(frame1,text="Chromatography",command=lambda: CreateNewObject("Chrom")).pack(side="left")    
    tk.Button(frame1,text="Device ON/OFF",command=lambda: CreateNewObject("Switch")).pack(side="left")    
    tk.Button(frame1,text="Titrate",command=lambda: CreateNewObject("Titr")).pack(side="left")    
    tk.Button(frame1,text="Function",command=lambda: CreateNewObject("Func")).pack(side="left")    

    tk.Button(frame3,text="Process Check",command=CheckProcedure).pack(side="left")        
    WizardWindow.mainloop()

