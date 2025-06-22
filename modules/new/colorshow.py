import matplotlib.colors as mcolors
import tkinter as tk

colors = mcolors.CSS4_COLORS  # Dictionary of color names and their hex codes

def draw_color_rectangles(colors):
    rect_width = 100
    rect_height = 20
    padding = 2

    # Calculate canvas height based on number of colors
    canvas_height = (rect_height + padding) * len(colors)//10 + padding*2
    canvas_width = rect_width*10 + 2 * padding

    root = tk.Tk()
    root.title("Tkinter named colors")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()
    num=0
    for color in colors:
     try:
        x_start=(num % 10)* rect_width  
        y_start = padding + num//10 * (rect_height + padding)
        canvas.create_rectangle(
            x_start,
            y_start,
            x_start + rect_width,
            y_start + rect_height,
            fill=color,
            outline="black"
        )
        canvas.create_text(
            x_start + 5,
            y_start + rect_height / 2,
            anchor="w",
            text=color
        )
        num+=1
     except: pass
    root.mainloop()

# Example list of color names
draw_color_rectangles(colors)
