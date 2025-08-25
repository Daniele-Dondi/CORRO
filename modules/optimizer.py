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
from tkinter import ttk, filedialog
import os
import modules.wizard as wiz
from modules.buildvercalculator import CRC
import pickle
import modules.helpview as Help
import modules.configurator as conf
import modules.BO_n_dimensions as BO
from modules.DOE import DesignOfExperiments

global NotSaved, WeAreOptimizing, run_parameters, doe_matrix, BO_next_point, MaxIterations


def GetRunInformations():
    global run_parameters, doe_matrix
    ProcedureName, OptimizerName, OptimizationParms, MinValues, MaxValues, Position, Cycle, RewardValue = run_parameters
    ProcedureName=os.path.basename(ProcedureName)
    OptimizerName=os.path.basename(OptimizerName)
    out_string="Optimization run for the file "+OptimizerName+"\nbased on procedure "+ProcedureName+"\nType of optimization:"
    Opt_Type=OptimizationParms[0]
    out_string+=Opt_Type+"\n"
    if Opt_Type=="Bayesian Optimization":  
        Opt_Type, Reward_Type, MaxIter, K, XI = OptimizationParms
        out_string+="Maximum number of iterations: "+str(MaxIter)+"\nkappa="+str(K)+"\nXi="+str(XI)+"\nOutput control: "+Reward_Type+"\n"
    elif Opt_Type=="DoE":
        Opt_Type, Reward_Type, DT, Levels = OptimizationParms
        out_string+="DoE type: "+DT+"\nLevels="+str(Levels)+"\nTotal number of experiments: "+str(len(doe_matrix))+"\n"
    out_string+="Current Cycle: "+str(Cycle)
    return out_string
    

def CreateNewValues():
    global run_parameters, doe_matrix, BO_next_point, MaxIterations
    ProcedureName, OptimizerName, OptimizationParms, MinValues, MaxValues, Position, Cycle, RewardValue = run_parameters
    Opt_Type=OptimizationParms[0] ##[Opt_Type, Reward_Type, MaxIter, K, XI] ##[Opt_Type, Reward_Type, DT, Levels]    
    if Cycle==0: #We have to init optimizers
        if Opt_Type=="Bayesian Optimization":  
            Opt_Type, Reward_Type, MaxIter, K, XI = OptimizationParms
            BO.BO_Initialization(K, XI, MinValues, MaxValues, MaxIter)
            MaxIterations=MaxIter
        elif Opt_Type=="DoE":
            Opt_Type, Reward_Type, DT, Levels = OptimizationParms
            Levels=[Levels]*len(MinValues)
            Minimums=[float(el[0]) for el in MinValues]
            Maximums=[float(el[0]) for el in MaxValues]
            doe = DesignOfExperiments(Levels, Minimums, Maximums)
            doe_matrix = doe.get_design()
            MaxIterations=len(doe_matrix)
        else:
            return None
    Cycle+=1
    run_parameters = [ProcedureName, OptimizerName, OptimizationParms, MinValues, MaxValues, Position, Cycle, RewardValue]
    if Cycle >= MaxIterations:
        return None            
    if Opt_Type=="Bayesian Optimization":
        BO_next_point=BO.BO_Cycle()
        next_point=float_list = list(BO_next_point.values())
        return CreateParmsToOptimize(next_point, Position)
    elif Opt_Type=="DoE":
        next_point=doe_matrix[Cycle]
        return CreateParmsToOptimize(next_point, Position)

def RecordTargetValues(target):
    global run_parameters, BO_next_point
    ProcedureName, OptimizerName, OptimizationParms, MinValues, MaxValues, Position, Cycle, RewardValue = run_parameters
    Opt_Type=OptimizationParms[0]
    if Opt_Type=="Bayesian Optimization":
        BO_Record(BO_next_point, target)
    elif Opt_Type=="DoE": #save values somewhere
        pass

def RetrieveOutputValue():
    global run_parameters
    ProcedureName, OptimizerName, OptimizationParms, MinValues, MaxValues, Position, Cycle, RewardValue = run_parameters
    Opt_Type=OptimizationParms[0]
    Reward_Type=OptimizationParms[1]
    TargetValue=0
    if Reward_Type=="MANUAL":
        newWin = tk.Tk()
        newWin.withdraw()
        TargetValue = tk.simpledialog.askfloat("Input", "Insert the value to optimize when ready",
                               parent=newWin)
        newWin.destroy()
    return TargetValue

def CreateParmsToOptimize(values,parms):
    output=[]
    for num in range(len(parms)):
        Obj_Pos, Pos_Array=parms[num]
        output.append([values[num], Obj_Pos, Pos_Array])
    return output


