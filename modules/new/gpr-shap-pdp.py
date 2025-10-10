import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.inspection import PartialDependenceDisplay
from sklearn.model_selection import train_test_split
import shap
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Load CSV and separate features/target
def load_data(filename):
    df = pd.read_csv(filename)
    y = df.iloc[:, -1].values
    X = df.iloc[:, :-1]
    feature_names = X.columns.tolist()
    return X, y, feature_names

# Normalize features to [0, 1]
def normalize_features(X):
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler

# Fit GPR model
def fit_gpr(X, y):
    kernel = C(1.0, (1e-3, 1e3)) * RBF(length_scale=1.0)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, normalize_y=True)
    gpr.fit(X, y)
    return gpr

# SHAP analysis
def shap_analysis(model, X, feature_names):
    explainer = shap.KernelExplainer(model.predict, X)
    shap_values = explainer.shap_values(X, nsamples=100)
    shap.summary_plot(shap_values, X, feature_names=feature_names)

# PDP analysis
def pdp_analysis(model, X, feature_names):
    PartialDependenceDisplay.from_estimator(model, X, features=range(X.shape[1]), feature_names=feature_names)
    plt.show()

# Main pipeline
def run_pipeline(filename):
    X_raw, y, feature_names = load_data(filename)
    X_scaled, scaler = normalize_features(X_raw)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    gpr_model = fit_gpr(X_train, y_train)

    print("Model fitted. Running SHAP analysis...")
    shap_analysis(gpr_model, X_test, feature_names)

    print("Running PDP analysis...")
    pdp_analysis(gpr_model, X_test, feature_names)

def load_csv():
    # Open file dialog to select CSV
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if file_path:
        run_pipeline(file_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("GPR pdp shap")
    root.geometry("300x150")

    # Add button to trigger CSV loading
    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()

