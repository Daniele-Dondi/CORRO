import tkinter as tk

class DragDropListbox(tk.Listbox):
    """A Tkinter Listbox with drag-and-drop reordering."""
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        super().__init__(master, kw)
        self.curIndex = None
        self.bind('<Button-1>', self.set_current)
        self.bind('<B1-Motion>', self.shift_selection)

    def set_current(self, event):
        self.curIndex = self.nearest(event.y)

    def shift_selection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i

# Example usage
root = tk.Tk()
root.title("Select the proper file order")

files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
tk.Label(root, text="Drag & Drop to select the proper file order").pack()
ddl = DragDropListbox(root, width=40, height=10)
ddl.pack(padx=10, pady=10)

for f in files:
    ddl.insert(tk.END, f)

root.mainloop()
