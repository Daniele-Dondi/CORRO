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


class BO_Object(tk.Frame):
    def __init__(self,container):
        self.Height=50
        self.Objects=[]
        self.text=""
        self.values=""
        super().__init__(container)
        self.config(relief=tk.GROOVE,borderwidth=4)        
        self.create_widgets()

    def create_widgets(self):
        self.Line1=tk.Frame(self)
        self.Line1.pack()
        self.Line2=tk.Frame(self)
        self.Line2.pack()        

        self.StatusLabel=tk.Label(self.Line2,text="---")
        self.StatusLabel.pack(side="left")

    def UserClicked(self,num):
        if self.Objects[num].config('relief')[-1] == 'raised':
            self.Objects[num].config(relief='sunken',bg="red")
        else:
            self.Objects[num].config(relief='raised',bg="white")

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
            self.Objects[-1].pack(side="left")

    
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
################################################################## end of classes ##################################################################
        
        
def InitVars():
    global ActionsArray, CurrentY, AvailableMacros, AvailableCommands, EmptyVolume
    ActionsArray=[]
    CurrentY=10

def StartBO_Window(window, OptimizerCode, **kwargs):
    InitVars()
                      
    def on_mousewheel(event):
        my_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def GetObjectPosition(object_y,sortedlist):
        try:
            for i,obj in enumerate(sortedlist):
                if obj[0]==object_y: return i
            return -1 #not found
        except:
            return -1

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


    Hidden=False
    filename=""
    for k, val in kwargs.items():
        if k=="Hide":
            Hidden=val
        elif k=="File":
            filename=val
    if filename:
        if Hidden:
            BO_Window.withdraw()
        LoadProcedures(filename)
        #CompiledCode=CheckProcedure(**kwargs)
        BO_Window.destroy()
        return CompiledCode
    
    BO_Window.mainloop()
