# Copyright (C) 2025 Daniele Dondi
#
# This work is licensed under a Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
#
# You are free to:
# - Share: copy and redistribute the material in any medium or format
# - Adapt: remix, transform, and build upon the material for any purpose, even commercially
#
# Under the following terms:
# - Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
#   You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
# - No additional restrictions: You may not apply legal terms or technological measures that legally restrict
#   others from doing anything the license permits.
#
# Author: Daniele Dondi
# Date: 2025

import tkinter as tk
from tkinter import *
from tkinter import ttk
from modules.configurator import *

class Pour(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.AvailableInputs=GetAllSyringeInputs()
        self.Height=50
        self.MacroName="Pour" #bind to macro name in macros folder
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()        
        self.Label1=tk.Label(self.Line1, text="Put")
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

    def GetValues(self):
        return [self.Label1.cget("text"), self.Label2.cget("text"), self.Label3.cget("text"),  self.Amount.get(), self.Units.get(), self.Source.get(), self.Destination.get(), self.StatusLabel.cget("text")]

    def RetrieveConnections(self):
        return [self.Source.get(), self.Destination.get()]

    def SetValues(self,parms):
        self.Label1.config(text=parms[0])
        self.Label2.config(text=parms[1])
        self.Label3.config(text=parms[2])
        self.Amount.delete(0,tk.END)
        self.Amount.insert(0,str(parms[3]))
        self.Units.set(parms[4])
        self.Source.set(parms[5])
        self.Destination.set(parms[6])
        self.StatusLabel.config(text=parms[7])
    
    def CheckValues(self):
        self.CheckInput()
        self.CheckUnit()
        Input=self.Source.get()
        Output=self.Destination.get()
        Quantity=self.Amount.get()
        Amount=Quantity #we keep Amount with the current units, Quantity will be transformed in mL
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
        syrnums=WhichSyringeIsConnectedTo(Input)
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
        self.StatusLabel.config(text="Syringe "+' or '.join(AvailableSyringes)+" "+str(Quantity)+" mL")
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

    def CheckUnit(self):
        Unit=self.Units.get()
        if Unit=="ALL":
            MaxVol=GetMaxVolumeApparatus(self.Source.get())
            if MaxVol>0:
                self.Amount.delete(0,tk.END)
                self.Amount.insert(0,str(MaxVol))
                self.Units.set("mL")
            else:
                self.Units.set("")

    
    def UnitTypecallback(self,event):
        self.CheckUnit()

    def MaxCharsInList(self,List):
        maxlength=8
        try:
            maxlength=max([len(List[i]) for i in range(len(List))])
        except:
            pass
        return maxlength

    def CheckInput(self):
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
        SyrNums=WhichSyringeIsConnectedTo(Input)
        OutputsList=[]
        if len(SyrNums)==0: #database has changed meanwhile
            self.Source.set("")
            self.Destination.set("")
            return
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
    
    def InputTypecallback(self,event):
        self.CheckInput()


class Heat(tk.Frame):
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
        self.Label1=tk.Label(self.Line1, text="Heat")
        self.Label1.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly')
        self.Source.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="at")
        self.Label2.pack(side="left")
        self.Temperature=tk.Entry(self.Line1,state="normal",width=10)
        self.Temperature.pack(side="left")
        self.Label3=tk.Label(self.Line1, text="°C for")
        self.Label3.pack(side="left")
        self.Time=tk.Entry(self.Line1,state="normal",width=10)
        self.Time.insert(0,"0")
        self.Time.pack(side="left")
        self.Label4=tk.Label(self.Line1,text="min")
        self.Label4.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.Checked=tk.IntVar()
        self.Wait4Cooling=tk.Checkbutton(self.Line2,text="wait for cooling at ",variable=self.Checked,command=self.SetEndTemp)
        self.Wait4Cooling.select()
        self.Wait4Cooling.pack(side="left")
        self.EndTemperature=tk.Entry(self.Line2,state="normal",width=10)
        self.EndTemperature.insert(0,"25")
        self.EndTemperature.pack(side="left")
        self.Label4=tk.Label(self.Line2, text="°C")
        self.Label4.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")
        self.HighTempAlertButton=tk.Button(self.Line2,text="Hot!",state="normal",bg="red",command=self.HighTempAlert)
        
    def SetEndTemp(self):
        if self.Checked.get()==0:
            self.EndTemperature.config(state="disabled")
        else:
            self.EndTemperature.config(state="normal")
      
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.Source.get(), self.Temperature.get(), self.Time.get(), self.Checked.get(), self.EndTemperature.get()]

    def RetrieveConnections(self):
        return [self.Source.get()]

    def SetValues(self,parms):
        self.Source.set(parms[0])
        self.Temperature.delete(0,tk.END)
        self.Temperature.insert(0,str(parms[1]))
        self.Time.delete(0,tk.END)
        self.Time.insert(0,str(parms[2]))
        self.Checked.set(parms[3])
        self.EndTemperature.delete(0,tk.END)
        self.EndTemperature.insert(0,str(parms[4]))

    def CheckValues(self):
        Apparatus=self.Source.get()
        Temperature=self.Temperature.get()
        Time=self.Time.get()
        Wait4Cooling=self.Checked.get()
        self.Action=[]        
        if Apparatus=="" or Temperature=="":
            self.StatusLabel.config(text="Invalid values")
            return
        if Time=="": Time=0
        try:
            Temperature=float(Temperature)
            Time=float(Time)
            if Time<0: Time/=0
        except:
            self.StatusLabel.config(text="Invalid values")
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
        maxlength=8
        try:
            maxlength=max([len(List[i]) for i in range(len(List))])
        except:
            pass
        return maxlength        


