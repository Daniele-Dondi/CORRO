import serial
from threading import Timer
import tkinter
import threading
from tkinter import *

command=""
cycling=True
ser = serial.Serial('/dev/ttyUSB0', 250000)

def keypress(event):  #keyboard input
  global command,cycling
  command+=event.char
  if event.keysym == 'Escape': #quit program
    cycling=False
    base.destroy()
  elif len(event.char)>0 and ord(event.char)==13:
    print()
    ser.write(command.encode())
    command=""
  else:
    print(event.char,end='')

def Listen():
 global cycling   
 if (ser.inWaiting() > 0):
        data_str = ser.read(ser.inWaiting()).decode('ascii')
        print(data_str, end='')
        for s in data_str.split('\n'):
         if s.strip()=="ok": print("OK MESSAGE DETECTED")
 if cycling: threading.Timer(0.5, Listen).start() #call itself

threading.Timer(0.1, Listen).start()  #call Listen and start cycling

#Main window
base = Tk()
base.bind('<Key>', keypress)
base.mainloop()


       



