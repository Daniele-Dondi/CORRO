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

import PIL.Image
from PIL import ImageTk
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
import sys
import time
import datetime as DT
import os
import serial
from os import listdir
from os.path import isfile, join
import modules.configurator as conf
from modules.wizard import *
from modules.listserialports import *
from modules.buildvercalculator import *
import traceback


#global vars
connected = 0
GO_Fullscreen=False #if True, app starts in fullscreen mode
AutoConnect=False #if True, corro connects directly to SyringeBOT
AutoInit=False #if True, after the connection starts immediately SyringeBOT initialization    --- NOT YET IMPLEMENTED ---
ShowMacrosPalettes=False
#USB sensors control vars
Sensors_var_names=[]
Sensors_var_values=[]
Charts_enabled=[]
Plot_B=[] #array of plot buttons
#SyringeBOT handles and USB parameters
HasRobot = False
HasSyringeBOT = False
#SyringeBOT queue vars 
SyringeBOTQueueIndex=0 
SyringeBOTQueue=0 
SyringeBOTReady=True 
SyringeBOTWorking=False 
SyringeBOTSendNow=""
#CORRO DEBUG SECTION
debug=True #if True print additional information to console
noprint_debug=False #if True save gcode commands to file instead sending them to SyringeBOT
if noprint_debug: cmdfile=open("gcodecmds.txt","w")
DoNotConnect=False #if True no module connections is done
#END OF CORRO DEBUG SECTION
WatchdogMax=2000 #max number of instructions before a message asking if there is an infinite loop
T_Actual = 0
T_SetPoint = 0
Temp_points=[] #array of temperature points
MAX_Temp=10
macrolist = [] #list of avail macros
macrob=[]      #macro button array
IsEditingMacro=0
IsDeletingMacro=0
#chart parameters
chart_w=600 #size of the temp and voltages chart
chart_h=200
graph_colors=['black','blue','green','red','dark violet','brown','orange','purple','Navy','Teal','Olive','Gold','Violet','Indigo','Maroon','Coral','Aquamarine']
graph_color_index=0
graph_all=True  #If True show all the data recorded. If false show only the last data
macrout=0      #global var for macros. Filled when macro returns a value
pixboundedmacro=[] # list of macros bound to pixels
colorsbound=[]     # list of colors bound. Refers to above macros name
NewColorAssignment=0 # if a user assign a color during runtime this var is set to 1
logfile=0
Gcode=[] #array for the gcode commands (buffer/print commands)
IsBuffered0=False
SyringeBOT_IS_BUSY=False
SyringeBOT_WAS_BUSY=False
SyringeBOT_IS_INITIALIZED=False
oldprogress=0 #progress in printing
#following parameters will be read from configuration.txt file
#NumSyringes=0 #Number of installed syringes
##SyringemmToMax=[] #Syringe height of graduated part in millimeters
##SyringeVolumes=[] #Syringe max volume in milliliters
##SyringeInletVolumes=[]   #volume of the inlet tube 
##SyringeOutletVolumes=[]  #volume of the outlet tube
SchematicImage="" #file name for the image
MaskImage=""      #file name for the mask image
MaskMacros=""     #file name for the bounded colors to macros
# Hooks for events
Temperature_Hook=False
Temperature_Hook_Value="" #valid values are >xxx <yyy
Temperature_Hook_Macro="" #macro to call when condition is True
Time_Hook=False
Time_Hook_Value="" #valid values are >xxx <yyy
Time_Hook_Macro="" #macro to call when condition is True
#macro global variables
#Macro global variables are variables that are available to all scripts and are kept up to program exit
#To access them use the commands getglobal and setglobal
global_vars=[]

BuildVersion=GetBuildVersion()

#print(AvailableSerialPorts())

def on_closing():
        Close()

def keypress(event):  #keyboard shortcuts
    if event.keysym == 'Escape': #quit program
        Close()

def ResetChart():
  global Temp_points
  Temp_points=[]
  for device in range(len(conf.USB_names)):
   conf.USB_var_points[device]=[]

def GraphZoom_Unzoom():
  global graph_all
  graph_all=not(graph_all)
  if graph_all:
    Zoom_B.config(text="View All")
  else:
    Zoom_B.config(text="View Last")       

def readConfigurationFiles():
    global SyringemmToMax,SyringeVolumes,SyringeInletVolumes,SyringeOutletVolumes,SchematicImage,MaskImage,MaskMacros,colorsbound,pixboundedmacro
    global HasRobot,HasSyringeBOT
    
    try:
        conf_file = open("conf"+os.sep+"configuration.txt", "r") #open configuration.txt and read parameters
        lines=conf_file.readlines()
        conf_file.close()
        NumSyringes=int(lines[1].strip())