def StartBO_Window(window, **kwargs):
    global ProcedureName,OptimizerName,CRC_Value,File_Size,CurrentY
    global CreatedProcedures
    global NotSaved

    NotSaved=False

    def disable_widgets(frame):
        for widget in frame.winfo_children():
            try:
                widget.configure(state='disabled')
            except tk.TclError:
                # Skip widgets that don't support 'state' (e.g. labels)
                pass

    def enable_widgets(frame):
        for widget in frame.winfo_children():
            try:
                widget.configure(state='normal')
            except tk.TclError:
                # Skip widgets that don't support 'state' (e.g. labels)
                pass        

    class MinMaxApp:
        def __init__(self, root):
            self.root = root
            
            # Create a frame
            self.frame = tk.Frame(self.root,relief=tk.GROOVE,borderwidth=4)
            self.frame.pack(side="left")#pady=20)

            # Min Entry
            label1=tk.Label(self.frame, text="Min Value:")
            label1.grid(row=0, column=0)
            self.min_entry = tk.Entry(self.frame)
            self.min_entry.grid(row=0, column=1, padx=5, pady=5)
            self.min_entry.bind("<KeyRelease>", self.on_key_release)

            # Max Entry
            label2=tk.Label(self.frame, text="Max Value:")
            label2.grid(row=1, column=0)
            self.max_entry = tk.Entry(self.frame)
            self.max_entry.grid(row=1, column=1, padx=5, pady=5)
            self.max_entry.bind("<KeyRelease>", self.on_key_release)

        def on_key_release(self,event):
            SetNotSaved(True)

        def SetMin(self,value):
            value=round(float(value),2)
            self.min_entry.delete(0,tk.END)
            self.min_entry.insert(0,str(value))

        def SetMax(self,value):
            value=round(float(value),2)
            self.max_entry.delete(0,tk.END)
            self.max_entry.insert(0,str(value))

        def GetValues(self):
            min_val = self.min_entry.get()
            max_val = self.max_entry.get()
            return [min_val, max_val]

        def GetEnabled(self):
            MinMaxEnabled = self.min_entry.cget("state")
            return MinMaxEnabled


    class BO_Object(tk.Frame):
        def __init__(self,container):
            self.Height=40
            self.Objects=[]
            self.MinMaxs=[] #links to minmax objects
            self.ParametersToChange=[] #contains the number of variable to change associate with possible BO variables
            self.text="" #display text with $..$ indicating possible BO variables
            self.values="" #values retrieved for the object
            self.Colors=["Cyan","Crimson","Purple","Red"]
            super().__init__(container)
            self.config(relief=tk.GROOVE,borderwidth=4)        
            self.create_widgets()

        def create_widgets(self):
            self.Line1=tk.Frame(self)
            self.Line1.pack()
            self.Line2=tk.Frame(self)
            self.Line2.pack(side="left")

        def SelectedColor(self,num):
            return self.Colors[num%len(self.Colors)]        

        def ButtonClicked(self,num):
            if self.Objects[num].config('relief')[-1] == 'raised':
                num_MinMax=num//2            
                self.Objects[num].config(relief='sunken',bg=self.SelectedColor(num_MinMax))
                SelectedMinMax=self.MinMaxs[num_MinMax].frame
                enable_widgets(SelectedMinMax)
                SelectedMinMax.config(highlightbackground=self.SelectedColor(num_MinMax), highlightthickness=1)
            else:
                self.Objects[num].config(relief='raised',bg="white")
                num_MinMax=num//2
                SelectedMinMax=self.MinMaxs[num_MinMax].frame
                disable_widgets(SelectedMinMax)
                SelectedMinMax.config(highlightbackground=None, highlightthickness=0)

        def UserClickedButton(self,num):
            SetNotSaved(True)
            self.ButtonClicked(num)

        def InitValues(self,element):
    ##        Structure of the array:
    ##        [[object array taken from procedure object],
    ##        [String with possible variable(s) to be optimized included in $num$. num is the position of the value(s) in the previous array],
    ##        [array containing Min and Max values for each opt parameter],
    ##        [array indicating if the opt. variable is selected or not. "disabled"=not selected, "normal"=selected ]]
    ##
    ##        Note: The array cannot start with the numeric value to change.
    ##        So, after splitting the string by "$", the odd values will be labels and the even values will be opt. variables
    ##        
    ##        Example:
    ##        [['Put', 'of', 'in', '10', 'mL', 'Reactant: Water', 'Apparatus: Reactor1 IN', 'Syringe 0 10.0 mL'], "Put $3$ mL of 'Reactant: Water' into 'Apparatus: Reactor1 IN'", [['8.0', '12.0']], ['disabled']]
    ##        [['Reactor1', '50', '10', 1, '25'], "Heat 'Reactor1' at $1$ °C and keep for $2$ min", [['4.0', '544.0'], ['8.0', '12.0']], ['normal', 'normal']], 
    ##        [['Reactant: Water', 'Apparatus: Reactor1', '3', '150.0'], "Wash 'Apparatus: Reactor1' with 'Reactant: Water'", [], []]
            
            text=element[1]
            self.text=element[1]
            values=element[0]
            self.values=element[0]
            parts=text.split("$")
            for num,part in enumerate(parts):
                if num % 2==0:
                    self.Objects.append(tk.Label(self.Line1, text=part, font="Verdana 12"))
                else:
                    self.Objects.append(tk.Button(self.Line1, text=values[int(part)], font="Verdana 12",bg="white",command=lambda j=num : self.UserClickedButton(j)))
                    self.Height=105
                    self.ParametersToChange.append(part)
                    ThisMinMax=MinMaxApp(self.Line2)
                    self.MinMaxs.append(ThisMinMax)
                    FloatValue=float(values[int(part)])
                    ThisMinMax.SetMin(FloatValue*0.8) #fill entries with +- 20% of current value
                    ThisMinMax.SetMax(FloatValue*1.2) #fill entries with +- 20% of current value
                    disable_widgets(ThisMinMax.frame)
                self.Objects[-1].pack(side="left")

        def SetValues(self,element):
            for num,parameter in enumerate(element[2]):
                ThisMinMax=self.MinMaxs[num]
                enable_widgets(ThisMinMax.frame) #enable widget, if not changes do not occur
                ThisMinMax.SetMin(parameter[0])
                ThisMinMax.SetMax(parameter[1])
            for num,parameter in enumerate(element[3]):
                ThisMinMax=self.MinMaxs[num].frame
                if parameter=="disabled":
                    disable_widgets(ThisMinMax)
                else:
                    self.ButtonClicked(1+num*2)

        def GetValues(self):
            output=[self.values,self.text]
            MinMaxValues=[]
            MinMaxEnabled=[]
            for MinMax in self.MinMaxs:
                MinMaxValues.append(MinMax.GetValues())
                MinMaxEnabled.append(MinMax.GetEnabled())
            output.append(MinMaxValues)
            output.append(MinMaxEnabled)
            return output

    
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################




    def SetNotSaved(Value):
        # Function to update title based on NotSaved
        global NotSaved
        NotSaved=Value
        base_title = "BAYESIAN OPTIMIZATION SETUP"
        if NotSaved:
            BO_Window.title(f"{base_title} - Not Saved")
        else:
            BO_Window.title(base_title)

    def InitVars():
        global CreatedProcedures, ProcedureName, CRC_Value, File_Size, CurrentY
        CreatedProcedures=[]
        ProcedureName=""
        CRC_Value=""
        File_Size=0
        CurrentY=10    
                      
    def on_mousewheel(event):
        my_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def Close():
        global NotSaved
        if NotSaved:
            MsgBox = tk.messagebox.askquestion('Exit Optimizer','Are you sure you want to exit the Optimizer?\nCurrent Data are not saved.',icon = 'warning')
            if MsgBox == 'yes':
                BO_Window.destroy()
        else:
            BO_Window.destroy()

    def SplitParmsToOptimize():
        Opt_Parms=GetParmsToOptimize()
        MinValues=[]
        MaxValues=[]
        Position=[]
        for Parm in Opt_Parms: # Parms must be [[min value, max value], object position in procedure, position in the object array]
            Min_Max, Obj_Pos, Pos_Array=Parm
            MinValues.append(Min_Max[0])
            MaxValues.append(Min_Max[1])
            Position.append([Obj_Pos,Pos_Array])
        return [MinValues, MaxValues, Position]

    def RunOptimizationButton(): 
        global NotSaved,ProcedureName,OptimizerName
        Check=ValuesAreCorrect()
        if not(Check=="OK"):
            tk.messagebox.showerror(Check[0], Check[1])
            if Check[0]=="ERROR":  #Check[0] could be either "ERROR" or "WARNING"
                return
        if NotSaved:
            tk.messagebox.showerror('DATA ARE NOT SAVED','Please save first current data before running Optimization',icon = 'warning')
            return
        result=CalcVolUsedForOptimization()
        if result==False: #something went wrong
            return
        response = tk.messagebox.askokcancel("Confirmation", "Do you want to proceed?")
        if response:
            MinValues, MaxValues, Position=SplitParmsToOptimize()
            Cycle=0
            RewardValue=None
            BO_Window.return_code=[ProcedureName, OptimizerName, GetOptimizationParms(), MinValues, MaxValues, Position, Cycle, RewardValue]
            Close()
        #print(CreateParmsToOptimize(MinValues,Position))

    def CalcVolUsedForOptimization():
        global ProcedureName
        Opt_Parms=GetParmsToOptimize()
        MinValues=[]
        MaxValues=[]
        for Parm in Opt_Parms: # Parms must be [[min value, max value], object position in procedure, position in the object array]
            Min_Max, Obj_Pos, Pos_Array=Parm
            MinValues.append([Min_Max[0],Obj_Pos,Pos_Array]) #split the min and max values in two different arrays
            MaxValues.append([Min_Max[1],Obj_Pos,Pos_Array])
        OptParms=GetOptimizationParms()
        if OptParms==False:
            return False
        elif OptParms[0]=="Bayesian Optimization":
            MaxSteps=GetNumberOfOptimizationSteps()
            if MaxSteps==False:
                tk.messagebox.showerror('ERROR','Cannot retrieve the maximum number of optimization steps',icon = 'warning')
                return False
            MinVolumes=wiz.StartWizard(window,Hide=True,File=ProcedureName,Mode="Volumes",New_Values=MinValues) #volumes=[ReactantsUsed,ApparatusUsed,StepByStepOps]
            MaxVolumes=wiz.StartWizard(window,Hide=True,File=ProcedureName,Mode="Volumes",New_Values=MaxValues)
            if "ERROR" in MaxVolumes:
                tk.messagebox.showerror('MAX VOLUME REACHED','Maximum capacity of reactor reached. Consider to scale down quantities',icon = 'warning')
                return False
            ReactantsUsed=MinVolumes[0]
            LastMinReactantVolumes=[vol*MaxSteps for vol in MinVolumes[-1][-1][0]]
            LastMaxReactantVolumes=[vol*MaxSteps for vol in MaxVolumes[-1][-1][0]]
            VolumesUsed=wiz.Grid(window)
            VolumesUsed.ChangeTitle("REACTANTS USED SUMMARY")
            VolumesUsed.WriteOnHeader("Reagent Name")
            VolumesUsed.WriteOnHeader("Minimum volume used for the optimization")
            VolumesUsed.WriteOnHeader("Maximum volume used for the optimization")
            VolumesUsed.CloseHeader()
            for num,chemical in enumerate(ReactantsUsed):
                VolumesUsed.AddItemToRow(chemical)
                VolumesUsed.AddItemToRow(LastMinReactantVolumes[num])
                VolumesUsed.AddItemToRow(LastMaxReactantVolumes[num])
                VolumesUsed.NextRow()
            VolumesUsed.wait_window()
            return True
        elif OptParms[0]=="DoE":
            Levels=[OptParms[3]]*len(MinValues)
            Minimums=[float(el[0]) for el in MinValues]
            Maximums=[float(el[0]) for el in MaxValues]
            NewValues=MinValues
            doe = DesignOfExperiments(Levels, Minimums, Maximums)
            matrix = doe.get_design()
            TotalExperiments=len(matrix)
            tk.messagebox.showinfo("Information", "For this optimization run "+str(TotalExperiments)+" experiments will be performed.")
            Sum=[] 
            for line in matrix:
                for num,element in enumerate(line):
                    NewValues[num][0]=element
                Volumes=wiz.StartWizard(window,Hide=True,File=ProcedureName,Mode="Volumes",New_Values=NewValues)
                if "ERROR" in Volumes:
                    tk.messagebox.showerror('MAX VOLUME REACHED','Maximum capacity of reactor reached. Consider to scale down quantities',icon = 'warning')
                    return False                
                ReactantVolumes=[vol for vol in Volumes[-1][-1][0]]
                if Sum==[]:
                    Sum=ReactantVolumes
                else:
                    Sum = [a + b for a, b in zip(ReactantVolumes, Sum)]
            ReactantsUsed=Volumes[0]
            VolumesUsed=wiz.Grid(window)
            VolumesUsed.ChangeTitle("REACTANTS USED SUMMARY")
            VolumesUsed.WriteOnHeader("Reagent Name")
            VolumesUsed.WriteOnHeader("TOTAL volume used for the optimization")
            VolumesUsed.CloseHeader()
            for num,chemical in enumerate(ReactantsUsed):
                VolumesUsed.AddItemToRow(chemical)
                VolumesUsed.AddItemToRow(Sum[num])
                VolumesUsed.NextRow()
            VolumesUsed.wait_window()
            return True
        else:
            return False

    def RetrieveOptVarsPosition(Value): #return an array with the position number of optimizable variable. The number refers to the position in the procedure object array.
        Var_Position=[]
        segments=Value.split("$")
        for i,segment in enumerate(segments):
            if not(i % 2==0):
                Var_Position.append(int(segment))
        return Var_Position

    def GetParmsToOptimize():
        AllValues=GetAllValues()
        OptValues=[]
        for num,Value in enumerate(AllValues):
            Var_Position=RetrieveOptVarsPosition(Value[1])
            if len(Var_Position)==0:
                continue
            for pos,element in enumerate(Value[3]):
                if element=="normal":
                    OptValues.append([Value[2][pos], num, Var_Position[pos]]) 
        return OptValues # return an array with [[min, max value], object position in procedure, position in the object array]

    def RenderOptimizerCode(OptimizerCode):
        global CurrentY,CreatedProcedures
        for element in OptimizerCode:
            Obj=BO_Object(frame2)
            CreatedProcedures.append(Obj)
            Obj.InitValues(element)
            YSize=Obj.Height
            Obj.place(x=10,y=CurrentY)
            CurrentY+=YSize

    def AskLoadOptimization():
        global CreatedProcedures
        if len(CreatedProcedures)>0:
            if AskDeleteAll()==False:
                return
        filetypes=(('SyringeBOT Optimizer files','*.Optimizer'),('All files','*.*'))
        filename = filedialog.askopenfilename(filetypes=filetypes,initialdir="optimizations")
        if filename=="": return
        LoadOptimization(filename)

    def SetObjValues(Values):
        global CreatedProcedures
        if not(len(Values)==len(CreatedProcedures)):
            tk.messagebox.showerror("ERROR","The number of objects differs with respect to number of parameters.")
            return
        for num,Value in enumerate(Values):
            CreatedProcedures[num].SetValues(Value)

    def SetOptParams(OptParams):
        OptType=OptParams[0]
        OptimizationType.set(OptType)
        create_widgets(OptType)
        OutputType.set(OptParams[1])
        if OptType=="Bayesian Optimization":
            MaxIterations.delete(0,tk.END)
            MaxIterations.insert(0,OptParams[2])
            kappa.delete(0,tk.END)
            kappa.insert(0,OptParams[3])
            xi.delete(0,tk.END)
            xi.insert(0,OptParams[4])
        elif OptType=="DoE":
            DOE_Type.set(OptParams[2])
            NumLevels.delete(0,tk.END)
            NumLevels.insert(0,str(OptParams[3]))
        else:
            tk.messagebox.showerror("ERROR","not yet implemented")

    def check_file_path(filepath):
       # Extract the filename only
       target_filename = os.path.basename(filepath)

       # Check if the file exists
       if os.path.isfile(filepath):
           return filepath
       else:
           tk.messagebox.showinfo("Information", f"Could not find the file {target_filename}\nPlease indicate the new location of the file: {target_filename}")
           # Ask for new location with file type filter (all extensions allowed, name restricted)
           new_path = tk.filedialog.askopenfilename(
               title=f"Select {target_filename}",initialdir="procedures",
               filetypes=[("Matching file", target_filename)],
           )

           # Validate the new selection
           if os.path.basename(new_path) == target_filename:
               SetNotSaved(True)
               return new_path
           else:
               return None

    def RetrieveOptimizerCode():
        global ProcedureName,CRC_Value,File_Size
        ProcedureName=check_file_path(ProcedureName) #check if the file exists, if it is not, maybe file is located somewhere else, so ask for the new location
        if ProcedureName==None:
            tk.messagebox.showerror("ERROR","Cannot continue, the procedure file was not found.")
            return False
        if not(CRC(ProcedureName)==CRC_Value):
            tk.messagebox.showerror("ERROR","Cannot continue, the procedure file "+ProcedureName+" has changed.")
            return False
        if not(os.path.getsize(ProcedureName)==File_Size):
            tk.messagebox.showerror("ERROR","Cannot continue, the procedure file "+ProcedureName+" has changed.")
            return False
        OptimizerCode=wiz.StartWizard(window,Hide=True,File=ProcedureName,Mode="Optimizer")
        if wiz.ThereAreErrors(window,OptimizerCode):
            tk.messagebox.showerror("ERROR","Cannot continue, the procedure file "+ProcedureName+" contains errors.")
            return False
        return OptimizerCode

    def LoadOptimization(filename): #filename must exist
        global ProcedureName,OptimizerName,CRC_Value,File_Size
        SetNotSaved(False)
        OptimizerName=filename        
        fin=open(filename, 'rb')
        ProcedureName=pickle.load(fin)
        CRC_Value=pickle.load(fin)
        File_Size=pickle.load(fin)
        Values=pickle.load(fin)
        OptParams=pickle.load(fin)
        fin.close()
        OptimizerCode=RetrieveOptimizerCode()
        if OptimizerCode==False:
            return
        RenderOptimizerCode(OptimizerCode)
        SetObjValues(Values)
        SetOptParams(OptParams)
        
    def GetOptimizationParms(): 
        Opt_Type=OptimizationType.get()
        Reward_Type=OutputType.get()
        if Opt_Type=="Bayesian Optimization":
            MaxIter=int(MaxIterations.get())
            K=float(kappa.get())
            XI=float(xi.get())
            return [Opt_Type, Reward_Type, MaxIter, K, XI]
        elif Opt_Type=="DoE":
            DT=DOE_Type.get()
            if DT=="Full Factorial":
                Levels=int(NumLevels.get())
                return [Opt_Type, Reward_Type, DT, Levels]
            else:
                return False

    def GetNumberOfOptimizationSteps():
        Opt_Type=OptimizationType.get()
        if Opt_Type=="Bayesian Optimization":
            try:
                MaxIter=int(MaxIterations.get())
                return MaxIter
            except:
                return False
        else:
            return False

    def OptimizationParametersAreCorrect():
        Opt_Type=OptimizationType.get()
        Reward_Type=OutputType.get()
        if Reward_Type=="":
            return ["ERROR","Insert a variable to be optimized"]
        if Opt_Type=="Bayesian Optimization":
            try:
                MaxIter=int(MaxIterations.get())
                K=float(kappa.get())
                XI=float(xi.get())
            except:
                return ["ERROR","Insert valid numerical data"]
            if MaxIter<=0: 
                return  ["ERROR","Number of iterations must be >=0 !"]
            if K<=0: 
                return  ["ERROR","K must be >=0 !"]
            if XI<0: 
                return  ["ERROR","xi must be >0 !"]                         
        elif Opt_Type=="DoE":
            try:
                Levels=int(NumLevels.get())
            except:
                return ["ERROR","Levels value must be a valid integer"]
            if DOE_Type.get()=="":
                return ["ERROR","Select a DoE type"]
        else:
            return ["ERROR","Please select an optimization method"]
        return "OK"

    def ValuesAreCorrect():
        global CreatedProcedures
        if len(CreatedProcedures)==0:
            return ["ERROR","Nothing to optimize"]
        ThereIsSomethingToOptimize=False
        for obj in CreatedProcedures:
            Values=obj.GetValues()
            for num,element in enumerate(Values[3]):
                obj.MinMaxs[num].frame.config(bg=obj.MinMaxs[num].frame.master.cget("bg")) #retrieve the background color from the master object
                if element=="normal":
                    ThereIsSomethingToOptimize=True
                    try:
                        minimum=float(Values[2][num][0])
                        maximum=float(Values[2][num][1])
                        if minimum>=maximum:
                            obj.MinMaxs[num].frame.config(bg="red")
                            return ["ERROR","Minimum cannot be greater or equal to the maximum"]
                    except:
                        obj.MinMaxs[num].frame.config(bg="red")
                        return ["ERROR", "Invalid floating point number"]
        if ThereIsSomethingToOptimize==False:
            return ["ERROR","There are no parameters to be optimized"]
        CanOptimize=OptimizationParametersAreCorrect()
        if not(CanOptimize=="OK"):
            return CanOptimize
        return "OK"

    def GetAllValues():
        global CreatedProcedures
        AllValues=[]
        for obj in CreatedProcedures:
            AllValues.append(obj.GetValues())
        return AllValues

    def SaveOptimization(filename):
        global ProcedureName,OptimizerName,CRC_Value,File_Size,CreatedProcedures
        AllValues=GetAllValues()
        OptimizerName=filename
        fout=open(filename, 'wb')
        pickle.dump(ProcedureName,fout)
        pickle.dump(CRC_Value,fout)
        pickle.dump(File_Size,fout)
        pickle.dump(AllValues,fout)
        pickle.dump(GetOptimizationParms(),fout)
        pickle.dump(GetParmsToOptimize(),fout)
        fout.close()
        SetNotSaved(False)

    def ProcessCheck():
        global CreatedProcedures
        Check=ValuesAreCorrect()
        if not(Check=="OK"):
            tk.messagebox.showerror(Check[0], Check[1])
            if Check[0]=="ERROR":  #Check[0] could be either "ERROR" or "WARNING"
                return
        RetrieveOptimizerCode()

    def AskSaveOptimization():
        global CreatedProcedures
        Check=ValuesAreCorrect()
        if not(Check=="OK"):
            tk.messagebox.showerror(Check[0], Check[1])
            if Check[0]=="ERROR":  #Check[0] could be either "ERROR" or "WARNING"
                return
        filetypes=(('SyringeBOT Optimizer files','*.Optimizer'),('All files','*.*'))
        filename=filedialog.asksaveasfilename(filetypes=filetypes,initialdir="optimizations")
        if filename=="": return          
        if not ".Optimizer" in filename: filename+=".Optimizer"        
        SaveOptimization(filename)

    def New_Setup():
        global ProcedureName,CRC_Value,File_Size,CurrentY,CreatedProcedures
        if len(CreatedProcedures)>0:
            if AskDeleteAll()==False:
                return
        ProcedureName=wiz.ChooseProcedureFile()
        if ProcedureName=="": return
        OptimizerCode=wiz.StartWizard(window,Hide=True,File=ProcedureName,Mode="Optimizer")
        if wiz.ThereAreErrors(window,OptimizerCode): return
        CRC_Value=CRC(ProcedureName)
        File_Size=os.path.getsize(ProcedureName)
        RenderOptimizerCode(OptimizerCode)

    def DeleteAll():
        global CreatedProcedures
        for obj in CreatedProcedures:
            obj.destroy()
        InitVars()

    def AskDeleteAll():
        global CreatedProcedures
        if len(CreatedProcedures)==0:
            return
        else:
            MsgBox = tk.messagebox.askquestion ('New Optimization','Are you sure you want to delete all?',icon = 'warning')
        if MsgBox == 'yes':
            DeleteAll()
            SetNotSaved(False)
            return True
        return False

    def on_key_release(event):
        SetNotSaved(True)

    def create_widgets(selection):
        # Clear old widgets
        for widget in frameOpt.winfo_children():
            widget.destroy()
        if selection == "Bayesian Optimization":
            global MaxIterations,kappa,xi
            Label2=tk.Label(frameOpt, text="Max number of iterations: ")
            Label2.pack(side="left")
            MaxIterations=tk.Entry(frameOpt,state="normal",width=10)
            MaxIterations.pack(side="left")
            MaxIterations.insert(0,"5")
            MaxIterations.bind("<KeyRelease>", on_key_release)
            Label3=tk.Label(frameOpt, text="kappa: ")
            Label3.pack(side="left")
            kappa=tk.Entry(frameOpt,state="normal",width=10)
            kappa.pack(side="left")
            kappa.insert(0,"2.5")
            kappa.bind("<KeyRelease>", on_key_release)
            Label4=tk.Label(frameOpt, text="xi: ")
            Label4.pack(side="left")
            xi=tk.Entry(frameOpt,state="normal",width=10)
            xi.pack(side="left")
            xi.insert(0,"0.0")
            xi.bind("<KeyRelease>", on_key_release)
        elif selection == "DoE":
            global DOE_Type,NumLevels
            DOE_Type=ttk.Combobox(frameOpt, values = ("Full Factorial","Level Full-Factorial","Level Fractional-Factorial","Plackett-Burman"), state = 'readonly',width=20)
            DOE_Type.pack(side="left")
            Label2=tk.Label(frameOpt, text="Number of Levels: ")
            Label2.pack(side="left")
            NumLevels=tk.Spinbox(frameOpt, from_=2, to=10, repeatdelay=500, repeatinterval=200,width=4)
            NumLevels.pack(side="left")
            

    def on_select(event):
        selected_option = OptimizationType.get()
        SetNotSaved(True)
        create_widgets(selected_option)    

    BO_Window=tk.Toplevel(window)
    BO_Window.title("BAYESIAN OPTIMIZATION SETUP")
    BO_Window.geometry('1000x800+400+10')
    BO_Window.grab_set()
    BO_Window.return_code=None
    BO_Window.wm_iconphoto(True, tk.PhotoImage(file='icons/BO.png'))    
    menubar = tk.Menu(BO_Window)
    file_menu = tk.Menu(menubar,tearoff=0)
    file_menu.add_command(label='Clear All',command=AskDeleteAll)
    file_menu.add_separator()    
    file_menu.add_command(label='Load Procedure to be optimized',command=New_Setup)
    file_menu.add_separator()
    file_menu.add_command(label='Load Optimization',command=AskLoadOptimization)
    file_menu.add_command(label='Save Optimization',command=AskSaveOptimization)
    file_menu.add_separator()
    file_menu.add_command(label='Exit',command=Close)
    #settings_menu = tk.Menu(menubar,tearoff=0)
    #settings_menu.add_command(label='Default macro settings')
    BO_Window.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)
    #menubar.add_cascade(label="Settings",menu=settings_menu)
    menubar.add_cascade(label="Process Check",command=ProcessCheck)
    frame1 = tk.Frame(BO_Window)
    frame1.pack(side="top")
    Optimizer = tk.Frame(BO_Window, bd=1, relief=tk.RAISED, background="#e0e0e0")
    Optimizer.pack(side="top",pady=10)
    frameOpt = tk.Frame(BO_Window, bd=1, relief=tk.RAISED, background="#e0e0e0")
    frameOpt.pack(side="top")    
    Label1=tk.Label(Optimizer, text="Optimization Type:")
    Label1.pack(side="left")
    OptimizationType=ttk.Combobox(Optimizer, values = ('Bayesian Optimization','DoE'), state = 'readonly',width=20)
    OptimizationType.pack(side="left")
    OptimizationType.bind("<<ComboboxSelected>>", on_select)
    Label2=tk.Label(Optimizer, text="Output verification:")
    Label2.pack(side="left",padx=10)
    OutputType=ttk.Combobox(Optimizer, values = ('MANUAL',conf.GetAllSensorsVarNames()),width=20)
    OutputType.pack(side="left")
    #OutputType.bind("<<ComboboxSelected>>", on_select)
    
    
