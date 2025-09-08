import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np

def choose_files():
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[ ("CORRO log Files", "*.txt"), ("Text Files", "*.txt"), ("All Files", "*.*")],
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
        self.config(cursor="hand2")
        self.bind('<Button-1>', self.set_current)
        self.bind('<B1-Motion>', self.shift_selection)
        self.bind('<ButtonRelease-1>', self.clear_current)

    def set_current(self, event):
        self.curIndex = self.nearest(event.y)

    def shift_selection(self, event):
        i = self.nearest(event.y)
        if i < 0 or i >= self.size():
            return
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
        self.selection_clear(0, tk.END)
        self.selection_set(i)

    def clear_current(self, event):
        self.curIndex = None

    def clear_all(self):
        self.delete(0, tk.END)

    def get_file_list(self):
        return list(self.get(0, tk.END))



class LogAnalyzer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Log tool analyzer/extractor")
        icon = tk.PhotoImage(file="icons/tools.png")
        self.iconphoto(False, icon)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Ordered list of step classes
        self.step_classes = [Step1, Step2, Step3, Step4]
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
        # Call refresh if the frame has it
        if hasattr(frame, "refresh"):
            frame.refresh()

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
        tk.Label(self, text="Choose File(s) to analyze").pack()
        self.file_paths=[]
        tk.Button(self, text="Choose", command=self.ChoseFile).pack(pady=10)

    def ChoseFile(self):
        self.file_paths = choose_files()
        if not self.file_paths:
            self.controller.destroy()
            return
        self.controller.next_step()
        
    def GetFiles(self):
        return list(self.file_paths)

class Step2(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="Drag & Drop to select the proper file order").pack()
        self.ddl = DragDropListbox(self, width=100, height=10)
        self.ddl.pack(padx=10, pady=10)
        
    def refresh(self):
        self.ddl.delete(0, tk.END)
        file_list = self.controller.frames[Step1].GetFiles()
        for f in file_list:
            self.ddl.insert(tk.END, f)
          

    def get_file_list(self):
        """Return the current order of files from the listbox."""
        return list(self.ddl.get(0, tk.END))


class Step3(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Select Variable(s) to extract").pack(pady=10)
        self.b_list=[]
        self.common=[]

    def refresh(self):
        if len(self.b_list)>0:
            for button in self.b_list:
                button.destroy()
            self.b_list=[]
        # Get the reordered file list from Step2
        file_list = self.controller.frames[Step2].get_file_list()

        # Collect all column names
        all_column_names = []
        for file in file_list:
            column_names = get_column_names(file)
            if not column_names:
                messagebox.showerror("Error", f"No valid header found in {file}")
                #self.controller.destroy()
                return
            all_column_names.append(column_names)

        # Find common columns
        self.common = common_columns(all_column_names)
        
        self.states = {}  # store ON/OFF state for each button
        for item in self.common:
            self.states[item] = False  # default OFF
            b = tk.Button(self, text=item, width=20,
                          relief=tk.RAISED,
                          command=lambda bname=item, bwidget=None: None)
            # We need to bind the widget after creation to capture it
            b.config(command=lambda btn=b, name=item: self.toggle(btn, name))
            b.pack()#padx=10, pady=5, anchor="w")
            self.b_list.append(b)

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

class Step4(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
      
        ttk.Label(self, text="Setup Average Analysis & Save").pack(pady=20)
        # Change Next to Done on last step
        self.next_btn.config(text="Done", command=self.Proceed)
        
        ttk.Label(self, text="Insert the number of points to average:").pack(pady=10)
        self.Average=tk.Entry(self)
        self.Average.delete(0,tk.END)  # Clear any existing text
        self.Average.insert(0,"100")        
        self.Average.pack()
        self.Average.config(state="normal")
        self.Average.focus_set()
        ttk.Label(self, text="Insert (eventually) a string to search").pack(pady=10)
        self.Search=tk.Entry(self)
        self.Search.pack()
        self.output_path = tk.StringVar()
        
        tk.Button(self, text="Proceed", command=self.Proceed).pack(pady=10)

    def choose_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Select output file"
        )
        if filename:
            self.output_path.set(filename)

    def Check(self):
        FileList = self.controller.frames[Step2].get_file_list()
        if len(FileList)==0:
            messagebox.showerror("Error", "No log files were chosen")
            return False           
        Variables = self.controller.frames[Step3].common
        if len(Variables)==0:
            messagebox.showerror("Error", "No variables to analyze. Check if the file chosen is a proper CORRO log file")
            return False
        SelectedVars = self.controller.frames[Step3].get_button_states()
        if len(SelectedVars)==0:
            messagebox.showerror("Error", "No variables to analyze were selected")
            return False
        
        return True
    
    def Shrink(self):
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showerror("Error", "Please choose an output file.")
            return
        FileList = self.controller.frames[Step2].get_file_list()
        SelectedVars = self.controller.frames[Step3].get_button_states()
        AvgSize=int(self.Average.get())
        SearchString=self.Search.get()
        for File in FileList:
            compute_selected_column_averages(
                file_path=File,
                chunk_size=AvgSize,
                selected_columns_names=SelectedVars,
                output_path=output_file,
                find_string=SearchString
            )            
        
    def Proceed(self):
        try:
            a=int(self.Average.get())
            if a<=0:
                1/0
        except:
            messagebox.showerror("ERROR", "Insert a valid integer value for the average")
        else:
            if self.Check():
                self.choose_output_file()
                self.Shrink()

