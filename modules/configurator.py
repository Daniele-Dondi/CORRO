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
import os
from modules.listserialports import AvailableSerialPorts
from .serialmon import SerialMon
from .shelly import TurnShellyPlugON, TurnShellyPlugOFF
from .showstream import CameraPopup

def InitAllData():
    global ReactantsArray, CurrentReactant, ApparatusArray, CurrentApparatus, DevicesArray, CurrentDevice
    global ValveOptions,CurrentSyringe,ValvesArray,SyringesArray,SyringeVolumes,SyringeInletVolumes,SyringeOutletVolumes,SyringemmToMax
    global DefaultDeviceParameters, PIDList, ThermoList, PowerList
    global USB_names,USB_deviceready,USB_ports,USB_baudrates,USB_types
    global USB_num_vars,USB_var_names,USB_var_points,USB_last_values,Sensors_var_names,Sensors_var_values
    global PlugsArray,CurrentPlug,DefaultPlugParameters
    global CurrentFileName
    global FileIsModified
    global DefaultConfigurationFile
    global CamerasArray, CurrentCamera, FileIsModified, DefaultCameraParameters

    CamerasArray = []
    CurrentCamera = 1
    FileIsModified = False
    DefaultCameraParameters = ["", "IPCam", "", True, "http://default-stream", "http://default-control"]    

    DefaultConfigurationFile=os.path.join("conf", "default.conf")
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
    PlugsArray=[]
    CurrentPlug=1
    DefaultDeviceParameters=["","","","","",True,"0",""]
    DefaultPlugParameters=["","","",True,"/relay/0?turn=on","/relay/0?turn=off"]
    PIDList=["None","Heater 1","Heater 2"]
    ThermoList=["None","Thermocouple 1","Thermocouple 2"]
    PowerList=["None","BT channel 1","BT channel 2","BT channel 3","BT channel 4","BT channel 5","BT channel 6"]
    USB_names=[]; USB_deviceready=[]; USB_ports=[]; USB_baudrates=[]; USB_types=[]
    USB_num_vars=[]; USB_var_names=[]; USB_var_points=[]; USB_last_values=[]; Sensors_var_names=[]; Sensors_var_values=[]
    CurrentFileName=""
    FileIsModified=False

InitAllData()

def GetPlugNames():
    global PlugsArray #[PlugName.get(), PlugType.get(), Plug_IP.get(), PlugDefaultParms.get(), PlugCommandON.get(), PlugCommandOFF.get()]
    PlugList=[]
    for element in PlugsArray:
        PlugList.append(element[0])
    return PlugList

def GetPlugIPFromName(plug_name):
    global PlugsArray
    plug_names=GetPlugNames()
    if plug_name in plug_names:
        return PlugsArray[plug_names.index(plug_name)][2]
    else:
        return -1

def TurnPlugON(plug_name):
    IP=GetPlugIPFromName(plug_name)
    if IP==-1:
        return "ERROR: plug "+plug_name+" not found"
    return TurnShellyPlugON(IP)

def TurnPlugOFF(plug_name):
    IP=GetPlugIPFromName(plug_name)
    if IP==-1:
        return "ERROR: plug "+plug_name+" not found"
    return TurnShellyPlugOFF(IP)

def GetAllSensorsVarNames():
    return " ".join(USB_var_names).split()

def GetAllReactorApparatus():
    global ApparatusArray
    outlist=[]
    for apparatus in ApparatusArray:
        if "reactor" in apparatus[1]:
            outlist.append(apparatus[0])
##    if len(outlist)==0:
##        messagebox.showinfo(message="It looks like no Apparatus are connected to SyringeBOT.\nPlease run Configurator.")            
    return outlist

def GetAllHeatingApparatus():
    global ApparatusArray
    outlist=[]
    for apparatus in ApparatusArray:
        if apparatus[1]=="Heated reactor":
            outlist.append(apparatus[0])
##    if len(outlist)==0:
##        messagebox.showinfo(message="It looks like no Heating apparatus are connected to SyringeBOT.\nPlease run Configurator.")            
    return outlist

def GetMaxVolumeApparatus(Name):
    global ApparatusArray
    if Name[-1:]=="T": Name=Name[:-4] #removes OUT
    else: Name=Name[:-3] #removes IN
    try:    
       NamesArray=["Apparatus: "+ApparatusArray[i][0] for i in range(len(ApparatusArray))]
       MaxVol=float(ApparatusArray[NamesArray.index(Name)][5])
    except:
       MaxVol=0.0
    return MaxVol

def GetMolarityOfInput(Name):
    global ReactantsArray
    try:    
       NamesArray=["Reactant: "+ReactantsArray[i][0] for i in range(len(ReactantsArray))]
       Molarity=float(ReactantsArray[NamesArray.index(Name)][10].split(":")[1].split()[0])
    except:
       Molarity=0.0
    return Molarity

def GetMMOfInput(Name):
    global ReactantsArray
    try:    
       NamesArray=["Reactant: "+ReactantsArray[i][0] for i in range(len(ReactantsArray))]
       MM=float(ReactantsArray[NamesArray.index(Name)][3])
    except:
       MM=0.0
    return MM

def ValvePositionFor(syr,name):
    global ValvesArray
    try:
       return (ValvesArray[int(syr)].index(name))
    except Exception as e:
        print(e)
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
##    if len(value)==0:
##        messagebox.showinfo(message="It looks like syringes are not connected to any chemicals.\nPlease run Configurator.")
    return value

