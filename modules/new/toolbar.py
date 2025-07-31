import tkinter as tk

root = tk.Tk()
root.title("Toolbar Example")

# Create the toolbar frame
toolbar = tk.Frame(root, bd=1, relief=tk.RAISED, background="#e0e0e0")
toolbar.pack(side=tk.TOP, fill=tk.X)

# Add buttons to the toolbar
new_btn = tk.Button(toolbar, text="New")
open_btn = tk.Button(toolbar, text="Open")
save_btn = tk.Button(toolbar, text="Save")

new_btn.pack(side=tk.LEFT, padx=2, pady=2)
open_btn.pack(side=tk.LEFT, padx=2, pady=2)
save_btn.pack(side=tk.LEFT, padx=2, pady=2)

root.mainloop()
