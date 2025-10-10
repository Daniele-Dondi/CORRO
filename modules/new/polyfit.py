import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import tkinter as tk
from tkinter import filedialog
import os

### Paste your data as a multiline string
##raw_data = """
##0.570291777	0.157142857	0.30952381	0.059171598	41.26452613
##0.570291777	0.141527002	0.085539715	0.05952381	62.78571552
##0.570291777	0.173553719	1	0.113207547	53.33497035
##0.643070788	0.149333333	1	0.052941176	17.55880282
##0.83643617	0.160390516	0.085539715	0.052941176	5.529906697
##1	0.173553719	0.085539715	0.128342246	42.81292825
##"""  
##
### Convert to NumPy array
##data = np.array([list(map(float, line.split())) for line in raw_data.strip().split('\n')])
##
### Split into X and Y
##X = data[:, :4]  # First 4 columns
##Y = data[:, 4]   # Last column

def PolyFit(filename):
    df = pd.read_csv(filename)
    # Separate last column into Y
    last_column = df.columns[-1]
    Y = df[last_column].tolist()
    
    # Remaining columns into X
    X = df.drop(columns=[last_column])
    print()
    print(os.path.basename(filename))
    for degree in [1, 2, 3]:
        print(f"\nPolynomial Regression (Degree {degree})")
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, Y)

        #print("Coefficients:", model.coef_)
        terms = poly.get_feature_names_out()
        for term, coef in zip(terms, model.coef_):
            print(" ",end="")
            if coef>0:
                print("+",end="")
            print(f"{coef:.3f}*{term}",end="")
        print()
        y_pred = model.predict(X_poly)
        r_squared = r2_score(Y, y_pred)

        print("Intercept:", model.intercept_)
        print("R² score:", r_squared)

def load_csv():
    # Open file dialog to select CSV
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if file_path:
        PolyFit(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polynomial Fit")
    root.geometry("300x150")

    # Add button to trigger CSV loading
    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()

