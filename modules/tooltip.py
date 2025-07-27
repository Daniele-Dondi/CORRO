import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("Arial", 10))
        label.pack(ipadx=5, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

### Main application
##root = tk.Tk()
##root.title("Button with Tooltip")
##
##button = tk.Button(root, text="Hover over me!")
##button.pack(pady=20, padx=20)
##
### Add tooltip to the button
##ToolTip(button, "This is a helpful hint!")
##
##root.mainloop()
##
####Explanation:
####
##ToolTip Class:
##
##Handles the creation and destruction of the tooltip window.
##Displays the tooltip when the mouse enters the widget and hides it when the mouse leaves.
##
##Binding Events:
##
##<Enter>: Triggered when the mouse pointer enters the widget.
##<Leave>: Triggered when the mouse pointer leaves the widget.
##
##Styling:
##
##The tooltip is styled with a yellow background, solid border, and padding for better visibility.
##
##This approach is reusable, so you can attach tooltips to multiple widgets by creating instances of the ToolTip class.
