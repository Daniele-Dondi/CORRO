import numpy as np
from sklearn.preprocessing import MinMaxScaler
from numpy.polynomial.legendre import legval
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

def LegendreFit(filename,order=3):
    df = pd.read_csv(filename)
    # Separate last column into Y
    last_column = df.columns[-1]
    y_raw = df[last_column].tolist()
    
    # Remaining columns into X
    X_raw = df.drop(columns=[last_column])

    # Normalize X to [-1, 1]
    scaler = MinMaxScaler(feature_range=(-1, 1))
    X = scaler.fit_transform(X_raw)

##    # Define polynomial order
##    order = 3

    # Generate Legendre basis for each feature
    def legendre_features(X, order):
        n_samples, n_features = X.shape
        features = []
        for i in range(n_features):
            col = X[:, i]
            for deg in range(order + 1):
                coeffs = [0] * (deg) + [1]
                features.append(legval(col, coeffs))
        return np.column_stack(features)

    X_leg = legendre_features(X, order)

    model = LinearRegression()
    model.fit(X_leg, y_raw)

    # Predict and evaluate
    y_pred = model.predict(X_leg)

    print("\nLegendre decomposition")
    print(os.path.basename(filename))
    print("Order: "+str(order))
    print("RMSE:", np.sqrt(mean_squared_error(y_raw, y_pred)))
    print("Coefficients:", model.coef_)
    print("Intercept:", model.intercept_)
    print("R² score:", r2_score(y_raw, y_pred))

    import matplotlib.pyplot as plt
    feature_names = X_raw.columns.tolist()
    n_features = X_raw.shape[1]
    coefs = model.coef_.reshape(n_features, order + 1)

    for i in range(n_features):
        plt.plot(range(order + 1), coefs[i], label=f'{feature_names[i]}')
    plt.xlabel('Legendre Degree')
    plt.ylabel('Coefficient Value')
    plt.title('Legendre Coefficients per Feature')
    plt.legend()
    plt.show()
    
    

def load_csv():
    # Open file dialog to select CSV
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if file_path:
        order=E_Order.get()
        LegendreFit(file_path,order=int(order))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Legendre Fit")
    root.geometry("300x150")

    # Add button to trigger CSV loading
    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
    load_button.pack(pady=20)
    tk.Label(root,text="order").pack()
    E_Order=tk.Entry(root)
    E_Order.pack()
    E_Order.insert(0,"3")

    # Run the GUI loop
    root.mainloop()
