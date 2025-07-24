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
     print(e)   
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
            response = messagebox.askyesno("ERROR", "Cannot execute procedure. \nDo you want to see the missing objects?")
            if response:  # True if "Yes" is clicked
                if len(Missing)>1:
                    plural="s"
                else:
                    plural=""
                MissingObjects=Grid(window)
                MissingObjects.WriteOnHeader("Number of missing object"+plural)
                MissingObjects.WriteOnHeader("Object missing (Reagent, Connection, Apparatus)")
                MissingObjects.CloseHeader()
                for i,Missed in enumerate(Missing):
                    MissingObjects.AddItemToRow(str(i+1))
                    MissingObjects.AddItemToRow(Missed)
                    MissingObjects.NextRow()
                
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
    settings_menu = Menu(menubar,tearoff=0)
    settings_menu.add_command(label='Default macro settings')
    WizardWindow.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)
    menubar.add_cascade(label="Settings",menu=settings_menu)
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
