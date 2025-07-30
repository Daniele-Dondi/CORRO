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
import os
from modules.configurator import *

class Pour(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.AvailableInputs=GetAllSyringeInputs()
        self.Height=50
        self.IsContainer=False
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
        self.Units.bind("<<ComboboxSelected>>", self.UnitTypeCallback)
        self.Units.pack(side="left")
        self.Label2=tk.Label(self.Line1,text="of")
        self.Label2.pack(side="left")
        self.Source=ttk.Combobox(self.Line1, values = self.AvailableInputs, width=self.MaxCharsInList(self.AvailableInputs), state = 'readonly')
        self.Source.bind("<<ComboboxSelected>>", self.InputTypeCallback)
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

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return parms[0]+" $3$ "+parms[4]+" of '"+parms[5]+"' into '"+parms[6]+"'"

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
        self.Action=[]        
        self.CheckInput()
        self.CheckUnit()
        Input=self.Source.get()
        Output=self.Destination.get()
        Quantity=self.Amount.get()
        Amount=Quantity #we keep Amount with the current units, Quantity will be transformed in mL
        Unit=self.Units.get()
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

    
    def UnitTypeCallback(self,event):
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
        Output=self.Destination.get()
        if Input=="" or Output=="": return
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
            #self.Source.set("")
            #self.Destination.set("")
            #print("Cannot find any connections to "+Input)
            return "Cannot find any connections to "+Input
        for SyringeNum in SyrNums:
            AvailableOutputs=GetAllOutputsOfSyringe(int(SyringeNum))
            for Out in AvailableOutputs:
                if Out not in OutputsList:
                    OutputsList.append(Out)
        PossibleOutputs=[OutputsList[i][0] for i in range(len(OutputsList))]
        PossibleOutputs.sort()
        self.Destination.config(values = PossibleOutputs,state="readonly",width=self.MaxCharsInList(PossibleOutputs))
        if not Output in PossibleOutputs:
            #self.Destination.set("")
            #print("Cannot find connections from ",Input," to ",Output)
            return "Cannot find connections from "+str(Input)+" to "+str(Output)
            
    
    def InputTypeCallback(self,event):
        self.CheckInput()


class Heat(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.AvailableApparatus=GetAllHeatingApparatus()
        self.Height=75
        self.IsContainer=False
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

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "Heat '"+parms[0]+"' at $1$ °C and keep for $2$ min"

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
        EndTemperature=self.EndTemperature.get()
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
            self.Action=[Apparatus,Temperature,Time,Wait4Cooling,EndTemperature]
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
        self.IsContainer=False
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
        self.Destination.bind("<<ComboboxSelected>>", self.InputTypeCallback)
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
        self.Cycles=tk.Spinbox(self.Line2, from_=1, to=10, repeatdelay=500, repeatinterval=200)
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

    def InputTypeCallback(self,event):
        self.CheckInput()

    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.Source.get(), self.Destination.get(), self.Cycles.get(), self.Volume.get()]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "Wash '"+parms[1]+"' with '"+parms[0]+"'"

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
        self.IsContainer=False
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
        self.Units=ttk.Combobox(self.Line1, values = ("s","m","h"), width=4,state = 'readonly')
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

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "Wait $0$ "+parms[1]

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
            self.StatusLabel.config(text="Valid values")
            self.Action=[Time,Units]

class IF(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginIndent=True
        self.IsContainer=True 
        self.Content=[]     
        self.First=0
        self.Last=0
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
        self.IfType=ttk.Combobox(self.Line1, values = ["Sensor vars","Custom"], width=12,state = 'readonly')
        self.IfType.set("Sensor vars")
        self.IfType.bind("<<ComboboxSelected>>", self.IfTypeCallback)
        self.IfType.pack(side="left")
        self.Variable=ttk.Combobox(self.Line1, values = GetAllSensorsVarNames(), width=10,state = 'readonly')
        self.Variable.pack(side="left")
        self.Condition=ttk.Combobox(self.Line1, values = ["<",">","=","<>",">=","<="], width=4,state = 'readonly')
        self.Condition.pack(side="left")        
        self.Value=tk.Entry(self.Line1,state="normal",width=10)
        self.Value.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")

    def IfTypeCallback(self,event):
        if self.IfType.get()=="Sensor vars":
            self.Variable.config(state="readonly")
            self.Condition.config(state="readonly")
            self.Value.config(width=10)            
        else:
            self.Variable.config(state="disabled")
            self.Condition.config(state="disabled")
            self.Value.config(width=40)
        
    def DeleteMe(self):
        for Item in self.Content: DeleteObjByIdentifier(Item)            
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self):
        return [self.IfType.get(), self.Variable.get(), self.Condition.get(), self.Value.get()]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        if parms[0]=="Custom":
            return "IF "+parms[3]
        else:
            return "IF '"+parms[1]+parms[2]+"' $3$"

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        self.IfType.set(parms[0])
        self.Variable.set(parms[1])
        self.Condition.set(parms[2])        
        self.Value.delete(0,tk.END)
        self.Value.insert(0,str(parms[3]))        

    def CheckValues(self):
        self.Action=[]
        self.StatusLabel.config(text="---")
        IfType=self.IfType.get()
        Variable=self.Variable.get()
        Condition=self.Condition.get()
        Value=self.Value.get()
        if IfType=="Custom":
            if Value=="": return
        else:
            if Variable=="" or Condition=="" or Value=="": return
        self.Action=[IfType, Variable, Condition, Value]
        self.StatusLabel.config(text="OK")
               

class ELSE(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=45
        self.BeginIndent=True        
        self.EndIntend=True        
        self.IsContainer=True 
        self.First=0
        self.Last=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=20,width=500,bg="lightgreen")
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

    def GetOptimizableParameters(self):
        return "ELSE"

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return

    def CheckValues(self):
        return


class ENDIF(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=45
        self.EndIntend=True
        self.IsContainer=True 
        self.First=0
        self.Last=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=20,width=500,bg="lightgreen")
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

    def GetOptimizableParameters(self):
        return "ENDIF"

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return

    def CheckValues(self):
        return

class GET(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginIndent=False
        self.IsContainer=False 
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="gold")
        self.Line1.pack_propagate(False)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()
        self.Label1=tk.Label(self.Line1, text="Get Value")
        self.Label1.pack(side="left")
        self.Value=tk.Entry(self.Line1,state="normal",width=10)
        self.Value.pack(side="left")
        self.Variable=ttk.Combobox(self.Line1, values = GetAllSensorsVarNames(), width=4,state = 'readonly')
        self.Variable.pack(side="left")
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
        return [self.Value.get(), self.Variable.get()]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "Get "+parms[0]+" "+parms[1]

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms):
        return
