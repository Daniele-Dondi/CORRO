import serial
from threading import Timer
import tkinter
import threading
from tkinter import *
from tkinter import filedialog as fd

connected=True
SyringeQueueIndex=0
SyringeQueue=0
Gcode=[]
SyringeReady=True
SyringeWorking=False


syringe = serial.Serial('/dev/ttyUSB0', 250000)

def LoadGcode():
  filename = fd.askopenfilename(filetypes=(
        ('GCODE files', '*.gcode'),
        ('All files', '*.*')
    ))
  print(filename)
  with open(filename, 'r') as infile:
   for line in infile: 
    T.insert('end',line)

def keypress(event):  #keyboard input
  global connected
  if event.keysym == 'Escape': #quit program
    connected=False
    base.destroy()

def SyringeCycle(): #listen and send messages to SyringeBOT
 global syringe,connected,SyringeReady,Gcode,SyringeWorking,SyringeQueueIndex   
 if (syringe.inWaiting() > 0):
    data_str = syringe.read(syringe.inWaiting()).decode('ascii')
    print(data_str, end='')
    for s in data_str.split('\n'):
     if s.strip()=="ok":
       print("Printer ready")
       SyringeReady=True
    if (data_str.find(' B:')>0 and data_str.find('root')<0):
        temp=data_str[data_str.find('B')+2:data_str.find('@')]; #filter all messages but temperature
        #print(temp)
        [T_Actual, T_SetPoint]=temp.split('/',2)
        print("T:",T_Actual, T_SetPoint)
 if (SyringeWorking) and (SyringeReady):
       syringe.write((Gcode[SyringeQueueIndex]+'\n').encode())
       print('sent',Gcode[SyringeQueueIndex])
       SyringeReady=False
       SyringeQueueIndex+=1
       if SyringeQueueIndex==len(Gcode):
         print('Printing queue finished')
         SyringeWorking=False          
 if connected: threading.Timer(0.05, SyringeCycle).start() #call itself


def SendGcode():
  global Gcode,SyringeWorking,SyringeQueueIndex,SyringeQueue
  Gcode = T.get('1.0', END).splitlines()
  SyringeQueueIndex=0
  SyringeQueue=len(Gcode)
  SyringeWorking=True



threading.Timer(0.1, SyringeCycle).start()  #call SyringeBOT cycle

#Main window
base = Tk()
base.bind('<Key>', keypress)
T = Text(base, height = 20, width = 40)
T.pack()
Button(base, text="load gcode", command=LoadGcode).pack();
Button(base, text="send gcode", command=SendGcode).pack();
base.mainloop()