##        for x in range(NumSyringes):
##            l=lines[3+x].split(";")
##            SyringemmToMax[x]=float(l[0].strip())*2 #annoyngly we have to multiply by 2 to have the correct movement in mm
##            SyringeVolumes[x]=float(l[1].strip())
        curline=4+NumSyringes
        #VolInlet=float(lines[curline].strip())
        curline+=2
        #VolOutlet=float(lines[curline].strip())
        curline+=2
        SchematicImage="conf"+os.sep+lines[curline].strip()
        MaskImage=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-mask.png" #define automatically the names of mask and binds from the schematic image name
        MaskMacros=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-binds.txt"
 
        LoadConfFile('startup.conf')


    except Exception as e:
     print(e)       
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

def SyringeBOT_is_ready():
    global SyringeBOT_IS_BUSY,Temperature_Hook,Time_Hook
    if SyringeBOT_IS_BUSY:
     MsgBox = tkinter.messagebox.showerror ('SyringeBOT is BUSY','SyringeBOT IS BUSY! Wait for the task end',icon = 'error')
     return False
    if (Temperature_Hook) or (Time_Hook):
     MsgBox = tkinter.messagebox.showerror ('SyringeBOT is event-driven','SyringeBOT is waiting for Time or Temperature events. An action could create problems',icon = 'error')
     return False
    return True
        
def onclick(event):
    global pix,pixboundedmacro,colorsbound,debug
    global IsEditingMacro,IsDeletingMacro
    if IsEditingMacro or IsDeletingMacro:
     return       
    if SyringeBOT_is_ready():
     try:
      color=pix[event.x,event.y]
      if (debug):
       print ("clicked at", event.x, event.y)
       print (color)
      if color in colorsbound:
       macroname=pixboundedmacro[colorsbound.index(color)]   
       if(debug): print(macroname)
       try:
         macronum=macrolist.index(macroname)
         Macro(macronum,str(str(color[0])+','+str(color[1])+','+str(color[2]))) #by default passes color arguments to macro
       except Exception as e:
         tkinter.messagebox.showerror("ERROR","Problem executing macro "+macroname)
         print("onclick error:",e)
     except:
        print("Clicked out of image")
        pass

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

def Parse(line,variables):    #parse macro line and execute statements
    global logfile,IsBuffered0,Gcode,debug,cmdfile,SyringeBOT_IS_INITIALIZED
    global SyringemmToMax, SyringeVolumes, SyringeInletVolumes, SyringeOutletVolumes #global parameters for syringes taken from configuration.txt
    global Temperature_Hook,Temperature_Hook_Value,Temperature_Hook_Macro,Time_Hook,Time_Hook_Value,Time_Hook_Macro
    global Sensors_var_names,Sensors_var_values
    global global_vars
    if line=="": return
    if line.find('log')==0: #print string to log file
     try:
      commands=line.split(' ',1)
      commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
      if(debug): print(commands[1])
      logfile.write(str(DT.datetime.now())+"\t"+commands[1]+"\n")  
     except:
      tkinter.messagebox.showerror("ERROR in log method","use: log text")
      return "Error"
    elif (line.find('buffer')==0)or(line.find('record')==0): #buffer all commands, send later. Used for long gcode sequence where send will fail
        IsBuffered0=True
        Gcode=[]
    elif (line.find('print')==0)or(line.find('play')==0): #send all buffered commands. Used for long gcode sequences
        if (IsBuffered0):
            IsBuffered0=False
            if noprint_debug==False: StartPrint0()
            else:
             cmdfile.write("                     "+str(DT.datetime.now())+"\n")
             for lin in Gcode:
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
      RefreshVarValues("$syringemax$",SyringemmToMax[commands[1]],variables)
      RefreshVarValues("$syringevol$",SyringeVolumes[commands[1]],variables)
      RefreshVarValues("$volinlet$",SyringeInletVolumes[commands[1]],variables) 
      RefreshVarValues("$voloutlet$",SyringeOutletVolumes[commands[1]],variables) 
      RefreshVarValues("$axisname$",axisnames[commands[1]],variables)
      RefreshVarValues("$numsyringes$",len(SyringeVolumes),variables)
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
    elif line.find('getvalue')==0: #we've to retrieve a sensor variable
      try:
       commands=line.split(',',1)
       commands[0]=commands[0][9:] # remove getvalue
       x = Sensors_var_values[Sensors_var_names.index(commands[1])]
       RefreshVarValues(commands[0],x,variables)
      except Exception as e:
       tkinter.messagebox.showerror("ERROR in getvalue method","use: getvalue $varname$,sensor_value"+e)
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
         datet=DT.datetime.now()         
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
        fp.write('\n'.join(map(str, Gcode)))
       fp.close() 
      except:
       tkinter.messagebox.showerror("ERROR in writegcode method","use: writegcode filename")
       return "Error"
    elif line.find('readgcode')==0: #we've to read the gcode recorded
      try:
       commands=line.split(' ',1)
       with open(commands[1]) as fp:
        Gcode = fp.readlines()
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
    elif line.find('getglobal')==0: #retrieve a variable from the global variable list            
      try:
       commands=line.split(' ')
       for var in commands[1:]:
        var_name=var
        value=SubstituteVarValues(var,global_vars) #retrieve its value
        RefreshVarValues(var_name,value,variables) #register it in local variables
      except:
       tkinter.messagebox.showerror("ERROR in getglobal method","use: getglobal $varname$ [$varname2$]") 
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

