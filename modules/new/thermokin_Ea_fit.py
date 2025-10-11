import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


# Constants
R = 8.314  # J/mol·K
T = 298.15  # K

def plot_ea_heatmap(df, R=8.314, T=298.15):
    df = df.copy()
    df['Ligand_Short_Hand'] = df['Ligand_Short_Hand'].fillna('None').str.strip()
    df['Base'] = df['Base'].fillna('Unknown').astype(str).str.strip()
    df['Yield'] = df['Yield'].clip(lower=1e-3)
    df['Ea_rel'] = -R * T * np.log(df['Yield'])

    pivot = df.pivot(index='Base', columns='Ligand_Short_Hand', values='Ea_rel')

    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, cbar_kws={'label': 'Ea (J/mol)'})
    plt.title("Relative Activation Energy (Ea) Heatmap")
    plt.xlabel("Ligand")
    plt.ylabel("Base")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Core logic
def estimate_Ea(yield_values):
    return -R * T * np.log(np.clip(yield_values, 1e-3, None))

def load_and_process_csv(filepath):
    df = pd.read_csv(filepath, sep=',')
    df['Ligand_Short_Hand'] = df['Ligand_Short_Hand'].fillna('None').str.strip()
    df['Base'] = df['Base'].fillna('No Base').astype(str).str.strip()
    df['Ligand_eq'] = df['Ligand_eq'].fillna(0.0)
    df['Ea_rel'] = estimate_Ea(df['Yield'])
    return df

def update_plot():
    ligand = ligand_var.get()
    base = base_var.get()
    mode = view_mode.get()

    ax.clear()

    if mode == "Ligand vs Base":
        filtered = df[df['Base'] == base]
        ax.bar(filtered['Ligand_Short_Hand'], filtered['Ea_rel'], color='teal')
        ax.set_title(f'Ea across ligands with {base}')
        ax.set_xlabel('Ligand')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
    else:
        filtered = df[df['Ligand_Short_Hand'] == ligand]
        ax.bar(filtered['Base'], filtered['Ea_rel'], color='darkorange')
        ax.set_title(f'Ea across bases for {ligand}')
        ax.set_xlabel('Base')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()

    ax.set_ylabel('Relative Ea (J/mol)')
    canvas.draw()

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
    if filepath:
        global df
        df = load_and_process_csv(filepath)
        ligands = sorted(df['Ligand_Short_Hand'].unique())
        bases = sorted(df['Base'].astype(str).unique())
        ligand_menu['values'] = ligands
        base_menu['values'] = bases
        ligand_var.set(ligands[0])
        base_var.set(bases[0])
        update_plot()

##MAXIMUM THERMODYNAMIC YIELD
#It calculates the maximum thermodynamic Yield for a reaction, knowing the deltaG value in J/mol, the stoichiometry and the initial concentrations of reactants.
def equilibrium_yield_stoichiometry(DeltaG, A0, B0, a, b, c, d, T=298.15, R=8.314):
    Keq = np.exp(-DeltaG / (R * T))

    def equilibrium_eq(x):
        numerator = (c * x)**c * (d * x)**d
        denominator = (A0 - a * x)**a * (B0 - b * x)**b
        return Keq * denominator - numerator

    from scipy.optimize import brentq
    x_max = min(A0 / a, B0 / b)
    x_eq = brentq(equilibrium_eq, 0, x_max)

    yield_C = c * x_eq
    yield_fraction = yield_C / (c * x_max)
    return yield_C, yield_fraction        

# GUI setup
root = tk.Tk()
root.title("Thermokinetic Ligand/Base Analyzer")

frame = ttk.Frame(root, padding=10)
frame.pack()

ttk.Button(frame, text="Select CSV File", command=select_file).grid(row=0, column=0, columnspan=2, pady=5)

ligand_var = tk.StringVar()
base_var = tk.StringVar()

# Add this near the top of your GUI setup
view_mode = tk.StringVar(value="Ligand vs Base")  # Default view

ttk.Label(frame, text="Ligand:").grid(row=1, column=0, sticky='e')
ligand_menu = ttk.Combobox(frame, textvariable=ligand_var, state="readonly")
ligand_menu.grid(row=1, column=1)

ttk.Label(frame, text="Base:").grid(row=2, column=0, sticky='e')
base_menu = ttk.Combobox(frame, textvariable=base_var, state="readonly")
base_menu.grid(row=2, column=1)

ttk.Label(frame, text="View Mode:").grid(row=3, column=0, sticky='e')
view_menu = ttk.Combobox(frame, textvariable=view_mode, state="readonly")
view_menu['values'] = ["Ligand vs Base", "Base vs Ligand"]
view_menu.grid(row=3, column=1)

ttk.Button(frame, text="Update Ea", command=update_plot).grid(row=4, column=0, columnspan=2, pady=5)

ttk.Button(frame, text="Show Ea Heatmap", command=lambda: plot_ea_heatmap(df)).grid(row=5, column=0, columnspan=2, pady=5)




# Matplotlib plot
fig, ax = plt.subplots(figsize=(5, 3))
#canvas = plt.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=root)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