def GetAllSyringeOutputs():
    value=[]
    for Syringe, element in enumerate(ValvesArray):
      for Exit,connection in enumerate(element):
          if ("Apparatus" in connection and "IN" in connection) and not connection in value:
            value.append(connection) #value.append([str(Syringe),str(Exit),connection])
    value.sort()
##    if len(value)==0:
##        messagebox.showinfo(message="It looks like syringes are not connected to any outputs.\nPlease run Configurator.")
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
        value.append(connection) #value.append([str(Exit),connection])
    return value

def GetAllConnectionsOfSyringe(num):
    return ValvesArray[num]

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
        value.append("Reactant: "+element[0])
    return value

def GetApparatusNames():
    value=[]
    for element in ApparatusArray:
        value.append("Apparatus: "+element[0])
    return value

def GetReactantsArray():
    return ReactantsArray

def GetApparatusArray():
    return ApparatusArray

def GetValvesArray():
    return ValvesArray

def SplitSyringesArray():
    global SyringesArray,ValvesArray,SyringeVolumes,SyringeInletVolumes,SyringeOutletVolumes,SyringemmToMax
    for element in SyringesArray:
        SyringeVolumes.append(element[0])
        SyringemmToMax.append(element[1])        
        SyringeInletVolumes.append(element[2])
        SyringeOutletVolumes.append(element[3])
        ValvesArray.append(element[4:])

def SplitDevicesArray():
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
        USB_last_values.append(("0.0 "*int(NumVariables)).strip())

def LoadConfFile(filename=DefaultConfigurationFile):
    global ReactantsArray,SyringesArray,ApparatusArray,DevicesArray,PlugsArray,CamerasArray
    global CurrentFileName
    global DefaultConfiguration
    #DefaultConfigurationFile="conf/default.conf"
    if filename=="": filename=DefaultConfiguration
    InitAllData()
    try:
     fin=open(filename, 'rb')
     ReactantsArray=pickle.load(fin)
     SyringesArray=pickle.load(fin)
     SplitSyringesArray()
     ApparatusArray=pickle.load(fin)
     DevicesArray=pickle.load(fin)
     SplitDevicesArray()
     PlugsArray=pickle.load(fin)
     CamerasArray=pickle.load(fin)
     fin.close()
    except Exception as e:
     print(e)
     messagebox.showerror("ERROR", "Cannot load "+filename+"\nCreate the correct configuration in order to use CORRO")
     CurrentFileName=DefaultConfigurationFile
    else:
     CurrentFileName=filename

