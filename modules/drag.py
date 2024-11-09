import tkinter as tk
from tkinter import ttk

def make_draggable(widget):
    widget.bind("<Button-1>", on_drag_start)
    widget.bind("<B1-Motion>", on_drag_motion)

def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

main = tk.Tk()
main.geometry('800x620+500+150')

F=tk.Frame(main, bd=10, bg="grey")
F.place(x=10,y=10)
make_draggable(F)
frdame = tk.Label(F,text="Put")
frdame.pack(side="left")
rdame = tk.Entry(F)
rdame.pack(side="left")
unit=ttk.Combobox(F, values = ('g', 'mg', 'mol', 'mmol'), state = 'readonly')
unit.pack(side="left")
frdame = tk.Label(F,text="of")
frdame.pack(side="left")
sunit=ttk.Combobox(F, values = ('water','pee'), state = 'readonly')
sunit.pack(side="left")
yfrdame = tk.Label(F,text="in")
yfrdame.pack(side="left")
ysunit=ttk.Combobox(F, values = ('Reactor 1','Trash'), state = 'readonly')
ysunit.pack(side="left")




G=tk.Frame(main, bd=10, bg="grey")
G.place(x=10,y=40)
frdame = tk.Button(G,text="tdast")
frdame.pack()
rdame = tk.Button(G,text="tdost")
rdame.pack()

make_draggable(G)