##        self.Value.set(parms[0])  #####
##        self.Variable.set(parms[1])

    def CheckValues(self):
        self.Action="OK" 

class Function(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=125
        self.BeginIndent=False
        self.IsContainer=False
        self.AvailableFunctions=AvailableCommands+AvailableMacros
        self.FunctionNames=[self.AvailableFunctions[i][0] for i in range(len(self.AvailableFunctions))]
        self.FunctionNumVars=[self.AvailableFunctions[i][1] for i in range(len(self.AvailableFunctions))]
        self.FunctionHeader=[self.AvailableFunctions[i][2] for i in range(len(self.AvailableFunctions))]
        self.Values=[]
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=40,width=500,bg="lime")
        self.Line1.pack_propagate(False)
        self.Line1.pack()
        self.Line2=tk.Frame(self,bg="lime")
        self.Line2.pack()
        self.Line3=tk.Frame(self)
        self.Line3.pack()        
        self.Label1=tk.Label(self.Line1, text="Function")
        self.Label1.pack(side="left")
        self.Function=ttk.Combobox(self.Line1, values = self.FunctionNames, width=self.MaxCharsInList(self.FunctionNames)+2,state = 'readonly')
        self.Function.bind("<<ComboboxSelected>>", self.InputTypeCallback)
        self.Function.pack(side="left")
        self.description = tk.Text(self.Line2, wrap="word", height=4, width=90,bg="lightgray")
        self.description.config(state='disabled')
        self.description.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.Line2, orient="vertical", command=self.description.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.description.config(yscrollcommand=self.scrollbar.set)        
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line3,text="---")
        self.StatusLabel.pack(side="left")
        
    def DeleteMe(self):
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.GetValues()

    def GetValues(self):
        Values=[]
        Values=[Value.get() for Value in self.Values]
        return [self.Function.get(), Values]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "FUNCTION "+parms[0]

    def RetrieveConnections(self):
        return []

    def Setup(self): #create enrtries in a number as requested by function
        self.description.config(state='normal')
        self.description.delete(1.0,tk.END)
        self.description.insert('end', self.FunctionHeader[self.Function.current()])
        self.description.config(state='disabled')
        self.Check.pack_forget()
        self.Delete.pack_forget()
        for entryobject in self.Values:
            entryobject.destroy()
        self.Values=[]
        Num_Vars=self.FunctionNumVars[self.Function.current()]
        for i in range(Num_Vars):
            entrywidth=int(50/Num_Vars)            
            self.Values.append(tk.Entry(self.Line1,state="normal",width=entrywidth))
            self.Values[-1].pack(side="left")
        self.Check.pack(side="left")
        self.Delete.pack(side="left")
        
    def InputTypeCallback(self,event):
        self.Setup()
            
    def MaxCharsInList(self,List):
        maxlength=8
        try:
            maxlength=max([len(List[i]) for i in range(len(List))])
        except:
            pass
        return maxlength    

    def SetValues(self,parms):
        self.Function.set(parms[0])
        self.Setup()
        try:
            for num,value in enumerate(parms[1]):
                self.Values[num].delete(0,tk.END)
                self.Values[num].insert(0,str(value))
        except:
            pass
        
    def CheckValues(self):
        return 

