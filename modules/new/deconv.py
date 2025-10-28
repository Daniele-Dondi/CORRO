import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF

class SpectralDeconvolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectral Deconvolution with NMF")
        self.spectra = []

        # GUI Elements
        tk.Button(root, text="Load Spectra CSV Files", command=self.load_files).pack(pady=10)
        tk.Label(root, text="Number of Components:").pack()
        self.components_entry = tk.Entry(root)
        self.components_entry.pack()
        tk.Button(root, text="Run NMF", command=self.run_nmf).pack(pady=10)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if not file_paths:
            return
        self.spectra = []
        for path in file_paths:
            try:
                df = pd.read_csv(path)
                if df.shape[1] < 2:
                    raise ValueError("CSV must have at least two columns (X and Y)")
                self.spectra.append(df.iloc[:, 1].values)  # Use Y values only
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {path}:\n{e}")
        messagebox.showinfo("Loaded", f"Loaded {len(self.spectra)} spectra.")

    def run_nmf(self):
        if not self.spectra:
            messagebox.showwarning("No Data", "Please load spectra first.")
            return
        try:
            n_components = int(self.components_entry.get())
            data_matrix = np.array(self.spectra)
            model = NMF(n_components=n_components, init='random', random_state=0)
            W = model.fit_transform(data_matrix)
            H = model.components_

            # Plot estimated pure spectra
            plt.figure(figsize=(10, 6))
            for i, spectrum in enumerate(H):
                plt.plot(spectrum, label=f'Component {i+1}')
            plt.title('Estimated Pure Component Spectra')
            plt.xlabel('Wavelength Index')
            plt.ylabel('Intensity')
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run NMF:\n{e}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SpectralDeconvolutionApp(root)
    root.mainloop()
