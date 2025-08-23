import tkinter as tk



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
 else:    tk.messagebox.showerror("ERROR","Not connected. Connect first")


root = tk.Tk()
F = F = tk.Frame(root)
F.pack()


K = tk.Frame(F)
K.pack(side="bottom")
J = tk.Frame(F)
J.pack(side="bottom")
I = tk.Frame(F)
I.pack(side="bottom")
H = tk.Frame(F)
H.pack(side="bottom")
G = tk.Frame(F)
G.pack(side="bottom")

#Frames G,H,I,J,K
step=tk.StringVar()
lControl = tk.Label(G, text="ROBOT MANUAL CONTROL",bg='pink')
lControl.pack()
tk.Button(H, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(H, text="+Y", command=lambda: MoveRobot('+Y'),width=3).pack(side="left")
tk.Button(H, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(H, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(H, text="+Z", command=lambda: MoveRobot('+Z'),width=3).pack(side="left")
tk.Button(I, text="-X", command=lambda: MoveRobot('-X'),width=3).pack(side="left")
tk.Button(I, text="HM", command=lambda: MoveRobot('XY0'),width=3).pack(side="left")
tk.Button(I, text="+X", command=lambda: MoveRobot('+X'),width=3).pack(side="left")
tk.Button(I, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(I, text="Z0",command=lambda: MoveRobot('Z0'),width=3).pack(side="left")
tk.Button(J, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(J, text="-Y", command=lambda: MoveRobot('-Y'),width=3).pack(side="left")
tk.Button(J, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(J, text="", state="disabled",bd=0,width=3).pack(side="left")
tk.Button(J, text="-Z", command=lambda: MoveRobot('-Z'),width=3).pack(side="left")
tk.Label(K, text="Step:").pack(side="left")
eStep = tk.Entry(K,width=4,textvariable=step)
eStep.pack(side="left")
step.set(10)
tk.Label(K, text="mm").pack(side="left")


root.mainloop()
