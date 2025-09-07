import tkinter as tk

def toggle(btn, name):
    """Toggle the button's state and appearance."""
    states[name] = not states[name]  # flip state
    if states[name]:
        btn.config(relief=tk.SUNKEN, bg="lightblue")
    else:
        btn.config(relief=tk.RAISED, bg="SystemButtonFace")

def show_states():
    """Print current ON/OFF states."""
    for name, state in states.items():
        print(f"{name}: {'ON' if state else 'OFF'}")

# Example list
items = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]

root = tk.Tk()
root.title("Sunken Toggle Buttons")

states = {}  # store ON/OFF state for each button

for item in items:
    states[item] = False  # default OFF
    b = tk.Button(root, text=item, width=20,
                  relief=tk.RAISED,
                  command=lambda bname=item, bwidget=None: None)
    # We need to bind the widget after creation to capture it
    b.config(command=lambda btn=b, name=item: toggle(btn, name))
    b.pack(padx=10, pady=5, anchor="w")

tk.Button(root, text="Show States", command=show_states).pack(pady=10)

root.mainloop()