class LOOP(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=65
        self.BeginIndent=True
        self.IsContainer=True 
        self.Content=[]     
        self.First=0
        self.Last=0
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
        self.LoopType=ttk.Combobox(self.Line1, values = ("Forever","Num Cycles","If Condition True"), width=20,state = 'readonly')
        self.LoopType.set("Forever")
        self.LoopType.bind("<<ComboboxSelected>>", self.LoopTypeCallback)        
        self.LoopType.pack(side="left")
        self.Cycles=tk.Spinbox(self.Line1, from_=1, to=10000, repeatdelay=500, repeatinterval=200, width=4, state = 'disabled')
        self.Cycles.pack(side="left")
        self.Condition=tk.Entry(self.Line1,width=35, state = 'disabled')
        self.Condition.pack(side="left")
        self.Check=tk.Button(self.Line1,text="check",command=self.CheckValues)
        self.Check.pack(side="left")
        self.Delete=tk.Button(self.Line1,text="DEL",command=self.DeleteMe)
        self.Delete.pack(side="left")
        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")

    def LoopTypeCallback(self,event):
        LoopType=self.LoopType.get()
        if LoopType=="Forever":
            self.Cycles.config(state="disabled")
            self.Condition.config(state="disabled")
        elif LoopType=="Num Cycles":
            self.Cycles.config(state="normal")
            self.Condition.config(state="disabled")
        else:
            self.Cycles.config(state="disabled")
            self.Condition.config(state="normal")

    def DeleteMe(self):
        for Item in self.Content: DeleteObjByIdentifier(Item)        
        DeleteObjByIdentifier(self)

    def GetAction(self):
        return self.Action

    def GetValues(self): 
        return [self.LoopType.get(), self.Cycles.get(), self.Condition.get()]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        if parms[0]=="Forever": return "LOOP"
        if parms[0]=="Num Cycles": return "LOOP $1$ cycles"
        if parms[0]=="If Condition True": return"LOOP IF "+parms[2]+"=True"
        return "Heat '"+parms[0]+"' at $1$ °C and keep for $2$ min"

    def RetrieveConnections(self):
        return []

    def SetValues(self,parms): 
        self.LoopType.set(parms[0])
        self.Cycles.delete(0,tk.END)
        self.Cycles.insert(0,str(parms[1]))
        self.Condition.delete(0,tk.END)
        self.Condition.insert(0,str(parms[2]))

    def CheckValues(self):
        self.Action=[]
        self.StatusLabel.config(text="---")
        LoopType=self.LoopType.get()
        Cycles=self.Cycles.get()
        Condition=self.Condition.get()
        if LoopType=="If Condition True" and len(Condition)==0: return
        self.Action=[LoopType, Cycles, Condition]
        self.StatusLabel.config(text="OK")

class ENDLOOP(tk.Frame):
    def __init__(self,container):
        self.Action=[]
        self.Height=45
        self.EndIntend=True
        self.IsContainer=True 
        self.First=0
        self.Last=0
        super().__init__(container)
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self,height=20,width=500,bg="orange")
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

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return "ENDLOOP"

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
        self.IsContainer=False
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
        return [self.Remark.get()]

    def GetValues(self):
        return [self.Remark.get()]

    def GetOptimizableParameters(self):
        parms=self.GetValues()
        return parms[0]

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

    
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
        
def GetAvailMacros():
    function_inputs=["$"+str(i)+"$" for i in range(1,21)]
    AvailableMacros=[]
    try:
     for file in os.listdir("macros"):
        if file.endswith(".txt"): #all files in macros folder having .txt extension are considered macros
           with open('macros'+os.sep+file) as f:
            num_vars=0
            function_header=""
            first_line = f.readline().lower()
            if "function" in first_line:
                line = f.readline()
                while line.find(";")==0:
                    function_header+=line[1:]
                    for function_input in function_inputs:
                     if function_input in line:
                        num_vars+=1
                    line = f.readline()
            AvailableMacros.append([file[:-4],num_vars,function_header]) #remove .txt from name
    except Exception as e:
     print(e)
     messagebox.showerror("ERROR", "MACRO directory unreachable")
    return AvailableMacros

def GetAvailCommands():
    AvailableCommands=[]
    try:
       command_header=""
       command=""
       FirstLine=False
       with open('conf'+os.sep+"commands.txt", encoding='utf-8') as f:
           for line in f:
            line = line.strip()
            if len(line)>0:
                if line.find("#")==0:
                    if command=="": 1/0
                    else:
                        if FirstLine:
                            num_vars=0
                            try:
                                num_vars=int(line[1:])
                            except:
                                command_header+=line[1:]+"\n"
                            FirstLine=False
                        else:
                            command_header+=line[1:]+"\n"
                else:
                    command=line
                    FirstLine=True
            else:
                if not(command==""):
                    AvailableCommands.append([command,num_vars,command_header])
                    command=""
                    command_header=""
    except Exception as e:
     print(e)
     messagebox.showerror("ERROR", "Error reading commands.txt")
    return AvailableCommands
        
def InitVars():
    global ActionsArray, CurrentY, AvailableMacros, AvailableCommands, EmptyVolume
    ActionsArray=[]
    AvailableMacros=GetAvailMacros()
    AvailableCommands=GetAvailCommands()
    CurrentY=10
    EmptyVolume=10 #Extra volume to be used to remove all reactors content

def CreateMacroCode(*args):
    numvars=-1
    for macro in AvailableMacros:
        if macro[0]==args[0]:
            macroname=macro[0]
            numvars=macro[1]
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
    return code

