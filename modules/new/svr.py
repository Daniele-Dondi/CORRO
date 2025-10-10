import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV


def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        data = pd.read_csv(file_path)
        if data.shape[1] < 2:
            messagebox.showerror("Error", "CSV must contain at least one feature and one target column.")
            return

        X = data.iloc[:, :-1].values  # All columns except last
        y = data.iloc[:, -1].values   # Last column (reaction yield)

        # Split and scale
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        param_grid = {
            'C': [0.1, 1, 10, 100],
            'epsilon': [0.01, 0.1, 0.5],
            'kernel': ['rbf', 'linear'],
            'gamma': ['scale', 'auto']
        }
        

        # SVR model
        grid = GridSearchCV(SVR(), param_grid, cv=5, scoring='r2')
        grid.fit(X_train_scaled, y_train)

        best_model = grid.best_estimator_
        y_pred = best_model.predict(X_test_scaled)
        

        # Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        result_text = (
            f"Best Parameters: {grid.best_params_}\n\n"
            f"R² Score: {r2:.3f}\nRMSE: {rmse:.3f}\nMAE: {mae:.3f}"
        )
        print(result_text)
        messagebox.showinfo("Model Evaluation", result_text)
        

        # Plot
        plt.figure(figsize=(6, 6))
        plt.scatter(y_test, y_pred, alpha=0.7)
        plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')
        plt.xlabel("Actual Yield")
        plt.ylabel("Predicted Yield")
        plt.title("SVR Prediction vs Actual")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

# GUI setup
root = tk.Tk()
root.title("Reaction Yield Prediction with SVR")
root.geometry("400x200")

label = tk.Label(root, text="Load a CSV file to predict reaction yield using SVR", wraplength=350)
label.pack(pady=20)

load_button = tk.Button(root, text="Load CSV", command=load_csv, width=20)
load_button.pack(pady=10)

root.mainloop()
