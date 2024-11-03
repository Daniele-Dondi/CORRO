import tkinter as tk                     
from tkinter import ttk, Menu, messagebox
  
root = tk.Tk() 
root.title("CORRO CONFIGURATOR")
root.geometry('500x600+500+200')
menubar = Menu(root)
file_menu = Menu(menubar,tearoff=0)
file_menu.add_command(label='Open')
file_menu.add_command(label='Save')
file_menu.add_separator()
file_menu.add_command(label='Exit',command=root.destroy)
root.config(menu=menubar)
menubar.add_cascade(label="File",menu=file_menu)

tabControl = ttk.Notebook(root) 
tab1 = ttk.Frame(tabControl) 
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl) 
  
tabControl.add(tab1, text ='Reactants') 
tabControl.add(tab2, text ='Reactors')
tabControl.add(tab3, text ='Syringes') 
tabControl.pack(expand = 1, fill ="both")

def rtypecallback(eventObject):
    ReactantType=rtype.get()
    #print("Selected value rtype:", ReactantType)
    if ReactantType=="Pure liquid":
        purity.configure(state='normal')
        concentration.configure(state='disabled')
        ConcNumType.configure(state='disabled')
        ConcDenType.configure(state='disabled')    
    elif ReactantType=="Solution":
        purity.configure(state='disabled')
        concentration.configure(state='normal')
        ConcNumType.configure(state='normal')
        ConcDenType.configure(state='normal')
    elif ReactantType=="Solvent":
        purity.configure(state='disabled')
        concentration.configure(state='disabled')
        ConcNumType.configure(state='disabled')
        ConcDenType.configure(state='disabled')
        

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
     MW.delete(0,tk.END)  # Clear any existing text
     MW.insert(0,str(MM))  # Insert new text

def Try2CalculateMolarity():
    ReactantType=rtype.get()
    if ReactantType=="Solution":
        value=concentration.get()
        UnitNum=ConcNumType.get()
        UnitDen=ConcDenType.get()
        den=density.get()
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
            #now we should have moles
            if UnitDen=="L":
                return value
            if UnitDen=="mL":
                return value*1000
            if UnitDen=="100g":
                den=float(den)                
                return value*10*den
        except:
            return 0
    if ReactantType=="Pure liquid":
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
    if rname.get()=="":
        messagebox.showerror("ERROR", "Reactant name cannot be empty. Insert a valid name and retry.")
        return False
    if rtype.get()=="":
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
        print("Calculated molarity: ",M)
    print("Reactant parameters are correct")
    return True

def SaveReactantParameters():
    if CheckReactantParameters():
      print("save reactant")

def ClearParameters():
    answer = messagebox.askyesno(title="Confirmation", message="Do you want to delete all parameters inserted?")
    if answer:
      name.delete(0,tk.END)
      rformula.delete(0,tk.END)
      MW.delete(0,tk.END)
      purity.delete(0,tk.END)
      purity.insert(0,"100")
      density.delete(0,tk.END)
      density.insert(0,"1")
  
ttk.Label(tab1,text ="Reactant Name").pack(); rname=ttk.Entry(tab1); rname.pack()
ttk.Label(tab1,text ="Reactant Type").pack(); rtype=ttk.Combobox(tab1, values = ('Solution','Solvent','Pure liquid'), state = 'readonly'); rtype.pack(); rtype.bind("<<ComboboxSelected>>", rtypecallback)
ttk.Label(tab1,text ="Chemical formula").pack(); rformula=ttk.Entry(tab1); rformula.pack()
ttk.Label(tab1,text ="Molecular Mass").pack(); MW=ttk.Entry(tab1); MW.pack(); MW.bind("<Button-1>", Try2CalculateMWfromFormula)
ttk.Label(tab1,text ="Purity %").pack(); purity=ttk.Entry(tab1); purity.insert(0, '100'); purity.pack()
conclabel=ttk.Label(tab1,text ="Concentration"); conclabel.pack(); concentration=ttk.Entry(tab1); concentration.pack()
ttk.Label(tab1,text ="Concentration units (numerator)").pack(); ConcNumType=ttk.Combobox(tab1, values = ('g', 'mg', 'mol', 'mmol'), state = 'readonly'); ConcNumType.pack(); ConcNumType.bind("<<ComboboxSelected>>", ConcNumTypecallback)
ttk.Label(tab1,text ="Concentration units (denominator)").pack(); ConcDenType=ttk.Combobox(tab1, values = ('L', 'mL','100g'), state = 'readonly'); ConcDenType.pack(); ConcDenType.bind("<<ComboboxSelected>>", ConcDenTypecallback)
ttk.Label(tab1,text ="Density (g/mL)").pack(); density=ttk.Entry(tab1); density.insert(0, '1'); density.pack()
ttk.Button(tab1, text="Check values", command=CheckReactantParameters).pack()
ttk.Button(tab1, text="Save changes", command=SaveReactantParameters).pack()
ttk.Button(tab1, text="Clear all values", command=ClearParameters).pack()
ttk.Button(tab1, text="Add Reactant", command=lambda: print("add reactant")).pack()
ttk.Button(tab1, text="Remove Reactant", command=lambda: print("remove reactant")).pack()


def reactortypecallback(eventObject):
  print("reactor type callback")

ttk.Label(tab2,text ="REACTOR").pack()
ttk.Label(tab2,text ="Name").pack(); reactor_name=ttk.Entry(tab2); reactor_name.pack()
ttk.Label(tab2,text ="Type").pack(); reactor_type=ttk.Combobox(tab2, values = ('Heated reactor','Non heated reactor','Chromatographic column','Liquid/liquid separator'), state = 'readonly'); reactor_type.pack(); reactor_type.bind("<<ComboboxSelected>>", reactortypecallback)
ttk.Label(tab2,text ="Heater connection").pack(); heated=ttk.Entry(tab2); heated.pack()
ttk.Label(tab2,text ="Stirrer connection").pack(); stirred=ttk.Entry(tab2); stirred.pack()
ttk.Label(tab2,text ="Min. volume (mL)").pack(); minvol=ttk.Entry(tab2); minvol.pack()
ttk.Label(tab2,text ="Max. volume (mL)").pack(); maxvol=ttk.Entry(tab2); maxvol.pack()
ttk.Button(tab2, text="Add Reactor", command=lambda: print("on clicked!")).pack()

ttk.Label(tab3,text ="SYRINGE").pack()
ttk.Label(tab3,text ="Valve exit n.1").pack(); exit1type=ttk.Combobox(tab3, values = ('Air/Waste', 'Reactant1', 'Reactant2'), state = 'readonly'); exit1type.pack()
ttk.Label(tab3,text ="Valve exit n.2").pack(); exit2type=ttk.Combobox(tab3, values = ('Air/Waste', 'Reactant1', 'Reactant2'), state = 'readonly'); exit2type.pack()
ttk.Label(tab3,text ="Valve exit n.3").pack(); exit3type=ttk.Combobox(tab3, values = ('Air/Waste', 'Reactant1', 'Reactant2'), state = 'readonly'); exit3type.pack()
ttk.Label(tab3,text ="Valve exit n.4").pack(); exit4type=ttk.Combobox(tab3, values = ('Air/Waste', 'Reactant1', 'Reactant2'), state = 'readonly'); exit4type.pack()
ttk.Label(tab3,text ="Valve exit n.5").pack(); exit5type=ttk.Combobox(tab3, values = ('Air/Waste', 'Reactant1', 'Reactant2'), state = 'readonly'); exit5type.pack()

ttk.Button(tab3, text="Save changes", command=lambda: print("on clicked!")).pack()
  
root.mainloop()   