def IndentObjects(): #set the x position (indentation) of the object
    global CurrentY
    CurrentY=10
    Sorted=GetYStack()
    x=10    
    for element in Sorted:
        Item=element[1]
        try:
            if Item.EndIntend: x-=20            
        except:
            pass
        Item.place(x=x, y=CurrentY)
        try:
            if Item.BeginIndent: x+=20
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
    except Exception as e:
     #print(e)   
     pass
    return Result

def DeleteObjByIdentifier(ObjIdentifier):
    global ActionsArray
    num=ActionsArray.index(ObjIdentifier)
    ActionsArray.pop(num)
    ObjIdentifier.destroy()
    IndentObjects()

def ChooseProcedureFile():
    filetypes = (('SyringeBOT Procedure files', '*.Procedure'),('All files', '*.*'))
    filename = filedialog.askopenfilename(filetypes=filetypes)
    return filename

def AskToShowMissingConnections(window,Missing):
    response = messagebox.askyesno("ERROR", "Cannot execute procedure. \nDo you want to see the missing objects?")
    if response:  # True if "Yes" is clicked
        if len(Missing)>1:
            plural="s"
        else:
            plural=""
        MissingObjects=Grid(window)
        MissingObjects.WriteOnHeader("Number of missing object"+plural)
        MissingObjects.WriteOnHeader("---------------- Object missing (Reagent, Connection, Apparatus) ----------------")
        MissingObjects.CloseHeader()
        for i,Missed in enumerate(Missing):
            MissingObjects.AddItemToRow(str(i+1))
            MissingObjects.AddItemToRow(Missed)
            MissingObjects.NextRow()

def ThereAreErrors(window,CompiledCode):
  if CompiledCode=="" or CompiledCode==None:
     return True
  test="ERROR" in CompiledCode
  if test:
     AskToShowMissingConnections(window,CompiledCode[1])     
  return test            

