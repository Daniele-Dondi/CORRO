##import matplotlib.pyplot as plt
##from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
##from tkinter import Frame, Button, filedialog
##
##class GraphDrawer(Frame):
##    def __init__(self, master=None, width=800, height=600):
##        super().__init__(master)
##        self.pack()
##        self.figure, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
##        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
##        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
##        self.toolbar.update()
##        self.canvas.get_tk_widget().pack(fill="both", expand=True)
##
##        # Optional: Add export button
##        export_btn = Button(self, text="Export", command=self.export_graph)
##        export_btn.pack()
##
##    def plot_series(self, x_data, y_data, label=None, color=None, linestyle='-'):
##        """Add a new series to the plot."""
##        self.ax.plot(x_data, y_data, label=label, color=color, linestyle=linestyle)
##        self.ax.legend()
##        self.canvas.draw()
##
##    def clear_plot(self):
##        """Clear all data from the plot."""
##        self.ax.cla()
##        self.canvas.draw()
##
##    def export_graph(self):
##        """Save the current figure to PNG or SVG."""
##        file_path = filedialog.asksaveasfilename(defaultextension=".png",
##                                                 filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
##        if file_path:
##            self.figure.savefig(file_path)
##
### Example usage in a Tkinter app
##if __name__ == "__main__":
##    import tkinter as tk
##    root = tk.Tk()
##    root.title("Scientific Graph Viewer")
##    graph = GraphDrawer(master=root)
##    graph.plot_series([0, 1, 2], [0, 1, 4], label="Series A", color="blue")
##    graph.plot_series([0, 1, 2], [0, 2, 3], label="Series B", color="green")
##    root.mainloop()

import tkinter as tk
from tkinter import Frame, Button, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class GraphDrawer(Frame):
    def __init__(self, master=None, width=800, height=600):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # Create Matplotlib figure and axis
        self.figure, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

        # Embed Matplotlib canvas in Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Add Matplotlib toolbar for zoom/pan
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

##        # Optional export button
##        export_btn = Button(self, text="Export", command=self.export_graph)
##        export_btn.pack(pady=5)

    def plot_multiple_series(self, x_data, y_series_list, labels=None, colors=None, linestyles=None):
        """
        Plot multiple Y-series against a shared X-series.
        """
        for i, y_data in enumerate(y_series_list):
            label = labels[i] if labels and i < len(labels) else f"Series {i+1}"
            color = colors[i] if colors and i < len(colors) else None
            linestyle = linestyles[i] if linestyles and i < len(linestyles) else '-'
            self.ax.plot(x_data, y_data, label=label, color=color, linestyle=linestyle)

        self.ax.legend()
        self.canvas.draw()

    def clear_plot(self):
        """Clear all data from the plot."""
        self.ax.cla()
        self.canvas.draw()

##    def export_graph(self):
##        """Save the current figure to PNG or SVG."""
##        file_path = filedialog.asksaveasfilename(defaultextension=".png",
##                                                 filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
##        if file_path:
##            self.figure.savefig(file_path)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scientific Graph Viewer")

    graph = GraphDrawer(master=root)

    # Shared X-axis
    x = list(range(1, 11))

    # Multiple Y-series
    y_series = [
        [i for i in x],                      # Linear
        [i**2 for i in x],                   # Quadratic
        [10 - i for i in x]                  # Inverted
    ]
    labels = ["Linear", "Quadratic", "Inverted"]
    colors = ["blue", "green", "red"]

    graph.plot_multiple_series(x, y_series, labels=labels, colors=colors)

    root.mainloop()
