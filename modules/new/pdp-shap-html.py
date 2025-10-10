import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.inspection import PartialDependenceDisplay
from sklearn.model_selection import cross_val_score
from itertools import combinations
import shap
import webbrowser
import os
import tkinter as tk
from tkinter import filedialog

def Pdp_Shap2HTML(filename):
    df = pd.read_csv(filename)
    # Separate last column into Y
    last_column = df.columns[-1]
    Y = df[last_column].tolist()
    
    # Remaining columns into X
    X_df = df.drop(columns=[last_column])
    
    # Fit a model (Random Forest works well for PDP)
    rf_model = RandomForestRegressor()
    rf_model.fit(X_df, Y)

    #RANDOM FOREST FITTING EVALUATION START

    # Predict on training or test set
    Y_pred = rf_model.predict(X_df)

    # Evaluate
    base_name = os.path.basename(filename)
    RF_EVALUATION=f"<h2>Processed filename: {base_name}</h2>"
    RF_EVALUATION+="<h1>Model fitting</h1><br>Data are fitted with a <strong>Random Forest</strong> Algorithm. <br>Values of fitting are displayed below:<br>"
    RF_EVALUATION+="R<sup>2</sup>:"+str(r2_score(Y, Y_pred))+"<br>"
    RF_EVALUATION+="MAE :"+str(mean_absolute_error(Y, Y_pred))+"<br>"
    RF_EVALUATION+="RMSE :"+str(np.sqrt(mean_squared_error(Y, Y_pred)))+"<br>"
    ##print("R²:", r2_score(Y, Y_pred))
    ##print("MAE:", mean_absolute_error(Y, Y_pred))
    ##print("RMSE:", np.sqrt(mean_squared_error(Y, Y_pred)))


    scores = cross_val_score(rf_model, X_df, Y, cv=5, scoring='r2')  # or 'neg_mean_squared_error'
    RF_EVALUATION+="Cross-validated R<sup>2</sup> scores:<br>"+str(scores)+"<br>"
    RF_EVALUATION+="Mean R<sup>2</sup> :"+str(scores.mean())+"<br>"
    ##print("Cross-validated R² scores:", scores)
    ##print("Mean R²:", scores.mean())

    residuals = Y - Y_pred
    plt.scatter(Y_pred, residuals)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel("Predicted")
    plt.ylabel("Residuals")
    plt.title("Residual Plot")
    plt.savefig("RF_residues.png", dpi=300)
    plt.close()

    RF_EVALUATION+="""<h3>Residuals</h3>The residual graph should appear like random distributed points<br><img src="RF_residues.png" width="600"><br>"""

    importance = rf_model.feature_importances_
    pd.Series(importance, index=X_df.columns).sort_values(ascending=False).plot(kind='bar')
    plt.title("Feature Importances")
    plt.savefig("RF_feature_importance.png", dpi=300)
    plt.close()

    RF_EVALUATION+="""<br>Below the parameters sorted from the most important to the less important<br>"""
    RF_EVALUATION+="""<img src="RF_feature_importance.png" width="600"><br><br>"""

    #RANDOM FOREST FITTING EVALUATION END

    # Plot PDP for one or more features
    #features_to_plot = ['x1', 'x2', 'x3', 'x4']  # You can include single features or tuples for interactions
    features_to_plot = df.columns[:-1].tolist()

    # Define number of plots and layout
    n_features = len(features_to_plot)
    n_cols = 2
    n_rows = (n_features + n_cols - 1) // n_cols  # Ceiling division

    # Create figure and axes manually
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))

    # Flatten axes for compatibility
    axes = axes.flatten()

    # Plot PDPs
    PartialDependenceDisplay.from_estimator(
        rf_model,
        X_df,
        features_to_plot,
        ax=axes[:n_features]  # Use only the needed axes
    )

    plt.tight_layout()
    plt.savefig("pdp_feature.png", dpi=300)
    plt.close()

    # Generate all pairwise combinations of features
    feature_names = X_df.columns.tolist()
    pairwise_features = list(combinations(feature_names, 2))

    # Layout: 2 columns, calculate rows
    n_cols = 2
    n_rows = (len(pairwise_features) + n_cols - 1) // n_cols

    # Create figure and axes
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
    axes = axes.flatten()

    # Plot each pairwise PDP into its own subplot
    for i, pair in enumerate(pairwise_features):
        PartialDependenceDisplay.from_estimator(
            rf_model,
            X_df,
            [pair],
            ax=axes[i]
        )

    # Hide unused axes if any
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig("pdp_pairs.png", dpi=300, bbox_inches='tight')
    plt.close()

    # === SHAP Integration ===
    # Create SHAP explainer
    explainer = shap.Explainer(rf_model, X_df)

    # Compute SHAP values
    shap_values = explainer(X_df)

    # === SHAP Summary Plot ===
    shap.summary_plot(shap_values, X_df, show=False)
    plt.tight_layout()
    plt.savefig("shap_summary.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Prepare subplot grid
    n_features = X_df.shape[1]
    n_cols = 2
    n_rows = (n_features + n_cols - 1) // n_cols  # Ceiling division

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows))
    axes = axes.flatten()

    # Plot each dependence plot into its own subplot
    for i, feature in enumerate(X_df.columns):
        shap.dependence_plot(
            feature,
            shap_values.values,
            X_df,
            ax=axes[i],
            show=False  # Prevent SHAP from auto-displaying
        )

    # Hide any unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig("shap_dependence.png", dpi=300)
    plt.close()

    html_content = """
    <html>
    <head><title>Model Interpretation Report</title></head>
    <body>
    <h1>Model Interpretation Report</h1>
    """

    html_content +=RF_EVALUATION

    # === PDP Main Effects ===
    html_content += "<h2>Partial Dependence Plots (Main Effects)</h2>"
    html_content += """
    <h3>Features</h3>
    <p>This plot shows how the feature affects the model's prediction on average, keeping all other features constant.</p>
    <img src="pdp_feature.png" width="600"><br>
    """

    # === PDP Interactions ===
    html_content += """
    <h2>Partial Dependence Plots (All Feature Interactions)</h2>
    <p>This grid shows how pairs of features interact to influence the model's predictions. Look for curved surfaces or ridges to spot nonlinear effects and dependencies.</p>
    <img src="pdp_pairs.png" width="800"><br>
    """

    # === SHAP Summary Plot ===
    html_content += "<h2>SHAP Summary Plot</h2>"
    html_content += """
    <h3>Shap</h3>
    <p>
    1. Y-axis: Feature Names<br>
    Ranked by importance (top = most influential).<br>
    Importance is based on the average absolute SHAP value = how much each feature contributes to predictions overall.<br>
    2. X-axis: SHAP Value<br>
    Represents the impact of the feature on the model’s output.<br>
    Positive SHAP value -> pushes prediction higher.<br>
    Negative SHAP value -> pushes prediction lower.<br>
    3. Color: Feature Value<br>
    Each dot is a sample.<br>
    Color shows the actual value of the feature for that sample:<br>
    Red = high feature value<br>
    Blue = low feature value</p>
    <img src="shap_summary.png" width="600"><br>
    """


    # === SHAP Dependence Plots ===
    html_content += "<h2>SHAP Dependence Plots</h2>"
    html_content += """
    <h3>Dependence</h3>
    <p>This SHAP dependence plot shows how the value of a <strong>feature</strong> impacts the prediction for each sample. Color indicates the value of interacting features, revealing potential nonlinear or interaction effects.</p>
    <img src="shap_dependence.png" width="600"><br>
    """

    html_content += "</body></html>"

    # Save HTML file
    html_filename = "model_report.html"
    with open(html_filename, "w") as f:
        f.write(html_content)

    # Display HTML file in the default browser
    full_path = os.path.abspath(html_filename)
    webbrowser.open(f"file:///{full_path}")

def load_csv():
    # Open file dialog to select CSV
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if file_path:
        Pdp_Shap2HTML(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Random Forest HTML")
    root.geometry("300x150")

    # Add button to trigger CSV loading
    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()