def ExecuteMacro(num):
       if(debug): print('executing macro:',macrolist[num])
       with open('macros/'+macrolist[num]+'.txt') as macro_file: 
        lines=macro_file.readlines() #read the entire file and put lines into an array
        i=0
        for j in range(len(lines)): #analyze all macro code and record the labels line position
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
          exitcode=Parse(line,variables) #no flow commands are present, executes the statement present in the line
          if exitcode=="Error": #execute code contained in line. In the case of error abort macro execution
              tkinter.messagebox.showerror("Error in code:","macro name: "+macrolist[num]+"\nline: "+str(i)+"\ncommand: "+line)
              return "Error"
          elif exitcode=="Cancel":
              tkinter.messagebox.showwarning("Warning","Operation interrupted by the user")    
              return "Error"    
       if '$return$' in variables: macrout=SubstituteVarValues("$return$",variables) #when a macro returns a value it's automatically set the reserved variable $return$
       if (debug): print (variables)  #DEBUG


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
       if SyringeBOT_IS_INITIALIZED==False: #SyringeBOT is not initialized
        if not(macrolist[num])=="INIT_ALL": #only call to INIT_ALL is allowed
         MsgBox = tkinter.messagebox.showerror ('SyringeBOT is not initialized','Initialize first',icon = 'error')
         return
        else:
         SyringeBOT_IS_INITIALIZED=True #we set True because we are executing INIT_ALL
       if SyringeBOT_IS_BUSY==True:
        MsgBox = tkinter.messagebox.showerror ('SyringeBOT is BUSY','SyringeBOT IS BUSY! Wait for the task end',icon = 'error')
        return
       ExecuteMacro(num)
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
    global SyringeBOT_IS_BUSY,Temperature_Hook,Time_Hook
    if (SyringeBOT_IS_BUSY) or (Temperature_Hook) or (Time_Hook):
     return       
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
    if (SyringeBOT_IS_BUSY) or (Temperature_Hook) or (Time_Hook):
     return           
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

def CancelPrint():
 global SyringeBOTWorking
 MsgBox = tkinter.messagebox.askquestion ('Stop process','Are you sure you want to stop the process?',icon = 'warning')
 if MsgBox == 'yes':  
  SyringeBOTWorking=False
'''
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
'''  

def sendcommand(cmd,where): #send a gcode command
    global connected,IsBuffered0,debug,cmdfile,Gcode,SyringeBOTSendNow
    destination=['SyringeBOT','Robot']
    if connected==1:
      if where==0:  #0 = SyringeBOT
       if (IsBuffered0):
           Gcode.append(cmd)
       else:
        if noprint_debug==False:
          SyringeBOTSendNow=cmd      
          time.sleep(0.1)
        else:
          cmdfile.write("                     "+str(DT.datetime.now())+"\n")
          cmdfile.write(cmd+"\n") 
      else:         #1 = robot
       if (HasRobot):   
        if noprint_debug: robot.send(cmd)
      if(debug): print(cmd,"->",destination[where])
    else:    tkinter.messagebox.showerror("ERROR","Not connected. Connect first")


def StartPrint0(): #send gcode array to SyringeBOT
     global Gcode,SyringeBOTWorking,SyringeBOTQueueIndex,SyringeBOTReady
     if len(Gcode)>0:
      SyringeBOTQueueIndex=0
      SyringeBOTReady=True
      SyringeBOTWorking=True
  

