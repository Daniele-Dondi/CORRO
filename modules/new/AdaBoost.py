import pandas as pd
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import sys
import tkinter as tk
from tkinter import filedialog
import shap
from sklearn.inspection import PartialDependenceDisplay
import warnings
import numpy as np


warnings.filterwarnings("ignore", message="X has feature names, but")


def run_pipeline(filename):
    data = pd.read_csv(filename)

    # === Separate features and target ===
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    # === Train-test split ===
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # === AdaBoost model ===
    model = AdaBoostRegressor(
        estimator=DecisionTreeRegressor(max_depth=3),
        n_estimators=50,
        learning_rate=1.0,
        random_state=42
    )
    model.fit(X_train, y_train)

    # === Predictions and evaluation ===
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"R² Score: {r2:.4f}")
    print(f"Mean Squared Error: {mse:.2f}")

    # === Feature importance ===
    importances = model.feature_importances_
    feature_names = X.columns

    plt.figure(figsize=(8, 5))
    plt.bar(feature_names, importances, color='steelblue')
    plt.title('Feature Importance in Reaction Yield Prediction')
    plt.ylabel('Importance Score')
    plt.xlabel('Variables')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # === SHAP analysis ===
    # Select one of the base estimators from AdaBoost
    base_model = model.estimators_[0]  # You can loop through more if needed

    # Create SHAP explainer for the base decision tree
    explainer = shap.Explainer(base_model.predict, X_test)
    shap_values = explainer(X_test)

    # Plot SHAP values
    shap.summary_plot(shap_values, X_test)

    # Collect SHAP values from multiple estimators
    shap_matrix = []
    for base_model in model.estimators_[:3]:
        explainer = shap.Explainer(base_model.predict, X_test)
        shap_values = explainer(X_test)
        shap_matrix.append(shap_values.values)

    # Average SHAP values across estimators
    avg_shap_values = np.mean(shap_matrix, axis=0)

    # Plot the averaged SHAP values
    shap.summary_plot(avg_shap_values, X_test)


    # === PDP analysis ===
    print("\nGenerating Partial Dependence Plots...")
    PartialDependenceDisplay.from_estimator(model, X_train, features=list(feature_names), kind='average')
    plt.tight_layout()
    plt.show()


##def run_pipeline(filename):
##    data = pd.read_csv(filename)
##
##    # === Separate features and target ===
##    # Assumes last column is the yield
##    X = data.iloc[:, :-1]
##    y = data.iloc[:, -1]
##
##    # === Train-test split ===
##    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
##
##    # === AdaBoost model ===
##    model = AdaBoostRegressor(
##        estimator=DecisionTreeRegressor(max_depth=3),
##        n_estimators=50,
##        learning_rate=1.0,
##        random_state=42
##    )
##    model.fit(X_train, y_train)
##    
##    # === Predictions and evaluation ===
##    y_pred = model.predict(X_test)
##    mse = mean_squared_error(y_test, y_pred)
##    r2 = r2_score(y_test, y_pred)
##    
##    print(f"R² Score: {r2:.4f}")
##    print(f"\nMean Squared Error: {mse:.2f}")
##
##    # === Feature importance ===
##    importances = model.feature_importances_
##    feature_names = X.columns
##
##    # === Plotting ===
##    plt.figure(figsize=(8, 5))
##    plt.bar(feature_names, importances, color='steelblue')
##    plt.title('Feature Importance in Reaction Yield Prediction')
##    plt.ylabel('Importance Score')
##    plt.xlabel('Variables')
##    plt.xticks(rotation=45)
##    plt.tight_layout()
##    plt.show()

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
    root.title("ADA Boost pdp shap")
    root.geometry("300x150")

    # Add button to trigger CSV loading
    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()
