import tkinter as tk                     
from tkinter import ttk, Menu, messagebox

ReactantsArray=[]
CurrentReactant=1

SyringesOptions=["Not in use","Air/Waste"]
CurrentSyringe=1
TotalNumberOfSyringes=6
SyringesArray=[[SyringesOptions[1 if i==0 else 0] for i in range(5)] for j in range(TotalNumberOfSyringes)]

def SaveAllData():
    return

root = tk.Tk() 
root.title("CORRO CONFIGURATOR")
root.geometry('500x550+500+200')
menubar = Menu(root)
file_menu = Menu(menubar,tearoff=0)
file_menu.add_command(label='Open')
file_menu.add_command(label='Save',command=SaveAllData)
file_menu.add_separator()
file_menu.add_command(label='Exit',command=root.destroy)
root.config(menu=menubar)
menubar.add_cascade(label="File",menu=file_menu)



def on_tab_selected(event):
    global SyringesOptions
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == "Syringes":
        SyringesOptions=["Not in use","Air/Waste"]
        count=0
        for element in ReactantsArray:
            count+=1
            SyringesOptions.append("Reactant"+str(count)+": "+element[0])
        #same with apparatus    
        exit1type.config(values=SyringesOptions)
        exit2type.config(values=SyringesOptions)
        exit3type.config(values=SyringesOptions)
        exit4type.config(values=SyringesOptions)
        exit5type.config(values=SyringesOptions)    
   

tabControl = ttk.Notebook(root)
tabControl.bind("<<NotebookTabChanged>>", on_tab_selected)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
  
tabControl.add(tab1, text ='Reactants') 
tabControl.add(tab2, text ='Apparatus')
tabControl.add(tab3, text ='Syringes') 
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

def LoadReactantParameters():
    global CurrentReactant
    answer = messagebox.askyesno(title="Confirmation", message="Revert back to saved data?")
    if answer:
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

def NotSavedDataTab1():
    global CurrentReactant
    return not(len(ReactantsArray)>CurrentReactant-1) or not(GetTab1Variables()==ReactantsArray[CurrentReactant-1])

def AddReactant():
    global CurrentReactant
    if NotSavedDataTab1():
        messagebox.showinfo(message="Finish first to edit the current reagent")
        return
    CurrentReactant=len(ReactantsArray)+1
    HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(CurrentReactant))
    ClearAllValuesT1()
    SetStatusNextPrevButtonsT1()

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
ttk.Button(F2T1, text="Ignore changes", command=LoadReactantParameters).pack(side="left")
ttk.Button(F2T1, text="Clear all values", command=ClearReactantParameters).pack(side="left")
ttk.Button(F3T1, text="Add new Reactant", command=AddReactant).pack(side="left")
ttk.Button(F3T1, text="Remove Reactant", command=DeleteCurrentReactant).pack(side="left")

##################   E N D   O F   T A B  1   #############################################################

def ApparatusTypeCallback(eventObject):
  print("reactor type callback")

def NextT2():
    global CurrentReactant
    if NotSavedDataTab1():
     messagebox.showinfo(message="Finish first to edit the current reagent")
     return
    CurrentReactant+=1
    HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(len(ReactantsArray)))
    ClearAllValuesT1()
    SetTab1Variables(ReactantsArray[CurrentReactant-1])
    SetStatusNextPrevButtonsT1()
    
def PrevT2():
    global CurrentReactant
    if NotSavedDataTab1():
     messagebox.showinfo(message="Finish first to edit the current reagent")
     return
    CurrentReactant-=1
    HeaderLabelT1.config(text="Reactant n. "+str(CurrentReactant)+" of "+str(len(ReactantsArray)))
    ClearAllValuesT1()
    SetTab1Variables(ReactantsArray[CurrentReactant-1])
    SetStatusNextPrevButtonsT1()
 
