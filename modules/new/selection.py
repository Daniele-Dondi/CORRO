import tkinter as tk

class DragSelectCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.start_x = self.start_y = 0
        self.rect = None

        # Bind mouse events
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvasx(event.x)
        self.start_y = self.canvasy(event.y)
        # Create a rectangle at the start position
        self.rect = self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                          outline="blue", width=2)

    def on_drag(self, event):
        cur_x = self.canvasx(event.x)
        cur_y = self.canvasy(event.y)
        # Update rectangle coordinates
        self.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        print("Selection finished.")
        # Optionally: do something with selected region

def main():
    root = tk.Tk()
    root.title("Dragging Selection Rectangle")
    canvas = DragSelectCanvas(root, width=400, height=300, bg="white")
    canvas.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
