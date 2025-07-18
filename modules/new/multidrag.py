import tkinter as tk

class DragDropApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=400, bg="lightblue")
        self.canvas.pack()

        # Create multiple objects
        self.objects = [
            self.canvas.create_rectangle(50, 50, 100, 100, fill="red"),
            self.canvas.create_oval(150, 50, 200, 100, fill="green"),
            self.canvas.create_rectangle(250, 50, 300, 100, fill="blue")
        ]

        self.selected_objects = set()
        self.start_x = 0
        self.start_y = 0

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_click(self, event):
        # Detect if an object is clicked
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        if clicked_item in self.objects:
            if clicked_item not in self.selected_objects:
                self.selected_objects.add(clicked_item)
                self.canvas.itemconfig(clicked_item, outline="yellow", width=2)
            else:
                self.selected_objects.remove(clicked_item)
                self.canvas.itemconfig(clicked_item, outline="", width=1)

        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        # Move all selected objects
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        for obj in self.selected_objects:
            self.canvas.move(obj, dx, dy)
        self.start_x = event.x
        self.start_y = event.y

    def on_release(self, event):
        # Reset outline on release
        for obj in self.selected_objects:
            self.canvas.itemconfig(obj, outline="", width=1)

# Create the Tkinter window
root = tk.Tk()
root.title("Drag and Drop Multiple Objects")
app = DragDropApp(root)
root.mainloop()
##
##Explanation:
##Canvas Widget: Used to create and manage graphical objects like rectangles and ovals.
##Object Selection: Clicking on an object adds it to the selected_objects set. Clicking again deselects it.
##Dragging: The <B1-Motion> event moves all selected objects by calculating the difference in mouse position (dx, dy).
##Visual Feedback: Selected objects are highlighted with a yellow outline for clarity.
##
##This approach allows you to select multiple objects and drag them together seamlessly. Let me know if you need further customization! 😊
