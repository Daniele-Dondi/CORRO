import tkinter as tk
import threading
import queue
import time
import random

# Thread-safe queue for graph data
data_queue = queue.Queue()

# Worker thread: simulates reading from serial and producing graph points
def worker_loop():
    x = 0
    while running:
        y = random.uniform(0, 100)  # Simulated sensor value
        data_queue.put((x, y))
        x += 1
        time.sleep(0.5)  # Simulate delay between readings

# Main thread: updates the graph
def update_graph():
    while not data_queue.empty():
        x, y = data_queue.get_nowait()
        x_data.append(x)
        y_data.append(y)

        # Keep only last 50 points
        if len(x_data) > 50:
            x_data.pop(0)
            y_data.pop(0)

        # Clear and redraw
        canvas.delete("graph")
        if len(x_data) > 1:
            # Scale values to fit canvas
            max_y = max(y_data) if y_data else 1
            for i in range(1, len(x_data)):
                x1 = (i-1) * 10
                y1 = 200 - (y_data[i-1] / max_y) * 180
                x2 = i * 10
                y2 = 200 - (y_data[i] / max_y) * 180
                canvas.create_line(x1, y1, x2, y2, fill="blue", tags="graph")

    root.after(100, update_graph)  # Schedule next update

# Tkinter setup
root = tk.Tk()
root.title("Live Tkinter Graph")

canvas = tk.Canvas(root, width=500, height=200, bg="white")
canvas.pack()

x_data, y_data = [], []
running = True

# Start worker thread
threading.Thread(target=worker_loop, daemon=True).start()

# Start graph update loop
root.after(100, update_graph)

# Handle window close
def on_close():
    global running
    running = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()


