import tkinter as tk

class DragManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Bind mouse events to the canvas
        self.canvas.tag_bind("movable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("movable", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind("movable", "<ButtonRelease-1>", self.on_drag_stop)

    def on_drag_start(self, event):
        # Record the item and its location
        self._drag_data["item"] = self.canvas.find_withtag("current")[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag_move(self, event):
        # Compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # Move the object by the same amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)

        # Update the drag data
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag_stop(self, event):
        # Reset the drag data
        self._drag_data = {"x": 0, "y": 0, "item": None}

root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

# Create two rectangles with the same tag
rect1 = canvas.create_rectangle(50, 50, 100, 100, fill="blue", tags="movable")
rect2 = canvas.create_rectangle(150, 150, 200, 200, fill="red", tags="movable")

# Initialize the drag manager
drag_manager = DragManager(canvas)

root.mainloop()
