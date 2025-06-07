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
from tkinter import ttk, Menu, messagebox, filedialog
import pickle
import serial
import time
from modules.listserialports import *
from .serialmon import *

def InitAllData():
    global ReactantsArray, CurrentReactant, ApparatusArray, CurrentApparatus, DevicesArray, CurrentDevice
    global ValveOptions,CurrentSyringe,ValvesArray,SyringesArray,SyringeVolumes,SyringeInletVolumes,SyringeOutletVolumes,SyringemmToMax
    global DefaultDeviceParameters, PIDList, ThermoList, PowerList
    global USB_handles,USB_names,USB_deviceready,USB_ports,USB_baudrates,USB_types
    global USB_num_vars,USB_var_names,USB_var_points,USB_last_values,Sensors_var_names,Sensors_var_values
    ReactantsArray=[]
    CurrentReactant=1
    ValveOptions=["Not in use","Air/Waste"]
    CurrentSyringe=1
    SyringesArray=[]
    ValvesArray=[]
    SyringeVolumes=[]#60,10,60,10,60,10]
    SyringeInletVolumes=[]#10,10,10,10,10,10]
    SyringeOutletVolumes=[]#5,5,10,10,10,10]
    SyringemmToMax=[]#92.5,59,92.5,59,92.5,59]    
    ApparatusArray=[]
    CurrentApparatus=1
    DevicesArray=[]
    CurrentDevice=1
    DefaultDeviceParameters=["","","","","",True,"0",""]
    PIDList=["None","Heater 1","Heater 2"]
    ThermoList=["None","Thermocouple 1","Thermocouple 2"]
    PowerList=["None","BT channel 1","BT channel 2","BT channel 3","BT channel 4","BT channel 5","BT channel 6"]
    USB_handles=[]; USB_names=[]; USB_deviceready=[]; USB_ports=[]; USB_baudrates=[]; USB_types=[]
    USB_num_vars=[]; USB_var_names=[]; USB_var_points=[]; USB_last_values=[]; Sensors_var_names=[]; Sensors_var_values=[]

InitAllData()

def GetAllReactorApparatus():
    global ApparatusArray
    outlist=[]
    for apparatus in ApparatusArray:
        if "reactor" in apparatus[1]:
            outlist.append(apparatus[0])
    return outlist

def GetAllHeatingApparatus():
    global ApparatusArray
    outlist=[]
    for apparatus in ApparatusArray:
        if apparatus[1]=="Heated reactor":
            outlist.append(apparatus[0])
    return outlist

def GetMaxVolumeApparatus(Name):
    global ApparatusArray
    if Name[-1:]=="T": Name=Name[:-4] #removes OUT
    else: Name=Name[:-3] #removes IN
    try:    
       NamesArray=["Apparatus"+str(i+1)+": "+ApparatusArray[i][0] for i in range(len(ApparatusArray))]
       MaxVol=float(ApparatusArray[NamesArray.index(Name)][8])
    except:
       MaxVol=0.0
    return MaxVol

def GetMolarityOfInput(Name):
    global ReactantsArray
    try:    
       NamesArray=["Reactant"+str(i+1)+": "+ReactantsArray[i][0] for i in range(len(ReactantsArray))]
       Molarity=float(ReactantsArray[NamesArray.index(Name)][10].split(":")[1].split()[0])
    except:
       Molarity=0.0
    return Molarity

def GetMMOfInput(Name):
    global ReactantsArray
    try:    
       NamesArray=["Reactant"+str(i+1)+": "+ReactantsArray[i][0] for i in range(len(ReactantsArray))]
       MM=float(ReactantsArray[NamesArray.index(Name)][3])
    except:
       MM=0.0
    return MM

def ValvePositionFor(syr,name):
    global ValvesArray
    try:
       return (ValvesArray[int(syr)].index(name))
    except:
        print("ERROR Valvepos")
        return -1

def WhichSyringeIsConnectedTo(Name):
    value=[]
    for i, element in enumerate(ValvesArray):
        if Name in element:
            value.append(str(i))
    return value

def GetAllSyringeInputs():
    value=[]
    for Syringe, element in enumerate(ValvesArray):
      for Exit,connection in enumerate(element):
          if ("Reactant" in connection or ("Apparatus" in connection and "OUT" in connection)) and not connection in value:
            value.append(connection) #value.append([str(Syringe),str(Exit),connection])
    value.sort()        
    return value

def GetAllSyringeOutputs():
    value=[]
    for Syringe, element in enumerate(ValvesArray):
      for Exit,connection in enumerate(element):
          if ("Apparatus" in connection and "IN" in connection) and not connection in value:
            value.append(connection) #value.append([str(Syringe),str(Exit),connection])
    value.sort()        
    return value

def GetAllOutputsOfSyringe(num):
    value=[]
    for Exit,connection in enumerate(ValvesArray[num]):
      if ("Apparatus" in connection and "IN" in connection) or "Air/Waste" in connection: #and not connection in value???
        value.append([connection]) #value.append([str(Exit),connection])
    return value

def GetAllInputsOfSyringe(num):
    value=[]
    for Exit,connection in enumerate(ValvesArray[num]):
      if ("Reactant" in connection) and not connection in value:
        value.append([connection]) #value.append([str(Exit),connection])
    return value

def GetSyringeVolume(num):
    if num<len(SyringesArray):
        return SyringeVolumes[num]

def GetSyringeInletvolume(num):
    if num<len(SyringesArray):
        return SyringeInletVolumes[num]

def GetSyringeOutletvolume(num):
    if num<len(SyringesArray):
        return SyringeOutletVolumes[num]        

def GetReactantsNames():
    value=[]
    for element in ReactantsArray:
        value.append(element[0])
    return value

def ApparatusNames():
    value=[]
    for element in ApparatusArray:
        value.append(element[0])
    return value

def GetReactantsArray():
    return ReactantsArray

def GetApparatusArray():
    return ApparatusArray

def GetValvesArray():
    return ValvesArray

def SplitSyringesArray():
    global SyringesArray,ValvesArray,SyringeVolumes,SyringeInletVolumes,SyringeOutletVolumes,SyringemmToMax
    SyringeVolumes=[]
    SyringeInletVolumes=[]
    SyringeOutletVolumes=[]
    SyringemmToMax=[]
    ValvesArray=[]
    for element in SyringesArray:
        SyringeVolumes.append(element[0])
        SyringeInletVolumes.append(element[1])
        SyringeOutletVolumes.append(element[2])
        SyringemmToMax.append(element[3])
        ValvesArray.append(element[4:])

def SplitDevicesArray():
    global USB_handles,USB_names,USB_deviceready,USB_ports,USB_baudrates,USB_types
    global USB_num_vars,USB_var_names,USB_var_points,USB_last_values,Sensors_var_names,Sensors_var_values
    global DevicesArray
    for device in DevicesArray:
        DeviceName, DeviceType, DeviceUSB, USBBaudRate, Protocol, SensorEnabled, NumVariables, VarNames=device
        USB_names.append(DeviceName)
        USB_types.append(DeviceType)                
        USB_ports.append(DeviceUSB)
        USB_baudrates.append(USBBaudRate)
        USB_num_vars.append(int(NumVariables))
        USB_var_names.append(VarNames)
        USB_var_points.append([])
        USB_deviceready.append(SensorEnabled)