def Draw_Chart(data):  #update graph
    global graph_color_index,graph_colors,graph_all,Charts_enabled    
    try:
        color=graph_colors[graph_color_index % len(graph_colors)]
        xtextpos=20+graph_color_index*50
        if Charts_enabled[graph_color_index-1]==False: return
        graph_color_index+=1        
        if len(data)<2: return #no data to plot          
        try:
         maximum=max(data)
        except:
         maximum=0.01       
        maximum+=maximum*0.05
        if maximum==0: maximum=0.05 #avoid division by zero
        w.create_text(xtextpos,10,text="{:.2f}".format(maximum),fill=color)        
        num_points=len(data)        
        pp=[]
        startloop=0
        if num_points>2:
         w.create_text(chart_w-xtextpos-10,10,text="{:.2f}".format(data[-1]),fill=color)   
         if num_points<chart_w:
             endloop=num_points
         else:
           if graph_all:      
             endloop=chart_w
           else: #only the  last chart_w points are plotted
             endloop=num_points
             startloop=num_points-chart_w
             maximum=max(data[startloop:endloop])
             maximum+=maximum*0.05
             if maximum==0: maximum=0.05 #avoid division by zero
         for x in range(startloop,endloop):
          if graph_all: index=round((x+1)*num_points/endloop)
          else: index=x
          pp.append(x-startloop)
          pp.append(round(chart_h-data[index-1]*(chart_h-20)/maximum))
         w.create_line(pp,fill=color)
    except Exception as e:
         print("Draw_Chart error ",e)
         print(traceback.format_exc())

def Enable_Disable_plot(j):
   global Charts_enabled,Plot_B
   Charts_enabled[j]=not(Charts_enabled[j])
   if Charts_enabled[j]:
    Plot_B[j].config(relief=RAISED)           
   else:        
    Plot_B[j].config(relief=SUNKEN)

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        if (debug): print(f"Directory '{directory_path}' already exists.")

def ConnectSyringeBOT(USB,USBrate):
    global connected,robot,SyringeBOT,logfile,HasRobot,HasSyringeBOT,SyringeBOT_IS_INITIALIZED
    global Temperature_Hook,Time_Hook
    global DoNotConnect
    global chart_h
    global USB_handles
    try:
     SyringeBOT = serial.Serial(USB,USBrate)
     USB_handles.append(SyringeBOT)
     time.sleep(1)         
     while (SyringeBOT.inWaiting() > 0):
      data_str = SyringeBOT.read(SyringeBOT.inWaiting()).decode('ascii') 
      print(data_str, end='')          
    except Exception as e:
     tkinter.messagebox.showerror("ERROR", "SyringeBOT unit not connected! \ncheck connections\nand restart")
     print("ERROR Connect(): ",e)
     HasSyringeBOT=False
     USB_handles.append("")
     w2.pack_forget()
    else:
     connected = 1
     HasSyringeBOT=True
     threading.Timer(0.1, SyringeBOTCycle).start()  #call SyringeBOT cycle
    conf.USB_last_values.append("0")

def Connect(): #connect/disconnect robot, SyringeBOT and sensors. Start cycling by calling MainCycle
    global connected,robot,SyringeBOT,logfile,HasRobot,HasSyringeBOT,SyringeBOT_IS_INITIALIZED
    global USB_handles,Charts_enabled,Plot_B
    global Temperature_Hook,Time_Hook
    global DoNotConnect
    global chart_h
    SyringeBOT_IS_INITIALIZED=False
    ResetChart()
    if DoNotConnect:
            connected=1
            return
    if connected == 0:  #if it is not connected, connect
        ensure_directory_exists("log")    
        LoadConfFile('startup.conf')
        for device in range(len(conf.USB_names)): #connect all the sensors
         if conf.USB_deviceready[device]:
          if conf.USB_types[device]=="SyringeBOT":
                  ConnectSyringeBOT(conf.USB_ports[device],conf.USB_baudrates[device])
                  conf.USB_deviceready[device]=HasSyringeBOT
          else:
           try:
            USB_handles.append(serial.Serial(conf.USB_ports[device],conf.USB_baudrates[device]))
            #conf.USB_deviceready[device]=True
            if (debug): print("USB device #",device+1,"port:",conf.USB_ports[device],"num vars=",conf.USB_num_vars[device])
            conf.USB_last_values.append(("0.01 " *int(conf.USB_num_vars[device])).strip())
           except Exception as e:
            print(e)       
            conf.USB_deviceready[device]=False       
            tkinter.messagebox.showerror("ERROR", conf.USB_names[device]+" not ready! \ncheck connections\nand restart\n if error persists check parameters in Configurator")
           else:
            connected=1
        if connected==0:
                tkinter.messagebox.showerror("ERROR", "NO DEVICES FOUND. ABORTING CONNECTION.\n check parameters in Configurator")
                return
        if HasSyringeBOT==False: #No SyringeBOT, only sensors. Expand Graph
                w.pack_forget()
                chart_h=600
                w.config(width=chart_w,height=chart_h)
                w.pack(expand=YES,fill=BOTH)
        Sensors_var_names=" ".join(conf.USB_var_names).split() #prepare var names array for getvalues
        #create buttons to enable/disable plots
        Charts_enabled=[False]*len(Sensors_var_names)
        print(Sensors_var_names)
        cntr=0
        j=0
        for device in range(len(conf.USB_names)):
         for variable in range(int(conf.USB_num_vars[device])):
          if conf.USB_deviceready[device]:                  
           var_name=Sensors_var_names[cntr]
           btn=Button(GRP, text=var_name, command=lambda num=j: Enable_Disable_plot(num),bg=graph_colors[(cntr)% len(graph_colors)],fg="white",bd=4)
           j+=1
           Plot_B.append(btn)
           btn.pack()
           Charts_enabled[cntr]=True
          cntr+=1
        threading.Timer(0.1, HookEventsCycle).start()  #call HooksEventsCycle and start cycling
        threading.Timer(0.1, MainCycle).start()  #call MainCycle and start cycling
        try:
            logfile=open("log"+os.sep+"log"+str(DT.datetime.now()).replace(":","-")+".txt","a")  #log file name is log+current date time. The replace is needed for Windows to avoid invalid characters
            logfile.write("----------------------------------\n")
            logfile.write("-         PROCESS STARTS         -\n")
            logfile.write("----------------------------------\n")
            logfile.write(str(DT.datetime.now())+"\n")
            logfile.write("\nTimestamp")
            if (HasSyringeBOT): logfile.write("\tActual Temperature\tSetPoint")
            for device in range(len(conf.USB_names)):
              logfile.write("\t"+conf.USB_var_names[device].replace(" ","\t"))      
            logfile.write("\n")               
        except Exception as e:
           print(e)     
           tkinter.messagebox.showerror("ERROR", "Error writing log file")
    else:  #if it is connected, disconnect
     MsgBox = tkinter.messagebox.askquestion ('Disconnect','Are you sure you want to disconnect?',icon = 'warning')
     if MsgBox == 'yes':
      connected=0;
      time.sleep(1) #wait to stop all threads
      Time_Hook=False
      b_clock.pack_forget()
      Temperature_Hook=False
      b_temp.pack_forget()          
      #if HasSyringeBOT: SyringeBOT.close()
      for device in range(len(conf.USB_names)):
        if conf.USB_deviceready[device]:
            conf.USB_deviceready[device]=False    
            USB_handles[device].close()
      USB_handles=[] #remove all handles
      HasSyringeBOT=False
      for btn in Plot_B:
        btn.destroy()
      Plot_B=[]  
      logfile.write("---------------------------------\n")
      logfile.write("-         PROCESS ENDED         -\n")
      logfile.write("---------------------------------\n")
      logfile.write(str(DT.datetime.now())+"\n")
      logfile.close()