def StartConfigurator(window):
    global ReactantsArray, CurrentReactant, ValveOptions, CurrentSyringe, ValvesArray, ApparatusArray, CurrentApparatus, DevicesArray, CurrentDevice
    global SyringeVolumes, SyringeInletVolumes, SyringeOutletVolumes, SyringemmToMax    
    global DefaultDeviceParameters, PIDList, ThermoList, PowerList    
    ConfiguratorWindow=tk.Toplevel(window)
    ConfiguratorWindow.title("CORRO CONFIGURATOR")
    ConfiguratorWindow.geometry('500x620+500+150')
    ConfiguratorWindow.grab_set()
    ConfiguratorWindow.wm_iconphoto(True, tk.PhotoImage(file='icons/configurator.png'))
    
    def Close():
      if NotSavedDataTab1() or NotSavedDataTab2() or NotSavedDataTab3() or FileIsModified:  
       MsgBox = tk.messagebox.askquestion ('Exit Configurator','Are you sure you want to exit configurator? Unsaved data are present',icon = 'warning')
      else:
       MsgBox="yes"
      if MsgBox == 'yes':  
       ConfiguratorWindow.destroy()
       
    ConfiguratorWindow.protocol("WM_DELETE_WINDOW", Close)

    def SetTabAndVars(ObjectArray,CurrentObject,SetNextPrevButtons,LoadObjectParm,Header,ObjName):
        CurrentObject=1
        SetNextPrevButtons()
        LoadObjectParm()
        a=len(ObjectArray)
        if a==0: a=1
        Header.config(text=ObjName+" n. "+str(CurrentObject)+" of "+str(a))

    def ShowData():
        global CurrentReactant,CurrentSyringe,CurrentApparatus,CurrentDevice,PlugsArray,CurrentPlug
        global ReactantsArray,SyringesArray,ApparatusArray,DevicesArray,CamerasArray,CurrentCamera
        SetTabAndVars(ReactantsArray, CurrentReactant,  SetStatusNextPrevButtonsT1,  LoadReactantParameters,  HeaderLabelT1, "Reactant")
        SetTabAndVars(ApparatusArray, CurrentApparatus, SetStatusNextPrevButtonsT2,  LoadApparatusParameters, HeaderLabelT2, "Apparatus")
        SetTabAndVars(SyringesArray,  CurrentSyringe,   SetStatusNextPrevButtonsT3,  LoadSyringeParameters,   HeaderLabelT3, "Syringe")
        SetTabAndVars(DevicesArray,   CurrentDevice,    SetStatusNextPrevButtonsT4,  LoadDeviceParameters,    HeaderLabelT4, "Device")
        SetTabAndVars(PlugsArray,     CurrentPlug,      SetStatusNextPrevButtonsT5,  LoadPlugParameters,      HeaderLabelT5, "Plug")
        SetTabAndVars(CamerasArray,   CurrentCamera,    SetStatusNextPrevButtonsCam, LoadCameraParameters,    HeaderLabelCam, "Camera")
        
    
    def LoadAllData():
     global CurrentReactant,CurrentSyringe,CurrentApparatus,ReactantsArray,SyringesArray,ApparatusArray,DevicesArray
     if NotSavedDataTab1() or NotSavedDataTab2() or NotSavedDataTab3():
         MsgBox = tk.messagebox.askquestion ('Load Data','By loading data from file current data will be overwritten. Proceed?',icon = 'warning')
     else:
         MsgBox="yes"
     if MsgBox == 'yes':  
         filetypes = (('SyringeBOT configuration files', '*.conf'),('All files', '*.*'))
         filename = filedialog.askopenfilename(filetypes=filetypes,initialdir="conf")
         if filename=="": return
         LoadConfFile(filename)
         SetSyringeOptions()
         ShowData()

    def SaveConfFile(filename):
     global CurrentFileName,FileIsModified
     try:
      fout=open(filename, 'wb')
      pickle.dump(ReactantsArray,fout)
      pickle.dump(SyringesArray,fout)
      pickle.dump(ApparatusArray,fout)
      pickle.dump(DevicesArray,fout)
      pickle.dump(PlugsArray,fout)
      pickle.dump(CamerasArray,fout)
      fout.close()
     except Exception as e:
      print(e)
      messagebox.showerror("ERROR", "Cannot save "+filename)
     else:
      CurrentFileName=filename
      FileIsModified=False

    def SaveData():
        SaveConfFile(CurrentFileName)

    def SaveAndExit():
        SaveConfFile(CurrentFileName)
        Close()
         
    def SaveAsData():
     filetypes=(('SyringeBOT cconfiguration files','*.conf'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes,initialdir="conf")
     if filename=="": return
     if not filename[-5:]==".conf": filename+=".conf"
     SaveConfFile(filename)

    def ClearAllData():
     MsgBox = tk.messagebox.askquestion ('Clear Data','Current data will be overwritten. Proceed?',icon = 'warning')
     if MsgBox == 'yes':
         InitAllData()
         ShowData()
        
    menubar = Menu(ConfiguratorWindow)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='Open',command=LoadAllData)
    file_menu.add_command(label='Save',command=SaveData)
    file_menu.add_command(label='Save & Exit',command=SaveAndExit)
    file_menu.add_command(label='Save As',command=SaveAsData)
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
            #ValveOptions.append("Reactant"+str(count)+": "+element[0])
            ValveOptions.append("Reactant: "+element[0])
        count=0
        for element in ApparatusArray:
            count+=1
            #name="Apparatus"+str(count)+": "+element[0]
            name="Apparatus: "+element[0]
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
    tab5 = ttk.Frame(tabControl)
    tab6 = ttk.Frame(tabControl)
      
    tabControl.add(tab1, text ='Reactants') 
    tabControl.add(tab2, text ='Apparatus')
    tabControl.add(tab3, text ='SyringeBOT')
    tabControl.add(tab4, text ='USB devices')
    tabControl.add(tab5, text ='Smart Plugs')
    tabControl.add(tab6, text ='IP Cameras') 
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

    def FormatNumber(num):
        # Define thresholds for scientific notation
        lower_threshold = 0.01
        upper_threshold = 1000
        if num < lower_threshold or num > upper_threshold:
            # Use scientific notation
            return f"{num:.2e}"
        else:
            # Use two decimal places
            return f"{num:.2f}"

    def CheckReactantParameters():
        global ReactantsArray,CurrentReactant
        Name=ReactantName.get()
        if Name=="":
            messagebox.showerror("ERROR", "Reactant name cannot be empty. Insert a valid name and retry.")
            return False
        for R_num,Reactant in enumerate(ReactantsArray):
         if Name in Reactant:
          if not(R_num==CurrentReactant-1):
             messagebox.showerror("ERROR", "Duplicated reactant name.")
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
            molaritylabel.config(text="Calculated molarity: "+FormatNumber(M)+" M")
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
        global CurrentReactant,FileIsModified
        if CheckReactantParameters():
          newvalues=GetTab1Variables()
          if len(ReactantsArray)==CurrentReactant-1:  
           ReactantsArray.append(newvalues)
           FileIsModified=True
          elif NotSavedDataTab1():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current reactant?")
           if answer:
            FileIsModified=True   
            if not ReactantName.get()==ReactantsArray[CurrentReactant-1][0]: #Reactant name has changed, we have to update the ValvesArray
                #UpdateEntryFromValvesArray(ReactantsArray[CurrentReactant-1][0],CurrentReactant,"Reactant"+str(CurrentReactant)+": "+ReactantName.get(),"Reactant")
                UpdateEntryFromValvesArray(ReactantsArray[CurrentReactant-1][0],CurrentReactant,"Reactant: "+ReactantName.get(),"Reactant")           
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
        global SyringesArray
        #Item=EntryType+str(position)+": "+Item # EntryType should be Reactant or Apparatus
        Item=EntryType+": "+Item # EntryType should be Reactant or Apparatus
        for element in SyringesArray:
          for i, n in enumerate(element):
           if EntryType=="Apparatus":
            if n==Item+" IN":
              element[i]=NewValue+" IN"
            elif n==Item+" OUT":
              element[i]=NewValue+" OUT"
           else:    
            if n==Item:
              element[i]=NewValue
        SetTab3Variables(SyringesArray[CurrentSyringe-1])      
           

    def DeleteCurrentReactant():
        global CurrentReactant,FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current reactant?")
        if answer:
         ClearAllValuesT1()
         FileIsModified=True
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
             FileIsModified=True
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

    ##################   T A B 2   #############################################################

    def CheckApparatusParameters(avoid):
        Name=ApparatusName.get()
        if Name=="":
            messagebox.showerror("ERROR", "Apparatus name cannot be empty. Insert a valid name and retry.")
            return False
        for A_Name in ApparatusArray:
         if Name in A_Name[0]:
            messagebox.showerror("ERROR", "Duplicated apparatus name.")
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
#
        # item=stirred.get()
        # if not(item=="None"):
        #     testarray.append(item)
        #     if item in InUseBT:
        #         messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
        #         return False
        # item=onoff.get()
        # if not(item=="None"):
        #     if item in InUseBT:
        #         messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
        #         return False
        #     if item in testarray:
        #         messagebox.showerror("ERROR", "Cannot use the same BT connection for more devices.")
        #         return False
        #     testarray.append(item)
        # item=otheronoff.get()
        # if not(item=="None"):
        #     if item in InUseBT:
        #         messagebox.showerror("ERROR", "Connection "+item+" already used in other apparatus")
        #         return False
        #     if item in testarray:
        #         messagebox.showerror("ERROR", "Cannot use the same BT connection for more devices.")
        #         return False
        return True

    def EnableDisableTab2():
        return

    def SetTab2Variables(parms):
        ApparatusName.insert(0,parms[0])
        ApparatusType.set(parms[1])
        thermo.set(parms[2])
        heated.set(parms[3])
        minvol.insert(0,parms[4])
        maxvol.insert(0,parms[5])
        maxinputs.delete(0,tk.END)
        maxinputs.insert(0,parms[6])
        maxoutputs.delete(0,tk.END)
        maxoutputs.insert(0,parms[7])
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
        return [ApparatusName.get(),ApparatusType.get(),thermo.get(),heated.get(),minvol.get(),maxvol.get(),maxinputs.get(),maxoutputs.get()]

    def SaveApparatusParameters():
        global CurrentApparatus,FileIsModified
        if CheckApparatusParameters(CurrentApparatus):
          newvalues=GetTab2Variables()
          if len(ApparatusArray)==CurrentApparatus-1:  
           ApparatusArray.append(newvalues)
           FileIsModified=True
          elif NotSavedDataTab2():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Apparatus?")
           if answer:
            FileIsModified=True   
            if not ApparatusName.get()==ApparatusArray[CurrentApparatus-1][0]: #Apparatus name has changed, we have to update the ValvesArray
                #UpdateEntryFromValvesArray(ApparatusArray[CurrentApparatus-1][0],CurrentApparatus,"Apparatus"+str(CurrentApparatus)+": "+ApparatusName.get(),"Apparatus")
                UpdateEntryFromValvesArray(ApparatusArray[CurrentApparatus-1][0],CurrentApparatus,"Apparatus: "+ApparatusName.get(),"Apparatus")           
            ApparatusArray[CurrentApparatus-1]=newvalues

    def ClearAllValuesT2():
          ApparatusName.delete(0,tk.END)
          ApparatusType.set("")
          thermo.set("None")
          heated.set("None")
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
        return GetTab2Variables()==['', '', 'None', 'None', '', '', '1', '1']

    def NotSavedDataTab2():
        global CurrentApparatus
        if len(ApparatusArray)==CurrentApparatus-1:
         if Tab2HavingDefaultValues():
               return False
         else:
             return True
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
        global CurrentApparatus,FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Apparatus?")
        if answer:
         ClearAllValuesT2()
         FileIsModified=True
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
             FileIsModified=True
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

    ##################   T A B 3   #############################################################
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
        if not(len(SyringesArray)>CurrentSyringe-1): return
        SetTab3Variables(SyringesArray[CurrentSyringe-1])
        
    def SaveSyringeParameters():
        global CurrentSyringe,FileIsModified
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
        FileIsModified=True        
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
        global CurrentSyringe,FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Syringe?")
        if answer:
         ClearSyringeParameters()
         FileIsModified=True
         if CurrentSyringe>len(SyringesArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentSyringe==1:
                 return
             else:
                 CurrentSyringe-=1
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(CurrentSyringe))
                 SetTab3Variables(SyringesArray[CurrentSyringe-1])
         else:
             del SyringesArray[CurrentSyringe-1]
             FileIsModified=True
             if CurrentSyringe>len(SyringesArray): #we deleted the first and only Syringe
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(CurrentSyringe))
             else:    
                 HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(len(SyringesArray)))
                 SetTab3Variables(SyringesArray[CurrentSyringe-1])
         SetStatusNextPrevButtonsT3()        
        
    
    F1T3 = ttk.Frame(tab3); F1T3.pack()
    PrevT3Button=ttk.Button(F1T3, text="Prev", command=PrevT3,state='disabled'); PrevT3Button.pack(side="left")
    NextT3Button=ttk.Button(F1T3, text="Next", command=NextT3,state='disabled'); NextT3Button.pack(side="left")
    HeaderLabelT3=ttk.Label(tab3,text ="Pump n. 1 of 1",font=("Arial", 12)); HeaderLabelT3.pack(pady="10");
    ttk.Label(tab3,text ="Pump Type").pack(); pumptype=ttk.Combobox(tab3, values = ("Not used","Syringe","Peristaltic"), state = 'readonly',width=25); pumptype.current(1); pumptype.pack()     
    ttk.Label(tab3,text ="Valve Type").pack(); valvetype=ttk.Combobox(tab3, values = ("No valves","2 servos, 3 exits","2 servos, 4 exits","1 servo, 5 exits"), state = 'readonly',width=25); valvetype.current(2); valvetype.pack()
    ttk.Label(tab3,text ="Valve Start Address").pack(); valveaddr=ttk.Combobox(tab3, values=tuple(str(i) for i in range(13)), state = 'readonly',width=25); valveaddr.current(2); valveaddr.pack()     
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

    ##################   T A B 4   #############################################################
   
    def GetTab4Variables():
        return [DeviceName.get(), DeviceType.get(), DeviceUSB.get(), USBBaudRate.get(), Protocol.get(), SensorEnabled.get(), NumVariables.get(), VarNames.get()]

    def SetTab4Variables(parms):
        DeviceName.delete(0,tk.END); DeviceName.insert(0,str(parms[0]))
        DeviceType.set(parms[1])
        DeviceUSB.set(parms[2])
        USBBaudRate.set(parms[3])
        Protocol.set(parms[4])
        SensorEnabled.set(parms[5])
        DevEnabled.update()
        NumVariables.delete(0,tk.END); NumVariables.insert(0,str(parms[6]))
        NumVariables.update()
        VarNames.delete(0,tk.END); VarNames.insert(0,str(parms[7]))
        VarNames.update()

    def LoadDeviceParameters():
         global DevicesArray,CurrentDevice
         if not(len(DevicesArray)>CurrentDevice-1): return         
         tabControl.unbind("<<NotebookTabChanged>>")
         SetTab4Variables(DevicesArray[CurrentDevice-1])
         tabControl.bind("<<NotebookTabChanged>>", on_tab_selected)
         

    def SaveDeviceParameters():
        global CurrentDevice,FileIsModified
        if CheckDeviceParameters():
          newvalues=GetTab4Variables()
          if len(DevicesArray)==CurrentDevice-1:  
           DevicesArray.append(newvalues)
           FileIsModified=True
          elif NotSavedDataTab4():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Device?")
           if answer:
            DevicesArray[CurrentDevice-1]=newvalues
            FileIsModified=True

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
        global CurrentDevice,FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Device?")
        if answer:
         ClearDeviceParameters()
         FileIsModified=True
         if CurrentDevice>len(DevicesArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentDevice==1:
                 return
             else:
                 CurrentDevice-=1
                 HeaderLabelT4.config(text="Device n. "+str(CurrentDevice)+" of "+str(CurrentDevice))
                 SetTab4Variables(DevicesArray[CurrentDevice-1])
         else:
             del DevicesArray[CurrentDevice-1]
             FileIsModified=True
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
         else:
             return True
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
#
        try:
            parms=GetTab4Variables()
            if parms[2]=="" or parms[3]=="": return
            SerialMon(ConfiguratorWindow,parms[2],parms[3])
            #Test=serial.Serial(parms[2],parms[3])
            #time.sleep(0.5)
        except Exception as e:
            print(e)
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
    SensorEnabled=tk.BooleanVar(); SensorEnabled.set(True); DevEnabled=tk.Checkbutton(tab4,text="Device enabled",variable=SensorEnabled); DevEnabled.pack()
    ttk.Label(tab4,text ="Num. of Variables to read").pack(); NumVariables=tk.Spinbox(tab4, from_=0, to=10000, repeatdelay=500, repeatinterval=200); NumVariables.pack()
    ttk.Label(tab4,text ="Variable names (base name or space separated)").pack(); VarNames=ttk.Entry(tab4); VarNames.pack(); 
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

#########################################
    def GetTab5Variables():
        return [PlugName.get(), PlugType.get(), Plug_IP.get(), PlugDefaultParms.get(), PlugCommandON.get(), PlugCommandOFF.get()]

    def SetTab5Variables(parms):
        PlugName.delete(0,tk.END); PlugName.insert(0,str(parms[0]))
        PlugType.set(parms[1])
        Plug_IP.delete(0,tk.END); Plug_IP.insert(0,str(parms[2]))
        PlugDefaultParms.set(parms[3])
        PlgEnabled.update()
        PlugCommandON.delete(0,tk.END); PlugCommandON.insert(0,str(parms[4]))
        PlugCommandON.update()
        PlugCommandOFF.delete(0,tk.END); PlugCommandOFF.insert(0,str(parms[5]))
        PlugCommandOFF.update()

    def LoadPlugParameters():
         global PlugsArray,CurrentPlug
         if (len(PlugsArray)<CurrentPlug-1): return
         tabControl.unbind("<<NotebookTabChanged>>")
         SetTab5Variables(PlugsArray[CurrentPlug-1])
         tabControl.bind("<<NotebookTabChanged>>", on_tab_selected)
         
    def SavePlugParameters():
        global CurrentPlug,FileIsModified
        if CheckPlugParameters():
          newvalues=GetTab5Variables()
          if len(PlugsArray)==CurrentPlug-1:  
           PlugsArray.append(newvalues)
           FileIsModified=True
          elif NotSavedDataTab5():
           answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Plug?")
           if answer:
            PlugsArray[CurrentPlug-1]=newvalues
            FileIsModified=True

    def AskLoadPlugParameters():
        global CurrentPlug
        answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
        if answer:
            LoadPlugParameters()        
    
    def ClearPlugParameters():
        global DefaultPlugParameters
        SetTab5Variables(DefaultPlugParameters)

    def AddPlug():
        global CurrentPlug,PlugsArray 
        if len(PlugsArray)==CurrentPlug-1:
            messagebox.showinfo(message="Finish first to edit the current Plug")
            return
        if NotSavedDataTab5():
            messagebox.showinfo(message="Unsaved data for the current Plug")
            return
        CurrentPlug=len(PlugsArray)+1
        HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(CurrentPlug))
        ClearPlugParameters()
        SetStatusNextPrevButtonsT5()

    def DeleteCurrentPlug(): 
        global CurrentPlug,FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Plug?")
        if answer:
         ClearPlugParameters()
         FileIsModified=True
         if CurrentPlug>len(PlugsArray): #we have the number but still it is not saved in the array. So the array is shorter
             if CurrentPlug==1:
                 return
             else:
                 CurrentPlug-=1
                 HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(CurrentPlug))
                 SetTab5Variables(PlugsArray[CurrentPlug-1])
         else:
             del PlugsArray[CurrentPlug-1]
             FileIsModified=True
             if CurrentPlug>len(PlugsArray): #we deleted the first and only Plug
                 HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(CurrentPlug))
             else:    
                 HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(len(PlugsArray)))
                 SetTab5Variables(PlugsArray[CurrentPlug-1])
         SetStatusNextPrevButtonsT5()

    def NotSavedDataTab5():
        global CurrentPlug,DefaultPlugParameters
        if len(PlugsArray)==CurrentPlug-1:
         if GetTab5Variables()==DefaultPlugParameters:
               return False
         else:
             return True
        return not(GetTab5Variables()==PlugsArray[CurrentPlug-1])        

    def CheckPlugParameters():
        global CurrentPlug,PlugsArray
        parms=GetTab5Variables()
        if parms[0]=="":
            messagebox.showerror("ERROR", "Plug name cannot be empty. Insert a valid name and retry.")
            return False
        if parms[1]=="":
            messagebox.showerror("ERROR", "Plug type cannot be empty.")
            return False
        if parms[2]=="":
            messagebox.showerror("ERROR", "IP address cannot be empty.")
            return False
        if Is_Valid_IP(str(parms[2]))==False:
            messagebox.showerror("ERROR", str(parms[2])+" is not a valid IP address")
            return False
        if (parms[3]==False and( parms[4]=="" or parms[5]=="")):
            messagebox.showerror("ERROR", "Plug parameters cannot be empty if parameters are not default.")
            return False
        for i,element in enumerate(PlugsArray):
            if  not i==CurrentPlug-1:
                if parms[0] in element:
                    messagebox.showerror("ERROR", "Name already in use")
                    return False
                if parms[2] in element:
                    messagebox.showerror("ERROR", "IP "+str(parms[2])+" already in use")
                    return False
        return True

    def PlugTypecallback(eventObject):
        global DefaultPlugParameters
        if PlugType.get()=="Shelly":
            parms=GetTab5Variables()
            parms[3]=True
            parms[4]=DefaultPlugParameters[4]
            parms[5]=DefaultPlugParameters[5]
            SetTab5Variables(parms)
    
    def SetStatusNextPrevButtonsT5():
        global CurrentPlug
        if CurrentPlug-1>0:
            PrevT5Button.configure(state='enabled')
        else:
            PrevT5Button.configure(state='disabled')
        if CurrentPlug<len(PlugsArray):
            NextT5Button.configure(state='enabled')
        else:
            NextT5Button.configure(state='disabled')        

    def NextT5():
        global CurrentPlug
        if NotSavedDataTab5():
         messagebox.showinfo(message="Finish first to edit the current Plug")
         return
        CurrentPlug+=1
        HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(len(PlugsArray)))
        SetTab5Variables(PlugsArray[CurrentPlug-1])
        SetStatusNextPrevButtonsT5()
        
    def PrevT5():
        global CurrentPlug
        if NotSavedDataTab5():
         messagebox.showinfo(message="Finish first to edit the current Plug")
         return
        CurrentPlug-=1
        HeaderLabelT5.config(text="Plug n. "+str(CurrentPlug)+" of "+str(len(PlugsArray)))
        SetTab5Variables(PlugsArray[CurrentPlug-1])
        SetStatusNextPrevButtonsT5()

    def Try2Trigger(on_off):
        try:
            parms=GetTab5Variables()
            if parms[2]=="": return
            if on_off=="ON":
                TurnShellyPlugON(parms[2])
            else:
                TurnShellyPlugOFF(parms[2])
        except:
            messagebox.showerror("ERROR", "Cannot connect")

    def Is_Valid_IP(IP):
        parts=IP.split(".")
        if not(len(parts))==4: return False
        try:
            for part in parts:
                num=int(part)
                if num<0 or num>255: return False
        except:
            return False
        return True

    F1T5 = ttk.Frame(tab5); F1T5.pack()    
    PrevT5Button=ttk.Button(F1T5, text="Prev", command=PrevT5,state='disabled'); PrevT5Button.pack(side="left")
    NextT5Button=ttk.Button(F1T5, text="Next", command=NextT5,state='disabled'); NextT5Button.pack(side="left")
    HeaderLabelT5=ttk.Label(tab5,text ="Plug n. 1 of 1",font=("Arial", 12)); HeaderLabelT5.pack(pady="10");
    ttk.Label(tab5,text ="Plug Name").pack(); PlugName=ttk.Entry(tab5); PlugName.pack();
    ttk.Label(tab5,text ="Plug type").pack(); PlugType=ttk.Combobox(tab5, values = ("Shelly","Other"), state = 'readonly'); PlugType.pack();
    PlugType.bind("<<ComboboxSelected>>", PlugTypecallback)
    ttk.Label(tab5,text ="Plug IP").pack(); Plug_IP=ttk.Entry(tab5); Plug_IP.pack();
    PlugDefaultParms=tk.BooleanVar(); PlgEnabled=tk.Checkbutton(tab5,text="Use default commands",variable=PlugDefaultParms); PlgEnabled.pack()
    ttk.Label(tab5,text ="Command to switch ON").pack(); PlugCommandON=ttk.Entry(tab5); PlugCommandON.pack();
    ttk.Label(tab5,text ="Command to switch OFF").pack(); PlugCommandOFF=ttk.Entry(tab5); PlugCommandOFF.pack();     
    Pluglabel=ttk.Label(tab5,text ="---"); Pluglabel.pack();
    F2T5 = ttk.Frame(tab5); F2T5.pack()
    F3T5 = ttk.Frame(tab5); F3T5.pack()
    F4T5 = ttk.Frame(tab5); F4T5.pack(pady="10")
    ttk.Button(F2T5, text="Save changes", command=SavePlugParameters).pack(side="left")
    ttk.Button(F2T5, text="Ignore changes", command=AskLoadPlugParameters).pack(side="left")
    ttk.Button(F2T5, text="Clear all values", command=ClearPlugParameters).pack(side="left")
    ttk.Button(F3T5, text="TEST ON", command=lambda: Try2Trigger("ON")).pack(side="left")
    ttk.Button(F3T5, text="TEST OFF", command=lambda: Try2Trigger("OFF")).pack(side="left")
    ttk.Button(F4T5, text="Add new Plug", command=AddPlug).pack(side="left")
    ttk.Button(F4T5, text="Remove Plug", command=DeleteCurrentPlug).pack(side="left")

    