def LoadConfFile(filename):
    global ReactantsArray,SyringesArray,ApparatusArray,DevicesArray
    try:
     fin=open(filename, 'rb')
     ReactantsArray=pickle.load(fin)
     SyringesArray=pickle.load(fin)
     SplitSyringesArray()
     ApparatusArray=pickle.load(fin)
     DevicesArray=pickle.load(fin)
     SplitDevicesArray()
     fin.close()
    except Exception as e:
     print(e)
     messagebox.showerror("ERROR", "Cannot load "+filename)

def StartConfigurator(window):
    global ReactantsArray, CurrentReactant, ValveOptions, CurrentSyringe, ValvesArray, ApparatusArray, CurrentApparatus, DevicesArray, CurrentDevice
    global SyringeVolumes, SyringeInletVolumes, SyringeOutletVolumes, SyringemmToMax    
    global DefaultDeviceParameters, PIDList, ThermoList, PowerList    
    ConfiguratorWindow=tk.Toplevel(window)
    ConfiguratorWindow.title("CORRO CONFIGURATOR")
    ConfiguratorWindow.geometry('500x620+500+150')
    ConfiguratorWindow.grab_set()
    
    def Close():
      if NotSavedDataTab1() or NotSavedDataTab2() or NotSavedDataTab3():  
       MsgBox = tk.messagebox.askquestion ('Exit Configurator','Are you sure you want to exit configurator? Unsaved data are present',icon = 'warning')
      else:
       MsgBox="yes"
      if MsgBox == 'yes':  
       ConfiguratorWindow.destroy()
       
    ConfiguratorWindow.protocol("WM_DELETE_WINDOW", Close)

    def ShowData():
        global CurrentReactant,CurrentSyringe,CurrentApparatus,CurrentDevice
        global ReactantsArray,SyringesArray,ApparatusArray,DevicesArray
        CurrentReactant=1
        CurrentSyringe=1     
        CurrentApparatus=1
        CurrentDevice=1
        SetStatusNextPrevButtonsT1()
        SetStatusNextPrevButtonsT2()
        SetStatusNextPrevButtonsT3()
        SetStatusNextPrevButtonsT4()
        LoadReactantParameters()
        LoadSyringeParameters()
        LoadApparatusParameters()
        LoadDeviceParameters()
        a=len(ReactantsArray)
        if a==0: a=1
        HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(a))
        a=len(ApparatusArray)
        if a==0: a=1
        HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(a))
        a=len(SyringesArray)
        if a==0: a=1
        HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(a))
        a=len(DevicesArray)
        if a==0: a=1
        HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(a))
    
    def LoadAllData():
     global CurrentReactant,CurrentSyringe,CurrentApparatus,ReactantsArray,SyringesArray,ApparatusArray,DevicesArray
     if NotSavedDataTab1() or NotSavedDataTab2() or NotSavedDataTab3():
         MsgBox = tk.messagebox.askquestion ('Load Data','By loading data from file current data will be overwritten. Proceed?',icon = 'warning')
     else:
         MsgBox="yes"
     if MsgBox == 'yes':  
         filetypes = (('SyringeBOT configuration files', '*.conf'),('All files', '*.*'))
         filename = filedialog.askopenfilename(filetypes=filetypes)
         if filename=="": return
         LoadConfFile(filename)
         SetSyringeOptions()
         ShowData()

    def SaveAllData():
     filetypes=(('SyringeBOT cconfiguration files','*.conf'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes)
     if filename=="": return
     if not ".conf" in filename: filename+=".conf"
     fout=open(filename, 'wb')
     pickle.dump(ReactantsArray,fout)
     pickle.dump(SyringesArray,fout)
     pickle.dump(ApparatusArray,fout)
     pickle.dump(DevicesArray,fout)     
     fout.close()

    def ClearAllData():
     MsgBox = tk.messagebox.askquestion ('Clear Data','Current data will be overwritten. Proceed?',icon = 'warning')
     if MsgBox == 'yes':
         InitAllData()
         ShowData()
        
    menubar = Menu(ConfiguratorWindow)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='Open',command=LoadAllData)
    file_menu.add_command(label='Save',command=SaveAllData)
    file_menu.add_separator()
    file_menu.add_command(label='Clear all data',command=ClearAllData)
    file_menu.add_separator()    
    file_menu.add_command(label='Exit',command=Close)
    ConfiguratorWindow.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)

    def SetSyringeOptions():
        global ValveOptions
        ValveOptions=["Not in use","Air/Waste"]
        count=0
        for element in ReactantsArray:
            count+=1
            ValveOptions.append("Reactant"+str(count)+": "+element[0])
        count=0
        for element in ApparatusArray:
            count+=1
            name="Apparatus"+str(count)+": "+element[0]
            ValveOptions.append(name+" IN")
            ValveOptions.append(name+" OUT")
        exit1type.config(values=ValveOptions)
        exit2type.config(values=ValveOptions)
        exit3type.config(values=ValveOptions)
        exit4type.config(values=ValveOptions)
        exit5type.config(values=ValveOptions)


    def on_tab_selected(event):
        SelectedTabNum=event.widget.index(event.widget.select())
        if NotSavedDataTab1() and not SelectedTabNum==0:
            messagebox.showinfo(message="Unsaved data in Reactants tab")
            tabControl.select(0)
        if NotSavedDataTab2() and not SelectedTabNum==1:
            messagebox.showinfo(message="Unsaved data in Apparatus tab")
            tabControl.select(1)
        if NotSavedDataTab3() and not SelectedTabNum==2:
            messagebox.showinfo(message="Unsaved data in Syringe tab")
            tabControl.select(2)
        if NotSavedDataTab4() and not SelectedTabNum==3:
            messagebox.showinfo(message="Unsaved data in USB tab")
            tabControl.select(3)
            
        if SelectedTabNum==2: #Syringes tab
            SetSyringeOptions()
      

    tabControl = ttk.Notebook(ConfiguratorWindow)
    tabControl.bind("<<NotebookTabChanged>>", on_tab_selected)
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
      
    tabControl.add(tab1, text ='Reactants') 
    tabControl.add(tab2, text ='Apparatus')
    tabControl.add(tab3, text ='SyringeBOT')
    tabControl.add(tab4, text ='USB devices') 
    tabControl.pack(expand = 1, fill ="both")


    ##################   T A B 1   #############################################################
    def EnableDisableTab1():
        TypeOfReactant=ReactantType.get()
        if TypeOfReactant=="Pure liquid":
            purity.configure(state='normal')
            concentration.configure(state='disabled')
            ConcNumType.configure(state='disabled')
            ConcDenType.configure(state='disabled')    
        elif TypeOfReactant=="Solution":
            purity.configure(state='disabled')
            concentration.configure(state='normal')
            ConcNumType.configure(state='readonly')
            ConcDenType.configure(state='readonly')
        elif TypeOfReactant=="Solvent":
            purity.configure(state='disabled')
            concentration.configure(state='disabled')
            ConcNumType.configure(state='disabled')
            ConcDenType.configure(state='disabled')
        else:    
            purity.configure(state='normal')
            concentration.configure(state='normal')
            ConcNumType.configure(state='readonly')
            ConcDenType.configure(state='readonly')


    def ReactantTypecallback(eventObject):
        EnableDisableTab1()   

    def ConcNumTypecallback(eventObject):
        numerator=ConcNumType.get()
        denominator=ConcDenType.get()
        conclabel.config(text="Concentration ("+numerator+"/"+denominator+")")
        #print("Selected value ConcNumType:", numerator)

    def ConcDenTypecallback(eventObject):
        numerator=ConcNumType.get()
        denominator=ConcDenType.get()
        conclabel.config(text="Concentration ("+numerator+"/"+denominator+")")
        #print("Selected value ConcDenType:", ConcDenType.get())

    def CalcMW(formula):
        def AtomicMass(symbol):
            list="H HeLiBeB C N O F NeNaMgAlSiP S ClArK CaScTiV CrMnFeCoNiCuZnGaGeAsSeBrKrRbSrY ZrNbMoTcRuRhPdAgCdInSnSbTeI XeCsBaLaCePrNdPmSmEuGdTbDyHoErTmYbLuHfTaW ReOsIrPtAuHgTlPbBiPoAtRnFrRaAcThPaU NpPuAmCmBkCfEsFmMdNoLrRfDbSgBhHsMtDsRgCnNhFlMcLvTsOg"
            AM_array=[1.008,4.0026,6.94,9.0122,10.81,12.011,14.007,15.999,18.998,20.18,22.99,24.305,26.982,28.085,30.974,32.06,35.45,39.95,39.098,40.078,44.956,47.867,50.942,51.996,54.938,55.845,58.933,58.693,63.546,65.38,69.723,72.63,74.922,78.971,79.904,83.798,85.468,87.62,88.906,91.224,92.906,95.95,97,101.07,102.91,106.42,107.87,112.41,114.82,118.71,121.76,127.6,126.9,131.29,132.91,137.33,138.91,140.12,140.91,144.24,145,150.36,151.96,157.25,158.93,162.5,164.93,167.26,168.93,173.05,174.97,178.49,180.95,183.84,186.21,190.23,192.22,195.08,196.97,200.59,204.38,207.2,208.98,209,210,222,223,226,227,232.04,231.04,238.03,237,244,243,247,247,251,252,257,258,259,266,267,268,267,270,271,278,281,282,285,286,289,290,293,294,294]
            index = list.find(symbol)
            if index==-1 or not(index % 2==0):
                return 0
            else:
                if int(index/2)<len(AM_array):
                    return AM_array[int(index/2)]
                else:
                    return 0

        if len(formula)==0: return 0
        formula=formula.replace("[", "(")
        formula=formula.replace("]", ")")            
        closed_parentheses=formula.find(")")
        while not closed_parentheses==-1:
            cnt=closed_parentheses-1
            while cnt>0 and not formula[cnt]=="(":
                cnt-=1
            if not formula[cnt]=="(": return 0
            opened_parentheses=cnt
            i=closed_parentheses
            cx=""
            while ((i+1)<len(formula) and formula[i+1].isdigit()):
             i+=1         
             cx=cx+formula[i]
            if cx=="": cx=1
            substring=formula[opened_parentheses+1:closed_parentheses]
            substring=substring*int(cx)        
            formula=formula[0:opened_parentheses]+substring+formula[i+1:]
            closed_parentheses=formula.find(")")
        if not formula.find("(")==-1: return 0
        
        i=0
        MW=0
        while i<len(formula):
         symbol=formula[i]
         if symbol.isupper():
            if ((i+1)<len(formula) and formula[i+1].islower()):
              i+=1  
              symbol=symbol+formula[i]
         cx=""
         while ((i+1)<len(formula) and formula[i+1].isdigit()):
           i+=1         
           cx=cx+formula[i]
         if cx=="": cx=1  
         #print(symbol)
         #print(cx)
         MW+=AtomicMass(symbol)*int(cx)
         i+=1
        return MW

    def Try2CalculateMWfromFormula(eventObject):
        formula=rformula.get()
        if not formula=="":
         MM=CalcMW(formula)
         if not MM == 0:
          MW.delete(0,tk.END)  # Clear any existing text
          MW.insert(0,str(MM))  # Insert new text

    def Try2CalculateMolarity():
        TypeOfReactant=ReactantType.get()
        if TypeOfReactant=="Solution":
            value=concentration.get()
            UnitNum=ConcNumType.get()
            UnitDen=ConcDenType.get()
            if UnitNum=="" or UnitDen=="": return 0
            try:
                value=float(value)
                if value==0: return 0
                if UnitNum=="mmol":
                    value=value/1000
                if UnitNum=="g" or UnitNum=="mg":
                    if UnitNum=="mg":
                        value=value/1000
                    MM=float(MW.get())
                    if MM<1: return 0
                    value=value/MM
                #now value should be in moles/somethg
                if UnitDen=="L":
                    return value
                if UnitDen=="mL":
                    return value*1000
                if UnitDen=="100g":
                    den=float(density.get())              
                    return value*10*den
            except:
                return 0
        if TypeOfReactant=="Pure liquid":
            try:
             MM=float(MW.get())
             if MM<1: return 0
             pur=float(purity.get())
             den=float(density.get())
             return den*10/MM*pur
            except:
                return 0
        return 0

    def CheckReactantParameters():
        if ReactantName.get()=="":
            messagebox.showerror("ERROR", "Reactant name cannot be empty. Insert a valid name and retry.")
            return False
        if ReactantType.get()=="":
            messagebox.showerror("ERROR", "Reactant type cannot be empty. Insert a valid type and retry.")
            return False
        try:
         pur=float(purity.get())
         if pur<=0 or pur>100:
             raise Exception("purity should be in the range >0 .. <=100")
        except:  
            messagebox.showerror("ERROR", "Insert a valid purity value and retry.")
            return False
        try:
         den=float(density.get())
         if den<=0 or den>10:
             raise Exception("density should be in the range >0 .. <=10")
        except:  
            messagebox.showerror("ERROR", "Insert a valid density value and retry.")
            return False
        M=Try2CalculateMolarity()
        if M>0:
            molaritylabel.config(text="Calculated molarity: "+str(M)+" M")
        return True

    def SetTab1Variables(parms):
        purity.delete(0,tk.END)
        density.delete(0,tk.END)
        ReactantName.insert(0,parms[0])
        ReactantType.set(parms[1])
        rformula.insert(0,parms[2])
        MW.insert(0,parms[3])
        purity.insert(0,parms[4])
        conclabel.config(text=parms[5])
        concentration.insert(0,parms[6])
        ConcNumType.set(parms[7])
        ConcDenType.set(parms[8])
        density.insert(0,parms[9])
        molaritylabel.config(text=parms[10])
        EnableDisableTab1()   

    def AskLoadReactantParameters():
        global CurrentReactant
        answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
        if answer:
            LoadReactantParameters()
            
    def LoadReactantParameters():            
         ClearAllValuesT1()   
         if not(len(ReactantsArray)>CurrentReactant-1): return
         SetTab1Variables(ReactantsArray[CurrentReactant-1])

    def GetTab1Variables():
        return [ReactantName.get(),ReactantType.get(),rformula.get(),MW.get(),purity.get(),conclabel.cget("text"),concentration.get(),ConcNumType.get(),ConcDenType.get(),density.get(),molaritylabel.cget("text")]  

    def SaveReactantParameters():
        global CurrentReactant
        if CheckReactantParameters():
          newvalues=GetTab1Variables()
          if len(ReactantsArray)==CurrentReactant-1:  
           ReactantsArray.append(newvalues)
          elif NotSavedDataTab1():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current reactant?")
           if answer:
            if not ReactantName.get()==ReactantsArray[CurrentReactant-1][0]: #Reactant name has changed, we have to update the ValvesArray
                UpdateEntryFromValvesArray(ReactantsArray[CurrentReactant-1][0],CurrentReactant,"Reactant"+str(CurrentReactant)+": "+ReactantName.get(),"Reactant")           
            ReactantsArray[CurrentReactant-1]=newvalues

    def ClearAllValuesT1():
          ReactantName.delete(0,tk.END)
          ReactantType.set("")
          rformula.delete(0,tk.END)
          MW.delete(0,tk.END)
          purity.delete(0,tk.END)
          purity.insert(0,"100")
          conclabel.config(text ="Concentration")
          concentration.delete(0,tk.END)
          ConcNumType.set("")
          ConcDenType.set("")
          density.delete(0,tk.END)
          density.insert(0,"1")
          molaritylabel.config(text="---")
          EnableDisableTab1()

    def SetStatusNextPrevButtonsT1():
        global CurrentReactant
        if CurrentReactant-1>0:
            PrevT1Button.configure(state='enabled')
        else:
            PrevT1Button.configure(state='disabled')
        if CurrentReactant<len(ReactantsArray):
            NextT1Button.configure(state='enabled')
        else:
            NextT1Button.configure(state='disabled')
            

    def ClearReactantParameters():
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete all parameters inserted?")
        if answer: ClearAllValuesT1()

    def Tab1HavingDefaultValues():
        return GetTab1Variables()==['', '', '', '', '100', 'Concentration', '', '', '', '1', '---']

    def NotSavedDataTab1():
        global CurrentReactant
        if len(ReactantsArray)==CurrentReactant-1:
         if Tab1HavingDefaultValues():
               return False
         else: return True
        return not(GetTab1Variables()==ReactantsArray[CurrentReactant-1])

    def AddReactant():
        global CurrentReactant
        if len(ReactantsArray)==CurrentReactant-1:
            messagebox.showinfo(message="Finish first to edit the current reagent")
            return
        if NotSavedDataTab1():
            messagebox.showinfo(message="Unsaved data for the current reagent")
            return
        CurrentReactant=len(ReactantsArray)+1
        HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(CurrentReactant))
        ClearAllValuesT1()
        SetStatusNextPrevButtonsT1()

    def UpdateEntryFromValvesArray(Item,position,NewValue,EntryType):
        global ValvesArray
        Item=EntryType+str(position)+": "+Item # EntryType should be Reactant or Apparatus
        for element in ValvesArray:
          for i, n in enumerate(element):
           if EntryType=="Apparatus":
            if n==Item+" IN":
              element[i]=NewValue+" IN"
            elif n==Item+" OUT":
              element[i]=NewValue+" OUT"
           else:    
            if n==Item:
              element[i]=NewValue
        SetTab3Variables(ValvesArray[CurrentSyringe-1])      
           

    def DeleteCurrentReactant():
        global CurrentReactant
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current reactant?")
        if answer:
         ClearAllValuesT1()
         if CurrentReactant>len(ReactantsArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentReactant==1:
                 return
             else:
                 CurrentReactant-=1
                 HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(CurrentReactant))
                 SetTab1Variables(ReactantsArray[CurrentReactant-1])
         else:
             UpdateEntryFromValvesArray(ReactantsArray[CurrentReactant-1][0],CurrentReactant,"Not in use","Reactant")
             del ReactantsArray[CurrentReactant-1]
             if CurrentReactant>len(ReactantsArray): #we deleted the first and only reactant
                 HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(CurrentReactant))
             else:    
                 HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(len(ReactantsArray)))
                 SetTab1Variables(ReactantsArray[CurrentReactant-1])
         SetStatusNextPrevButtonsT1()
        

    def NextT1():
        global CurrentReactant
        if NotSavedDataTab1():
         messagebox.showinfo(message="Finish first to edit the current reagent")
         return
        CurrentReactant+=1
        HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(len(ReactantsArray)))
        ClearAllValuesT1()
        SetTab1Variables(ReactantsArray[CurrentReactant-1])
        SetStatusNextPrevButtonsT1()
        

    def PrevT1():
        global CurrentReactant
        if NotSavedDataTab1():
         messagebox.showinfo(message="Finish first to edit the current reagent")
         return
        CurrentReactant-=1
        HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(len(ReactantsArray)))
        ClearAllValuesT1()
        SetTab1Variables(ReactantsArray[CurrentReactant-1])
        SetStatusNextPrevButtonsT1()

    F1T1 = ttk.Frame(tab1); F1T1.pack()    
    PrevT1Button=ttk.Button(F1T1, text="Prev", command=PrevT1,state='disabled'); PrevT1Button.pack(side="left")
    NextT1Button=ttk.Button(F1T1, text="Next", command=NextT1,state='disabled'); NextT1Button.pack(side="left")
    HeaderLabelT1=ttk.Label(tab1,text ="Reactant n. 1 of 1",font=("Arial", 12)); HeaderLabelT1.pack(pady="10");
    ttk.Label(tab1,text ="Reactant Name").pack(); ReactantName=ttk.Entry(tab1); ReactantName.pack(); 
    ttk.Label(tab1,text ="Reactant Type").pack(); ReactantType=ttk.Combobox(tab1, values = ('Solution','Solvent','Pure liquid'), state = 'readonly'); ReactantType.pack(); ReactantType.bind("<<ComboboxSelected>>", ReactantTypecallback)
    ttk.Label(tab1,text ="Chemical formula").pack(); rformula=ttk.Entry(tab1); rformula.pack(); 
    ttk.Label(tab1,text ="Molecular Mass").pack(); MW=ttk.Entry(tab1); MW.pack(); MW.bind("<Button-1>", Try2CalculateMWfromFormula)
    ttk.Label(tab1,text ="Purity %").pack(); purity=ttk.Entry(tab1); purity.insert(0, '100'); purity.pack(); 
    conclabel=ttk.Label(tab1,text ="Concentration"); conclabel.pack(); concentration=ttk.Entry(tab1); concentration.pack(); 
    ttk.Label(tab1,text ="Concentration units (numerator)").pack(); ConcNumType=ttk.Combobox(tab1, values = ('g', 'mg', 'mol', 'mmol'), state = 'readonly'); ConcNumType.pack(); ConcNumType.bind("<<ComboboxSelected>>", ConcNumTypecallback)
    ttk.Label(tab1,text ="Concentration units (denominator)").pack(); ConcDenType=ttk.Combobox(tab1, values = ('L', 'mL','100g'), state = 'readonly'); ConcDenType.pack(); ConcDenType.bind("<<ComboboxSelected>>", ConcDenTypecallback)
    ttk.Label(tab1,text ="Density (g/mL)").pack(); density=ttk.Entry(tab1); density.insert(0, '1'); density.pack(); 
    molaritylabel=ttk.Label(tab1,text ="---"); molaritylabel.pack();
    F2T1 = ttk.Frame(tab1); F2T1.pack(pady="10")
    F3T1 = ttk.Frame(tab1); F3T1.pack()
    ttk.Button(F2T1, text="Check values", command=CheckReactantParameters).pack(side="left")
    ttk.Button(F2T1, text="Save changes", command=SaveReactantParameters).pack(side="left")
    ttk.Button(F2T1, text="Ignore changes", command=AskLoadReactantParameters).pack(side="left")
    ttk.Button(F2T1, text="Clear all values", command=ClearReactantParameters).pack(side="left")
    ttk.Button(F3T1, text="Add new Reactant", command=AddReactant).pack(side="left")
    ttk.Button(F3T1, text="Remove Reactant", command=DeleteCurrentReactant).pack(side="left")

    ##################   E N D   O F   T A B  1   #############################################################

    def CheckApparatusParameters(avoid):
        if ApparatusName.get()=="":
            messagebox.showerror("ERROR", "Apparatus name cannot be empty. Insert a valid name and retry.")
            return False
        if ApparatusType.get()=="":
            messagebox.showerror("ERROR", "Apparatus type cannot be empty. Insert a valid type and retry.")
            return False
        InUseThermo=""
        InUseHeater=""
        InUseBT=""
        i=0
        for element in ApparatusArray:
            if not(i==avoid-1):
             InUseThermo+=element[2]
             InUseHeater+=element[3]
             InUseBT+=element[4]+element[5]+element[6]
            i+=1 
        item=thermo.get()
        if not(item=="None") and item in InUseThermo:
                messagebox.showerror("ERROR", "Thermocouple "+item+" already used in other apparatus")
                return False
        item=heated.get()
        if not(item=="None") and item in InUseHeater:
                messagebox.showerror("ERROR", "Heather connection "+item+" already used in other apparatus")
                return False
        testarray=[]
        item=stirred.get()
        if not(item=="None"):
            testarray.append(item)
            if item in InUseBT:
                messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
                return False
        item=onoff.get()
        if not(item=="None"):
            if item in InUseBT:
                messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
                return False
            if item in testarray:
                messagebox.showerror("ERROR", "Cannot use the same BT connection for more devices.")
                return False
            testarray.append(item)
        item=otheronoff.get()
        if not(item=="None"):
            if item in InUseBT:
                messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
                return False
            if item in testarray:
                messagebox.showerror("ERROR", "Cannot use the same BT connection for more devices.")
                return False
        return True

    def EnableDisableTab2():
        return

    def SetTab2Variables(parms):
        ApparatusName.insert(0,parms[0])
        ApparatusType.set(parms[1])
        thermo.set(parms[2])
        heated.set(parms[3])
        stirred.set(parms[4])
        onoff.set(parms[5])
        otheronoff.set(parms[6])
        minvol.insert(0,parms[7])
        maxvol.insert(0,parms[8])
        maxinputs.delete(0,tk.END)
        maxinputs.insert(0,parms[9])
        maxoutputs.delete(0,tk.END)
        maxoutputs.insert(0,parms[10])
        EnableDisableTab2()   

    def AskLoadApparatusParameters():
        global CurrentApparatus
        answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
        if answer:
            LoadApparatusParameters()
            
    def LoadApparatusParameters():            
         ClearAllValuesT2()   
         if not(len(ApparatusArray)>CurrentApparatus-1): return
         SetTab2Variables(ApparatusArray[CurrentApparatus-1])

    def GetTab2Variables():
        return [ApparatusName.get(),ApparatusType.get(),thermo.get(),heated.get(),stirred.get(),onoff.get(),otheronoff.get(),minvol.get(),maxvol.get(),maxinputs.get(),maxoutputs.get()]

    def SaveApparatusParameters():
        global CurrentApparatus
        if CheckApparatusParameters(CurrentApparatus):
          newvalues=GetTab2Variables()
          if len(ApparatusArray)==CurrentApparatus-1:  
           ApparatusArray.append(newvalues)
          elif NotSavedDataTab2():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Apparatus?")
           if answer:
            if not ApparatusName.get()==ApparatusArray[CurrentApparatus-1][0]: #Apparatus name has changed, we have to update the ValvesArray
                UpdateEntryFromValvesArray(ApparatusArray[CurrentApparatus-1][0],CurrentApparatus,"Apparatus"+str(CurrentApparatus)+": "+ApparatusName.get(),"Apparatus")           
            ApparatusArray[CurrentApparatus-1]=newvalues

    def ClearAllValuesT2():
          ApparatusName.delete(0,tk.END)
          ApparatusType.set("")
          thermo.set("None")
          heated.set("None")
          stirred.set("None")
          onoff.set("None")
          otheronoff.set("None")
          minvol.delete(0,tk.END)
          maxvol.delete(0,tk.END)
          maxinputs.delete(0,tk.END)
          maxinputs.insert(0,"1")
          maxoutputs.delete(0,tk.END)
          maxoutputs.insert(0,"1")
          EnableDisableTab2()

    def SetStatusNextPrevButtonsT2():
        global CurrentApparatus
        if CurrentApparatus-1>0:
            PrevT2Button.configure(state='enabled')
        else:
            PrevT2Button.configure(state='disabled')
        if CurrentApparatus<len(ApparatusArray):
            NextT2Button.configure(state='enabled')
        else:
            NextT2Button.configure(state='disabled')
            
    def ClearApparatusParameters():
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete all parameters inserted?")
        if answer: ClearAllValuesT2()

    def Tab2HavingDefaultValues():
        return GetTab2Variables()==['', '', 'None', 'None', 'None', 'None', 'None', '', '', '1', '1']

    def NotSavedDataTab2():
        global CurrentApparatus
        if len(ApparatusArray)==CurrentApparatus-1:
         if Tab2HavingDefaultValues():
               print("1")
               return False
         else:
             print("2")
             return True
        print("3")    
        return not(GetTab2Variables()==ApparatusArray[CurrentApparatus-1])    

    def AddApparatus():
        global CurrentApparatus
        if len(ApparatusArray)==CurrentApparatus-1:
            messagebox.showinfo(message="Finish first to edit the current apparatus")
            return
        if NotSavedDataTab2():
            messagebox.showinfo(message="Unsaved data for the current apparatus")
            return
        CurrentApparatus=len(ApparatusArray)+1
        HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(CurrentApparatus))
        ClearAllValuesT2()
        SetStatusNextPrevButtonsT2()

    def DeleteCurrentApparatus():
        global CurrentApparatus
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Apparatus?")
        if answer:
         ClearAllValuesT2()
         if CurrentApparatus>len(ApparatusArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentApparatus==1:
                 return
             else:
                 CurrentApparatus-=1
                 HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(CurrentApparatus))
                 SetTab2Variables(ApparatusArray[CurrentApparatus-1])
         else:
             UpdateEntryFromValvesArray(ApparatusArray[CurrentApparatus-1][0],CurrentApparatus,"Not in use","Apparatus")
             del ApparatusArray[CurrentApparatus-1]
             if CurrentApparatus>len(ApparatusArray): #we deleted the first and only Apparatus
                 HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(CurrentApparatus))
             else:    
                 HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(len(ApparatusArray)))
                 SetTab2Variables(ApparatusArray[CurrentApparatus-1])
         SetStatusNextPrevButtonsT2()
        
    def ApparatusTypeCallback(eventObject):
      EnableDisableTab2()

    def NextT2():
        global CurrentApparatus
        if NotSavedDataTab2():
         messagebox.showinfo(message="Finish first to edit the current apparatus")
         return
        CurrentApparatus+=1
        HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(len(ApparatusArray)))
        ClearAllValuesT2()
        SetTab2Variables(ApparatusArray[CurrentApparatus-1])
        SetStatusNextPrevButtonsT2()
        
    def PrevT2():
        global CurrentApparatus
        if NotSavedDataTab2():
         messagebox.showinfo(message="Finish first to edit the current apparatus")
         return
        CurrentApparatus-=1
        HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(len(ApparatusArray)))
        ClearAllValuesT2()
        SetTab2Variables(ApparatusArray[CurrentApparatus-1])
        SetStatusNextPrevButtonsT2()
     
    F1T2 = ttk.Frame(tab2); F1T2.pack()
    PrevT2Button=ttk.Button(F1T2, text="Prev", command=PrevT2,state='disabled'); PrevT2Button.pack(side="left")
    NextT2Button=ttk.Button(F1T2, text="Next", command=NextT2,state='disabled'); NextT2Button.pack(side="left")
    HeaderLabelT2=ttk.Label(tab2,text ="Apparatus n. 1 of 1",font=("Arial", 12)); HeaderLabelT2.pack(pady="10");
    ttk.Label(tab2,text ="Name").pack(); ApparatusName=ttk.Entry(tab2); ApparatusName.pack()
    ttk.Label(tab2,text ="Type").pack(); ApparatusType=ttk.Combobox(tab2, values = ("Heated reactor","Non heated reactor","Chromatographic column","Liquid/liquid separator","Photo reactor","Flow reactor","Other"), state = "readonly")
    ApparatusType.pack(); ApparatusType.bind("<<ComboboxSelected>>", ApparatusTypeCallback)
    ttk.Label(tab2,text ="Thermocouple connection").pack(); thermo=ttk.Combobox(tab2, values = ThermoList, state = "readonly"); thermo.current(0); thermo.pack() 
    ttk.Label(tab2,text ="Heater connection").pack(); heated=ttk.Combobox(tab2, values = PIDList, state = "readonly"); heated.current(0); heated.pack()
    ttk.Label(tab2,text ="Stirrer connection").pack(); stirred=ttk.Combobox(tab2, values = PowerList, state = "readonly"); stirred.current(0); stirred.pack()
    ttk.Label(tab2,text ="Power ON/OFF connection").pack(); onoff=ttk.Combobox(tab2, values = PowerList, state = "readonly"); onoff.current(0); onoff.pack()
    ttk.Label(tab2,text ="Other ON/OFF connection").pack(); otheronoff=ttk.Combobox(tab2, values = PowerList, state = "readonly"); otheronoff.current(0); otheronoff.pack()    
    ttk.Label(tab2,text ="Min. volume (mL)").pack(); minvol=ttk.Entry(tab2); minvol.pack()
    ttk.Label(tab2,text ="Max. volume (mL)").pack(); maxvol=ttk.Entry(tab2); maxvol.pack()
    ttk.Label(tab2,text ="Number of inputs:").pack(); maxinputs=tk.Spinbox(tab2, from_=1, to=10, repeatdelay=500, repeatinterval=200); maxinputs.pack()
    ttk.Label(tab2,text ="Number of outputs:").pack(); maxoutputs=tk.Spinbox(tab2, from_=0, to=10, repeatdelay=500, repeatinterval=200); maxoutputs.pack()
    maxoutputs.delete(0,tk.END)
    maxoutputs.insert(0,"1")
    F2T2 = ttk.Frame(tab2); F2T2.pack(pady="10")
    F3T2 = ttk.Frame(tab2); F3T2.pack()
    ttk.Button(F2T2, text="Save changes", command=SaveApparatusParameters).pack(side="left")
    ttk.Button(F2T2, text="Ignore changes", command=AskLoadApparatusParameters).pack(side="left")
    ttk.Button(F2T2, text="Clear all values", command=ClearApparatusParameters).pack(side="left")
    ttk.Button(F3T2, text="Add new Apparatus", command=AddApparatus).pack(side="left")
    ttk.Button(F3T2, text="Remove Apparatus", command=DeleteCurrentApparatus).pack(side="left")


    def NotSavedDataTab3():
        global CurrentSyringe
        if len(SyringesArray)==CurrentSyringe-1:
            return False
        return not(SyringesArray[CurrentSyringe-1]==GetTab3Variables())
        
    def GetTab3Variables():
        return [maxvolsyr.get(), mmtomax.get(), inletvol.get(), outletvol.get(), exit1type.get(), exit2type.get(), exit3type.get(), exit4type.get(), exit5type.get()]  

    def SetTab3Variables(parms):
        global CurrentSyringe
        maxvolsyr.delete(0,tk.END); maxvolsyr.insert(0,str(parms[0]))
        mmtomax.delete(0,tk.END); mmtomax.insert(0,str(parms[1]))
        inletvol.delete(0,tk.END); inletvol.insert(0,str(parms[2]))
        outletvol.delete(0,tk.END); outletvol.insert(0,str(parms[3]))
        exit1type.set(parms[4])
        exit2type.set(parms[5])
        exit3type.set(parms[6])
        exit4type.set(parms[7])
        exit5type.set(parms[8])

    def SetStatusNextPrevButtonsT3():
        global CurrentSyringe
        if CurrentSyringe-1>0:
            PrevT3Button.configure(state='enabled')
        else:
            PrevT3Button.configure(state='disabled')
        if CurrentSyringe<len(SyringesArray):
            NextT3Button.configure(state='enabled')
        else:
            NextT3Button.configure(state='disabled')        

    def LoadSyringeParameters():
        global CurrentSyringe
        SetTab3Variables(SyringesArray[CurrentSyringe-1])
        
    def SaveSyringeParameters():
        global CurrentSyringe
        #if NotSavedDataTab3():
        SyringeConnections=GetTab3Variables()
        for i,element in enumerate(SyringeConnections[:3]):
            try:
                a=float(element)
                if a<0:
                    messagebox.showerror("ERROR", "values must be >0")
                    return
                if a==0 and i<2:
                    messagebox.showerror("ERROR", "volumes and mm must be <>0")
                    return
            except:
                messagebox.showerror("ERROR", "Insert a valid floating numbers")
                return
        if "Air/Waste" not in SyringeConnections:
            messagebox.showerror("ERROR", "One exit MUST BE Air/Waste")
            return
        for i,Connection in enumerate(SyringeConnections[4:]):
             if not(Connection=="Not in use") and Connection in SyringeConnections[i+5:]:
                  messagebox.showerror("ERROR", "Duplicated connection: "+Connection)
                  return
        if len(SyringesArray)==CurrentSyringe-1:  
           SyringesArray.append(SyringeConnections)
        else:   
           SyringesArray[CurrentSyringe-1]=SyringeConnections    

    def NextT3():
        global CurrentSyringe
        if NotSavedDataTab3():
         messagebox.showinfo(message="Finish first to edit the current syringe")
         return
        CurrentSyringe+=1
        HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(len(SyringesArray)))
        SetTab3Variables(SyringesArray[CurrentSyringe-1])
        SetStatusNextPrevButtonsT3()
        
    def PrevT3():
        global CurrentSyringe
        if NotSavedDataTab3():
         messagebox.showinfo(message="Finish first to edit the current syringe")
         return
        CurrentSyringe-=1
        HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(len(SyringesArray)))
        SetTab3Variables(SyringesArray[CurrentSyringe-1])
        SetStatusNextPrevButtonsT3()

    def ClearSyringeParameters():
        SetTab3Variables([0,0,0,0]+[ValveOptions[1 if i==0 else 0] for i in range(5)])

    def AddSyringe():
        global CurrentSyringe 
        if len(SyringesArray)==CurrentSyringe-1:
            messagebox.showinfo(message="Finish first to edit the current Syringe")
            return
        if NotSavedDataTab3():
            messagebox.showinfo(message="Unsaved data for the current Syringe")
            return
        CurrentSyringe=len(SyringesArray)+1
        HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(CurrentSyringe))
        ClearSyringeParameters()
        SetStatusNextPrevButtonsT3()

    def DeleteCurrentSyringe(): 
        global CurrentSyringe
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Syringe?")
        if answer:
         ClearSyringeParameters()
         if CurrentSyringe>len(SyringesArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentSyringe==1:
                 return
             else:
                 CurrentSyringe-=1
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(CurrentSyringe))
                 SetTab3Variables(SyringesArray[CurrentSyringe-1])
         else:
             del SyringesArray[CurrentSyringe-1]
             if CurrentSyringe>len(SyringesArray): #we deleted the first and only Syringe
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(CurrentSyringe))
             else:    
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(len(SyringesArray)))
                 SetTab3Variables(SyringesArray[CurrentSyringe-1])
         SetStatusNextPrevButtonsT3()        
        
    
    F1T3 = ttk.Frame(tab3); F1T3.pack()
    PrevT3Button=ttk.Button(F1T3, text="Prev", command=PrevT3,state='disabled'); PrevT3Button.pack(side="left")
    NextT3Button=ttk.Button(F1T3, text="Next", command=NextT3,state='disabled'); NextT3Button.pack(side="left")
    HeaderLabelT3=ttk.Label(tab3,text ="Syringe n. 1 of 1",font=("Arial", 12)); HeaderLabelT3.pack(pady="10");
    #ttk.Label(tab3,text ="Type").pack(); pumptype=ttk.Combobox(tab3, values = ("Syringe","Peristaltic"), state = 'readonly',width=25); pumptype.current(0); pumptype.pack()     
    ttk.Label(tab3,text ="Max. volume (mL)").pack(); maxvolsyr=ttk.Entry(tab3); maxvolsyr.pack(); maxvolsyr.delete(0,tk.END); maxvolsyr.insert(0,"0")
    ttk.Label(tab3,text ="0 to max sign distance (mm)").pack(); mmtomax=ttk.Entry(tab3); mmtomax.pack(); mmtomax.delete(0,tk.END); mmtomax.insert(0,"0")
    ttk.Label(tab3,text ="Inlet tube volume (mL)").pack(); inletvol=ttk.Entry(tab3); inletvol.pack(); inletvol.delete(0,tk.END); inletvol.insert(0,"0")
    ttk.Label(tab3,text ="Outlet tube volume (mL)").pack(); outletvol=ttk.Entry(tab3); outletvol.pack(); outletvol.delete(0,tk.END); outletvol.insert(0,"0")
    #ttk.Label(tab3,text ="Max. speed (mL/min)").pack(); maxspeed=ttk.Entry(tab3); maxspeed.pack()
    ttk.Label(tab3,text ="Valve exit n.1").pack(); exit1type=ttk.Combobox(tab3, values = ValveOptions, state = 'readonly',width=25); exit1type.current(1); exit1type.pack() 
    ttk.Label(tab3,text ="Valve exit n.2").pack(); exit2type=ttk.Combobox(tab3, values = ValveOptions, state = 'readonly',width=25); exit2type.current(0); exit2type.pack()
    ttk.Label(tab3,text ="Valve exit n.3").pack(); exit3type=ttk.Combobox(tab3, values = ValveOptions, state = 'readonly',width=25); exit3type.current(0); exit3type.pack()
    ttk.Label(tab3,text ="Valve exit n.4").pack(); exit4type=ttk.Combobox(tab3, values = ValveOptions, state = 'readonly',width=25); exit4type.current(0); exit4type.pack()
    ttk.Label(tab3,text ="Valve exit n.5").pack(); exit5type=ttk.Combobox(tab3, values = ValveOptions, state = 'readonly',width=25); exit5type.current(0); exit5type.pack()
    F2T3 = ttk.Frame(tab3); F2T3.pack(pady="10")
    F3T3 = ttk.Frame(tab3); F3T3.pack(pady="10")    
    ttk.Button(F2T3, text="Save changes", command=SaveSyringeParameters).pack(side="left")
    ttk.Button(F2T3, text="Ignore changes", command=LoadSyringeParameters).pack(side="left")
    ttk.Button(F3T3, text="Add new Syringe", command=AddSyringe).pack(side="left")
    ttk.Button(F3T3, text="Remove Syringe", command=DeleteCurrentSyringe).pack(side="left")    
   
    def GetTab4Variables():
        return [DeviceName.get(), DeviceType.get(), DeviceUSB.get(), USBBaudRate.get(), Protocol.get(), SensorEnabled.get(), NumVariables.get(), VarNames.get()]

    def SetTab4Variables(parms):
        DeviceName.delete(0,tk.END); DeviceName.insert(0,str(parms[0]))
        DeviceType.set(parms[1])
        DeviceUSB.set(parms[2])
        USBBaudRate.set(parms[3])
        Protocol.set(parms[4])
        SensorEnabled=parms[5]
        DevEnabled.select()
        NumVariables.delete(0,tk.END); NumVariables.insert(0,str(parms[6]))
        VarNames.delete(0,tk.END); VarNames.insert(0,str(parms[7]))

    def LoadDeviceParameters():
         if not(len(DevicesArray)>CurrentDevice-1): return
         SetTab4Variables(DevicesArray[CurrentDevice-1])

    def SaveDeviceParameters():
        global CurrentDevice
        if CheckDeviceParameters():
          newvalues=GetTab4Variables()
          if len(DevicesArray)==CurrentDevice-1:  
           DevicesArray.append(newvalues)
          elif NotSavedDataTab4():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Device?")
           if answer:
            DevicesArray[CurrentDevice-1]=newvalues

    def AskLoadDeviceParameters():
        global CurrentDevice
        answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
        if answer:
            LoadDeviceParameters()        
    
    def ClearDeviceParameters():
        global DefaultDeviceParameters
        SetTab4Variables(DefaultDeviceParameters)

    def AddDevice():
        global CurrentDevice 
        if len(DevicesArray)==CurrentDevice-1:
            messagebox.showinfo(message="Finish first to edit the current Device")
            return
        if NotSavedDataTab4():
            messagebox.showinfo(message="Unsaved data for the current Device")
            return
        CurrentDevice=len(DevicesArray)+1
        HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(CurrentDevice))
        ClearDeviceParameters()
        SetStatusNextPrevButtonsT4()

    def DeleteCurrentDevice(): 
        global CurrentDevice
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Device?")
        if answer:
         ClearDeviceParameters()
         if CurrentDevice>len(DevicesArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentDevice==1:
                 return
             else:
                 CurrentDevice-=1
                 HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(CurrentDevice))
                 SetTab4Variables(DevicesArray[CurrentDevice-1])
         else:
             del DevicesArray[CurrentDevice-1]
             if CurrentDevice>len(DevicesArray): #we deleted the first and only Device
                 HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(CurrentDevice))
             else:    
                 HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(len(DevicesArray)))
                 SetTab4Variables(DevicesArray[CurrentDevice-1])
         SetStatusNextPrevButtonsT4()

    def NotSavedDataTab4():
        global CurrentDevice,DefaultDeviceParameters
        if len(DevicesArray)==CurrentDevice-1:
         if GetTab4Variables()==DefaultDeviceParameters:
               return False
         else: return True
        return not(GetTab4Variables()==DevicesArray[CurrentDevice-1])        

    def CheckDeviceParameters():
        global CurrentDevice
        parms=GetTab4Variables()
        try:
            numvariables=int(parms[6])
        except:
            messagebox.showerror("ERROR", "Number of variables must be an integer")
            return False
        if parms[0]=="":
            messagebox.showerror("ERROR", "Device name cannot be empty. Insert a valid name and retry.")
            return False
        if parms[1]=="" or parms[2]=="" or parms[3]=="" or parms[4]=="":
            messagebox.showerror("ERROR", "Device connection parameters cannot be empty.")
            return False
        if parms[1]=="Sensor" and (parms[6]==0 or parms[7]==""):
            messagebox.showerror("ERROR", "Number of variables to read or variable name cannot be empty")
            return False
        if "Read" in parms[4] and (numvariables>0 and parms[7]==""):
            messagebox.showerror("ERROR", "Cannot read a variable without having a name assigned")
            return False
        for i,element in enumerate(DevicesArray):
            if  not i==CurrentDevice-1:
                if parms[0] in element:
                    messagebox.showerror("ERROR", "Name already in use")
                    return False
                if parms[2] in element:
                    messagebox.showerror("ERROR", "Port "+str(parms[2])+" already in use")
                    return False
        return True

    def DeviceTypecallback(eventObject):
        print(Protocol.get())
        if "Read" in Protocol.get():
            NumVariables.config(state="normal")
            VarNames.config(state="normal")
        else:
            NumVariables.config(state="disabled")
            VarNames.config(state="disabled")
            
    def SetStatusNextPrevButtonsT4():
        global CurrentDevice
        if CurrentDevice-1>0:
            PrevT4Button.configure(state='enabled')
        else:
            PrevT4Button.configure(state='disabled')
        if CurrentDevice<len(DevicesArray):
            NextT4Button.configure(state='enabled')
        else:
            NextT4Button.configure(state='disabled')        

    def NextT4():
        global CurrentDevice
        if NotSavedDataTab4():
         messagebox.showinfo(message="Finish first to edit the current device")
         return
        CurrentDevice+=1
        HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(len(DevicesArray)))
        SetTab4Variables(DevicesArray[CurrentDevice-1])
        SetStatusNextPrevButtonsT4()
        
    def PrevT4():
        global CurrentDevice
        if NotSavedDataTab4():
         messagebox.showinfo(message="Finish first to edit the current device")
         return
        CurrentDevice-=1
        HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(len(DevicesArray)))
        SetTab4Variables(DevicesArray[CurrentDevice-1])
        SetStatusNextPrevButtonsT4()

    def Try2Connect():
        data_str=""
        try:
            parms=GetTab4Variables()
            if parms[2]=="" or parms[3]=="": return
            app = SerialMon(ConfiguratorWindow,parms[2],parms[3])
            #Test=serial.Serial(parms[2],parms[3])
            #time.sleep(0.5)
        except:
            messagebox.showerror("ERROR", "Cannot connect")

    def RefreshUSB():
        DeviceUSB.config(values=AvailableSerialPorts())

    F1T4 = ttk.Frame(tab4); F1T4.pack()    
    PrevT4Button=ttk.Button(F1T4, text="Prev", command=PrevT4,state='disabled'); PrevT4Button.pack(side="left")
    NextT4Button=ttk.Button(F1T4, text="Next", command=NextT4,state='disabled'); NextT4Button.pack(side="left")
    HeaderLabelT4=ttk.Label(tab4,text ="USB device n. 1 of 1",font=("Arial", 12)); HeaderLabelT4.pack(pady="10");
    ttk.Label(tab4,text ="Device Name").pack(); DeviceName=ttk.Entry(tab4); DeviceName.pack();
    ttk.Label(tab4,text ="Device type").pack(); DeviceType=ttk.Combobox(tab4, values = ("SyringeBOT","Sensor","Robot"), state = 'readonly'); DeviceType.pack(); 
    ttk.Label(tab4,text ="Device USB").pack(); DeviceUSB=ttk.Combobox(tab4, values = AvailableSerialPorts()); DeviceUSB.pack(); #DeviceUSB.bind("<<ComboboxSelected>>", ReactantTypecallback)
    ttk.Label(tab4,text ="USB Baudrate").pack(); USBBaudRate=ttk.Combobox(tab4, values =("9600", "14400", "19200", "28800", "38400", "56000", "57600", "115200", "128000", "250000", "256000")); USBBaudRate.pack();
    protlabel=ttk.Label(tab4,text ="Protocol"); protlabel.pack(); Protocol=ttk.Combobox(tab4, values =("Readonly","Read/Write","Writeonly"),state="readonly"); Protocol.pack(); Protocol.bind("<<ComboboxSelected>>", DeviceTypecallback)
    SensorEnabled=tk.BooleanVar(value=True); DevEnabled=tk.Checkbutton(tab4,text="Device enabled",variable=SensorEnabled); DevEnabled.select(); DevEnabled.pack()
    ttk.Label(tab4,text ="Num. of Variables to read").pack(); NumVariables=tk.Spinbox(tab4, from_=0, to=10000, repeatdelay=500, repeatinterval=200); NumVariables.pack()
    ttk.Label(tab4,text ="Variable names (base name or comma separated)").pack(); VarNames=ttk.Entry(tab4); VarNames.pack(); 
    USBlabel=ttk.Label(tab4,text ="---"); USBlabel.pack();
    F2T4 = ttk.Frame(tab4); F2T4.pack()
    F3T4 = ttk.Frame(tab4); F3T4.pack()
    F4T4 = ttk.Frame(tab4); F4T4.pack(pady="10")
    ttk.Button(F2T4, text="Save changes", command=SaveDeviceParameters).pack(side="left")
    ttk.Button(F2T4, text="Ignore changes", command=AskLoadDeviceParameters).pack(side="left")
    ttk.Button(F2T4, text="Clear all values", command=ClearDeviceParameters).pack(side="left")
    ttk.Button(F3T4, text="TEST", command=Try2Connect).pack(side="left")
    ttk.Button(F3T4, text="Rescan USB", command=RefreshUSB).pack(side="left")
    ttk.Button(F4T4, text="Add new Device", command=AddDevice).pack(side="left")
    ttk.Button(F4T4, text="Remove Device", command=DeleteCurrentDevice).pack(side="left")

    LoadConfFile('startup.conf')
    SetSyringeOptions()
    ShowData()      
    #ConfiguratorWindow.mainloop()