def SyringeBOTCycle(): #listen and send messages to SyringeBOT
 global SyringeBOT,connected,SyringeBOTReady,Gcode,SyringeBOTWorking,SyringeBOTQueue,SyringeBOTQueueIndex,SyringeBOTSendNow,T_Actual,T_SetPoint
 while (SyringeBOT.inWaiting() > 0):
  data_str = SyringeBOT.read(SyringeBOT.inWaiting()).decode('ascii')
  for s in data_str.split('\n'):
    if s.strip()=="ok":
       SyringeBOTReady=True
       #print("   SyringeBOT Ready",data_str)
    try:   
     if (data_str.find(' B:')>0 and data_str.find('root')<0):
        temp=data_str[data_str.find('B')+2:data_str.find('@')]; #filter all messages but temperature
        [T1, T2]=temp.split('/',2)
        T_Actual=float(T1)
        T_SetPoint=float(T2)
    except:
     #print(DT.datetime.now(),"whops")
     pass       
 if (SyringeBOTWorking):
   if (SyringeBOTReady):
     if not(SyringeBOTSendNow==""):
       SyringeBOT.write((SyringeBOTSendNow+'\n').encode())  #if there is an immediate code and we are processing give the priority to the immediate sending
       #print('sent M105')
       SyringeBOTSendNow=""
     else:  
       SyringeBOT.write((Gcode[SyringeBOTQueueIndex]+'\n').encode())
       #print("   Sent ",Gcode[SyringeBOTQueueIndex])
       SyringeBOTReady=False
       SyringeBOTQueueIndex+=1
       SyringeBOTQueue=len(Gcode)
       if SyringeBOTQueueIndex==SyringeBOTQueue:
         SyringeBOTWorking=False
         Gcode=[]
 elif not(SyringeBOTSendNow==""):
       SyringeBOT.write((SyringeBOTSendNow+'\n').encode())  #if there is an immediate code send even if it is not ready
       SyringeBOTSendNow=""
        
 if connected: threading.Timer(0.05, SyringeBOTCycle).start() #call itself

