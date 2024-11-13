import urllib.request
from tkinter import *
from tkinter.tix import *

root = Tk()
root.wm_title('Got Skills\' Skill Tracker')
frame = Frame(width="500",height="500")
frame.pack()
swin = ScrolledWindow(frame, width=500, height=500)
swin.pack()
win = swin.window


def show():
  name = "zezima"
  #page = urllib.request.urlopen('http://hiscore.runescape.com/index_lite.ws?player=' + name)
  page = ["dew","","frefr","frefrefre","dew","frefr","dew","","frefr","frefrefre","dew","frefr","frefrefre","dew","frefr","frefrefre","dew","frefr","frefrefre","gregergr","d3r3","frefr","frefrefre","gregergr","d3r3","frefr","frefrefre","gregergr","d3r3"]#page.readlines()

  skills = []
  for line in page:
    skills.append([line])

  #skills = skills[0:25]

  for item in skills:
    toPrint = item
    w = Message(win, text=' '.join(toPrint), width=500)
    w.pack()


menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="Commands", menu=filemenu)
filemenu.add_command(label="Show Skills", command=show)


root.mainloop()
