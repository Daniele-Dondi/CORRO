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
from modules.wizard import *
from modules.buildvercalculator import CRC

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

        # Max Entry
        label2=tk.Label(self.frame, text="Max Value:")
        label2.grid(row=1, column=0)
        self.max_entry = tk.Entry(self.frame)
        self.max_entry.grid(row=1, column=1, padx=5, pady=5)

    def SetMin(self,value):
        value=round(value,2)
        self.min_entry.delete(0,tk.END)
        self.min_entry.insert(0,str(value))

    def SetMax(self,value):
        value=round(value,2)
        self.max_entry.delete(0,tk.END)
        self.max_entry.insert(0,str(value))

    def GetValues(self):
        min_val = self.min_entry.get()
        max_val = self.max_entry.get()
        return [min_val, max_val]

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

    def UserClicked(self,num):
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

    def SetValues(self,element):
        text=element[1]
        self.text=element[1]
        values=element[0]
        self.values=element[0]
        parts=text.split("$")
        for num,part in enumerate(parts):
            if num % 2==0:
                self.Objects.append(tk.Label(self.Line1, text=part, font="Verdana 12"))
            else:
                self.Objects.append(tk.Button(self.Line1, text=values[int(part)], font="Verdana 12",bg="white",command=lambda j=num : self.UserClicked(j)))
                self.Height=105
                self.ParametersToChange.append(part)
                ThisMinMax=MinMaxApp(self.Line2)
                self.MinMaxs.append(ThisMinMax)
                FloatValue=float(values[int(part)])
                ThisMinMax.SetMin(FloatValue*0.8) #fill entries with +- 20% of current value
                ThisMinMax.SetMax(FloatValue*1.2)
                disable_widgets(ThisMinMax.frame)
            self.Objects[-1].pack(side="left")

    
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################

def StartOptimizer(window): 
    Optimizer_Window=tk.Toplevel(window)
    Optimizer_Window.title("REACTION OPTIMIZER SETUP")
    Optimizer_Window.geometry('200x500+400+10')
    Optimizer_Window.grab_set()
    New_icon = PhotoImage(file = r"icons/new_setup.png")
    bNewSetup=Button(Optimizer_Window, text="NEW", command=lambda: New_Setup(Optimizer_Window),image = New_icon, compound = LEFT)
    bNewSetup.pack()
    Load_icon = PhotoImage(file = r"icons/load_setup.png")
    bLoad=Button(Optimizer_Window, text="EDIT", command=lambda: Edit_Setup(Optimizer_Window),image = Load_icon, compound = LEFT)
    bLoad.pack()
    Run_icon = PhotoImage(file = r"icons/run_setup.png")
    bRun=Button(Optimizer_Window, text="RUN", command=lambda: Run_Setup(Optimizer_Window),image = Run_icon, compound = LEFT)
    bRun.pack()
    Exit_icon = PhotoImage(file = r"icons/exit_setup.png")
    bExit=Button(Optimizer_Window, text="EXIT", command=lambda: Exit_Setup(Optimizer_Window),image = Exit_icon, compound = LEFT)
    bExit.pack()
                               
    Optimizer_Window.mainloop()


def New_Setup(window):
    filename=ChooseProcedureFile()
    if filename=="": return
    OptimizerCode=StartWizard(window,Hide=True,File=filename,Mode="Optimizer")
    if ThereAreErrors(window,OptimizerCode): return
    StartBO_Window(window,OptimizerCode,File=filename)    

def Edit_Setup(window):
    return

def Run_Setup(window):
    return

def Exit_Setup(window):
    window.destroy()

def StartBO_Window(window, OptimizerCode, **kwargs):
                      
    def on_mousewheel(event):
        my_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def Close():
        BO_Window.destroy()

    BO_Window=tk.Toplevel(window)
    BO_Window.title("BAYESIAN OPTIMIZATION SETUP")
    BO_Window.geometry('1000x800+400+10')
    BO_Window.grab_set()
    menubar = Menu(BO_Window)
    file_menu = Menu(menubar,tearoff=0)
    file_menu.add_command(label='New')#,command=New)
    file_menu.add_separator()    
    file_menu.add_command(label='Load Procedure')#,command=AskLoadProcedures)
    file_menu.add_command(label='Append Procedure')#,command=AskImportProcedures)    
    file_menu.add_command(label='Save Procedure')#,command=AskSaveProcedures)
    file_menu.add_separator()
    file_menu.add_command(label='Exit',command=Close)
    settings_menu = Menu(menubar,tearoff=0)
    settings_menu.add_command(label='Default macro settings')
    BO_Window.config(menu=menubar)
    menubar.add_cascade(label="File",menu=file_menu)
    menubar.add_cascade(label="Settings",menu=settings_menu)
    menubar.add_cascade(label="Process Check")#,command=CheckProcedure)
    frame1 = tk.Frame(BO_Window)
    frame1.pack(side="top")
    frame3 = tk.Frame(BO_Window,bg="gray",width=1000,height=30)
    frame3.pack(side="bottom")
    
    my_canvas = Canvas(BO_Window)
    my_canvas.pack(side=LEFT,fill=BOTH,expand=1)
    y_scrollbar = ttk.Scrollbar(BO_Window,orient=VERTICAL,command=my_canvas.yview)
    y_scrollbar.pack(side=RIGHT,fill=Y)
    my_canvas.configure(yscrollcommand=y_scrollbar.set)
    my_canvas.bind("<Configure>",lambda e: my_canvas.config(scrollregion= my_canvas.bbox(ALL)))
    BO_Window.bind("<MouseWheel>", on_mousewheel)
##    BO_Window.bind("<Button-1>", drag_start_canvas)
##    BO_Window.bind("<B1-Motion>", drag_motion_canvas)
##    BO_Window.bind("<ButtonRelease-1>", on_mouse_up_canvas)

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

    tk.Button(frame1,text="Pour liquid").pack(side="left")


    tk.Button(frame3,text="Process Check").pack(side="left")#,command=CheckProcedure).pack(side="left")
    
    CreatedProcedures=[]
    CurrentY=10
    for element in OptimizerCode:
        Obj=BO_Object(frame2)
        CreatedProcedures.append(Obj)
        Obj.SetValues(element)
        YSize=Obj.Height
        Obj.place(x=10,y=CurrentY)
        CurrentY+=YSize

    filename=""
    for k, val in kwargs.items():
        if k=="File":
            filename=val
            CRC_Value=CRC(filename)
            File_Size=os.path.getsize(filename)
            print(filename,CRC_Value,File_Size)
    
    BO_Window.mainloop()