class Wash(tk.Frame):
    def __init__(self,container):
        AvailableOutputs=GetAllSyringeOutputs()
        AvailableOutputs=[AvailableOutputs[i][:-3] for i in range(len(AvailableOutputs))] #remove IN
        AvailableInputs=GetAllSyringeInputs()
        AvailableInputs=[AvailableInputs[i][:-4] for i in range(len(AvailableInputs))]    #remove OUT
        self.AvailableApparatus=[]
        for Apparatus in AvailableOutputs:
            if Apparatus in AvailableInputs:
                if Apparatus not in self.AvailableApparatus:
                    self.AvailableApparatus.append(Apparatus)  #we need an Apparatus having IN and OUT
        self.SyrOutputs=""
        self.Action=[]
        self.Height=75
        self.MaxVol=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Line3=tk.Frame(self)
        self.Line3.pack()        
        self.Label1=tk.Label(self.Line1, text="Wash")
        self.Label1.pack(side="left")
        self.Destination=ttk.Combobox(self.Line1, values = self.AvailableApparatus, width=self.MaxCharsInList(self.AvailableApparatus),state = 'readonly')
        self.Destination.bind("<<ComboboxSelected>>", self.InputTypecallback)
        self.Destination.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="with")
        self.Label2.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = [], state = 'disabled') 
        self.Source.pack(side="left")
        self.Label3=tk.Label(self.Line2, text="Washing volume:")
        self.Label3.pack(side="left")
        self.Volume=tk.Entry(self.Line2,width=7)
        self.Volume.pack(side="left")
        self.Label4=tk.Label(self.Line2, text="mL")
        self.Label4.pack(side="left")
        self.AllButton=tk.Button(self.Line2,text="ALL",state="disabled",command=self.AllVolume)
        self.AllButton.pack(side="left")
        self.Label5=tk.Label(self.Line2, text="  Number of cycles:")
        self.Label5.pack(side="left")
        self.Cycles=tk.Spinbox(self.Line2, from_=1, to=10, repeatdelay=500, repeatinterval=200);
        self.Cycles.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")

    def AllVolume(self):
        self.Volume.delete(0,tk.END)
        self.Volume.insert(0,str(self.MaxVol))

    def CheckInput(self):
        Vessel=self.Destination.get()
        SyrInputs=WhichSyringeIsConnectedTo(Vessel+" IN")
        self.SyrOutputs=WhichSyringeIsConnectedTo(Vessel+" OUT")
        InputsList=[]
        for SyringeNum in SyrInputs:
            AvailableInputs=GetAllInputsOfSyringe(int(SyringeNum))
            for Input in AvailableInputs:
                if Input not in InputsList:
                    InputsList.append(Input)
        self.MaxVol=GetMaxVolumeApparatus(Vessel+" IN")
        self.AllButton.config(state="normal")
        try:
          vol=float(self.Volume.get())  
          if self.MaxVol>0 and vol>self.MaxVol:
            self.AllVolume()
        except:
          pass
        PossibleInputs=[InputsList[i][0] for i in range(len(InputsList))]
        PossibleInputs.sort()
        self.Source.config(values = PossibleInputs,state="readonly",width=self.MaxCharsInList(PossibleInputs))
        if not self.Source.get() in PossibleInputs:
            self.Source.set("")    

    def InputTypecallback(self,event):
        self.CheckInput()

    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.Source.get(), self.Destination.get(), self.Cycles.get(), self.Volume.get()]

    def RetrieveConnections(self):
        return [self.Source.get(), self.Destination.get()]

    def SetValues(self,parms):
        self.Source.set(parms[0])
        self.Destination.set(parms[1])
        self.Cycles.delete(0,tk.END)
        self.Cycles.insert(0,str(parms[2]))
        self.Volume.delete(0,tk.END)
        self.Volume.insert(0,str(parms[3]))

    def CheckValues(self):
        self.CheckInput()
        Destination=self.Destination.get()
        Source=self.Source.get()
        Cycles=self.Cycles.get()
        Volume=self.Volume.get()
        SyrInputs=WhichSyringeIsConnectedTo(Source)
        try:
            Volume=float(Volume)
        except:
            Volume=0.0
        self.Action=[]
        self.StatusLabel.config(text="---")
        if not Destination=="" and not Source=="" and Volume>0.0:
         self.Action=[Destination,Source,Cycles,Volume,SyrInputs,self.SyrOutputs]
         self.StatusLabel.config(text="Input syringe "+' or '.join(SyrInputs)+", Output syringe "+' or '.join(self.SyrOutputs))         
        else:
         self.Action=[]
         self.StatusLabel.config(text="---")   
    
    def MaxCharsInList(self,List):
        maxlength=8
        try:
            maxlength=max([len(List[i]) for i in range(len(List))])
        except:
            pass
        return maxlength        

