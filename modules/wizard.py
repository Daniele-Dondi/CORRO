import tkinter as tk
from tkinter import *
from modules.configurator import *

class Pour(ttk.Frame):
    def __init__(self,container):
        self.Action=""
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
        
    def CheckValues(self):
        Input=self.Source.get()
        Output=self.Destination.get()
        Quantity=self.Amount.get()
        Unit=self.Units.get()
        self.Action=""
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
        self.Action='Syr'.join(AvailableSyringes)+","+Input+","+Output+","+str(Quantity)
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
    def __init__(self,container):
        self.Action=""
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
            if self.Checked.get()==0:
                self.HighTempAlertButton.pack(side="left")
            else:
                self.HighTempAlertButton.pack_forget()            
    
    def HighTempAlert(self):
        messagebox.showerror("Warning", "The reactor will be hot after this step")
    
    def MaxCharsInList(self,list):
     return max([len(list[i]) for i in range(len(list))])


class Wash(ttk.Frame):
    def __init__(self,container):
        self.AvailableApparatus=GetAllVesselApparatus()
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
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly')
        self.Source.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="with")
        self.Label2.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly') #
        self.Source.pack(side="left")
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
            if self.Checked.get()==0:
                self.HighTempAlertButton.pack(side="left")
            else:
                self.HighTempAlertButton.pack_forget()            
    
    def HighTempAlert(self):
        messagebox.showerror("Warning", "The reactor will be hot after this step")
    
    def MaxCharsInList(self,list):
     return max([len(list[i]) for i in range(len(list))])

    

    

###################### end of classes ######################
ActionsArray=[]    
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

def DeleteObjByIdentifier(ObjIdentifier):
    global ActionsArray
    num=ActionsArray.index(ObjIdentifier)
    ActionsArray.pop(num)
    ObjIdentifier.destroy()

def StartWizard(window):
    
    LoadConnFile('test.conn')

    def CreateNewObject(ObjType):
        global ActionsArray,CurrentY
        if ObjType=="Pour":
            Obj=Pour(frame2)
            YSize=50
        elif ObjType=="Heat":
            Obj=Heat(frame2)
            YSize=70
        elif ObjType=="Wash":
            Obj=Wash(frame2)
            YSize=50
        else:
            messagebox.showerror("ERROR", "Object "+ObjType+" Unknown")
            return
        Obj.place(x=10,y=CurrentY)
        CurrentY+=YSize
        make_draggable(Obj)
        ActionsArray.append(Obj)

    def GetYStack(array):
        Result=[]
        for item in array:
            if not item=="":
                #ObjName=str(item.__class__.__name__)                
                Result.append([item.winfo_y(),item])
        return Result

    def CheckProcedure():
        global PourArray,HeatArray,WashArray
        ToBeChecked=[PourArray,HeatArray,WashArray]
        Sorted=[]
        for ObjArray in ToBeChecked:
         Result=GetYStack(ObjArray)
         Sorted=[*Sorted,*Result]
        Sorted.sort()
        print(Sorted) #now we have the array of objects ordered w. respect to Y pos

    
    WizardWindow=tk.Toplevel(window)
    WizardWindow.title("CORRO WIZARD")
    WizardWindow.geometry('1000x600+500+10')
    WizardWindow.grab_set()
    frame1 = tk.Frame(WizardWindow)
    frame1.pack(side="top")
    frame2 = tk.Frame(WizardWindow,bg="white",width=1000,height=400)
    frame2.pack()
    frame3 = tk.Frame(WizardWindow,bg="cyan",width=1000,height=30)
    frame3.pack(side="bottom")    
    tk.Button(frame1,text="Pour liquid",command=lambda: CreateNewObject("Pour")).pack(side="left")
    tk.Button(frame1,text="Heat reactor",command=lambda: CreateNewObject("Heat")).pack(side="left")
    tk.Button(frame1,text="Wash reactor",command=lambda: CreateNewObject("Wash")).pack(side="left")
    tk.Button(frame1,text="Evaporate solvent",command=lambda: CreateNewObject("Evap")).pack(side="left")
    tk.Button(frame1,text="Chromatography",command=lambda: CreateNewObject("Chrom")).pack(side="left")    
    tk.Button(frame1,text="Device ON/OFF",command=lambda: CreateNewObject("Switch")).pack(side="left")    
    tk.Button(frame1,text="Titrate",command=lambda: CreateNewObject("Titr")).pack(side="left")    
    tk.Button(frame1,text="Function",command=lambda: CreateNewObject("Func")).pack(side="left")    

    tk.Button(frame3,text="Process Check",command=CheckProcedure).pack(side="left")        
    WizardWindow.mainloop()




##        global PourArray
##        PourArray[0].CheckValues()
##        print(PourArray[0].StatusLabel.cget("text"))