def StartWizard(window, **kwargs):
    InitVars()
    LoadConfFile('startup.conf')

    global selected_objects,Selecting_Objects,Selection_start_X,Selection_start_Y,Selection_end_X,Selection_end_Y
    global Dragging_Objects
    Selection_start_X=0
    Selection_start_Y=0
    Selection_end_X=0
    Selection_end_Y=0
    selected_objects=[]
    Selecting_Objects=False
    Dragging_Objects=False

    def Remove_Selection_Reactangle():
        try:
            SelectionCanvas.delete(SelectionCanvas.rect)
        except:
            pass        

    def drag_start_canvas(event):
        global selected_objects,Selecting_Objects,Selection_start_X,Selection_start_Y,Selection_end_X,Selection_end_Y
        global Dragging_Objects
        if SelectionCanvas.canvasx(event.x)<400: return
        if Dragging_Objects: return
        WizardWindow.focus_set()
        selected_objects=[]
        Selecting_Objects=True
        Selection_start_X=SelectionCanvas.canvasx(event.x)
        Selection_start_Y=SelectionCanvas.canvasy(event.y)
        Selection_end_X=Selection_start_X
        Selection_end_Y=Selection_start_Y
        SelTopButton.place(x=Selection_start_X,y=Selection_start_Y)
        SelTopButton.config(height=1,width=1)
        SelTopButton.lift()
        SelBottomButton.place(x=Selection_start_X,y=Selection_start_Y)
        SelBottomButton.config(height=1,width=1)
        SelBottomButton.lift()
        SelLeftButton.place(x=Selection_start_X,y=Selection_start_Y)
        SelLeftButton.config(height=1,width=1)
        SelLeftButton.lift()
        SelRightButton.place(x=Selection_start_X,y=Selection_start_Y)
        SelRightButton.config(height=1,width=1)
        SelRightButton.lift()
        Remove_Selection_Reactangle()

    def drag_motion_canvas(event):
        global Selecting_Objects,Selection_start_X,Selection_start_Y,Selection_end_X,Selection_end_Y
        if Selecting_Objects:
            Selection_end_X=SelectionCanvas.canvasx(event.x)
            Selection_end_Y=SelectionCanvas.canvasy(event.y)
            SelTopButton.config(width=abs(Selection_start_X-Selection_end_X))
            SelBottomButton.config(width=abs(Selection_start_X-Selection_end_X))
            SelBottomButton.place(y=Selection_end_Y)
            if Selection_start_X>Selection_end_X:
                SelTopButton.place(x=Selection_end_X)
                SelBottomButton.place(x=Selection_end_X)
            SelLeftButton.config(height=abs(Selection_start_Y-Selection_end_Y))
            SelRightButton.config(height=abs(Selection_start_Y-Selection_end_Y))
            SelRightButton.place(x=Selection_end_X)
            if Selection_start_Y>Selection_end_Y:
                SelLeftButton.place(y=Selection_end_Y)
                SelRightButton.place(y=Selection_end_Y)

    def on_mouse_up_canvas(event):
        global selected_objects,Selecting_Objects,Selection_start_X,Selection_start_Y,Selection_end_X,Selection_end_Y
        if Selecting_Objects:
            Selecting_Objects=False
            SelTopButton.place_forget()
            SelBottomButton.place_forget()
            SelLeftButton.place_forget()
            SelRightButton.place_forget()
            Min_Y=min(Selection_start_Y,Selection_end_Y)
            Max_Y=max(Selection_start_Y,Selection_end_Y)
            Min_X=min(Selection_start_X,Selection_end_X)
            if Min_X>500: return #we never catched the blocks
            Sorted=GetYStack()
            for element in Sorted:
                Y_pos=element[0]                  
                obj=element[1]
                if Y_pos>=Min_Y and Y_pos<=Max_Y:
                    if obj.IsContainer: # if in our selection we included a container, we might need to expand the selection if we never taken all the contained objects
                        contained_Min_Y=obj.First.winfo_y()
                        contained_Max_Y=obj.Last.winfo_y()
                        Min_Y=min(contained_Min_Y,Min_Y)
                        Max_Y=max(contained_Max_Y,Max_Y)
            for element in Sorted: #put in the selection all the objects within the container
              try:
                Y_pos=element[0]                  
                obj=element[1]
                if Y_pos>=Min_Y and Y_pos<=Max_Y:
                    selected_objects.append(obj)
                    obj._drag_start_x = event.x
                    obj._drag_start_y = event.y
                    obj.lift()
              except:
                pass
            Selecting_Objects=False
            if len(selected_objects)>0: # adjust rectangle size to fit the selected objects
                Min_Y=selected_objects[0].winfo_y()-1
                lastobj=selected_objects[-1]                
                Max_Y=lastobj.winfo_y()+lastobj.Height-2
                SelectionCanvas.rect=SelectionCanvas.create_rectangle(2,Min_Y,600,Max_Y,outline="blue", width=2)
            else:
                Remove_Selection_Reactangle()
        
    def make_draggable(widget):
        widget.bind("<Button-1>", on_drag_start)
        widget.bind("<B1-Motion>", on_drag_motion)
        widget.bind("<ButtonRelease-1>", on_mouse_up)

    def on_drag_start(event):
        global selected_objects
        global Dragging_Objects
        Dragging_Objects=True
        Remove_Selection_Reactangle()    
        widget = event.widget
        if widget in selected_objects: #if the user clicked in one of the selected object we have to move the selected block. Otherwise, let's go with single object
            for obj in selected_objects:
                obj._drag_start_x = event.x
                obj._drag_start_y = event.y
                obj.lift()
            return
        else:
            selected_objects=[]
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
        selected_objects.append(widget)
        widget.lift()        
        try:
         if widget.IsContainer:
            Sorted=GetYStack()                   
            Min_Y=widget.First.winfo_y()
            Max_Y=widget.Last.winfo_y()
            for element in Sorted: #put in the selection all the objects within the container
              try:
                Y_pos=element[0]                  
                obj=element[1]
                if Y_pos>=Min_Y and Y_pos<=Max_Y:
                    selected_objects.append(obj)
                    obj._drag_start_x = event.x
                    obj._drag_start_y = event.y
                    obj.lift()
              except:
                pass
        except Exception as e:
            print(e)
            pass


    def on_drag_motion(event):
        global Selecting_Objects
        if Selecting_Objects: return
        global selected_objects
        # Move all selected objects
        for widget in selected_objects:
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y() - widget._drag_start_y + event.y
            widget.place(x=x, y=y)            

    def on_mouse_up(event): #stop dragging
      global selected_objects
      global Dragging_Objects
      for num,widget in enumerate(selected_objects):
        x = widget.winfo_x() - widget._drag_start_x + event.x
        if num==0:
            y = widget.winfo_y() - widget._drag_start_y + event.y
        else:
            y+=1
        widget.place(x=x, y=y)
        widget.update()
      selected_objects=[]
      Dragging_Objects=False
      IndentObjects()

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
        elif ObjType=="Function":
            Obj=Function(frame2)            
        elif ObjType=="GET":
            Obj=GET(frame2)
        elif ObjType=="IF Block":
            Obj1=CreateNewObject("IF")
            Obj2=CreateNewObject("ELSE")            
            Obj3=CreateNewObject("ENDIF")
            Obj1.Content.append(Obj2)
            Obj1.Content.append(Obj3)
            Obj1.First=Obj1
            Obj1.Last=Obj3
            Obj2.First=Obj1
            Obj2.Last=Obj3
            Obj3.First=Obj1
            Obj3.Last=Obj3
            return
        elif ObjType=="LOOP Block":
            Obj1=CreateNewObject("LOOP")
            Obj2=CreateNewObject("ENDLOOP")
            Obj1.Content.append(Obj2)            
            Obj1.First=Obj1
            Obj1.Last=Obj2
            Obj2.First=Obj1
            Obj2.Last=Obj2
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
        MissingConnections=[]        
        Sorted=GetYStack()
        for Action in Sorted:
            Object=Action[1]
            connections=Object.RetrieveConnections()
            for connection in connections:
                if connection=="":
                    continue
                if "Reactant" in connection:
                 if connection not in ReactantsUsed:
                     ReactantsUsed.append(connection)
                if "Apparatus" in connection:
                 if connection not in ApparatusUsed:
                     ApparatusUsed.append(connection)
            try:
                result=Object.CheckInput()
                if len(result)>0:
                    MissingConnections.append(result)
            except:
                pass
        AvailableReactants=GetReactantsNames()
        for reactant in ReactantsUsed:
            if not(reactant in AvailableReactants):
                #print(reactant,"is missing")
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
                
    
    def CheckProcedure(**kwargs):
        global EmptyVolume

        Phantom_Mode=False
        GetCodeAndExit=False
        GetVolumesAndExit=False
        GetOptimizerParameteraAndExit=False

        for k, val in kwargs.items():
            if k=="Hide":
                if val:Phantom_Mode=True #suppress interaction with user
            if k=="Mode":
                if val=="Code":
                    GetCodeAndExit=True
                elif val=="Volumes":
                    GetVolumesAndExit=True
                elif val=="Optimizer":
                    GetOptimizerParameteraAndExit=True
        
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

        global BoolVarCounter
        BoolVarCounter=0
        def CreateBoolVariable():
            global BoolVarCounter
            BoolVarCounter+=1
            return "$test"+str(BoolVarCounter)+"$"

        global LabelCounter
        LabelCounter=0
        def CreateLabel():
            global LabelCounter
            LabelCounter+=1
            return "LABEL_"+str(LabelCounter)

        global LoopVarCounter
        LoopVarCounter=0
        def CreateLoopVar():
            global LoopVarCounter
            LoopVarCounter+=1
            return "$count_"+str(LoopVarCounter)+"$"
        
        Missing=CheckIfConnectionsArePresent() #check if our SyringeBOT having the proper reactants/apparatus
        if not(len(Missing)==0):
          if Phantom_Mode:
              return ['ERROR',Missing]
          else:
            AskToShowMissingConnections(WizardWindow,Missing)  
            return
        
        ReactantsUsed=[]
        VolumesOfReactantsUsed=[]
        ApparatusUsed=[]
        VolumesInApparatus=[]
        StepByStepOps=[]
        CompiledCode=[]
        LoopStack=[]
        OptimizerCode=[]
        Sorted=GetYStack()
        NumActions=len(Sorted)
        if NumActions==0: return
            
        for Step,Action in enumerate(Sorted):
            Object=Action[1]
            ObjType=str(Object.__class__.__name__)
            Object.CheckValues() #most of the objects needs to setup internal variables before retrieving the action
            Action=Object.GetAction()
            if len(Action)==0:
                messagebox.showerror("ERROR", "Invalid or unfinished settings are present")
                return
            if ObjType=="Pour":
                AvailableSyringes,Quantity,Amount,Unit,Input,Output=Action
                Quantity=float(Quantity)
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
                 CompiledCode.append(CreateMacroCode("Pour",SyringeToUse,Quantity,V_in,V_out,V_waste))
                 OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                 
            elif ObjType=="Wash":
                Destination,Source,Cycles,Volume,SyrInputs,SyrOutputs=Action
                BestInputSyringe=ChooseProperSyringe(SyrInputs,Volume)
                BestOutputSyringe=ChooseProperSyringe(SyrOutputs,Volume)
                try:
                    ResidualVolume=VolumesInApparatus[ApparatusUsed.index(Destination)]
                    if ResidualVolume>0: #reactor not empty. Before the washing we have to remove the content
                        V_in=ValvePositionFor(BestOutputSyringe,Destination+" OUT")
                        V_waste=ValvePositionFor(BestOutputSyringe,'Air/Waste')
                        V_out=V_waste
                        CompiledCode.append(CreateMacroCode("Pour",BestOutputSyringe,ResidualVolume+EmptyVolume,V_in,V_out,V_waste))
                except:
                    print("error wash 3")
                for i in range(int(Cycles)):
                    V_in=ValvePositionFor(BestInputSyringe,Source)
                    V_out=ValvePositionFor(BestInputSyringe,Destination+" IN")
                    V_waste=ValvePositionFor(BestInputSyringe,'Air/Waste')
                    CompiledCode.append(CreateMacroCode("Pour",BestInputSyringe,Volume,V_in,V_out,V_waste))
                    V_in=ValvePositionFor(BestOutputSyringe,Destination+" OUT")
                    V_out=ValvePositionFor(BestOutputSyringe,'Air/Waste')
                    V_waste=V_out
                    CompiledCode.append(CreateMacroCode("Pour",BestOutputSyringe,Volume+EmptyVolume,V_in,V_out,V_waste))
                    
                UpdateVolumes(Source,float(Cycles)*float(Volume),ReactantsUsed,VolumesOfReactantsUsed)
                UpdateVolumes(Destination,-1e10,ApparatusUsed,VolumesInApparatus)
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                
            elif ObjType=="Heat":
                Apparatus,Temperature,Time,Wait4Cooling,EndTemperature=Action
                CompiledCode.append(CreateMacroCode("SetTemp",Temperature))
                CompiledCode.append("hook temp >"+str(Temperature))
                CompiledCode.append("hook time >"+str(Time)+"m")
                if Wait4Cooling:
                    CompiledCode.append("hook temp <"+str(EndTemperature))
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])

            elif ObjType=="Wait":
                    Time,Units=Action
                    CompiledCode.append("hook time >"+str(Time)+str(Units))
                    OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])

            elif ObjType=="IF":
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                IfType,Variable,Condition,Value=Action
                TestVariable=CreateBoolVariable()
                tmp_string=""
                if IfType=="Custom":
                    tmp_string=Value
                else:
                    CompiledCode.append("getvalue $"+Variable+"$,"+Variable)
                    tmp_string="$"+Variable+"$"+Condition+Value
                CompiledCode.append("eval "+TestVariable+","+tmp_string)
                CompiledCode.append("if "+TestVariable)

            elif ObjType=="ELSE":
                CompiledCode.append("else")
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                
            elif ObjType=="ENDIF":
                CompiledCode.append("endif")
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])

            elif ObjType=="LOOP":
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                LoopType, Cycles, Condition=Action  #"Forever","Num Cycles","If Condition True"
                if LoopType=="Forever":
                    JumpLabel=CreateLabel()
                    LoopStack.append(LoopType)
                    LoopStack.append(JumpLabel)
                    CompiledCode.append("label "+JumpLabel)
                elif LoopType=="Num Cycles":
                    LoopVariable=CreateLoopVar()
                    LoopStack.append(LoopType)
                    LoopStack.append(Cycles)
                    CompiledCode.append("for "+LoopVariable+" "+Cycles)
                elif LoopType=="If Condition True":
                    JumpLabel=CreateLabel()
                    TestVariable=CreateBoolVariable()
                    LoopStack.append(LoopType)
                    LoopStack.append(JumpLabel)
                    CompiledCode.append("label "+JumpLabel)                    
                    CompiledCode.append("eval "+TestVariable+","+Condition)
                    CompiledCode.append("if "+TestVariable)
                else:
                    print("ERROR 21")
                    return

            elif ObjType=="ENDLOOP":
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                parameter=LoopStack.pop()
                LoopType=LoopStack.pop()
                if LoopType=="Forever":
                    CompiledCode.append("jump "+parameter)
                elif LoopType=="Num Cycles":
                    CompiledCode.append("next")
                elif LoopType=="If Condition True":
                    CompiledCode.append("jump "+parameter)
                    CompiledCode.append("endif")
                else:
                    print("ERROR 454")

            elif ObjType=="REM":
                CompiledCode.append("; "+Action[0])
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])

            elif ObjType=="Function":
                AvailMacros=GetAvailMacros()
                MacroNames=[MacroName[0] for MacroName in AvailMacros]
                if Action[0] in MacroNames:
                    Action[0]='macro "'+Action[0]+'"'
                parameters=[]
                for parameter in Action[1]:
                    parameters.append(parameter)
                values=",".join(parameters)
                if len(values)>0:
                    values=" "+values
                CompiledCode.append(Action[0]+values)
                OptimizerCode.append([Object.GetValues(),Object.GetOptimizableParameters()])
                
            StepByStepOps.append([[*VolumesOfReactantsUsed],[*VolumesInApparatus],ObjType])
        #print(CompiledCode)
        #print(OptimizerCode)
        if GetCodeAndExit:
            return CompiledCode
        if GetOptimizerParameteraAndExit:
            return OptimizerCode
        if GetVolumesAndExit:
            return [ReactantsUsed,ApparatusUsed,StepByStepOps]
        if Phantom_Mode:
            return
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

    def LoadProcedures(filename):
        fin=open(filename, 'rb')
        ProceduresArray=pickle.load(fin)
        fin.close()
        CreatedProcedures=[]
        for Procedure in ProceduresArray:
            ObjType=Procedure[0]
            ObjValues=Procedure[1]
            ObjXPos=Procedure[2]
            ObjYPos=Procedure[3]
            Obj=CreateNewObject(ObjType)
            CreatedProcedures.append(Obj)
            Obj.SetValues(ObjValues)
            Obj.place(x=ObjXPos)
        for i,Procedure in enumerate(ProceduresArray):
            IsContainer=Procedure[4]
            ObjContent=Procedure[5]
            first=Procedure[6]
            last=Procedure[7]
            if IsContainer:
                if len(ObjContent)>0:
                    for Item in ObjContent:
                        CreatedProcedures[i].Content.append(CreatedProcedures[Item])
                if not(first==-1):
                    CreatedProcedures[i].First=CreatedProcedures[first]
                if not(last==-1):
                    CreatedProcedures[i].Last=CreatedProcedures[last]

    def AskLoadProcedures():
        global ActionsArray
        filename=ChooseProcedureFile()
        if filename=="": return
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('Load Procedures','By loading, current Procedures will be deleted. Proceed anyway?',icon = 'warning')
            if MsgBox == 'yes':
                DeleteAllProcedures()
            else:
                return
        LoadProcedures(filename)

    def AskImportProcedures():
        global ActionsArray
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('Append Procedures','Import Procedure will add Procedures to the current project. Proceed?',icon = 'warning')
            if MsgBox == 'yes':
                filetypes = (('SyringeBOT Procedure files', '*.Procedure'),('All files', '*.*'))
                filename = filedialog.askopenfilename(filetypes=filetypes)
                if filename=="": return
                LoadProcedures(filename)                

    def SaveProcedures(filename):
        Sorted=GetYStack()
        NumActions=len(Sorted)
        if NumActions==0: return
        #print(NumActions," Actions")
        ProceduresArray=[]
        for Action in Sorted:
            Actions=[]
            Object=Action[1]
            ObjType=str(Object.__class__.__name__)
            Actions.append(ObjType)            
            Actions.append(Object.GetValues())           
            Actions.append(Object.winfo_x())
            Actions.append(Object.winfo_y())
            try:
             if Object.IsContainer:
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
                    first=Object.First
                    Actions.append(GetObjectPosition(first.winfo_y(),Sorted))
                except:
                    Actions.append(-1)
                    pass
                try:
                    last=Object.Last
                    Actions.append(GetObjectPosition(last.winfo_y(),Sorted))
                except:
                    Actions.append(-1)
                    pass
             else:
                Actions.append(False)
                Actions.append([])                
                Actions.append(-1)
                Actions.append(-1)
            except:
                Actions.append(False)
                Actions.append([])                
                Actions.append(-1)
                Actions.append(-1)
                pass
            ProceduresArray.append(Actions)
        fout=open(filename, 'wb')
        pickle.dump(ProceduresArray,fout)
        fout.close()

    def AskSaveProcedures():
     filetypes=(('SyringeBOT Procedure files','*.Procedure'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes)
     if filename=="": return
     if not ".Procedure" in filename: filename+=".Procedure"
     SaveProcedures(filename)

    def Close():
        WizardWindow.destroy()

    def DeleteAllProcedures():
        global ActionsArray
        while len(ActionsArray)>0:
            DeleteObjByIdentifier(ActionsArray[0])
        ActionsArray=[]

    def New():
        global ActionsArray
        if len(ActionsArray)>0:
            MsgBox = tk.messagebox.askquestion ('New procedure','Are you sure you want to delete all?',icon = 'warning')
            if MsgBox == 'yes':
                DeleteAllProcedures()

    WizardWindow=tk.Toplevel(window)
    WizardWindow.title("CORRO WIZARD")
    WizardWindow.geometry('1000x800+400+10')
    WizardWindow.grab_set()
    menubar = Menu(WizardWindow)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='New',command=New)
    file_menu.add_separator()    
    file_menu.add_command(label='Load Procedure',command=AskLoadProcedures)
    file_menu.add_command(label='Append Procedure',command=AskImportProcedures)    
    file_menu.add_command(label='Save Procedure',command=AskSaveProcedures)
    file_menu.add_separator()
    file_menu.add_command(label='Exit',command=Close)
    WizardWindow.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)
    menubar.add_cascade(label="Process Check",command=CheckProcedure)
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
    WizardWindow.bind("<MouseWheel>", on_mousewheel)
    WizardWindow.bind("<Button-1>", drag_start_canvas)
    WizardWindow.bind("<B1-Motion>", drag_motion_canvas)
    WizardWindow.bind("<ButtonRelease-1>", on_mouse_up_canvas)

    frame2=tk.Frame(my_canvas,bg="white",height=10000,width=1000)
    frame2.pack()

    #Selection frame, composed by 4 stretched buttons
    pixel = PhotoImage(width=1, height=1)        
    SelTopButton = Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
    SelBottomButton = Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
    SelLeftButton = Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
    SelRightButton = Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
    
    my_canvas.create_window((0,0),window=frame2, anchor="nw")
    
    # Create a canvas inside the frame
    SelectionCanvas = Canvas(frame2,height=10000,width=1000,bg="white")
    SelectionCanvas.pack()

    tk.Button(frame1,text="Pour liquid",command=lambda: CreateNewObject("Pour")).pack(side="left")
    tk.Button(frame1,text="Heat reactor",command=lambda: CreateNewObject("Heat")).pack(side="left")
    tk.Button(frame1,text="Wash reactor",command=lambda: CreateNewObject("Wash")).pack(side="left")
    tk.Button(frame1,text="Wait",command=lambda: CreateNewObject("Wait")).pack(side="left")
    tk.Button(frame1,text="IF",command=lambda: CreateNewObject("IF Block")).pack(side="left")
    tk.Button(frame1,text="LOOP",command=lambda: CreateNewObject("LOOP Block")).pack(side="left")
    tk.Button(frame1,text="Comment",command=lambda: CreateNewObject("REM")).pack(side="left")
    tk.Button(frame1,text="Get Value",command=lambda: CreateNewObject("GET")).pack(side="left")
    tk.Button(frame1,text="Function",command=lambda: CreateNewObject("Function")).pack(side="left")        
##    tk.Button(frame1,text="L/L separation",command=lambda: CreateNewObject("Liq")).pack(side="left")
##    tk.Button(frame1,text="Evaporate solvent",command=lambda: CreateNewObject("Evap")).pack(side="left")
    tk.Button(frame1,text="Chromatography",command=lambda: CreateNewObject("Chrom")).pack(side="left")    
    tk.Button(frame1,text="Device ON/OFF",command=lambda: CreateNewObject("Switch")).pack(side="left")    
    tk.Button(frame1,text="Titrate",command=lambda: CreateNewObject("Titr")).pack(side="left")    

    tk.Button(frame3,text="Process Check",command=CheckProcedure).pack(side="left")

    Hidden=False
    filename=""
    for k, val in kwargs.items():
        if k=="Hide":
            Hidden=val
        elif k=="File":
            filename=val
    if filename:
        if Hidden:
            WizardWindow.withdraw()
        LoadProcedures(filename)
        CompiledCode=CheckProcedure(**kwargs)
        WizardWindow.destroy()
        return CompiledCode
    
    WizardWindow.mainloop()
