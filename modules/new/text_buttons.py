import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Multiple Checkbuttons in Text Widget")

# Create a Text widget
text_widget = tk.Text(root, width=40, height=15)
text_widget.pack(pady=10)

# Define options for checkbuttons
options = ["Option A", "Option B", "Option C", "Option D"]
check_vars = []

# Insert checkbuttons into the Text widget
for option in options:
    var = tk.IntVar()
    checkbutton = tk.Checkbutton(root, text=option, variable=var)
    check_vars.append((option, var))
    text_widget.insert(tk.END, "\n")
    text_widget.window_create(tk.END, window=checkbutton)

# Define the button callback
def show_selected():
    selected = [label for label, var in check_vars if var.get()]
    print("Selected options:", selected)

# Create and insert the Button into the Text widget
text_widget.insert(tk.END, "\n\n")
button = tk.Button(root, text="Show Selected", command=show_selected)
text_widget.window_create(tk.END, window=button)

# Run the application
root.mainloop()

