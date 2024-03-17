 # Program CORRO
 #
 # Copyright (c) 2024 Daniele Dondi
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program.  If not, see <https://www.gnu.org/licenses/>.
 #
 #
import PIL.Image
from threading import Timer
import tkinter
import threading
import math
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import dialog
from tkinter import ttk
import time
import datetime
import os
import serial
from os import listdir
from os.path import isfile, join
import sys
sys.path.append('Printrun') #put here your path to Printrun software
from printrun.printcore import *
from printrun.utils import *
from printrun import gcoder
import logging

#global vars
connected = 0
#robot      #printrun handle for robot
#syringe #printrun handle for syringe
electrodes = 0 #serial handle for electrodes
loadcell = 0 #serial handle for load cell
HasRobot = False
HasElectrodes = False
HasLoadCell = False
SyringeUSB = ""
RobotUSB = ""
ElectrodesUSB = ""
LoadCellUSB = ""
SyringeUSBrate = 0
RobotUSBrate = 0
ElectrodesUSBrate = 0
LoadCellUSBrate = 0
debug=True #if true print additional information to console
noconnect=False #if true no connection with hardware is done
noprint_debug=False #if true save gcode commands to file instead sending them to syringebot
WatchdogMax=2000 #max number of instructions before a message asking if there is an infinite loop
if noprint_debug: cmdfile=open("gcodecmds.txt","a")
T_Actual = 0
T_SetPoint = 0
Temp_points=[] #array of temperature points
MAX_Temp=10
V1_points=[] #array of potential points (probe 1)
MAX_V1=0.01
V2_points=[] #array of potential points (probe 2)
MAX_V2=0.01
last_V1=0.01
last_V2=0.01
W_points=[] #array for weights
last_W=0.0
MAX_W=0.1
macrolist = [] #list of avail macros
macrob=[]      #macro button array
IsEditingMacro=0
IsDeletingMacro=0
visible = 1
chart_w=800 #size of the temp and voltages chart
chart_h=600
w_fullsize=True #chart starts fullsize. It can be resized with F1
Show_Macros_Button=True
macrout=0      #global var for macros. Filled when macro returns a value
pixboundedmacro=[] # list of macros bound to pixels
colorsbound=[]     # list of colors bound. Refers to above macros name
NewColorAssignment=0 # if a user assign a color during runtime this var is set to 1
logfile=0
Gcode0=[] #array for the gcode commands (buffer/print commands)
IsBuffered0=False
SyringeBOT_IS_BUSY=False
SyringeBOT_WAS_BUSY=False
SyringeBOT_IS_INITIALIZED=False
#following parameters will be read from configuration.txt file
NumSyringes=0 #Number of installed syringes
SyringeMax=[1,2,3,4,5,6] #Syringe height of graduated part in millimeters
SyringeVol=[1,2,3,4,5,6] #Syringe max volume in milliliters
VolInlet=0   #volume of the inlet tube
VolOutlet=0  #volume of the outlet tube
SchematicImage="" #file name for the image
MaskImage=""      #file name for the mask image
MaskMacros=""     #file name for the bounded colors to macros
oldprogress=0
# Hooks
Temperature_Hook=False
Temperature_Hook_Value="" #valid values are >xxx <yyy
Temperature_Hook_Macro="" #macro to call when condition is true
Time_Hook=False
Time_Hook_Value="" #valid values are >xxx <yyy
Time_Hook_Macro="" #macro to call when condition is true
#macro global variables.
#Global variables are variables that are available to all scripts and are kept up to program exit.
#To access them use the reserved commands getglobal and setglobal
global_vars=[]

def on_closing():
        Close()

def showscheme():
    global visible,chart_h,chart_w,w_fullsize
    if w_fullsize:
     chart_w=800
     chart_h=300
     w.config(width=chart_w,height=chart_h)
     IM.pack() #show graphical control
     w_fullsize=False
    else: 
     chart_w=800
     chart_h=600
     w.config(width=chart_w,height=chart_h)
     IM.pack_forget() #hide graphical control
     w_fullsize=True

def resize():
    global visible,chart_h,chart_w,w_fullsize,Show_Macros_Button
    if visible==1:
     Z.pack_forget()   
     F.pack_forget()
     visible = 0
    else:
     Graph.pack_forget() #hide chart
     IM.pack_forget() #hide graphical control
     F.pack(side="left",fill="y")
     if Show_Macros_Button==True: Z.pack(side="left",fill="y")
     Graph.pack(side="bottom")
     if not(w_fullsize): IM.pack() #show graphical control
     visible = 1
    

def keypress(event):  #keyboard shortcuts
    global Show_Macros_Button,visible
    if event.keysym == 'Escape': #quit program
        Close()
    if event.keysym == 'Alt_L': #show/hide commands
        resize()
    if event.keysym == 'F1': #show/hide schematic and resize chart canvas
        showscheme()
    if event.keysym == 'F2': #show/hide macro controls
        Show_Macros_Button=not(Show_Macros_Button)
        resize()
        resize()

def readConfigurationFiles():
    global NumSyringes,SyringeMax,SyringeVol,VolInlet,VolOutlet,SchematicImage,MaskImage,MaskMacros,colorsbound,pixboundedmacro
    global SyringeUSB,RobotUSB,ElectrodesUSB,LoadCellUSB,SyringeUSBrate,RobotUSBrate,ElectrodesUSBrate,LoadCellUSBRate
    global HasRobot,HasElectrodes,HasLoadCell
    try:
        conf_file = open("conf"+os.sep+"configuration.txt", "r") #open configuration.txt and read parameters
        lines=conf_file.readlines()
        conf_file.close()
        NumSyringes=int(lines[1].strip())
        for x in range(NumSyringes):
            l=lines[3+x].split(";")
            SyringeMax[x]=float(l[0].strip())*2 #annoyngly we have to multiply by 2 to have the correct movement in mm
            SyringeVol[x]=float(l[1].strip())
        curline=4+NumSyringes
        VolInlet=float(lines[curline].strip())
        curline+=2
        VolOutlet=float(lines[curline].strip())
        curline+=2
        SchematicImage="conf"+os.sep+lines[curline].strip()
        MaskImage=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-mask.png" #define automatically the names of mask and binds from the schematic image name
        MaskMacros=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-binds.txt"
        curline+=2; SyringeUSB=lines[curline].strip() 
        curline+=2; SyringeUSBrate=lines[curline].strip()
        curline+=2; ElectrodesUSB=lines[curline].strip()
        curline+=2; ElectrodesUSBrate=lines[curline].strip()
        curline+=2; RobotUSB=lines[curline].strip()
        curline+=2; RobotUSBrate=lines[curline].strip()
        curline+=2; LoadCellUSB=lines[curline].strip()
        curline+=2; LoadCellUSBrate=lines[curline].strip()
        if (ElectrodesUSB!=""): HasElectrodes = True; ElectrodesUSBrate=int(ElectrodesUSBrate)
        if (RobotUSB!=""): HasRobot = True; RobotUSBrate=int(RobotUSBrate)
        if (LoadCellUSB!=""): HasLoadCell = True; LoadCellUSBrate=int(LoadCellUSBrate)
    except:    
     tkinter.messagebox.showerror("ERROR","Error reading configuration file. Please quit program")
    try: #open configuration-binds.txt
     bind_file = open(MaskMacros, "r")
     lines=bind_file.readlines()
     bind_file.close()
     NumBinds=int(lines[1].strip())
     for x in range(NumBinds):        
      pixboundedmacro.append(lines[3+x].strip())
      colorsbound.append(eval(lines[4+x+NumBinds]))
    except:
     tkinter.messagebox.showwarning("Warning","Current schematic has no colors defined with macros")