F1T2 = ttk.Frame(tab2); F1T2.pack()
PrevT2Button=ttk.Button(F1T2, text="Prev", command=PrevT2,state='disabled'); PrevT2Button.pack(side="left")
NextT2Button=ttk.Button(F1T2, text="Next", command=NextT2,state='disabled'); NextT2Button.pack(side="left")
HeaderLabelT2=ttk.Label(tab2,text ="Apparatus n. 1 of 1",font=("Arial", 12)); HeaderLabelT2.pack(pady="10");
ttk.Label(tab2,text ="Name").pack(); ApparatusName=ttk.Entry(tab2); ApparatusName.pack()
ttk.Label(tab2,text ="Type").pack(); ApparatusType=ttk.Combobox(tab2, values = ('Heated reactor','Non heated reactor','Chromatographic column','Liquid/liquid separator'), state = 'readonly')
ApparatusType.pack(); ApparatusType.bind("<<ComboboxSelected>>", ApparatusTypeCallback)
ttk.Label(tab2,text ="Heater connection").pack(); heated=ttk.Entry(tab2); heated.pack()
ttk.Label(tab2,text ="Stirrer connection").pack(); stirred=ttk.Entry(tab2); stirred.pack()
ttk.Label(tab2,text ="Min. volume (mL)").pack(); minvol=ttk.Entry(tab2); minvol.pack()
ttk.Label(tab2,text ="Max. volume (mL)").pack(); maxvol=ttk.Entry(tab2); maxvol.pack()
ttk.Button(tab2, text="Add Reactor", command=lambda: print("on clicked!")).pack()

def NotSavedDataTab3():
    global CurrentSyringe
    return not(SyringesArray[CurrentSyringe-1]==GetTab3Variables())
    
def GetTab3Variables():
    return [exit1type.get(), exit2type.get(), exit3type.get(), exit4type.get(), exit5type.get()]  

def SetTab3Variables(parms):
    exit1type.set(parms[0])
    exit2type.set(parms[1])
    exit3type.set(parms[2])
    exit4type.set(parms[3])
    exit5type.set(parms[4])

def SetStatusNextPrevButtonsT3():
    global CurrentSyringe
    if CurrentSyringe==1:
        PrevT3Button.configure(state='disabled')
    else:
        PrevT3Button.configure(state='enabled')
    if CurrentSyringe>=6:
        NextT3Button.configure(state='disabled')
    else:
        NextT3Button.configure(state='enabled')

def LoadSyringeParameters():
    global CurrentSyringe
    SetTab3Variables(SyringesArray[CurrentSyringe-1])
    
def SaveSyringeParameters():
    global CurrentSyringe
    if NotSavedDataTab3():
     SyringesArray[CurrentSyringe-1]=GetTab3Variables()    

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

F1T3 = ttk.Frame(tab3); F1T3.pack()
PrevT3Button=ttk.Button(F1T3, text="Prev", command=PrevT3,state='enabled'); PrevT3Button.pack(side="left")
NextT3Button=ttk.Button(F1T3, text="Next", command=NextT3,state='enabled'); NextT3Button.pack(side="left")
HeaderLabelT3=ttk.Label(tab3,text ="Syringe n. 1 of 6",font=("Arial", 12)); HeaderLabelT3.pack(pady="10");
ttk.Label(tab3,text ="Valve exit n.1").pack(); exit1type=ttk.Combobox(tab3, values = SyringesOptions, state = 'readonly'); exit1type.current(1); exit1type.pack() 
ttk.Label(tab3,text ="Valve exit n.2").pack(); exit2type=ttk.Combobox(tab3, values = SyringesOptions, state = 'readonly'); exit2type.current(0); exit2type.pack()
ttk.Label(tab3,text ="Valve exit n.3").pack(); exit3type=ttk.Combobox(tab3, values = SyringesOptions, state = 'readonly'); exit3type.current(0); exit3type.pack()
ttk.Label(tab3,text ="Valve exit n.4").pack(); exit4type=ttk.Combobox(tab3, values = SyringesOptions, state = 'readonly'); exit4type.current(0); exit4type.pack()
ttk.Label(tab3,text ="Valve exit n.5").pack(); exit5type=ttk.Combobox(tab3, values = SyringesOptions, state = 'readonly'); exit5type.current(0); exit5type.pack()

ttk.Button(tab3, text="Save changes", command=SaveSyringeParameters).pack(pady="10")
ttk.Button(tab3, text="Ignore changes", command=LoadSyringeParameters).pack()

  
root.mainloop()   