####################################

    def GetCameraTabVariables():
        return [CameraName.get(), CameraType.get(), CameraIP.get(), CameraDefaultParms.get(), CameraStreamURL.get(), CameraControlURL.get()]

    def SetCameraTabVariables(parms):
        CameraName.delete(0, tk.END); CameraName.insert(0, str(parms[0]))
        CameraType.set(parms[1])
        CameraIP.delete(0, tk.END); CameraIP.insert(0, str(parms[2]))
        CameraDefaultParms.set(parms[3])
        CamEnabled.update()
        CameraStreamURL.delete(0, tk.END); CameraStreamURL.insert(0, str(parms[4]))
        CameraStreamURL.update()
        CameraControlURL.delete(0, tk.END); CameraControlURL.insert(0, str(parms[5]))
        CameraControlURL.update()

    def LoadCameraParameters():
        global CamerasArray, CurrentCamera
        if CurrentCamera - 1 >= len(CamerasArray): return
        tabControl.unbind("<<NotebookTabChanged>>")
        SetCameraTabVariables(CamerasArray[CurrentCamera - 1])
        tabControl.bind("<<NotebookTabChanged>>", on_tab_selected)

    def SaveCameraParameters():
        global CurrentCamera, FileIsModified
        if CheckCameraParameters():
            newvalues = GetCameraTabVariables()
            if len(CamerasArray) == CurrentCamera - 1:
                CamerasArray.append(newvalues)
                FileIsModified = True
            elif NotSavedDataTabCamera():
                answer = messagebox.askyesno(title="Confirmation", message="Overwrite current Camera?")
                if answer:
                    CamerasArray[CurrentCamera - 1] = newvalues
                    FileIsModified = True

    def AskLoadCameraParameters():
        global CurrentCamera
        answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
        if answer:
            LoadCameraParameters()

    def ClearCameraParameters():
        global DefaultCameraParameters
        SetCameraTabVariables(DefaultCameraParameters)

    def AddCamera():
        global CurrentCamera, CamerasArray
        if len(CamerasArray) == CurrentCamera - 1:
            messagebox.showinfo(message="Finish first to edit the current Camera")
            return
        if NotSavedDataTabCamera():
            messagebox.showinfo(message="Unsaved data for the current Camera")
            return
        CurrentCamera = len(CamerasArray) + 1
        HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(CurrentCamera))
        ClearCameraParameters()
        SetStatusNextPrevButtonsCam()

    def DeleteCurrentCamera():
        global CurrentCamera, FileIsModified
        answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete the current Camera?")
        if answer:
            ClearCameraParameters()
            FileIsModified = True
            if CurrentCamera > len(CamerasArray):
                if CurrentCamera == 1:
                    return
                else:
                    CurrentCamera -= 1
                    HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(CurrentCamera))
                    SetCameraTabVariables(CamerasArray[CurrentCamera - 1])
            else:
                del CamerasArray[CurrentCamera - 1]
                FileIsModified = True
                if CurrentCamera > len(CamerasArray):
                    HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(CurrentCamera))
                else:
                    HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(len(CamerasArray)))
                    SetCameraTabVariables(CamerasArray[CurrentCamera - 1])
            SetStatusNextPrevButtonsCam()

    def NotSavedDataTabCamera():
        global CurrentCamera, DefaultCameraParameters
        if len(CamerasArray) == CurrentCamera - 1:
            return GetCameraTabVariables() != DefaultCameraParameters
        return GetCameraTabVariables() != CamerasArray[CurrentCamera - 1]

    def CheckCameraParameters():
        parms = GetCameraTabVariables()
        if parms[0] == "":
            messagebox.showerror("ERROR", "Camera name cannot be empty.")
            return False
        if parms[1] == "":
            messagebox.showerror("ERROR", "Camera type cannot be empty.")
            return False
        if parms[2] == "":
            messagebox.showerror("ERROR", "IP address cannot be empty.")
            return False
        if not Is_Valid_IP(str(parms[2])):
            messagebox.showerror("ERROR", str(parms[2]) + " is not a valid IP address")
            return False
        if not parms[3] and (parms[4] == "" or parms[5] == ""):
            messagebox.showerror("ERROR", "Camera URLs cannot be empty if not using default.")
            return False
        for i, element in enumerate(CamerasArray):
            if i != CurrentCamera - 1:
                if parms[0] in element:
                    messagebox.showerror("ERROR", "Name already in use")
                    return False
                if parms[2] in element:
                    messagebox.showerror("ERROR", "IP " + str(parms[2]) + " already in use")
                    return False
        return True

    def CameraTypeCallback(eventObject):
        global DefaultCameraParameters
        if CameraType.get() == "IPCam":
            parms = GetCameraTabVariables()
            parms[3] = True
            parms[4] = DefaultCameraParameters[4]
            parms[5] = DefaultCameraParameters[5]
            SetCameraTabVariables(parms)

    def SetStatusNextPrevButtonsCam():
        global CurrentCamera
        PrevCamButton.configure(state='enabled' if CurrentCamera - 1 > 0 else 'disabled')
        NextCamButton.configure(state='enabled' if CurrentCamera < len(CamerasArray) else 'disabled')

    def NextCamera():
        global CurrentCamera
        if NotSavedDataTabCamera():
            messagebox.showinfo(message="Finish first to edit the current Camera")
            return
        CurrentCamera += 1
        HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(len(CamerasArray)))
        SetCameraTabVariables(CamerasArray[CurrentCamera - 1])
        SetStatusNextPrevButtonsCam()

    def PrevCamera():
        global CurrentCamera
        if NotSavedDataTabCamera():
            messagebox.showinfo(message="Finish first to edit the current Camera")
            return
        CurrentCamera -= 1
        HeaderLabelCam.config(text="Camera n. " + str(CurrentCamera) + " of " + str(len(CamerasArray)))
        SetCameraTabVariables(CamerasArray[CurrentCamera - 1])
        SetStatusNextPrevButtonsCam()

    def TryCameraConnection():
        try:
            parms = GetCameraTabVariables()
            if parms[2] == "" or parms[4] == "": return
            # Replace with actual connection logic
            CameraPopup(ConfiguratorWindow.winfo_toplevel(),parms[2])
        except Exception as e:
            print(e)
            messagebox.showerror("ERROR", "Cannot connect")

    def Is_Valid_IP(IP):
        parts = IP.split(".")
        if len(parts) != 4: return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except:
            return False


    F1Cam = ttk.Frame(tab6); F1Cam.pack()
     
    PrevCamButton = ttk.Button(F1Cam, text="Prev", command=PrevCamera, state='disabled'); PrevCamButton.pack(side="left")
    NextCamButton = ttk.Button(F1Cam, text="Next", command=NextCamera, state='disabled'); NextCamButton.pack(side="left")
    HeaderLabelCam = ttk.Label(tab6, text="Camera n. 1 of 1", font=("Arial", 12)); HeaderLabelCam.pack(pady="10")

    ttk.Label(tab6, text="Camera Name").pack(); CameraName = ttk.Entry(tab6); CameraName.pack()
    ttk.Label(tab6, text="Camera Type").pack(); CameraType = ttk.Combobox(tab6, values=("IPCam", "Other"), state='readonly'); CameraType.pack()
    CameraType.bind("<<ComboboxSelected>>", CameraTypeCallback)

    ttk.Label(tab6, text="Camera IP").pack(); CameraIP = ttk.Entry(tab6); CameraIP.pack()
    CameraDefaultParms = tk.BooleanVar(); CamEnabled = tk.Checkbutton(tab6, text="Use default URLs", variable=CameraDefaultParms); CamEnabled.pack()
    #tabCamera = ttk.Frame(tab6); tabCamera.pack()
    ttk.Label(tab6, text="Stream URL").pack(); CameraStreamURL = ttk.Entry(tab6); CameraStreamURL.pack()
    ttk.Label(tab6, text="Control URL").pack(); CameraControlURL = ttk.Entry(tab6); CameraControlURL.pack()
    ttk.Label(tab6,text ="---").pack();    
    F2Cam = ttk.Frame(tab6); F2Cam.pack()
    ttk.Button(F2Cam, text="Save changes", command=SaveCameraParameters).pack(side="left")
    ttk.Button(F2Cam, text="Ignore changes", command=AskLoadCameraParameters).pack(side="left")
    ttk.Button(F2Cam, text="Clear all values", command=ClearCameraParameters).pack(side="left")

    F3Cam = ttk.Frame(tab6); F3Cam.pack()
    ttk.Button(F3Cam, text="TEST Connection", command=TryCameraConnection).pack(side="left")

    F4Cam = ttk.Frame(tab6); F4Cam.pack(pady="10")
    ttk.Button(F4Cam, text="Add new Camera", command=AddCamera).pack(side="left")
    ttk.Button(F4Cam, text="Remove Camera", command=DeleteCurrentCamera).pack(side="left")



####################################
    

    LoadConfFile()
    SetSyringeOptions()
    ShowData()      
    #ConfiguratorWindow.mainloop()
