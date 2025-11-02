import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize

class SpectralDeconvolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectral Deconvolution with NMF")
        self.x_values = []
        self.y_values = []

        # GUI Elements
        tk.Button(root, text="Load Spectra CSV Files", command=self.load_files).pack(pady=10)

        tk.Label(root, text="Number of Components:").pack()
        self.components_entry = tk.Entry(root)
        self.components_entry.pack()

        self.normalize_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Normalize Spectra", variable=self.normalize_var).pack()

        tk.Button(root, text="Run NMF", command=self.run_nmf).pack(pady=10)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if not file_paths:
            return
        self.x_values = []
        self.y_values = []
        for path in file_paths:
            try:
                df = pd.read_csv(path)
                if df.shape[1] < 2:
                    raise ValueError("CSV must have at least two columns (X and Y)")
                self.x_values.append(df.iloc[:, 0].values)
                self.y_values.append(df.iloc[:, 1].values)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {path}:\n{e}")
        messagebox.showinfo("Loaded", f"Loaded {len(self.y_values)} spectra.")

    def run_nmf(self):
        if not self.y_values:
            messagebox.showwarning("No Data", "Please load spectra first.")
            return
        try:
            n_components = int(self.components_entry.get())
            # Interpolate all spectra to a common X grid
            common_x = np.linspace(min(x.min() for x in self.x_values),
                                   max(x.max() for x in self.x_values),
                                   500)
            aligned_spectra = []
            for x, y in zip(self.x_values, self.y_values):
                aligned_y = np.interp(common_x, x, y)
                aligned_spectra.append(aligned_y)
            data_matrix = np.array(aligned_spectra)

            # Normalize if selected
            if self.normalize_var.get():
                data_matrix = normalize(data_matrix, axis=1)

            # Run NMF
            model = NMF(n_components=n_components, init='nndsvda', random_state=0)
            W = model.fit_transform(data_matrix)
            H = model.components_

            # Plot estimated pure spectra
            plt.figure(figsize=(10, 6))
            for i, spectrum in enumerate(H):
                plt.plot(common_x, spectrum, label=f'Component {i+1}')
            plt.title('Estimated Pure Component Spectra')
            plt.xlabel('X (interpolated)')
            plt.ylabel('Intensity')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            # Save results
            np.savetxt("nmf_components.csv", H, delimiter=",")
            np.savetxt("nmf_weights.csv", W, delimiter=",")
            messagebox.showinfo("Success", "NMF completed and results saved.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run NMF:\n{e}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SpectralDeconvolutionApp(root)
    root.mainloop()
