##import tkinter as tk
##from tkinter import ttk
##
##class InteractiveChart:
##    def __init__(self, canvas, chart_w=600, chart_h=300, colors=None):
##        self.canvas = canvas
##        self.chart_w = chart_w
##        self.chart_h = chart_h
##        self.colors = colors if colors else ["red", "blue", "green", "orange"]
##        self.datasets = []
##
##        # Viewport state
##        self.view_start = 0
##        self.view_width = chart_w
##        self.zoom_factor = 1.2
##        self.pan_start_x = 0
##
##        # Bind interactions
##        self.canvas.bind("<MouseWheel>", self.on_zoom)          # Windows/Linux
##        self.canvas.bind("<Button-4>", self.on_zoom_scroll)     # macOS scroll up
##        self.canvas.bind("<Button-5>", self.on_zoom_scroll)     # macOS scroll down
##        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
##        self.canvas.bind("<B1-Motion>", self.on_pan_move)
##
##    def set_data(self, datasets):
##        self.datasets = datasets
##        self.view_start = 0
##        self.view_width = self.chart_w
##        self.redraw()
##
##    def redraw(self):
##        self.canvas.delete("all")
##        print("red")
##        for i, data in enumerate(self.datasets):
##            if not data or len(data) < 2:
##                continue
##
##            color = self.colors[i % len(self.colors)]
##            x_offset = 20 + i * 50
##
##            num_points = len(data)
##            start = self.view_start
##            end = min(start + self.view_width, num_points)
##            data_slice = data[start:end]
##
##            try:
##                max_val = max(data_slice)
##                min_val = min(data_slice)
##            except:
##                max_val = 0.01
##                min_val = 0.0
##
##            if max_val == min_val:
##                max_val += 0.05
##
##            # Labels
##            self.canvas.create_text(x_offset, 10, text=f"Max: {max_val:.2f}", fill=color, anchor="nw")
##            self.canvas.create_text(x_offset, self.chart_h - 10, text=f"Min: {min_val:.2f}", fill=color, anchor="sw")
##            self.canvas.create_text(self.chart_w - x_offset - 10, 10, text=f"{data[-1]:.2f}", fill=color, anchor="ne")
##
##            # Points
##            points = []
##            for x in range(end - start):
##                val = data[start + x]
##                y = self.chart_h - ((val - min_val) / (max_val - min_val)) * (self.chart_h - 20)
##                points.extend([x, round(y)])
##
##            self.canvas.create_line(points, fill=color)
##
##    def on_zoom(self, event):
##        direction = 1 if event.delta > 0 else -1
##        self.zoom(direction)
##
##    def on_zoom_scroll(self, event):
##        direction = 1 if event.num == 4 else -1
##        self.zoom(direction)
##
##    def zoom(self, direction):
##        if direction > 0:
##            self.view_width = max(50, int(self.view_width / self.zoom_factor))
##        else:
##            self.view_width = min(2000, int(self.view_width * self.zoom_factor))
##        self.redraw()
##
##    def on_pan_start(self, event):
##        self.pan_start_x = event.x
##
##    def on_pan_move(self, event):
##        dx = event.x - self.pan_start_x
##        shift = int(dx / 5)
##        self.view_start = max(0, self.view_start - shift)
##        self.pan_start_x = event.x
##        self.redraw()
##
##    def reset_zoom(self):
##        self.view_start = 0
##        self.view_width = self.chart_w
##        self.redraw()
##
##root = tk.Tk()
##canvas = tk.Canvas(root, width=800, height=600, bg="white")
##canvas.pack()
##
##chart = InteractiveChart(canvas,chart_w=600, chart_h=400)
##chart.set_data([
##    [0.1, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0],
##    [10, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28],
##    [100, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120]
##])
##
##ttk.Button(root, text="Reset Zoom", command=chart.reset_zoom).pack(pady=5)
##root.mainloop()

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab, ImageOps
import io

