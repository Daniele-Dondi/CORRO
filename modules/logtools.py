import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np

def choose_files():
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[ ("CORRO log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
        initialdir="."
    )
    return file_paths

def get_column_names(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            # Detect the header line by checking for known first column
            if line.startswith("Timestamp"):
                return line.split("\t")  # split by tab
    return []

def common_columns(list_of_lists):
    if not list_of_lists:
        return []

    # Start with the first list as a set
    common = set(list_of_lists[0])

    # Intersect with each subsequent list
    for cols in list_of_lists[1:]:
        common &= set(cols)

    return list(common)

def compute_selected_column_averages(file_path, chunk_size, selected_columns_names, output_path, find_string):
    Col_Names=get_column_names(file_path)
    selected_columns=[]
    for column in selected_columns_names:
        selected_columns.append(Col_Names.index(column))
    chunk = []
    i=0
    found=0
    with open(file_path, "r",encoding="utf-8", errors="ignore") as f, open(output_path, "w") as out:
        for line in f:
            i+=1
            if find_string:
                if find_string in line: found+=1
            try:
                values = line.strip().split("\t")
                numeric_values = [float(values[i]) for i in selected_columns]
            except:
                continue  # Skip problematic lines

            chunk.append(numeric_values)

            if len(chunk) == chunk_size:
                avg = np.mean(chunk, axis=0)
                out.write("\t".join(map(str, avg)) + "\n")
                chunk = []

        if chunk:
            avg = np.mean(chunk, axis=0)
            out.write("\t".join(map(str, avg)) + "\n")
    print("Read: "+str(i)+" lines")
    if find_string:
        print(find_string,"found", found,"times")

class DragDropListbox(tk.Listbox):
    """A Tkinter Listbox with drag-and-drop reordering."""
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        super().__init__(master, kw)
        self.curIndex = None
        self.bind('<Button-1>', self.set_current)
        self.bind('<B1-Motion>', self.shift_selection)

    def set_current(self, event):
        self.curIndex = self.nearest(event.y)

    def shift_selection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Log tool analyzer/extractor")

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
        self.prev_btn.config(state="disabled")

        # Ask for files
        file_paths = choose_files()
        if not file_paths:
            controller.destroy()
            return

        # Store original file list
        self.original_file_list = list(file_paths)

        # UI
        tk.Label(self, text="Drag & Drop to select the proper file order").pack()
        self.ddl = DragDropListbox(self, width=100, height=10)
        self.ddl.pack(padx=10, pady=10)

        # Populate listbox
        for f in self.original_file_list:
            self.ddl.insert(tk.END, f)

    def get_file_list(self):
        """Return the current order of files from the listbox."""
        return list(self.ddl.get(0, tk.END))


class Step2(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Get the reordered file list from Step1
        file_list = controller.frames[Step1].get_file_list()

        # Collect all column names
        all_column_names = []
        for file in file_list:
            column_names = get_column_names(file)
            if not column_names:
                messagebox.showerror("Error", f"No valid header found in {file}")
                controller.destroy()
                return
            all_column_names.append(column_names)

        # Find common columns
        common = common_columns(all_column_names)
        print("Common columns:", common)
        
        ttk.Label(self, text="Step 2: Common Columns Found").pack(pady=10)

        self.states = {}  # store ON/OFF state for each button
        for item in common:
            self.states[item] = False  # default OFF
            b = tk.Button(self, text=item, width=20,
                          relief=tk.RAISED,
                          command=lambda bname=item, bwidget=None: None)
            # We need to bind the widget after creation to capture it
            b.config(command=lambda btn=b, name=item: self.toggle(btn, name))
            b.pack()#padx=10, pady=5, anchor="w")

        #tk.Button(self, text="Show States", command=self.show_states).pack(pady=10)

    def get_button_states(self):
        """Print current ON/OFF states."""
        Selected=[]
        for name, state in self.states.items():
            if state:
                Selected.append(name)
        return Selected     
        
    def toggle(self,btn, name):
        """Toggle the button's state and appearance."""
        self.states[name] = not self.states[name]  # flip state
        if self.states[name]:
            btn.config(relief=tk.SUNKEN, bg="lightblue")
        else:
            btn.config(relief=tk.RAISED, bg="SystemButtonFace")

##    def show_states(self):
##        """Print current ON/OFF states."""
##        for name, state in self.states.items():
##            print(f"{name}: {'ON' if state else 'OFF'}")

class Step3(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Step 3: Finish").pack(pady=20)
        # Change Next to Done on last step
        self.next_btn.config(text="Done", command=controller.destroy)
        tk.Button(self, text="Proceed", command=self.Proceed).pack(pady=10)
        
    def Proceed(self):
        FileList = self.controller.frames[Step1].get_file_list()
        SelectedVars = self.controller.frames[Step2].get_button_states()
        print(SelectedVars)
        for File in FileList:
            compute_selected_column_averages(
                file_path=File,
                chunk_size=100,
                selected_columns_names=SelectedVars,
                output_path="averages_output.txt",
                find_string="bicarbonate"
            )        


if __name__ == "__main__":
    app = App()
    app.mainloop()
