import tkinter as tk

root=tk.Tk()
PAB=tk.Canvas(width=400, height=400, bg="gray")

class Rect:
    def __init__(self, x1, y1, name):

        tag = f"movable{id(self)}"
        rec = PAB.create_rectangle(x1,y1,x1+40,y1+40, fill='#c0c0c0', tag=(tag, ))
        text = PAB.create_text(x1+20,y1+20, text=name, tag=(tag,))

def in_bbox(event, item):  # checks if the mouse click is inside the item
    bbox = PAB.bbox(item)

    return bbox[0] < event.x < bbox[2] and bbox[1] < event.y < bbox[3]
    
#mouse click find object to move
def get_it(event):
    delta=5
    global cur_rec
    cur_rec = PAB.find_closest(event.x, event.y)  # returns the closest object

    if not in_bbox(event, cur_rec):  # if its not in bbox then sets current_rec as None
        cur_rec = None

#mouse movement moves object
def move_it(event):
    if cur_rec:
        xPos, yPos = event.x, event.y
        xObject, yObject = PAB.coords(cur_rec)[0],PAB.coords(cur_rec)[1]
                
        PAB.move(PAB.gettags(cur_rec)[0], xPos-xObject, yPos-yObject) 

PAB.bind('<Button-1>', get_it)
PAB.bind('<B1-Motion>', move_it)
#test rects
bob = Rect(20,20,'Bob')
rob = Rect(80,80,'Rob')
different_bob = Rect(160,160,'Bob')

PAB.pack()
root.mainloop()
