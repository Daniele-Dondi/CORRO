import serial
from threading import Timer
import tkinter
import threading
from tkinter import *

cycling=True
Gcode_counter=0
Gcode=[]
PrinterReady=True
Print=False


ser = serial.Serial('/dev/ttyUSB0', 250000)

def keypress(event):  #keyboard input
  global cycling
  if event.keysym == 'Escape': #quit program
    cycling=False
    base.destroy()


def Listening():
 global cycling,PrinterReady,Print   
 if (ser.inWaiting() > 0):
        data_str = ser.read(ser.inWaiting()).decode('ascii')
        print(data_str, end='')
        for s in data_str.split('\n'):
         if s.strip()=="ok":
           print("OK MESSAGE DETECTED")
           PrinterReady=True
 if cycling: threading.Timer(0.2, Listening).start() #call itself

def Sending():
 global Gcode,Print,Gcode_counter,PrinterReady
 if (Print) and (PrinterReady):
       ser.write((Gcode[Gcode_counter]+'\n').encode())
       print('sent',Gcode[Gcode_counter])
       PrinterReady=False
       Gcode_counter+=1
       if Gcode_counter==len(Gcode):
         print('Printing queue finished')
         Print=False
 if Print: threading.Timer(0.2, Sending).start() #call itself
          

def SendGcode():
  global Gcode,Print,Gcode_counter
  Gcode = T.get('1.0', END).splitlines()
  Gcode_counter=0
  Print=True
  threading.Timer(0.1, Sending).start()


threading.Timer(0.1, Listening).start()  #call Listen and start cycling

#Main window
base = Tk()
base.bind('<Key>', keypress)
T = Text(base, height = 20, width = 40)
T.pack()
B=Button(base, text="send gcode", command=SendGcode).pack();
base.mainloop()


       