def onclick(event):
    global pix,pixboundedmacro,colorsbound,debug   
    print ("clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print (color)
    if color in colorsbound:
     macroname=pixboundedmacro[colorsbound.index(color)]   
     if(debug): print(macroname)
     try:
       macronum=macrolist.index(macroname)
       Macro(macronum,str(color[0])+','+str(color[1])+','+str(color[2])) #by default passes color arguments to macro
     except:
       tkinter.messagebox.showerror("ERROR","Problem executing macro "+macroname)  

def onmiddleclick(event):
    global pix,pixboundedmacro,colorsbound    
    print ("clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print ('middle',color)
    if color in colorsbound:
     MsgBox = tkinter.messagebox.askquestion ('Unbound color','Are you sure you want to unbound macro for this color?',icon = 'warning')
     if MsgBox == 'yes':
      idx=colorsbound.index(color)
      del colorsbound[idx]
      del pixboundedmacro[idx]

def onrightclick(event):
    global pix
    print ("right clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print (color)
    if color in colorsbound:
        tkinter.messagebox.showerror('ERROR','Color already assigned. Use middle click do debound first')
        return
    binder = tkinter.Toplevel(base)
    binder.title("bind an event to this color")
    Label(binder,text='bind an event to this color').pack()
    comboMacro = ttk.Combobox(binder, values=macrolist, width=40)
    comboMacro.pack()
    Button(binder, text="OK",command=lambda: Bind(comboMacro.get(),color,binder)).pack()
    Button(binder, text="CANCEL",command=lambda: binder.destroy()).pack()
    binder.grab_set()

def Bind(text,color,window):
    global pixboundedmacro,colorsbound,NewColorAssignment,debug
    if text=="" or text==None: return
    if text in macrolist:
      if not(color in colorsbound):
          colorsbound.append(color)
          pixboundedmacro.append(text)
          window.destroy()
          if(debug): print('macro "',text,'" assigned to color ',color)
          NewColorAssignment=1
      else:     tkinter.messagebox.askquestion ('error','color already assigned',icon = 'warning')
    else:     tkinter.messagebox.askquestion ('error','macro not found',icon = 'warning')  
  
         
#Main window
base = Tk()
#base.attributes("-fullscreen", True) #go FULLSCREEN
base.bind('<Key>', keypress)
F = Frame(base)
F.pack(side="left",fill="y")
Z = Frame(base,bd=2,relief=RIDGE) #macros frame
Z.pack(side="left",fill="y")
try:  #read macros and decide if we have to create a second palette
 for file in os.listdir("macros"):
    if file.endswith(".txt"): #all files in macros folder having .txt extension are considered macros
        macrolist.append(file[:-4]) #remove .txt from name
except:
    tkinter.messagebox.showerror("ERROR", "MACRO directory unreachable")
else:
  macrolist.sort()     
  if len(macrolist)>28:
          ZZ = Frame(base,bd=2,relief=RIDGE) #macros frame
          ZZ.pack(side="left",fill="y")
          Label(ZZ, text="MACROS 2",font="Verdana 10 bold",bg='pink').pack(pady=10)
Z2 = Frame(base,bd=2,relief=RIDGE) #macros frame
Z2.pack(side="left",fill="y")          
K = Frame(F)
K.pack(side="bottom")
J = Frame(F)
J.pack(side="bottom")
I = Frame(F)
I.pack(side="bottom")
H = Frame(F)
H.pack(side="bottom")
G = Frame(F)
G.pack(side="bottom")
Graph=Frame(base)
Graph.pack(side="bottom")
w=Canvas(Graph,width=chart_w,height=chart_h)
w.pack(expand=YES,fill=BOTH)

IM=Frame(base)
IM.pack(side="left")
w2=Canvas(IM,width=800,height=600)
w2.bind("<Button-1>", onclick) #bind click procedure to graphic control
w2.bind("<Button-2>", onmiddleclick) #bind click procedure to graphic control
w2.bind("<Button-3>", onrightclick) #bind click procedure to graphic control
w2.pack()
#Load configuration file
readConfigurationFiles()
Aimage=PhotoImage(file=SchematicImage) # load the scheme of the current configuration
w2.create_image(0, 0, image = Aimage, anchor=NW)
im = PIL.Image.open(MaskImage) # load the mask here
pix = im.load()
#IM.pack_forget()
showscheme()


#FUNCTIONS

def SaveMacro(text,macronumber,window): #save a macro
    if macronumber==-1:
        while True:
         filename = tkinter.simpledialog.askstring('MACRO NAME','Please assign a name to this macro')
         if filename in macrolist: tkinter.messagebox.showerror("ERROR","Macro name already in use. Choose another name")
         elif filename == "": tkinter.messagebox.showerror("ERROR","Please assign a name")
         elif filename == None:
             tkinter.messagebox.showerror("ERROR","Macro will not be saved")
             window.destroy()
             return
         else: break
        macronumber=len(macrolist)
        macrolist.append(filename)
        macrob.append(Button(Z, text=filename,command=lambda j=macronumber : Macro(j)))
        macrob[len(macrob)-1].pack()
    text_file = open("macros/"+macrolist[macronumber]+".txt", "w")
    text_file.write(text)
    text_file.close()
    window.destroy()

def MacroEditor(macronumber): #edit a macro or create a new one
     if macronumber!=-1: title=macrolist[macronumber] #-1 = create a new macro
     else: title='NEW MACRO'
     t = tkinter.Toplevel(base)
     t.title(title)
     a=Text(t,width=90,height=30)
     if macronumber!=-1:
        text_file = open("macros/"+macrolist[macronumber]+".txt", "r")
        text=text_file.read()
        text_file.close()
        a.insert(INSERT, text)
     a.pack()
     Button(t, text="SAVE",command=lambda: SaveMacro(a.get("1.0",END),macronumber,t)).pack()
     Button(t, text="CANCEL",command=lambda: t.destroy()).pack()
     t.grab_set()
     
def SubstituteVarValues(line,variables): #substitute var names $var$ with their values
    global macrout
    for var in range(0,len(variables),2):
        line=line.replace(variables[var],str(variables[var+1]))
    line=line.replace('$return$',str(macrout))
    return line    

def RefreshVarValues(var_name,value,variables): #if a variable exists, update its value. If it does not exist, create it
    if not(var_name in variables):  #variable not present
       variables.append(var_name)   #save var name
       variables.append(value)      #save value
    else:
      variables[variables.index(var_name)+1]=value
      return 1

def GetVarValue(var_name,variables): #retrieve a value of var_name
    if not(var_name in variables):  #variable not present
     tkinter.messagebox.showerror("ERROR",var_name+" not present in variables")
    else:
      return variables[variables.index(var_name)+1]

def Parse(line,variables):    #parse macro lines and execute statements
    global logfile,IsBuffered0,Gcode0,debug,cmdfile,SyringeBOT_IS_INITIALIZED
    global NumSyringes, SyringeMax, SyringeVol, VolInlet, VolOutlet #global parameters for syringes taken from configuration.txt
    global Temperature_Hook,Temperature_Hook_Value,Temperature_Hook_Macro,Time_Hook,Time_Hook_Value,Time_Hook_Macro
    global global_vars
    #line = line.split(";", 1)[0] #remove comments (present eventually after ;)
    #line=line.rstrip()  #remove cr/lf
    if line=="": return
    if line.find('log')==0: #print string to log file
     try:
      commands=line.split(' ',1)
      commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
      if(debug): print(commands[1])
      logfile.write(str(datetime.datetime.now())+"\t"+commands[1]+"\n")
     except:
      tkinter.messagebox.showerror("ERROR in log method","use: log text")
      return "Error"
    elif (line.find('buffer')==0)or(line.find('record')==0): #buffer all commands, send later. Used for long gcode sequence where send will fail
        IsBuffered0=True
        Gcode0=[]
    elif (line.find('print')==0)or(line.find('play')==0): #send all buffered commands. Used for long gcode sequences
        if (IsBuffered0):
            IsBuffered0=False
            if noprint_debug==False: StartPrint0()
            else:
             cmdfile.write("                     "+str(datetime.datetime.now())+"\n")
             for lin in Gcode0:
              cmdfile.write(lin+'\n')
    elif line.find('ask')==0: #if ask, make question to user
     try:
      commands=line.split(',',6)
      commands[0]=commands[0][4:] # remove ask
      for c in range(len(commands)-1):
          commands[c+1]=SubstituteVarValues(commands[c+1],variables)
      x = tkinter.simpledialog.askfloat(commands[1], commands[2]+' ['+str(commands[4])+' ... '+str(commands[5]+']'),initialvalue=float(commands[3]), minvalue=float(commands[4]), maxvalue=float(commands[5]))
      if x==None: return "Cancel"
      RefreshVarValues(commands[0],x,variables)
     except:
      tkinter.messagebox.showerror("ERROR in ask method","use: ask $varname$,title,question,initialvalue,minvalue,maxvalue")
      return "Error"
    elif line.find('getsyringeparms')==0: #load the values for the syringe  
     try:
      axisnames=["X","Y","Z","I","J","K"]   
      commands=line.split(' ',1)
      commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
      commands[1]=int(commands[1])-1 #Syringe n is in n-1 position inside the array
      RefreshVarValues("$syringemax$",SyringeMax[commands[1]],variables)
      RefreshVarValues("$syringevol$",SyringeVol[commands[1]],variables)
      RefreshVarValues("$volinlet$",VolInlet,variables)
      RefreshVarValues("$voloutlet$",VolOutlet,variables)
      RefreshVarValues("$axisname$",axisnames[commands[1]],variables)
      RefreshVarValues("$numsyringes$",int(NumSyringes),variables)
     except:
      tkinter.messagebox.showerror("ERROR in getsyringeparms method","use: getsyringeparms syringenumber")
      return "Error"
    elif line.find('eval')==0: #we've to calculate somethg
      try:
       commands=line.split(',',1)
       commands[0]=commands[0][5:] # remove eval
       x = eval(SubstituteVarValues(commands[1],variables)) #substitute variable names with values
       RefreshVarValues(commands[0],x,variables)
      except:
       tkinter.messagebox.showerror("ERROR in eval method","use: eval $varname$,math_expression")
       return "Error"
    elif line.find('let')==0: #variable assignment
      try:
       commands=line.split(',',1)
       commands[0]=commands[0][4:] # remove command
       x = SubstituteVarValues(commands[1],variables) #substitute variable names with values
       RefreshVarValues(commands[0],x,variables)
      except:
       tkinter.messagebox.showerror("ERROR in let method","use: let $varname$,value or variable")
       return "Error"
    elif line.find('createarray')==0: #create an array of vars called base_varname1, 2, ...
      try:
       commands=line.split(',',1)
       commands[0]=commands[0][12:] # remove command
       basevarname="$"+commands[0]
       commands[1]=SubstituteVarValues(commands[1],variables) #number of elements might be a variable
       numvarsinarray=int(commands[1])+1
       for x in range(1,numvarsinarray):
         RefreshVarValues(basevarname+str(x)+"$",0,variables) #create vars from 1 to number
      except:
       tkinter.messagebox.showerror("ERROR in createarray method","use: createarray base_varname,number_of_elements_in_array")
       return "Error"
    elif line.find('getelement')==0: #retrieve an element from array
      try:
       commands=line.split(',',2)
       commands[0]=commands[0][11:] # remove command
       commands[2]=SubstituteVarValues(commands[2],variables) #number of element might be a variable
       varname="$"+commands[0]+commands[2]+"$"
       x=GetVarValue(varname,variables)
       RefreshVarValues(commands[1],x,variables) #store value in store_var
      except:
       tkinter.messagebox.showerror("ERROR in getelement method","use: getelement base_varname,store_var,number_of_element")
       return "Error"
    elif line.find('setelement')==0: #set an element of an array
      try:
       commands=line.split(',',2)
       commands[0]=commands[0][11:] # remove command
       commands[1]=SubstituteVarValues(commands[1],variables) #number of element might be a variable
       commands[2]=SubstituteVarValues(commands[2],variables) #value of element might be a variable
       varname="$"+commands[0]+commands[1]+"$"
       RefreshVarValues(varname,commands[2],variables) #store value in store_var
      except:
       tkinter.messagebox.showerror("ERROR in setelement method","use: setelement base_varname,number_of_element,value")
       return "Error"
    elif line.find('exec')==0: #we've to execute somethg
      try:
       commands=line.split('!,')
       commands[0]=commands[0][5:] # remove exec
       code=SubstituteVarValues(commands[0],variables) #substitute variable names with values
       code=code.replace('/n',os.linesep) # /n in code is translated in newline
       commands=commands[1].split(',')
       codevars=[]
       namevars=[]
       for x in range(0,len(commands)):
        temp=commands[x].split('=')   
        codevars.append(temp[0])
        namevars.append(temp[1])
       g=dict()
       l=dict()
       exec(code,g,l)
       for x in range(0,len(namevars)):
           RefreshVarValues(namevars[x],l[codevars[x]],variables)
      except:
       tkinter.messagebox.showerror("ERROR in exec method","use: exec code!,varname1=$var1$,...")
       return "Error"
    elif line.find('macro')==0: #we've to call a nested macro
      try:
       commands=line.split('"',2)
       try:
        num=macrolist.index(commands[1])
        if commands[2]!="": Macro(num,SubstituteVarValues(commands[2],variables))
        else:
         err=Macro(num)
         if err=="Error":
           print("Macro ended with an error")      
           return "Error"
       except ValueError:  tkinter.messagebox.showerror("ERROR in macro call",'macro '+commands[1]+' does not exist')
      except:
       tkinter.messagebox.showerror("ERROR in macro call",'use: macro "macroname" var1,var2..')
       return "Error"
    elif line.find('echo')==0: #we've to echo to the console
      try:
       commands=line.split(' ',1)
       commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
       if(debug): print(commands[1])
      except:
       tkinter.messagebox.showerror("ERROR in echo method","use: echo text $varname$")
       return "Error"
    elif line.find('hook')==0: #we've to create an hook (temperature or timer)
      try:
       commands=line.split(' ')
       macro_command=line.split('"')[1]
       num=macrolist.index(macro_command) #if macro does not exist we'll receive an error       
       if commands[1]=="temp":
         Temperature_Hook_Value=commands[2]
         Temperature_Hook_Value=SubstituteVarValues(Temperature_Hook_Value,variables) #eventually substitute var names with their values
         if not(Temperature_Hook_Value[0] in [">","<"]):
                 num=1/0
         Temperature_Hook_Macro=macro_command
         Temperature_Hook=True      
         b_temp.pack()     
       elif commands[1]=="time":
         time=commands[2]
         time=SubstituteVarValues(time,variables) #eventually substitute var names with their values
         hours=0
         minutes=0
         seconds=0
         if 'h' in time:
          hours=int(time.split('h',1)[0])
          time=time.split('h')[1]
         if 'm' in time:
          minutes=int(time.split('m',1)[0])
          time=time.split('m')[1]            
         if 's' in time:
          seconds=int(time.split('s',1)[0])
         datet=datetime.datetime.now()         
         new_datet=datet+datetime.timedelta(hours=hours,minutes=minutes,seconds=seconds)
         Time_Hook=True
         Time_Hook_Value=new_datet
         Time_Hook_Macro=macro_command
         b_clock.pack() 
       else:
         a=1/0      
       if(debug): print(commands[1])
      except:
       tkinter.messagebox.showerror("ERROR in hook method",'use: hook temp or time $value$ "macroname"\nif time is defined use the format xxhxxmxxs')
       return "Error"
    elif line.find('writegcode')==0: #we've to write the gcode recorded
      try:
       commands=line.split(' ',1)
       with open(commands[1], 'w') as fp:
        fp.write('\n'.join(map(str, Gcode0)))
       fp.close() 
      except:
       tkinter.messagebox.showerror("ERROR in writegcode method","use: writegcode filename")
       return "Error"
    elif line.find('readgcode')==0: #we've to read the gcode recorded
      try:
       commands=line.split(' ',1)
       with open(commands[1]) as fp:
        Gcode0 = fp.readlines()
       fp.close()
       IsBuffered0=True
      except:
       tkinter.messagebox.showerror("ERROR in readgcode method","use: readgcode filename")
       return "Error"
    elif line.find('message')==0: #show a messagebox
      try:
       commands=line.split(' ',1)
       commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
       tkinter.messagebox.showinfo('info',commands[1])
      except:
       tkinter.messagebox.showerror("ERROR in message method","use: message text $varname$")
       return "Error"
    elif line.find('setglobal')==0: #upload a variable in the global variable list
      try:
       commands=line.split(' ')
       for var in commands[1:]:
        var_name=var
        value=SubstituteVarValues(var,variables) #substitute var name with its value
        RefreshVarValues(var_name,value,global_vars) #register it in global variables
      except:
       tkinter.messagebox.showerror("ERROR in setglobal method","use: setglobal $varname$ [$varname2$]") 
       return "Error"
    elif line.find('getglobal')==0: #retrieve a variable in the global variable list            
      try:
       commands=line.split(' ')
       for var in commands[1:]:
        var_name=var
        value=SubstituteVarValues(var,global_vars) #retrieve its value
        RefreshVarValues(var_name,value,variables) #register it in local variables
      except:
       tkinter.messagebox.showerror("ERROR in setglobal method","use: getglobal $varname$ [$varname2$]") 
       return "Error"
    elif line.find('send')==0:
      try:
       commands=line   
       commands=line.split(',',1)
       commands[0]=commands[0][5:] # remove send
       commands[0] = SubstituteVarValues(commands[0],variables) #substitute variable names with values
       sendcommand(commands[0],int(commands[1]))
      except:
       tkinter.messagebox.showerror("ERROR in send method","use: send command,where")
       return "Error"
    else:
        #command not recognized
        print('unknown command')
        return "Error"

def Macro(num,*args): #run, delete or edit a macro 
    global IsEditingMacro,IsDeletingMacro,macrob,macrout,debug,WatchdogMax,SyringeBOT_IS_INITIALIZED,SyringeBOT_IS_BUSY
    watchdog=0 #this is used to avoid infinite loops
    variables=[] #macro's internal variables
    stack=[] #stack keeps line numbers for cycles
    labels=[] #labels are special variables containing line numbers to be used for goto and jump instructions
    for ar in args:  #we have some variables passed to the macro
      par=ar.split(',')
      for x in range(0,len(par)):
          RefreshVarValues('$'+str(x+1)+'$',par[x],variables)
    if IsEditingMacro==0:
     if IsDeletingMacro==0:
      if connected==0:   
        MsgBox = tkinter.messagebox.askquestion ('Not Connected','SyringeBOT is not connected. Connect now?',icon = 'error')
        if MsgBox == 'yes':
            Connect()
            try:
             num=macrolist.index("INIT_ALL")
            except:
             tkinter.messagebox.showerror("GENERAL ERROR","Macro INIT_ALL not found. Impossible to continue.")
             return
            Macro(num)
            return
      if connected==1:   #we are connected
       if SyringeBOT_IS_INITIALIZED==False: #syringebot is not initialized
        if not(macrolist[num])=="INIT_ALL": #only call to INIT_ALL is allowed
         MsgBox = tkinter.messagebox.showerror ('SyringeBOT is not initialized','Initialize first',icon = 'error')
         return
        else:
         SyringeBOT_IS_INITIALIZED=True #we set true because we are executing INIT_ALL
       if SyringeBOT_IS_BUSY==True:
        MsgBox = tkinter.messagebox.showerror ('SyringeBOT is BUSY','SyringeBOT IS BUSY! Wait for the task end',icon = 'error')
        return
       if(debug): print('executing macro:',macrolist[num])
       with open('macros/'+macrolist[num]+'.txt') as macro_file:
        lines=macro_file.readlines() #read the entire file and put lines into an array
        i=0
        for j in range(len(lines)):
         line=lines[j]
         line = line.split(";", 1)[0] #remove comments (present eventually after ;)
         line=line.strip()  #remove cr/lf
         lines[j]=line #save the cleaned string back to array 
         if (line.find('label')==0): #before executing the code search all the labels and put them into the label array
           label=line.split(' ',1)
           if (RefreshVarValues(label[1],j,labels)==1):  # insert the current line number in the labels set
             tkinter.messagebox.showerror("Duplicated label","Error: a label name is duplicated")      
             tkinter.messagebox.showerror("Error in code:","macro name: "+macrolist[num]+"\nline: "+str(i)+"\ncommand: "+line)
             return
        while (i<len(lines)):
         line=lines[i]
         i=i+1
         watchdog=watchdog+1
         if (watchdog>WatchdogMax): #watchdog counter, try to avoid infinite loops
          MsgBox = tkinter.messagebox.askquestion ('Infinite Loop?','It seems that we are doing a lot of cycles. Continue?',icon = 'warning')
          if MsgBox == 'yes': #if cycles exceed the number above and the user reply 'yes' continue to run
           watchdog=0
          else: return 
         isfor=line.find('for')==0
         isnext=line.find('next')==0
         islabel=line.find('label')==0
         isjump=line.find('jump')==0
         isif=line.find('if')==0
         if (isfor|isnext|islabel|isjump|isif): #in the case of for/next, label, jump and if statements, the code is analyzed in this section and not in the command parser
          if isfor: #for
           stack.append(i)
           var=line.split(' ',2)
           stack.append(var[1].rstrip())
           value=int(SubstituteVarValues(var[2].rstrip(),variables))
           RefreshVarValues(var[1],value,variables)
           if(debug): print(stack)
          elif isnext: #next
           for_variable=stack[-1]
           value=int(SubstituteVarValues(for_variable,variables))-1
           RefreshVarValues(for_variable,value,variables)
           if value>0:
            i=int(stack[-2])
            line=lines[i]
           else: 
            del(stack[-1])
            del(stack[-1])
          elif isjump: #jump (unconditioned jump)
           label=line.split(' ',1)
           try:
            i=labels[labels.index(label[1])+1]
           except:
            tkinter.messagebox.showerror("ERROR in jump","label not defined")
            tkinter.messagebox.showerror("Error in code:","macro name: "+macrolist[num]+"\nline: "+str(i)+"\ncommand: "+line)
            return
          elif isif: #if statement
           label=line.split(' ',2)
           if (SubstituteVarValues(label[1],variables))=="True":
            if label[2].find('macro')==0: #if macro is present we are going to execute a macro
             Parse(label[2],variables)
            else:                         #otherwise we are going to jump to a label
             try:
              i=int(SubstituteVarValues(label[2],labels))
             except:
              tkinter.messagebox.showerror("ERROR in if","label not defined")
              tkinter.messagebox.showerror("Error in code:","macro name: "+macrolist[num]+"\nline: "+str(i)+"\ncommand: "+line)
              return
         else:
          exitcode=Parse(line,variables)
          if exitcode=="Error": #execute code contained in line. In the case of error abort
              tkinter.messagebox.showerror("Error in code:","macro name: "+macrolist[num]+"\nline: "+str(i)+"\ncommand: "+line)
              return "Error"
          elif exitcode=="Cancel":
              tkinter.messagebox.showwarning("Warning","Operation interrupted by the user")    
              return "Error"    
       if '$return$' in variables: macrout=SubstituteVarValues("$return$",variables) #when a macro returns a value it's automatically set the reserved variable $return$
       if (debug): print (variables)  #DEBUG
      else:  tkinter.messagebox.showerror("ERROR","Not connected. Connect first")
     else:  #delete macro
      MsgBox = tkinter.messagebox.askquestion ('Delete macro','Are you sure you want to delete macro '+macrolist[num]+" ?",icon = 'warning')
      if MsgBox == 'yes':
        macrob[num].destroy() #remove macro button
        os.remove("macros/"+macrolist[num]+".txt") #delete text file (recovery is impossible)
        macrolist[num]=""  #remove macro from the list
      DeleteMacro()  
    else: #edit macro
     MacroEditor(num) #open the macro editor  
     EditMacro()


def CreateMacro():
     global IsEditingMacro,IsDeletingMacro
     if IsDeletingMacro==1: DeleteMacro()
     if IsEditingMacro==1: EditMacro()
     MacroEditor(-1) #-1 = create new macro
     
def EditMacro():
    global IsEditingMacro,IsDeletingMacro
    if IsEditingMacro==0:
     ToggleB.config(relief=SUNKEN)
     IsEditingMacro=1
     if IsDeletingMacro==1: DeleteMacro()
     base.config(cursor='cross')
    else:
     IsEditingMacro=0
     ToggleB.config(relief=RAISED)
     base.config(cursor='arrow')          

def DeleteMacro():
    global IsEditingMacro,IsDeletingMacro
    if IsDeletingMacro==0:
     ToggleB2.config(relief=SUNKEN)
     IsDeletingMacro=1
     if IsEditingMacro==1: EditMacro()
     base.config(cursor='pirate')
    else:
     IsDeletingMacro=0
     ToggleB2.config(relief=RAISED)
     base.config(cursor='arrow')     

#Quit program
def Close():
 global pixboundedmacro,colorsbound,NewColorAssignment,MaskMacros,cmdfile
 if connected != 0:
     tkinter.messagebox.showerror("ERROR","Disconnect first")
 else:
  MsgBox = tkinter.messagebox.askquestion ('Exit Application','Are you sure you want to exit the application?',icon = 'warning')
  if MsgBox == 'yes':  
     #insert here the save config file  TODO
     if NewColorAssignment==1:
        MsgBox = tkinter.messagebox.askquestion ('Save color assignment','Do you want to save new assignments?',icon = 'question')
        if MsgBox == 'yes':
         out_file = open(MaskMacros, "w")
         out_file.write("#num of bound colors\n")
         out_file.write(str(len(pixboundedmacro))+"\n#pixboundedmacro\n")
         for pix in pixboundedmacro:
          out_file.write(pix+"\n")
         out_file.write("#colorbound\n")
         for col in colorsbound:
          out_file.write(str(col)+"\n")          
         out_file.close()
         if(debug):
             print(pixboundedmacro)
             print(colorsbound)
     if noprint_debug: cmdfile.close()        
     base.destroy()

def ResetChart():
  global Temp_points,MAX_Temp,V1_points,V2_points,W_points,MAX_V1,MAX_V2,MAX_W
  Temp_points=[]
  MAX_Temp=10
  V1_points=[]
  MAX_V1=0.1
  V2_points=[]
  MAX_V2=0.1
  W_points=[]
  MAX_W=0.1
  
def LoadGcode():
 global connected
 var=[]
 if connected==0:
  tkinter.messagebox.showerror("ERROR","Not connected. Connect first")
  return
 filetypes = (('Gcode files', '*.gcode'),('All files', '*.*'))
 filename = filedialog.askopenfilename(filetypes=filetypes)
 print(filename)
 if str(filename)=="": return
 if Parse("readgcode "+filename,var)=="Error":
   tkinter.messagebox.showerror("ERROR","Cannot run Gcode "+filename)
    

#Robot direct interface for buttons
def MoveRobot(cmd):
 global connected,robot
 if connected==1:
  how_much=step.get()
  if cmd=='XY0': robot.send("G28 X Y")
  elif cmd=='Z0': robot.send("G28 Z")
  elif cmd=='+Y':
    robot.send("G91") #relative positioning
    robot.send("G1 Y"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='+X':
    robot.send("G91") #relative positioning
    robot.send("G1 X"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='+Z':
    robot.send("G91") #relative positioning
    robot.send("G1 Z"+str(how_much))
    robot.send("G90") #absolute positioning    
  elif cmd=='-Y':
    robot.send("G91") #relative positioning
    robot.send("G1 Y-"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='-X':
    robot.send("G91") #relative positioning
    robot.send("G1 X-"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='-Z':
    robot.send("G91") #relative positioning
    robot.send("G1 Z-"+str(how_much))
    robot.send("G90") #absolute positioning    
 else:    tkinter.messagebox.showerror("ERROR","Not connected. Connect first")
  

def sendcommand(cmd,where): #send a gcode command
    global connected,IsBuffered0,debug,cmdfile
    destination=['Syringe','Robot']
    if connected==1:
      if where==0:  #0 = syringe
       if (IsBuffered0):
           Gcode0.append(cmd)
       else:
        if noprint_debug==False:
          syringe.send(cmd)
        else:
          cmdfile.write("                     "+str(datetime.datetime.now())+"\n")
          cmdfile.write(cmd+"\n") 
      else:         #1 = robot
       if (HasRobot):   
        if noprint_debug: robot.send(cmd)
      if(debug): print(cmd,"->",destination[where])
    else:    tkinter.messagebox.showerror("ERROR","Not connected. Connect first")

def StartPrint0(): #print syringebot gcode
    global connected,syringe,Gcode0
    Gcode0 = gcoder.LightGCode(Gcode0)
    if len(Gcode0)>0:
      syringe.startprint(Gcode0)
   

def Draw_Chart(data,maximum,xtextpos,color):  #update graph
        w.create_text(xtextpos,10,text="{:.2f}".format(maximum),fill=color)        
        num_points=len(data)        
        pp=[]
        if num_points>2:
         w.create_text(chart_w-xtextpos-10,10,text="{:.2f}".format(data[-1]),fill=color)   
         if num_points<chart_w:
             endloop=num_points
         else:
             endloop=chart_w
         for x in range(0,endloop):
          index=round((x+1)*num_points/endloop)
          pp.append(x)
          pp.append(round(chart_h-data[index-1]*(chart_h-20)/maximum))
         w.create_line(pp,fill=color)


def filter_import_messages(record): #update temperature values. Filter out all other messages from Marlin
    global T_Actual,T_SetPoint,logfile
    if (record.msg.find(' B:')>0 and record.msg.find('root')<0):
        temp=record.msg[record.msg.find('B')+2:record.msg.find('@')]; #filter all messages but temperature
        #print(temp)
        [T_Actual, T_SetPoint]=temp.split('/',2)
    return False

        

logger = logging.getLogger().addFilter(filter_import_messages)     # bind filtering to printer messages

def Connect(): #connect/disconnect robot, syringebot and electrodes. Start cycling by calling MainCycle
    global connected,robot,syringe,electrodes,loadcell,logfile,HasRobot,HasElectrodes,HasLoadCell,noconnect,SyringeBOT_IS_INITIALIZED
    global SyringeUSB,RobotUSB,ElectrodesUSB,LoadCellUSB,SyringeUSBrate,RobotUSBrate,ElectrodesUSBrate,LoadCellUSBrate
    if noconnect:     #debug
         connected=not(connected)
         return
    if connected == 0:  #if it is not connected, connect
        SyringeBOT_IS_INITIALIZED=False    
        try:
         ser = serial.Serial(SyringeUSB,SyringeUSBrate)
         time.sleep(1)         
         while (ser.inWaiting() > 0):
          data_str = ser.read(ser.inWaiting()).decode('ascii') 
          print(data_str, end='')          
         time.sleep(1)
         ser.close()
         time.sleep(1)         
        except:
         print('serial connection failure')       
        try:
         syringe=printcore(SyringeUSB,SyringeUSBrate)
         syringe.loud=True
         times=0
         while not(syringe.online):
             time.sleep(1)
             print("waiting...")
             times=times+1
             if(times>10): syringe.disconnect(); times=times/0
        except:
         tkinter.messagebox.showerror("ERROR", "SYRINGE unit not connected! \ncheck connections\nand restart")
         return
        if (HasRobot):
         try:
          robot=printcore(RobotUSB,RobotUSBrate)
         except:
          tkinter.messagebox.showerror("ERROR", "ROBOT not connected! \ncheck connections\nand restart")
          HasRobot=False #Robot is not working if present
        if (HasElectrodes):  
         try:
          electrodes = serial.Serial(ElectrodesUSB,ElectrodesUSBrate)
         except:
          tkinter.messagebox.showerror("ERROR", "Electrodes not connected! \ncheck connections\nand restart")
          HasElectrodes=False #Electrodes are not working if present
        if (HasLoadCell):
         try:
          loadcell = serial.Serial(LoadCellUSB,LoadCellUSBrate)
         except:
          tkinter.messagebox.showerror("ERROR", "Load Cell not connected! \ncheck connections\nand restart")
          HasLoadCell=False #Load Cell is not working if present          
        setup_logging(sys.stdout,None,False)
        connected = 1
        threading.Timer(0.1, MainCycle).start()  #call MainCycle and start cycling       
        try:
            logfile=open("log"+os.sep+"log"+str(datetime.datetime.now())+".txt","a")
            logfile.write("----------------------------------\n")
            logfile.write("-         PROCESS STARTS         -\n")
            logfile.write("----------------------------------\n")
            logfile.write(str(datetime.datetime.now())+"\n")
            logfile.write("\nTimestamp / Actual Temperature / SetPoint")
            if (HasLoadCell):
               logfile.write(" / W")
            if (HasElectrodes):
               logfile.write(" / V1 / V2")
               logfile.write("\n")               
        except:
           tkinter.messagebox.showerror("ERROR", "Error writing log file")
    else:  #if it is connected, disconnect
     MsgBox = tkinter.messagebox.askquestion ('Disconnect','Are you sure you want to disconnect?',icon = 'warning')
     if MsgBox == 'yes':
      connected=0;
      if (HasRobot):robot.disconnect()
      syringe.disconnect()
      if (HasElectrodes): electrodes.close()
      if (HasLoadCell): loadcell.close()
      logfile.write("---------------------------------\n")
      logfile.write("-         PROCESS ENDED         -\n")
      logfile.write("---------------------------------\n")
      logfile.write(str(datetime.datetime.now())+"\n")
      logfile.close()
    

#MAIN CYCLE
def MainCycle():  #loop for sending temperature messages, reading electrodes values and updating graphs
  global syringe,electrodes,loadcell,connected,T_Actual,T_SetPoint,MAX_Temp,V1_points,V2_points,W_points,SyringeBOT_IS_BUSY,SyringeBOT_WAS_BUSY
  global MAX_V1,MAX_V2,last_V1,last_V2,last_W,MAX_W,HasElectrodes,HasLoadCell,oldprogress
  global Temperature_Hook,Temperature_Hook_Value,Temperature_Hook_Macro,Time_Hook,Time_Hook_Value,Time_Hook_Macro,macrolist
  if connected == 1:
   if syringe.printing:
        try:   
         progress =  float(syringe.queueindex) / len(syringe.mainqueue)
        except:
         progress = 0
        if not(oldprogress==progress):
                logfile.write(str(datetime.datetime.now())+"\tProcessing progress: "+str(progress*100)+" %\n")
        oldprogress=progress 
        #print(progress)
        if SyringeBOT_WAS_BUSY==False:
           w2.create_rectangle(5,200,795,400,fill='white')
           w2.create_text(400, 220, text="SyringeBOT is working...", fill="black", font=('Helvetica 15 bold'))
        w2.create_rectangle(10,300,progress*790,350,fill='red')
        SyringeBOT_IS_BUSY=True
        SyringeBOT_WAS_BUSY=True
   else:
        if SyringeBOT_WAS_BUSY==True:
          w2.create_image(0, 0, image = Aimage, anchor=NW)
          logfile.write(str(datetime.datetime.now())+"\tProcess finished\n")
        SyringeBOT_IS_BUSY=False
        SyringeBOT_WAS_BUSY=False
        #check hooks
        if Temperature_Hook:
           if ((Temperature_Hook_Value[0]=="<") and (float(T_Actual)<float(Temperature_Hook_Value[1:]))) or ((Temperature_Hook_Value[0]==">") and (float(T_Actual)>float(Temperature_Hook_Value[1:]))):
               Temperature_Hook=False
               b_temp.pack_forget()               
               print("Executing macro "+Temperature_Hook_Macro)
               Macro(macrolist.index(Temperature_Hook_Macro))
               #threading.Timer(0.1, delayedcall(macrolist.index(Temperature_Hook_Macro))).start() #open macro in a different thread
        if Time_Hook:
           datet=datetime.datetime.now()
           now = int(datet.timestamp())
           alarm = int(Time_Hook_Value.timestamp())
           if (now>=alarm):
               Time_Hook=False
               b_clock.pack_forget()                              
               print("Executing macro "+Time_Hook_Macro)
               Macro(macrolist.index(Time_Hook_Macro))
               #threading.Timer(0.1, delayedcall(macrolist.index(Time_Hook_Macro))).start() #open macro in a different thread

   syringe.send_now("M105")
   if (HasElectrodes):
    if electrodes.in_waiting:
        data=electrodes.readline()
        stringa=data.decode("utf-8")
        V=stringa.split('\t')
        if len(V)==2:
            try:
             V1=float(V[0])
             V2=float(V[1])
             last_V1=V1             
             last_V2=V2
             if V1>MAX_V1: MAX_V1=V1+0.1
             if V2>MAX_V2: MAX_V2=V2+0.1             
            except:
             pass
    V1_points.append(last_V1)
    V2_points.append(last_V2)
   if (HasLoadCell):
    if loadcell.in_waiting:
        data=loadcell.readline()
        stringa=data.decode("utf-8")
        try:
         W=float(stringa)
         last_W=W
         if W>MAX_W: MAX_W=W+0.1
        except:
         pass
    W_points.append(last_W)
   Temp_points.append(float(T_Actual))   
   logfile.write(str(datetime.datetime.now())+"\t"+str(T_Actual)+"\t"+str(T_SetPoint))
   if (HasLoadCell):
       logfile.write("\t"+str(last_W))
   if (HasElectrodes):
       logfile.write("\t"+str(last_V1)+"\t"+str(last_V2))
   logfile.write("\n")
   Y1=float(T_Actual)
   Y2=float(T_SetPoint)
   if max(Y1,Y2)>MAX_Temp: MAX_Temp=max(Y1,Y2)+5
   w.delete("all") #clear canvas
   Draw_Chart(Temp_points,MAX_Temp,20,'black')
   if Y2!=0 :          #if temperature setpoint is enabled, draw a dashed line at the value
     setpointp=round(chart_h-Y2*(chart_h-20)/MAX_Temp)
     w.create_line(0,setpointp,chart_w,setpointp,dash=(4, 2))
   if (HasElectrodes):  
    Draw_Chart(V1_points,MAX_V1,60,'blue')
    Draw_Chart(V2_points,MAX_V2,100,'green')
   if (HasLoadCell):  
    Draw_Chart(W_points,MAX_W,140,'red')
   threading.Timer(0.5, MainCycle).start() #call itself

def temp_button_click():
   tkinter.messagebox.showinfo('Temp Info', message = "Temperature Event\n\nWhen temperature "+str(Temperature_Hook_Value)+"\n Call macro: "+Temperature_Hook_Macro)
   #b_temp.pack_forget()

def time_button_click():
   tkinter.messagebox.showinfo('Timer Info', message = "Timer Event\n\nAt time= "+str(Time_Hook_Value)+"\n Call macro: "+Time_Hook_Macro)
   #b_temp.pack_forget()   

#Software name
F.master.title("CO.R.RO 1.1")

#Frame F
lTitle = Label(F, text="CO.R.RO",  font=("Verdana 15 bold"))
lTitle.pack(side="top")
bStart = Button(F, text="CONNECT/DISCONNECT", command=Connect)
bStart.pack(side="top", pady=10)
bSend_0 = Button(F, text="Send to syringebot", command=lambda: sendcommand(eCommand_0.get(),0))
bSend_0.pack(pady=10)
lCommand_0 = Label(F, text="Command:")
lCommand_0.pack()
eCommand_0 = Entry(F)
eCommand_0.insert(0, 'M304 P100 I1.5 D800')
eCommand_0.pack()
bSetTemp = Button(F, text="SetTemp", command=lambda: sendcommand("M140 S"+eTemperature.get(),0))
bSetTemp.pack(pady=10)
bOFFTemp = Button(F, text="Heating OFF", command=lambda: sendcommand("M140 S0",0))
bOFFTemp.pack(pady=10)
lTemperature = Label(F, text="Temperature: (°C)")
lTemperature.pack()
eTemperature = Entry(F)
eTemperature.insert(0, 60)
eTemperature.pack()
if (HasRobot):
 bSend_1 = Button(F, text="Send to robot", command=lambda: sendcommand(eCommand_1.get(),1))
 bSend_1.pack(pady=10)
 lCommand_1 = Label(F, text="Command:")
 lCommand_1.pack()
 eCommand_1 = Entry(F)
 eCommand_1.insert(0, 'G28 X Y')
 eCommand_1.pack()
Button(F, text="reset chart", command=ResetChart).pack();
Button(F, text="load gcode", command=LoadGcode).pack();
bClose = Button(F, text="EXIT", command=Close)
bClose.pack(pady=10)
temp_icon = PhotoImage(file = r"icons"+os.sep+"temp.png")
b_temp=Button(F, image=temp_icon,command=temp_button_click)
clock_icon = PhotoImage(file = r"icons"+os.sep+"clock.png")
b_clock=Button(F, image=clock_icon,command=time_button_click)



#Frames G,H,I,J,K
if (HasRobot):
 step=StringVar()
 lControl = Label(G, text="ROBOT MANUAL CONTROL",font="Verdana 10 bold",bg='pink')
 lControl.pack()
 Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(H, text="+Y", command=lambda: MoveRobot('+Y'),width=3).pack(side=LEFT)
 Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(H, text="+Z", command=lambda: MoveRobot('+Z'),width=3).pack(side=LEFT)
 Button(I, text="-X", command=lambda: MoveRobot('-X'),width=3).pack(side=LEFT)
 Button(I, text="XY0", command=lambda: MoveRobot('XY0'),width=3).pack(side=LEFT)
 Button(I, text="+X", command=lambda: MoveRobot('+X'),width=3).pack(side=LEFT)
 Button(I, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(I, text="Z0",command=lambda: MoveRobot('Z0'),width=3).pack(side=LEFT)
 Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(J, text="-Y", command=lambda: MoveRobot('-Y'),width=3).pack(side=LEFT)
 Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
 Button(J, text="-Z", command=lambda: MoveRobot('-Z'),width=3).pack(side=LEFT)
 Label(K, text="Step:").pack(side=LEFT)
 eStep = Entry(K,width=4,textvariable=step)
 eStep.pack(side=LEFT)
 step.set(10)
 Label(K, text="mm/deg").pack(side=LEFT)


#CREATE MACRO BUTTONS in frame Z and, eventually ZZ and functions in Z2
if len(macrolist)>0:
  Label(Z, text="MACROS",font="Verdana 10 bold",bg='pink').pack(pady=10)
  Button(Z, text="CREATE MACRO",command=CreateMacro).pack()
  ToggleB=Button(Z, text="EDIT MACRO",command=EditMacro)
  ToggleB.pack()
  ToggleB2=Button(Z, text="DELETE MACRO",command=DeleteMacro)
  ToggleB2.pack()
  Button(Z, text="", state=DISABLED,bd=0).pack() #space between buttons
  Label(Z2, text="Functions",font="Verdana 10 bold",bg='pink').pack(pady=10)
  i=0
  buttons_in_palette1=0
  for macro in macrolist:  #create a button for each macro
   with open('macros'+os.sep+macro+'.txt') as f:
    first_line = f.readline().lower()
   if "function" in first_line:
       palette=Z2
   else:
       palette=Z
       buttons_in_palette1+=1
       if buttons_in_palette1>28:
               palette=ZZ
   macrob.append(Button(palette, text=macro,command=lambda j=i : Macro(j)))
   macrob[i].pack()
   i=i+1



#Start the main loop
base.protocol("WM_DELETE_WINDOW", on_closing)
base.mainloop()