def HookEventsCycle():
  global connected,SyringeBOT_IS_BUSY,T_Actual
  global Temperature_Hook,Temperature_Hook_Value,Temperature_Hook_Macro,Time_Hook,Time_Hook_Value,Time_Hook_Macro,macrolist
  if not(SyringeBOT_IS_BUSY):
        #check hooks
        if Temperature_Hook:
           if ((Temperature_Hook_Value[0]=="<") and (float(T_Actual)<float(Temperature_Hook_Value[1:]))) or ((Temperature_Hook_Value[0]==">") and (float(T_Actual)>float(Temperature_Hook_Value[1:]))):
               Temperature_Hook=False
               b_temp.pack_forget()               
               print("Temp Hook: executing macro "+Temperature_Hook_Macro)
               Macro(macrolist.index(Temperature_Hook_Macro))
        if Time_Hook:
           datet=DT.datetime.now()
           now = int(datet.timestamp())
           alarm = int(Time_Hook_Value.timestamp())
           if (now>=alarm):
               Time_Hook=False
               b_clock.pack_forget()                              
               print("Time Hook: executing macro "+Time_Hook_Macro)
               Macro(macrolist.index(Time_Hook_Macro))
  if (connected): threading.Timer(1, HookEventsCycle).start() #call itself       

#MAIN CYCLE
def MainCycle():  #loop for sending temperature messages, reading sensor values and updating graphs
  global SyringeBOT,connected,T_Actual,T_SetPoint,MAX_Temp,SyringeBOT_IS_BUSY,SyringeBOT_WAS_BUSY
  global logfile
  global HasSyringeBOT
  global SyringeBOTWorking,SyringeBOTQueueIndex,SyringeBOTQueue,SyringeBOTSendNow 
  global oldprogress,graph_color_index
  global USB_handles
  if connected == 1:
   w.delete("all") #clear graph canvas
   graph_color_index=0
   log_text=""
   if HasSyringeBOT:
           if SyringeBOTWorking:
                try:   
                 progress=float(SyringeBOTQueueIndex/SyringeBOTQueue)
                except:
                 progress=0
                if not(oldprogress==progress):
                        logfile.write(str(DT.datetime.now())+"\tProcessing progress: "+str(progress*100)+" %\n")
                oldprogress=progress 
                #print(progress)
                if SyringeBOT_WAS_BUSY==False:
                   w2.create_rectangle(5,200,795,400,fill='white')
                   w2.create_text(400, 220, text="SyringeBOT is working...", fill="black", font=(BUSY_FONT))
                w2.create_rectangle(10,300,progress*780+10,350,fill='red')
                SyringeBOT_IS_BUSY=True
                SyringeBOT_WAS_BUSY=True
           else:
                if SyringeBOT_WAS_BUSY==True:
                  w2.create_image(0, 0, image = Aimage, anchor=NW)
                  logfile.write(str(DT.datetime.now())+"\tProcess finished\n")
                SyringeBOT_IS_BUSY=False
                SyringeBOT_WAS_BUSY=False

           SyringeBOTSendNow='M105' #send immediate gcode to SyringeBOT
           Temp_points.append(float(T_Actual))
           log_text+="\t"+str(T_Actual)+"\t"+str(T_SetPoint)
           #Draw_Chart(Temp_points)
           try:
            MAX_Temp=max(Temp_points)
           except:
            MAX_Temp=0.01       
           Y2=float(T_SetPoint)
           if (Y2!=0)and(MAX_Temp!=0) :          #if temperature setpoint is enabled, draw a dashed line at the setpoint value
             setpointp=round(chart_h-Y2*(chart_h-20)/MAX_Temp)
             w.create_line(0,setpointp,chart_w,setpointp,dash=(4, 2))
   ########################################################################################################################################  
   for sensor in range(len(conf.USB_names)):  #read values from all sensors connected to USB
     try:
      if (conf.USB_deviceready[sensor]):
       if conf.USB_types[sensor]=="SyringeBOT":
               conf.USB_last_values[sensor]=T_Actual
       elif USB_handles[sensor].in_waiting:
        data=USB_handles[sensor].readline()
        stringa=data.decode("utf-8").strip()
        V=stringa.split('\t')
        values=""
        if len(V)==conf.USB_num_vars[sensor]: #keep data only if they correspond to the number of real variables, to avoid misreadings
          for value in V:
            values+=str(abs(float(value)))+" "
          values=values.strip()
          conf.USB_last_values[sensor]=values 
        #elif debug:
        # print("no data received from sensor ",sensor)       
       conf.USB_var_points[sensor].append(str(conf.USB_last_values[sensor])+" ")
       log_text+="\t"+str(conf.USB_last_values[sensor]).replace(" ","\t")
       for datum in range(int(conf.USB_num_vars[sensor])):
          Draw_Chart([float(e.split(' ')[datum]) for e in conf.USB_var_points[sensor]])
     except Exception as e:
       a,b,tb=sys.exc_info()
       print("MainCycle",e," line ",tb.tb_lineno)
       
   logfile.write(str(DT.datetime.now())+log_text+"\n") 
   if (connected): threading.Timer(0.5, MainCycle).start() #call itself

