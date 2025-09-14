import PIL.Image
from PIL import ImageTk
import tkinter as tk
import threading
from tkinter import filedialog
from tkinter import ttk

chart_w=800 #size of the temp and voltages chart
chart_h=600

def draw_multi_chart(canvas, datasets, chart_w, chart_h, colors, draw_all=True):
    """
    Draws multiple datasets on a Tkinter canvas with individual scaling and min/max labels.

    Parameters:
        canvas (tk.Canvas): The canvas to draw on.
        datasets (list of lists): Each inner list is a dataset to plot.
        chart_w (int): Width of the chart area.
        chart_h (int): Height of the chart area.
        colors (list): List of colors for each dataset.
        draw_all (bool): If True, plots full dataset; else plots last chart_w points.
    """
    canvas.delete("all")  # Clear previous drawings

    for i, data in enumerate(datasets):
        if not data or len(data) < 2:
            continue

        color = colors[i % len(colors)]
        x_offset = 20 + i * 50

        # Determine plotting range
        num_points = len(data)
        if draw_all or num_points <= chart_w:
            start = 0
            end = num_points
        else:
            start = num_points - chart_w
            end = num_points

        data_slice = data[start:end]
        try:
            max_val = max(data_slice)
            min_val = min(data_slice)
        except:
            max_val = 0.01
            min_val = 0.0

        if max_val == min_val:
            max_val += 0.05  # Avoid flat line scaling

        # Draw max and min value labels
        canvas.create_text(x_offset, 10, text="Max: {:.2f}".format(max_val), fill=color, anchor="nw")
        canvas.create_text(x_offset, chart_h - 10, text="Min: {:.2f}".format(min_val), fill=color, anchor="sw")

        # Draw last value label (optional)
        canvas.create_text(chart_w - x_offset - 10, 10, text="{:.2f}".format(data[-1]), fill=color, anchor="ne")

        # Prepare points
        points = []
        for x in range(end - start):
            val = data[start + x]
            y = chart_h - ((val - min_val) / (max_val - min_val)) * (chart_h - 20)
            points.extend([x, round(y)])

        canvas.create_line(points, fill=color)

base = tk.Tk()
Graph=tk.Frame(base)  #frame for graph showing values
Graph.pack(side="bottom")
w=tk.Canvas(Graph,width=chart_w,height=chart_h)
w.pack(expand="yes",fill="both")



datasets = [
    [0.1, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0, 0.2, 0.5, 0.9, 1.2, 1.0],
    [10, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28, 20, 15, 25, 30, 28],
    [100, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120, 105, 102, 110, 115, 120]
]
colors = ["red", "blue", "green"]
draw_multi_chart(canvas=w, datasets=datasets, chart_w=800, chart_h=600, colors=colors, draw_all=False)

base.mainloop()
