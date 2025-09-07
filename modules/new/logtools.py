import numpy as np
import tkinter as tk
from tkinter import filedialog

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


root = tk.Tk()
root.withdraw()  # Hide the root window if you don't need it

FileList=choose_files()
if FileList:
    AllColumnNames=[]
    for File in FileList:
        ColumnNames=get_column_names(File)
        if len(ColumnNames)==0:
            error
        else:
            AllColumnNames.append(ColumnNames)

    print(common_columns(AllColumnNames))

    for File in FileList:
        compute_selected_column_averages(
            file_path=File,
            chunk_size=100,
            selected_columns_names=["pH","ORP"],
            output_path="averages_output.txt",
            find_string="bicarbonate"
        )