def DeleteTemperatureEvent(t):
 global Temperature_Hook,Time_Hook
 MsgBox = tkinter.messagebox.askquestion ('Delete Temperature Event','Are you sure you want to DELETE temperature event?',icon = 'warning')
 if MsgBox == 'yes':        
   Temperature_Hook=False
   b_temp.pack_forget()
 t.destroy()

def temp_button_click():
 t = tkinter.Toplevel(base)
 t.geometry("+%d+%d" % (100, 300)) 
 t.title('Temperature information')
 Label(t,text="Temperature Event\n\nWhen temperature "+str(Temperature_Hook_Value)+"\n Call macro: "+Temperature_Hook_Macro).pack()
 Button(t, text="OK",command=lambda: t.destroy()).pack()
 Button(t, text="DELETE EVENT",command=lambda: DeleteTemperatureEvent(t)).pack() 
 t.grab_set()   
   
def DeleteTimeEvent(t):
 global Temperature_Hook,Time_Hook        
 MsgBox = tkinter.messagebox.askquestion ('Delete Time Event','Are you sure you want to DELETE time event?',icon = 'warning')
 if MsgBox == 'yes':        
   Time_Hook=False
   b_clock.pack_forget()
 t.destroy()

def time_button_click():
 t = tkinter.Toplevel(base)
 t.geometry("+%d+%d" % (100, 300))  
 t.title('Timer information')
 Label(t,text="Timer Event\n\nAt time= "+str(Time_Hook_Value)+"\n Call macro: "+Time_Hook_Macro).pack()
 Button(t, text="OK",command=lambda: t.destroy()).pack()
 Button(t, text="DELETE EVENT",command=lambda: DeleteTimeEvent(t)).pack() 
 t.grab_set()


def UserClickedMacro(num):
 if SyringeBOT_is_ready():
  Macro(num)

def Record():
  return      

def Configurator():
  StartConfigurator(base)      

def Wizard():
  StartWizard(base)

############################################################################################################################
#                                                                                                                          #
#                M   A   I   N      P   R   O   G   R   A   M      S   T   A   R   T   S      H   E   R   E                #
#                                                                                                                          #
############################################################################################################################


#Main window
base = Tk()
# Apply a default font globally
base.option_add("*Font", ("Arial", 7))
CORRO_FONT="Verdana 15 bold"
HEADER_FONT="Verdana 8 bold"
BUSY_FONT='Helvetica 15 bold'
#base.iconbitmap("icons/main_icon.ico")
if GO_Fullscreen: base.attributes("-fullscreen", True) #go FULLSCREEN
base.bind('<Key>', keypress)
F = Frame(base)
F.pack(side="left",fill="y")
#Software name
F.master.title("CO.R.RO 1.2 Build "+str(BuildVersion))
#Frame F
lTitle = Label(F, text="CO.R.RO",  font=(CORRO_FONT))
lTitle.pack(side="top")
bStart = Button(F, text="CONNECT/DISCONNECT", command=Connect)
bStart.pack(side="top", pady=10)
bSend_0 = Button(F, text="Send to SyringeBOT", command=lambda: sendcommand(eCommand_0.get(),0))
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
'''
if (HasRobot):
 bSend_1 = Button(F, text="Send to robot", command=lambda: sendcommand(eCommand_1.get(),1))
 bSend_1.pack(pady=10)
 lCommand_1 = Label(F, text="Command:")
 lCommand_1.pack()
 eCommand_1 = Entry(F)
 eCommand_1.insert(0, 'G28 X Y')
 eCommand_1.pack()
''' 
Button(F, text="load gcode", command=LoadGcode).pack();
rec_icon = PhotoImage(file = r"icons/rec.png")
#Button(F, text="REC", command=Record,image = rec_icon, compound = LEFT).pack();
canc_icon = PhotoImage(file = r"icons/stop.png")
#Button(F, text="cancel print", command=CancelPrint,image = canc_icon, compound = LEFT).pack();
conf_icon = PhotoImage(file = r"icons/configurator.png")
Button(F, text="configurator", command=Configurator,image = conf_icon, compound = LEFT).pack();
wiz_icon = PhotoImage(file = r"icons/wizard.png")
Button(F, text="wizard", command=Wizard,image = wiz_icon, compound = LEFT).pack();
bo_icon = PhotoImage(file = r"icons/BO.png")
Button(F, text="B.O.", command=Wizard,image = bo_icon, compound = LEFT).pack();
bClose = Button(F, text="EXIT", command=Close)
bClose.pack(pady=10)
temp_icon = PhotoImage(file = r"icons"+os.sep+"temp.png")
b_temp=Button(F, image=temp_icon,command=temp_button_click)
clock_icon = PhotoImage(file = r"icons"+os.sep+"clock.png")
b_clock=Button(F, image=clock_icon,command=time_button_click)
Z = Frame(base,bd=2,relief=RIDGE) #macros frame
if ShowMacrosPalettes: Z.pack(side="left",fill="y")
try:  #read macros and decide if we have to create a second palette
 for file in os.listdir("macros"):
    if file.endswith(".txt"): #all files in macros folder having .txt extension are considered macros
        macrolist.append(file[:-4]) #remove .txt from name
