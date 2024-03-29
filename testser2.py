import serial
from threading import Timer
import tkinter
import threading
from tkinter import *
from tkinter import filedialog as fd

cycling=True
Gcode_counter=0
Gcode=[]
PrinterReady=True
Print=False


ser = serial.Serial('/dev/ttyUSB0', 250000)

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
  global cycling
  if event.keysym == 'Escape': #quit program
    cycling=False
    base.destroy()

def PrintingCycle(): #listen and send messages to printer
 global cycling,PrinterReady,Gcode,Print,Gcode_counter   
 if (ser.inWaiting() > 0):
        data_str = ser.read(ser.inWaiting()).decode('ascii')
        print(data_str, end='')
        for s in data_str.split('\n'):
         if s.strip()=="ok":
           print("Printer ready")
           PrinterReady=True
 if (Print) and (PrinterReady):
       ser.write((Gcode[Gcode_counter]+'\n').encode())
       print('sent',Gcode[Gcode_counter])
       PrinterReady=False
       Gcode_counter+=1
       if Gcode_counter==len(Gcode):
         print('Printing queue finished')
         Print=False          
 if cycling: threading.Timer(0.05, PrintingCycle).start() #call itself


def SendGcode():
  global Gcode,Print,Gcode_counter
  Gcode = T.get('1.0', END).splitlines()
  Gcode_counter=0
  Print=True



threading.Timer(0.1, PrintingCycle).start()  #call printer cycle

#Main window
base = Tk()
base.bind('<Key>', keypress)
T = Text(base, height = 20, width = 40)
T.pack()
Button(base, text="load gcode", command=LoadGcode).pack();
Button(base, text="send gcode", command=SendGcode).pack();
base.mainloop()