class Wait(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=50
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="Wait")
        self.Label1.pack(side="left")
        self.Time=tk.Entry(self.Line1,state="normal",width=10)
        self.Time.pack(side="left")
        self.Units=ttk.Combobox(self.Line1, values = ("s","m","h","d"), width=4,state = 'readonly')
        self.Units.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")
        
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.Time.get(), self.Units.get()]

    def RetrieveConnections(self):
        return []
    
    def SetValues(self,parms):
        self.Time.delete(0,tk.END)
        self.Time.insert(0,str(parms[0]))
        self.Units.set(parms[1])

    def CheckValues(self):
        Time=self.Time.get()
        Units=self.Units.get()
        self.Action=[]        
        try:
            Time=float(Time)
            if Time<=0: Time/=0
        except:
            self.StatusLabel.config(text="Invalid values")
            return
        else:
            if Units=="m": Time*=60
            if Units=="h": Time*=3600
            if Units=="d": Time*=86400
            self.StatusLabel.config(text="Valid values")
            self.Action=[Time]

class IF(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginBlock=True
        self.Container=True 
        self.Content=[]     
        self.MustBeAfter=0
        self.MustBeBefore=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="lightgreen")
        self.Line1.pack_propagate(False)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="IF")
        self.Label1.pack(side="left")
        self.Time=tk.Entry(self.Line1,state="normal",width=10)
        self.Time.pack(side="left")
        self.Units=ttk.Combobox(self.Line1, values = ("s","m","h","d"), width=4,state = 'readonly')
        self.Units.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")
        
    def DeleteMe(self):
        for Item in self.Content: DeleteObjByIdentifier(Item)            
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.Time.get(), self.Units.get()]

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return
##        self.Time.set(parms[0])  #####
##        self.Units.set(parms[1])

    def CheckValues(self):
        self.Action="OK"        

class ELSE(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginBlock=True        
        self.EndBlock=True        
        self.Container=True 
        self.MustBeAfter=0     
        self.MustBeBefore=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="lightgreen")
        self.Line1.pack_propagate(False)        
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="ELSE")
        self.Label1.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")        
        
    def GetAction(self):
        return "OK"

    def GetValues(self):
        return []

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return

    def CheckValues(self):
        return


class ENDIF(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.EndBlock=True
        self.Container=True 
        self.MustBeAfter=0     
        self.MustBeBefore=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="lightgreen")
        self.Line1.pack_propagate(False)        
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="ENDIF")
        self.Label1.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")        
        
    def GetAction(self):
        return "OK"

    def GetValues(self):
        return []

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return

    def CheckValues(self):
        return

class LOOP(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginBlock=True
        self.Container=True 
        self.Content=[]     
        self.MustBeAfter=0
        self.MustBeBefore=0     
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="orange")
        self.Line1.pack_propagate(False)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="LOOP")
        self.Label1.pack(side="left")
        self.Condition=tk.Entry(self.Line1,state="normal",width=10)
        self.Condition.pack(side="left")
        self.Units=ttk.Combobox(self.Line1, values = ("s","m","h","d"), width=4,state = 'readonly')
        self.Units.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")
        
    def DeleteMe(self):
        for Item in self.Content: DeleteObjByIdentifier(Item)        
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self): #######
        return [self.Condition.get(), self.Units.get()]

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms): #######
        self.Condition.delete(0,tk.END)
        self.Condition.insert(0,str(parms[0]))
        self.Units.set(parms[1])

    def CheckValues(self):
        self.Action="OK"        

