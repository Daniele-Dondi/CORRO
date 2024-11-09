import tkinter as tk                     
from tkinter import ttk, Menu, messagebox, filedialog
import pickle

ReactantsArray=[]
CurrentReactant=1
SyringesOptions=["Not in use","Air/Waste"]
CurrentSyringe=1
TotalNumberOfSyringes=6
SyringesArray=[[SyringesOptions[1 if i==0 else 0] for i in range(5)] for j in range(TotalNumberOfSyringes)]
ApparatusArray=[]
CurrentApparatus=1
PIDList=["None","Heater 1","Heater 2"]
ThermoList=["None","Thermocouple 1","Thermocouple 2"]
PowerList=["None","BT channel 1","BT channel 2","BT channel 3","BT channel 4","BT channel 5","BT channel 6"]


def InitAllData():
    return
 
def LoadConnFile(filename):
    return
##    global ReactantsArray,SyringesArray,ApparatusArray
##    fin=open(filename, 'rb')
##    ReactantsArray=pickle.load(fin)
##    SyringesArray=pickle.load(fin)
##    ApparatusArray=pickle.load(fin)
##    fin.close()

def StartWizard(window):
    WizazrdWindow=tk.Toplevel(window)
    WizazrdWindow.title("CORRO WIZARD")
    WizazrdWindow.geometry('500x620+500+150')
    WizazrdWindow.grab_set()
    
    def Close():
      MsgBox = tk.messagebox.askquestion ('Exit Wizazrd','Are you sure you want to exit Wizazrd?',icon = 'warning')
      if MsgBox == 'yes':  
       WizazrdWindow.destroy()
       
    WizazrdWindow.protocol("WM_DELETE_WINDOW", Close)
    
    def ShowData():
     global CurrentReactant,CurrentSyringe,CurrentApparatus,ReactantsArray,SyringesArray,ApparatusArray
     CurrentReactant=1
     CurrentSyringe=1     
     CurrentApparatus=1
     SetStatusNextPrevButtonsT1()
     SetStatusNextPrevButtonsT2()
     SetStatusNextPrevButtonsT3()
     LoadReactantParameters()
     LoadSyringeParameters()
     LoadApparatusParameters()
     a=len(ReactantsArray)
     if a==0: a=1
     HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(a))
     a=len(ApparatusArray)
     if a==0: a=1
     HeaderLabelT2.config(text="Apparatus n. "+str(CurrentApparatus)+" of "+str(a))
     a=len(SyringesArray)
     if a==0: a=1
     HeaderLabelT3.config(text="Syringe n. "+str(CurrentSyringe)+" of "+str(a))
        
    def LoadAllData():
     global CurrentReactant,CurrentSyringe,CurrentApparatus,ReactantsArray,SyringesArray,ApparatusArray
     MsgBox = tk.messagebox.askquestion ('Load Data','By loading data from file current data will be overwritten. Proceed?',icon = 'warning')
     if MsgBox == 'yes':  
         filetypes = (('SyringeBOT connection files', '*.conn'),('All files', '*.*'))
         filename = filedialog.askopenfilename(filetypes=filetypes)
         if filename=="": return
         LoadConnFile(filename)
         ShowData()

    def SaveAllData():
     filetypes=(('SyringeBOT connection files','*.conn'),('All files','*.*'))
     filename=filedialog.asksaveasfilename(filetypes=filetypes)
     if filename=="": return
     if not ".conn" in filename: filename+=".conn"
     fout=open(filename, 'wb')
     pickle.dump(ReactantsArray,fout)
     pickle.dump(SyringesArray,fout)
     pickle.dump(ApparatusArray,fout)
     fout.close()

    def ClearAllData():
     MsgBox = tk.messagebox.askquestion ('Clear Data','Current data will be overwritten. Proceed?',icon = 'warning')
     if MsgBox == 'yes':
         InitAllData()
         ShowData()
        
    
    menubar = Menu(WizazrdWindow)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='Open',command=LoadAllData)
    file_menu.add_command(label='Save',command=SaveAllData)
    file_menu.add_separator()
    file_menu.add_command(label='Clear all data',command=ClearAllData)
    file_menu.add_separator()    
    file_menu.add_command(label='Exit',command=Close)
    WizazrdWindow.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)

    InitAllData()
      
    #WizazrdWindow.mainloop()
