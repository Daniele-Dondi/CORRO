import tkinter as tk
from tkinter import ttk, messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wizard with Prev / Next / Cancel")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Ordered list of step classes
        self.step_classes = [Step1, Step2, Step3]
        self.frames = {}

        for F in self.step_classes:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_index = 0
        self.show_frame(self.step_classes[self.current_index])

    def show_frame(self, step_class):
        """Raise the given frame."""
        frame = self.frames[step_class]
        frame.tkraise()

    def next_step(self):
        if self.current_index < len(self.step_classes) - 1:
            self.current_index += 1
            self.show_frame(self.step_classes[self.current_index])

    def prev_step(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_frame(self.step_classes[self.current_index])

    def cancel_process(self):
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?"):
            self.destroy()

class BaseStep(tk.Frame):
    """Base class for steps with Prev / Next / Cancel buttons."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        nav_frame = tk.Frame(self)
        nav_frame.pack(side="bottom", pady=10)

        self.prev_btn = ttk.Button(nav_frame, text="Prev",
                                   command=controller.prev_step)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.next_btn = ttk.Button(nav_frame, text="Next",
                                   command=controller.next_step)
        self.next_btn.grid(row=0, column=1, padx=5)

        ttk.Button(nav_frame, text="Cancel",
                   command=controller.cancel_process).grid(row=0, column=2, padx=5)

class Step1(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Step 1: Make a selection").pack(pady=20)
        # Disable Prev on first step
        self.prev_btn.config(state="disabled")

class Step2(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Step 2: Confirm details").pack(pady=20)

class Step3(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Step 3: Finish").pack(pady=20)
        # Change Next to Done on last step
        self.next_btn.config(text="Done", command=controller.destroy)

if __name__ == "__main__":
    app = App()
    app.mainloop()