class InteractiveChart:
    def __init__(self, canvas, chart_w=600, chart_h=300, colors=None, zoom_label=None):
        self.canvas = canvas
        self.chart_w = chart_w
        self.chart_h = chart_h
        self.colors = colors if colors else ["red", "blue", "green", "orange"]
        self.datasets = []

        # Viewport state
        self.view_start = 0
        self.view_width = chart_w
        self.zoom_factor = 1.2
        self.pan_start_x = 0

        # UI elements
        self.zoom_label = zoom_label

        # Bind interactions
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom_scroll)
        self.canvas.bind("<Button-5>", self.on_zoom_scroll)
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)

    def set_data(self, datasets):
        self.datasets = datasets
        self.view_start = 0
        self.view_width = self.chart_w
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        for i, data in enumerate(self.datasets):
            if not data or len(data) < 2:
                continue

            color = self.colors[i % len(self.colors)]
            x_offset = 20 + i * 50

            num_points = len(data)
            start = self.view_start
            end = min(start + self.view_width, num_points)
            data_slice = data[start:end]

            try:
                max_val = max(data_slice)
                min_val = min(data_slice)
            except:
                max_val = 0.01
                min_val = 0.0

            if max_val == min_val:
                max_val += 0.05

            # Labels
            self.canvas.create_text(x_offset, 10, text=f"Max: {max_val:.2f}", fill=color, anchor="nw")
            self.canvas.create_text(x_offset, self.chart_h - 10, text=f"Min: {min_val:.2f}", fill=color, anchor="sw")
            self.canvas.create_text(self.chart_w - x_offset - 10, 10, text=f"{data[-1]:.2f}", fill=color, anchor="ne")

            # Points
            points = []
            for x in range(end - start):
                val = data[start + x]
                y = self.chart_h - ((val - min_val) / (max_val - min_val)) * (self.chart_h - 20)
                points.extend([x, round(y)])

            self.canvas.create_line(points, fill=color)

        # Update zoom label
        if self.zoom_label:
            self.zoom_label.config(text=f"Zoom: {self.view_width} pts")

    def on_zoom(self, event):
        direction = 1 if event.delta > 0 else -1
        self.zoom(direction)

    def on_zoom_scroll(self, event):
        direction = 1 if event.num == 4 else -1
        self.zoom(direction)

    def zoom(self, direction):
        if direction > 0:
            self.view_width = max(50, int(self.view_width / self.zoom_factor))
        else:
            self.view_width = min(2000, int(self.view_width * self.zoom_factor))
        self.redraw()

    def on_pan_start(self, event):
        self.pan_start_x = event.x

    def on_pan_move(self, event):
        dx = event.x - self.pan_start_x
        shift = int(dx / 5)
        self.view_start = max(0, self.view_start - shift)
        self.pan_start_x = event.x
        self.redraw()

    def reset_zoom(self):
        self.view_start = 0
        self.view_width = self.chart_w
        self.redraw()

    def export_as_image(self, filename="chart.png"):
        # Save canvas as postscript
        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img = ImageOps.expand(img, border=10, fill='white')  # optional padding
        img.save(filename)
        print(f"Chart saved as {filename}")

root = tk.Tk()
canvas = tk.Canvas(root, width=600, height=300, bg="white")
canvas.pack()

zoom_label = ttk.Label(root, text="Zoom: 600 pts")
zoom_label.pack()

chart = InteractiveChart(canvas, zoom_label=zoom_label)
chart.set_data([
    [0.1, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6, 0.2, 0.5, 0.9, 1.2, 1.0, 1.3, 1.5, 1.4, 1.6],
    [10, 20, 15, 25, 30, 28, 35, 40, 38, 42],
    [100, 105, 102, 110, 115, 120, 125, 130, 128, 135]
])

ttk.Button(root, text="Reset Zoom", command=chart.reset_zoom).pack(pady=5)
#ttk.Button(root, text="Export Chart", command=lambda: chart.export_as_image("chart.png")).pack(pady=5)

root.mainloop()
