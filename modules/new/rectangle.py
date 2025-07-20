import tkinter as tk

# Create the main window
root = tk.Tk()

# Set the window size
root.geometry("400x300")

# Set a specific color to be transparent
root.wm_attributes("-transparentcolor", "white")  # Replace "white" with your desired color

# Add a label with a transparent background
label = tk.Label(root, text="Hello, Transparent World!", bg="white", font=("Arial", 16))
label.pack(pady=50)

# Run the application
root.mainloop()