except:
    tkinter.messagebox.showerror("ERROR", "MACRO directory unreachable")
else:
  macrolist.sort()     
  if len(macrolist)>28:
          ZZ = Frame(base,bd=2,relief=RIDGE) #second macros frame
          if ShowMacrosPalettes: ZZ.pack(side="left",fill="y")
          Label(ZZ, text="MACROS 2",font=HEADER_FONT,bg='pink').pack(pady=10)
Z2 = Frame(base,bd=2,relief=RIDGE) #functions frame
if ShowMacrosPalettes: Z2.pack(side="left",fill="y")
Zcore = Frame(base,bd=2,relief=RIDGE) #core macros frame
if ShowMacrosPalettes: Zcore.pack(side="left",fill="y")
Label(Zcore, text="HAL MACROS",font=HEADER_FONT,bg='pink').pack(pady=10)
GRP = Frame(base,bd=2,relief=RIDGE) #graph controls frame
GRP.pack(side="left",fill="y")
Label(GRP, text="GRAPH CTRL",font=HEADER_FONT,bg='pink').pack(pady=10)
Button(GRP, text="reset chart", command=ResetChart).pack();
Zoom_B=Button(GRP, text="View All", command=GraphZoom_Unzoom)
Zoom_B.pack()
'''
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
'''
Graph=Frame(base)  #frame for graph showing values
Graph.pack(side="bottom")
w=Canvas(Graph,width=chart_w,height=chart_h)
w.pack(expand=YES,fill=BOTH)
#w.config(width=chart_w,height=chart_h)
#IM.pack() #show graphical control
IM=Frame(base)   #frame for main image with syringebot scheme
IM.pack(side="left")
w2=Canvas(IM,width=900,height=800)
w2.bind("<Button-1>", onclick) #bind click procedure to syringebot scheme
w2.bind("<Button-2>", onmiddleclick) #bind click procedure to syringebot scheme
w2.bind("<Button-3>", onrightclick) #bind click procedure to syringebot scheme
w2.pack()
#Load configuration file
readConfigurationFiles()
RESIZE_IMAGES=False
original_image = PIL.Image.open(SchematicImage)  # Replace with your actual image file
if (RESIZE_IMAGES):
        resized_image = original_image.resize((200, 200))  # Resize to desired dimensions
else:
        resized_image =original_image
# Convert to Tkinter-compatible image format
Aimage = ImageTk.PhotoImage(resized_image)
#Aimage=PhotoImage(file=SchematicImage) # load the scheme of the current configuration
w2.create_image(0, 0, image = Aimage, anchor=NW) #show image on canvas w2
if noprint_debug: w2.create_text(400,15,text="DEBUG MODE. NO DATA IS SENT TO SYRINGEBOT. Gcode commands are saved in gcodecmds.txt",fill="red") 
original_mask = PIL.Image.open(MaskImage) # load the mask here
if (RESIZE_IMAGES):
        resized_mask = original_mask.resize((200, 200))  # Resize to desired dimensions
else:
        resized_mask = original_mask
pix = resized_mask.load()

'''
#Frames G,H,I,J,K
if (HasRobot):
 step=StringVar()
 lControl = Label(G, text="ROBOT MANUAL CONTROL",font=HEADER_FONT,bg='pink')
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
'''

#CREATE MACRO BUTTONS in frame Z and, eventually ZZ and functions in Z2
if len(macrolist)>0:
  Label(Z, text="MACROS",font=HEADER_FONT,bg='pink').pack(pady=10)
  Button(Z, text="CREATE MACRO",command=CreateMacro).pack()
  ToggleB=Button(Z, text="EDIT MACRO",command=EditMacro)
  ToggleB.pack()
  ToggleB2=Button(Z, text="DELETE MACRO",command=DeleteMacro)
  ToggleB2.pack()
  Button(Z, text="", state=DISABLED,bd=0).pack() #space between buttons
  Label(Z2, text="Functions",font=HEADER_FONT,bg='pink').pack(pady=10)
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
   macrob.append(Button(palette, text=macro,command=lambda j=i : UserClickedMacro(j)))
   macrob[i].pack()
   i=i+1

if AutoConnect: Connect()

#Start the main loop
#base.protocol("WM_DELETE_WINDOW", on_closing)
base.mainloop()
