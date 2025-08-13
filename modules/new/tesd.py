import tkinter as tk

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.text = tk.Text(self, wrap="word")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.text_yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # create an info window in the bottom right corner and
        # inset a couple of pixels
        self.info = tk.Label(self.text, width=20, borderwidth=1, relief="solid")
        self.info.place(relx=1.0, rely=1.0, x=-100, y=-2,anchor="se")

    def text_yview(self, *args):
        ''' 
        This gets called whenever the yview changes.  For this example
        we'll update the label to show the line number of the first
        visible row. 
        '''
        # first, update the scrollbar to reflect the state of the widget
        self.vsb.set(*args)

        # get index of first visible line, and put that in the label
        index = self.text.index("@0,0")
        self.info.configure(text=index)

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