class ENDLOOP(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.EndBlock=True
        self.Container=True 
        self.MustBeAfter=0     
        self.MustBeBefore=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="orange")
        self.Line1.pack_propagate(False)        
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="ENDLOOP")
        self.Label1.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")        
        
    def GetAction(self):
        return "OK"

    def GetValues(self):
        return []

    def RetrieveConnections(self):
        return []
    
    def SetValues(self,parms):
        return

    def CheckValues(self):
        return

class REM(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=55
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="blue")
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="COMMENT")
        self.Label1.pack(side="left")
        self.Remark=tk.Entry(self.Line1,state="normal",width=50,bg="lightblue")
        self.Remark.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")        

    def DeleteMe(self):
        DeleteObjByIdentifier(self)
        
    def GetAction(self):
        return "OK"

    def GetValues(self):
        return [self.Remark.get()]

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        self.Remark.delete(0,tk.END)
        self.Remark.insert(0,str(parms[0]))

    def CheckValues(self):
        return   

class Grid(tk.Toplevel):
    def __init__(self,container):
        super().__init__(container)        
        self.title("WIZARD SUMMARY")
        self.grab_set()
        self.RowWidth=0
        self.ItemHeight=0
        self.Row=0
        self.Column=0
        self.Data=[]
        self.Line=""
        self.menubar = Menu(self)
        self.file_menu = Menu(self.menubar,tearoff=0)
        self.file_menu.add_command(label='Save',command=self.SaveData)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit')
        self.config(menu=self.menubar)
        self.menubar.add_cascade(label="File",menu=self.file_menu)
    def SaveData(self):
     filetypes=(('ASCII CSV file','*.csv'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes)
     if filename=="": return
     if not ".csv" in filename: filename+=".csv"
     fout=open(filename, 'w')
     fout.writelines(self.Data)
     fout.close()
    def WriteOnHeader(self,Item):
        text=str(Item)
        E=tk.Label(self,text=text)
        E.grid(row=0,column=self.Column)
        self.update()
        self.RowWidth+=E.winfo_width()
        self.ItemHeight=E.winfo_height()
        self.Line+=text+", "
        self.Column+=1
        self.Row=1
    def CloseHeader(self):
        self.Column=0
        self.Data.append(self.Line[:-2]+"\n")
        self.Line=""
    def AddItemToRow(self,Item):
        text=str(Item)
        E=tk.Label(self,text=text)
        E.grid(row=self.Row,column=self.Column)
        self.Line+=text+", "
        self.Column+=1
    def NextRow(self):
        self.geometry(str(self.RowWidth)+'x'+str(self.ItemHeight*(len(self.Data)+1))+'+400+100')
        self.Data.append(self.Line[:-2]+"\n")
        self.Line=""        
        self.Column=0
        self.Row+=1
        
    

###################### end of classes ######################
def InitVars():
    global ActionsArray, CurrentY, AvailableMacros, EmptyVolume
    ActionsArray=[]
    CurrentY=2
    AvailableMacros=[['Pour','Pour.txt',5]] #name, macroname, number of arguments  $1$: ml,  $2$: syr num, $3$: valve input, $4$: valve output, $5$: valve Air/Waste pos.
    EmptyVolume=10 #Extra volume to be used to remove all reactors content

def CreateCode(*args):
    numvars=-1
    for macro in AvailableMacros:
        if macro[0]==args[0]:
            macroname=macro[1]
            numvars=macro[2]
            break
    if numvars==-1:
        print("Macro",args[0],"not found! cannot compile code. Check the list of available macros")
        return
    if not(numvars==(len(args)-1)):
        print("Macro",args[0],"needs",numvars,"variables, but ",str(len(args)-1),"were given")
        return
    code='macro "'+str(macroname)+'"'
    for i,var in enumerate(args):
        if i>0:
            code+=str(var)
            if i<len(args)-1:
                code+=','
    print(code)

def ReorderObjects():
    global CurrentY
    CurrentY=2
    Sorted=GetYStack()
    x=10    
    for element in Sorted:
        Item=element[1]
        try:
            if Item.EndBlock: x-=20            
        except:
            pass
        Item.place(x=x, y=CurrentY)
        try:
            if Item.BeginBlock: x+=20
        except:
            pass
        CurrentY+=int(Item.Height)
            
def GetYStack():
    global ActionsArray
    Result=[]
    for item in ActionsArray:
        Result.append([item.winfo_y(),item])
    try:
     Result.sort() #now we have the array of objects ordered w. respect to Y pos
    except:
     pass
    return Result

def DeleteObjByIdentifier(ObjIdentifier):
    global ActionsArray
    num=ActionsArray.index(ObjIdentifier)
    ActionsArray.pop(num)
    ObjIdentifier.destroy()
    ReorderObjects()


def StartWizard(window):
    InitVars()
    LoadConfFile('startup.conf')

    def make_draggable(widget):
        widget.bind("<Button-1>", on_drag_start)
        widget.bind("<B1-Motion>", on_drag_motion)
        widget.bind("<ButtonRelease-1>", on_mouse_up)

    def on_drag_start(event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
##        try:
##         if widget.Container:
##            for Contained in widget.Content:
##                Contained.event_generate("<Button-1>")
##                #Contained.invoke(on_drag_start(event)
##        except:
##            pass
        widget.lift()

    def on_drag_motion(event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)

    def on_mouse_up(event): #stop dragging
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        try:
            if widget.Container:
                try:
                    ybefore=widget.MustBeBefore.winfo_y()
                    if y>ybefore:
                        y=ybefore-2
                except:
                    pass
                try:
                    yafter=widget.MustBeAfter.winfo_y()
                    if y<yafter:
                        y=yafter+2
                except:
                    pass
        except:
            pass
        widget.place(x=x, y=y)
        widget.update()
        ReorderObjects()

    def CreateNewObject(ObjType):
        global ActionsArray,CurrentY
        if ObjType=="Pour":
            Obj=Pour(frame2)
        elif ObjType=="Heat":
            Obj=Heat(frame2)
        elif ObjType=="Wash":
            Obj=Wash(frame2)
        elif ObjType=="Wait":
            Obj=Wait(frame2)
        elif ObjType=="IF":
            Obj=IF(frame2)
        elif ObjType=="ELSE":
            Obj=ELSE(frame2)
        elif ObjType=="ENDIF":
            Obj=ENDIF(frame2)
        elif ObjType=="LOOP":
            Obj=LOOP(frame2)
        elif ObjType=="ENDLOOP":
            Obj=ENDLOOP(frame2)
        elif ObjType=="REM":
            Obj=REM(frame2)
        elif ObjType=="IF Block":
            Obj1=CreateNewObject("IF")
            Obj2=CreateNewObject("ELSE")            
            Obj3=CreateNewObject("ENDIF")
            Obj1.Content.append(Obj2)
            Obj1.Content.append(Obj3)
            Obj1.MustBeBefore=Obj2
            Obj2.MustBeBefore=Obj3
            Obj2.MustBeAfter=Obj1            
            Obj3.MustBeAfter=Obj2            
            return
        elif ObjType=="LOOP Block":
            Obj1=CreateNewObject("LOOP")
            Obj2=CreateNewObject("ENDLOOP")
            Obj1.Content.append(Obj2)
            Obj1.MustBeBefore=Obj2
            Obj2.MustBeAfter=Obj1            
            return
        else:
            messagebox.showerror("ERROR", "Object "+ObjType+" Unknown")
            return
        YSize=Obj.Height
        Obj.place(x=10,y=CurrentY)
        CurrentY+=YSize
        make_draggable(Obj)
        ActionsArray.append(Obj)
        return Obj

    def CheckIfConnectionsArePresent():
        ReactantsUsed=[]
        ApparatusUsed=[]
        Sorted=GetYStack()
        for Action in Sorted:
            Object=Action[1]
            connections=Object.RetrieveConnections()
            for connection in connections:
                if "Reactant" in connection:
                 if connection not in ReactantsUsed:
                     ReactantsUsed.append(connection)
                if "Apparatus" in connection:
                 if connection not in ApparatusUsed:
                     ApparatusUsed.append(connection)
        MissingConnections=[]
        AvailableReactants=GetReactantsNames()
        for reactant in ReactantsUsed:
            if not(reactant in AvailableReactants):
                print(reactant,"is missing")
                MissingConnections.append(reactant)
        AvailableApparatus=GetApparatusNames()
        for apparatus in ApparatusUsed:
            if apparatus[-3:]==" IN":
                apparatus=apparatus[:-3]
            elif apparatus[-4:]==" OUT":
                apparatus=apparatus[:-4]
            if not(apparatus in AvailableApparatus):
                print(apparatus,"is missing")
                MissingConnections.append(apparatus)
        return MissingConnections
                
    
    def CheckProcedure():
        global EmptyVolume
        def UpdateVolumes(Input,Quantity,NamesArray,VolumesArray):
            if Input in NamesArray:
                idx=NamesArray.index(Input)
                VolumesArray[idx]+=Quantity
                if VolumesArray[idx]<=0: VolumesArray[idx]=0
            else:
                NamesArray.append(Input)
                if Quantity<0: Quantity=0
                VolumesArray.append(Quantity)

        def ApparatusVolContent(name):
            if name not in ApparatusUsed:
                return 0.0
            else:
                return VolumesInApparatus[ApparatusUsed.index(name)]
            
        def ChooseProperSyringe(ListOfSyringes,Volume):
            if len(ListOfSyringes)==1: return int(ListOfSyringes[0])
            SmallestVol=100000000
            SmallestSyr=-1
            BiggestVol=-1
            BiggestSyr=-1
            for Syringe in ListOfSyringes:
                SyrMaxVol=float(GetSyringeVolume(int(Syringe)))
                if SyrMaxVol>BiggestVol: BiggestSyr=Syringe
                if SyrMaxVol<SmallestVol: SmallestSyr=Syringe
                if (Volume<SyrMaxVol) and (Volume>SyrMaxVol/100): #not too big, not too small
                    return Syringe
            if Volume<SmallestVol: return SmallestSyr
            if Volume>BiggestVol: return BiggestSyr
            return ListOfSyringes[0] #it should not happen
        
        Missing=CheckIfConnectionsArePresent() #check if our SyringeBOT having the proper reactants/apparatus
        if not(len(Missing)==0):
            missinglist="\n".join(Missing)
            messagebox.showerror("ERROR", "Cannot execute procedure. \nThe following connections are missing:\n"+missinglist)
            return
        ReactantsUsed=[]
        VolumesOfReactantsUsed=[]
        ApparatusUsed=[]
        VolumesInApparatus=[]
        StepByStepOps=[]
        Sorted=GetYStack()
        NumActions=len(Sorted)
        if NumActions==0: return
        print(NumActions," Operations")
            
        for Step,Action in enumerate(Sorted):
            Object=Action[1]
            ObjType=str(Object.__class__.__name__)
            print(ObjType)
            Object.CheckValues()
            Action=Object.GetAction()
            if len(Action)==0:
                messagebox.showerror("ERROR", "Invalid or unfinished settings are present")
                return
            if ObjType=="Pour":
                AvailableSyringes,Quantity,Amount,Unit,Input,Output=Action
                Quantity=float(Quantity)
                #Amount=float(Amount)
                Transfered=Quantity
                if "Reactant" in Input:
                 UpdateVolumes(Input,Quantity,ReactantsUsed,VolumesOfReactantsUsed)
                if "Apparatus" in Input:
                 Input=Input[:-4] # remove OUT
                 CurrentLiquid=ApparatusVolContent(Input) # check the actual content of reactor and transfer only this
                 if Quantity>CurrentLiquid: Quantity=CurrentLiquid
                 UpdateVolumes(Input,-Quantity,ApparatusUsed,VolumesInApparatus)
                if "Apparatus" in Output:
                 MaxVol=GetMaxVolumeApparatus(Output)
                 Output2=Output[:-3]   #remove IN   Output2 is like output but without " IN"
                 if MaxVol>0:
                     CurrentLiquid=ApparatusVolContent(Output2)
                     if Quantity+CurrentLiquid>MaxVol:
                         messagebox.showerror("ERROR", "Exceeding the maximum volume of "+Output2+" in step n."+str(Step+1))
                         Object.StatusLabel.config(text="ERROR")
                         return                     
                 UpdateVolumes(Output2,Quantity,ApparatusUsed,VolumesInApparatus)
                 SyringeToUse=int(ChooseProperSyringe(AvailableSyringes,Quantity))
                 V_in=ValvePositionFor(SyringeToUse,Input)
                 V_out=ValvePositionFor(SyringeToUse,Output)
                 V_waste=ValvePositionFor(SyringeToUse,'Air/Waste')
                 CreateCode("Pour",SyringeToUse,Quantity,V_in,V_out,V_waste)
                 
            if ObjType=="Wash":
                Destination,Source,Cycles,Volume,SyrInputs,SyrOutputs=Action
                BestInputSyringe=ChooseProperSyringe(SyrInputs,Volume)
                BestOutputSyringe=ChooseProperSyringe(SyrOutputs,Volume)
                try:
                    ResidualVolume=VolumesInApparatus[ApparatusUsed.index(Destination)]
                    if ResidualVolume>0: #reactor not empty. Before the washing we have to remove the content
                        V_in=ValvePositionFor(BestOutputSyringe,Destination+" OUT")
                        V_waste=ValvePositionFor(BestOutputSyringe,'Air/Waste')
                        V_out=V_waste
                        CreateCode("Pour",BestOutputSyringe,ResidualVolume+EmptyVolume,V_in,V_out,V_waste)
                except:
                    print("error wash 3")
                for i in range(int(Cycles)):
                    V_in=ValvePositionFor(BestInputSyringe,Source)
                    V_out=ValvePositionFor(BestInputSyringe,Destination+" IN")
                    V_waste=ValvePositionFor(BestInputSyringe,'Air/Waste')
                    CreateCode("Pour",BestInputSyringe,Volume,V_in,V_out,V_waste)
                    V_in=ValvePositionFor(BestOutputSyringe,Destination+" OUT")
                    V_out=ValvePositionFor(BestOutputSyringe,'Air/Waste')
                    V_waste=V_out
                    CreateCode("Pour",BestOutputSyringe,Volume+EmptyVolume,V_in,V_out,V_waste)
                    
                UpdateVolumes(Source,float(Cycles)*float(Volume),ReactantsUsed,VolumesOfReactantsUsed)
                UpdateVolumes(Destination,-1e10,ApparatusUsed,VolumesInApparatus)
                
            StepByStepOps.append([[*VolumesOfReactantsUsed],[*VolumesInApparatus],ObjType])
        #print(StepByStepOps)
        StepByStepWindow=Grid(window)
        StepByStepWindow.WriteOnHeader("#")
        StepByStepWindow.WriteOnHeader("Action")
        for reactant in ReactantsUsed:
            StepByStepWindow.WriteOnHeader(reactant)
        for apparatus in ApparatusUsed:
            StepByStepWindow.WriteOnHeader(apparatus)
        StepByStepWindow.CloseHeader()
        for row in range(len(StepByStepOps)):
            CurrentStep=StepByStepOps[row]
            In=CurrentStep[0]
            Out=CurrentStep[1]
            ReactantsLen=len(ReactantsUsed)
            StepByStepWindow.AddItemToRow(str(row+1))
            StepByStepWindow.AddItemToRow(CurrentStep[2])
            for column in range(len(ReactantsUsed)+len(ApparatusUsed)):
                if column<ReactantsLen:
                    if column<len(In):
                        StepByStepWindow.AddItemToRow(In[column])
                    else:
                        StepByStepWindow.AddItemToRow(" ")
                else:
                    if (column-ReactantsLen)<len(Out):
                        StepByStepWindow.AddItemToRow(Out[column-ReactantsLen])
            StepByStepWindow.NextRow()
        #StepByStepWindow.mainloop()                        
                        
    def on_mousewheel(event):
        my_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def GetObjectPosition(object_y,sortedlist):
        try:
            for i,obj in enumerate(sortedlist):
                if obj[0]==object_y: return i
            return -1 #not found
        except:
            return -1

    def LoadModules(filename):
        fin=open(filename, 'rb')
        ModulesArray=pickle.load(fin)
        fin.close()
        CreatedModules=[]
        for Module in ModulesArray:
            ObjType=Module[0]
            ObjValues=Module[1]
            ObjXPos=Module[2]
            ObjYPos=Module[3]
            Obj=CreateNewObject(ObjType)
            CreatedModules.append(Obj)
            Obj.SetValues(ObjValues)
            Obj.place(x=ObjXPos)
        for i,Module in enumerate(ModulesArray):
            IsContainer=Module[4]
            ObjContent=Module[5]
            ObjBefore=Module[6]
            ObjAfter=Module[7]
            if IsContainer:
                if len(ObjContent)>0:
                    for Item in ObjContent:
                        CreatedModules[i].Content.append(CreatedModules[Item])
                if not(ObjBefore==-1):
                    CreatedModules[i].MustBeBefore=CreatedModules[ObjBefore]
                if not(ObjAfter==-1):
                    CreatedModules[i].MustBeAfter=CreatedModules[ObjAfter]
            

    def AskLoadModules():
        global ActionsArray
        filetypes = (('SyringeBOT module files', '*.modules'),('All files', '*.*'))
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename=="": return
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('Load modules','By loading, current modules will be deleted. Proceed anyway?',icon = 'warning')
            if MsgBox == 'yes':
                DeleteAllModules()
            else:
                return
        LoadModules(filename)

    def AskImportModules():
        global ActionsArray
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('Append modules','Import modules will add modules to the current project. Proceed?',icon = 'warning')
            if MsgBox == 'yes':
                filetypes = (('SyringeBOT module files', '*.modules'),('All files', '*.*'))
                filename = filedialog.askopenfilename(filetypes=filetypes)
                if filename=="": return
                LoadModules(filename)                

    def SaveModules(filename):
        Sorted=GetYStack()
        NumActions=len(Sorted)
        if NumActions==0: return
        #print(NumActions," Actions")
        ModulesArray=[]
        for Action in Sorted:
            Actions=[]
            Object=Action[1]
            ObjType=str(Object.__class__.__name__)
            Actions.append(ObjType)            
            Actions.append(Object.GetValues())           
            Actions.append(Object.winfo_x())
            Actions.append(Object.winfo_y())
            try:
             if Object.Container:
                Actions.append(True) 
                try:
                    ContentList=[]
                    for Item in Object.Content:
                        ContentList.append(GetObjectPosition(Item.winfo_y(),Sorted))
                    Actions.append(ContentList)
                except:
                    Actions.append([])
                    pass
                try:
                    before_y=Object.MustBeBefore.winfo_y()
                    before=GetObjectPosition(before_y,Sorted)
                    Actions.append(before)
                except:
                    Actions.append(-1)
                    pass
                try:
                    after_y=Object.MustBeAfter.winfo_y()
                    after=GetObjectPosition(after_y,Sorted)
                    Actions.append(after)
                except:
                    Actions.append(-1)
                    pass
            except:
                Actions.append(False)
                Actions.append([])                
                Actions.append(-1)
                Actions.append(-1)
                pass
            ModulesArray.append(Actions)
        fout=open(filename, 'wb')
        pickle.dump(ModulesArray,fout)
        fout.close()

    def AskSaveModules():
     filetypes=(('SyringeBOT module files','*.modules'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes)
     if filename=="": return
     if not ".modules" in filename: filename+=".modules"
     SaveModules(filename)

    def Close():
        WizardWindow.destroy()

    def DeleteAllModules():
        global ActionsArray
        print(ActionsArray)
        while len(ActionsArray)>0:
            DeleteObjByIdentifier(ActionsArray[0])
        ActionsArray=[]

    def New():
        global ActionsArray
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('New procedure','Are you sure you want to delete all?',icon = 'warning')
            if MsgBox == 'yes':
                DeleteAllModules()

    WizardWindow=tk.Toplevel(window)
    WizardWindow.title("CORRO WIZARD")
    WizardWindow.geometry('1000x800+200+10')
    WizardWindow.grab_set()
    menubar = Menu(WizardWindow)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='New',command=New)
    file_menu.add_separator()    
    file_menu.add_command(label='Load modules',command=AskLoadModules)
    file_menu.add_command(label='Append modules',command=AskImportModules)    
    file_menu.add_command(label='Save modules',command=AskSaveModules)
    file_menu.add_separator()
    file_menu.add_command(label='Exit',command=Close)
    settings_menu = Menu(menubar,tearoff=0)
    settings_menu.add_command(label='Default macro settings')
    WizardWindow.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)
    menubar.add_cascade(label="Settings",menu=settings_menu)
    frame1 = tk.Frame(WizardWindow)
    frame1.pack(side="top")
    frame3 = tk.Frame(WizardWindow,bg="gray",width=1000,height=30)
    frame3.pack(side="bottom")  
    my_canvas = Canvas(WizardWindow)
    my_canvas.pack(side=LEFT,fill=BOTH,expand=1)
    y_scrollbar = ttk.Scrollbar(WizardWindow,orient=VERTICAL,command=my_canvas.yview)
    y_scrollbar.pack(side=RIGHT,fill=Y)
    my_canvas.configure(yscrollcommand=y_scrollbar.set)
    my_canvas.bind("<Configure>",lambda e: my_canvas.config(scrollregion= my_canvas.bbox(ALL)))
    my_canvas.bind_all("<MouseWheel>", on_mousewheel)

    frame2=tk.Frame(my_canvas,bg="white",height=10000,width=1000)
    my_canvas.create_window((0,0),window=frame2, anchor="nw")    
  
    tk.Button(frame1,text="Pour liquid",command=lambda: CreateNewObject("Pour")).pack(side="left")
    tk.Button(frame1,text="Heat reactor",command=lambda: CreateNewObject("Heat")).pack(side="left")
    tk.Button(frame1,text="Wash reactor",command=lambda: CreateNewObject("Wash")).pack(side="left")
    tk.Button(frame1,text="Wait",command=lambda: CreateNewObject("Wait")).pack(side="left")
    tk.Button(frame1,text="IF",command=lambda: CreateNewObject("IF Block")).pack(side="left")
    tk.Button(frame1,text="LOOP",command=lambda: CreateNewObject("LOOP Block")).pack(side="left")
    tk.Button(frame1,text="Comment",command=lambda: CreateNewObject("REM")).pack(side="left")      
    tk.Button(frame1,text="L/L separation",command=lambda: CreateNewObject("Liq")).pack(side="left")
    tk.Button(frame1,text="Evaporate solvent",command=lambda: CreateNewObject("Evap")).pack(side="left")
    tk.Button(frame1,text="Chromatography",command=lambda: CreateNewObject("Chrom")).pack(side="left")    
    tk.Button(frame1,text="Device ON/OFF",command=lambda: CreateNewObject("Switch")).pack(side="left")    
    tk.Button(frame1,text="Titrate",command=lambda: CreateNewObject("Titr")).pack(side="left")    
    tk.Button(frame1,text="Function",command=lambda: CreateNewObject("Func")).pack(side="left")    

    tk.Button(frame3,text="Process Check",command=CheckProcedure).pack(side="left")        
    WizardWindow.mainloop()
