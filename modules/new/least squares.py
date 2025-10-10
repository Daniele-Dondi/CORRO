import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import re

class LeastSquaresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Least Squares Fitting")

        # === Widgets ===
        self.load_button = tk.Button(root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        self.func_label = tk.Label(root, text="Enter function (e.g., a*X1 + b*X1/X2):")
        self.func_label.pack()

        self.func_frame = tk.Frame(root)
        self.func_frame.pack(pady=5)

        self.func_scrollbar = tk.Scrollbar(self.func_frame, orient=tk.HORIZONTAL)
        self.func_entry = tk.Entry(self.func_frame, width=50, xscrollcommand=self.func_scrollbar.set)
        self.func_entry.pack(side=tk.TOP, fill=tk.X)
        self.func_scrollbar.config(command=self.func_entry.xview)
        self.func_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.var_button_frame = tk.Frame(root)
        self.var_button_frame.pack(pady=5)

        self.fit_button = tk.Button(root, text="Fit Function", command=self.fit_function)
        self.fit_button.pack(pady=10)

        # Frame to hold Text and Scrollbar
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)

        # Text widget with yscrollcommand linked to scrollbar
        self.result_text = tk.Text(self.text_frame, height=10, width=60, yscrollcommand=self.scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar to control the text widget
        self.scrollbar.config(command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.df = None

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.df.columns = [col.strip().replace(" ", "_") for col in self.df.columns]

                messagebox.showinfo("Success", f"Loaded {file_path}")

                # Clear previous buttons
                for widget in self.var_button_frame.winfo_children():
                    widget.destroy()

                # Create buttons for each input column (exclude last column)
                input_columns = self.df.columns[:-1]
                for col in input_columns:
                    btn = tk.Button(self.var_button_frame, text=col, command=lambda c=col: self.insert_variable(c))
                    btn.pack(side=tk.LEFT, padx=2)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def insert_variable(self, var_name):
        pos = self.func_entry.index(tk.INSERT)
        self.func_entry.insert(pos, var_name)
                
    def fit_function(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return

        func_str = self.func_entry.get()
        if not func_str:
            messagebox.showwarning("No Function", "Please enter a function to fit.")
            return

        try:
            Y = self.df.iloc[:, -1].values
            X = self.df.iloc[:, :-1]

            # Extract parameter names from function string
            param_names = sorted(set(re.findall(r'\b[a-zA-Z_]\w*\b', func_str)) - set(X.columns))

            def model_function(X_data, *params):
                # Ensure X_data is a DataFrame
                if not isinstance(X_data, pd.DataFrame):
                    X_data = pd.DataFrame(X_data, columns=self.df.columns[:-1])

                # Prepare local variables from columns
                local_vars = {col: X_data[col].values for col in X_data.columns}

                # Inject parameters safely
                for name, value in zip(param_names, params):
                    if value is None:
                        raise ValueError(f"Parameter '{name}' is None — check your function string and parameter count.")
                    local_vars[name] = float(value)

                # Evaluate the function string
                try:
                    result = eval(func_str, {}, local_vars)
                except Exception as e:
                    raise ValueError(f"Error evaluating function: {e}")

                return result


            # Convert X to numpy array for curve_fit
            X_array = X.to_numpy()

            # Fit the model
            params_opt, _ = curve_fit(lambda X_flat, *params: model_function(pd.DataFrame(X_flat, columns=X.columns), *params),
                                      X_array, Y, p0=[1.0]*len(param_names))

            # === Predict Y using fitted parameters ===
            Y_pred = model_function(X, *params_opt)

            # === Calculate R² and RMSE ===
            from sklearn.metrics import r2_score, root_mean_squared_error

            r2 = r2_score(Y, Y_pred)
            rmse = root_mean_squared_error(Y, Y_pred)

            # === Display results ===
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Fitted Parameters:\n")
            for name, value in zip(param_names, params_opt):
                self.result_text.insert(tk.END, f"{name} = {value:.4f}\n")

            self.result_text.insert(tk.END, f"\nR² = {r2:.4f}\n")
            self.result_text.insert(tk.END, f"RMSE = {rmse:.4f}\n")

            self.result_text.insert(tk.END, "\nMeasured Y vs Predicted Y:\n")
            for y_true, y_hat in zip(Y, Y_pred):
                self.result_text.insert(tk.END, f"{y_true:.4f} → {y_hat:.4f}\n")
            

        except Exception as e:
            messagebox.showerror("Error", f"Fitting failed: {e}")

# === Run the App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = LeastSquaresApp(root)
    root.mainloop()