##    frame3 = tk.Frame(BO_Window,bg="gray",width=1000,height=30)
##    frame3.pack(side="bottom")
    
    my_canvas = tk.Canvas(BO_Window)
    my_canvas.pack(side="left",fill=tk.BOTH,expand=1)
    y_scrollbar = ttk.Scrollbar(BO_Window,orient=tk.VERTICAL,command=my_canvas.yview)
    y_scrollbar.pack(side="right",fill=tk.Y)
    my_canvas.configure(yscrollcommand=y_scrollbar.set)
    my_canvas.bind("<Configure>",lambda e: my_canvas.config(scrollregion= my_canvas.bbox(tk.ALL)))
    BO_Window.bind("<MouseWheel>", on_mousewheel)
##    BO_Window.bind("<Button-1>", drag_start_canvas)
##    BO_Window.bind("<B1-Motion>", drag_motion_canvas)
##    BO_Window.bind("<ButtonRelease-1>", on_mouse_up_canvas)

    frame2=tk.Frame(my_canvas,bg="white",height=10000,width=1000)
    frame2.pack()

##    #Selection frame, composed by 4 stretched buttons
##    pixel = tk.PhotoImage(width=1, height=1)        
##    SelTopButton = tk.Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
##    SelBottomButton = tk.Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
##    SelLeftButton = tk.Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
##    SelRightButton = tk.Button(frame2, image=pixel,height=1, width=1,borderwidth=0,bg="red")
    
    my_canvas.create_window((0,0),window=frame2, anchor="nw")
    
    # Create a canvas inside the frame
    SelectionCanvas = tk.Canvas(frame2,height=10000,width=1000,bg="white")
    SelectionCanvas.pack()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    help_path = os.path.join(parent_dir, "help","Optimizer")

    New_icon = tk.PhotoImage(file = r"icons/new_setup.png")
    bNewSetup=tk.Button(frame1, text="NEW", command=New_Setup,image = New_icon, compound = tk.LEFT)
    bNewSetup.pack(side="left",padx=10)
    Load_icon = tk.PhotoImage(file = r"icons/load_setup.png")
    bLoad=tk.Button(frame1, text="LOAD", command=AskLoadOptimization,image = Load_icon, compound = tk.LEFT)
    bLoad.pack(side="left",padx=10)
    Save_icon = tk.PhotoImage(file = r"icons/save_setup.png")
    bSave=tk.Button(frame1, text="SAVE", command=AskSaveOptimization,image = Save_icon, compound = tk.LEFT)
    bSave.pack(side="left",padx=10)
    Run_icon = tk.PhotoImage(file = r"icons/run_setup.png")
    bRun=tk.Button(frame1, text="RUN", command=RunOptimizationButton,image = Run_icon, compound = tk.LEFT)
    bRun.pack(side="left",padx=10)
    Exit_icon = tk.PhotoImage(file = r"icons/exit_setup.png")
    bExit=tk.Button(frame1, text="EXIT", command=Close,image = Exit_icon, compound = tk.LEFT)
    bExit.pack(side="left",padx=10)

    Help_icon = tk.PhotoImage(file = r"icons/help_setup.png")
    bHelp=tk.Button(frame1, text="HELP", command=lambda: Help.ShowHelp(help_path),image = Help_icon, compound = tk.LEFT)
    bHelp.pack(side="left",padx=20)
    
    InitVars()

    ProcedureName=""
    for k, val in kwargs.items():
        if k=="File":
            ProcedureName=val
            CRC_Value=CRC(ProcedureName)
            File_Size=os.path.getsize(ProcedureName)

    BO_Window.wait_window()

    return BO_Window.return_code
