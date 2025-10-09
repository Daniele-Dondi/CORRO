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

# Paste your data as a multiline string
raw_data = """
0.570291777	0.157142857	0.30952381	0.059171598	41.26452613
0.570291777	0.141527002	0.085539715	0.05952381	62.78571552
0.570291777	0.173553719	1	0.113207547	53.33497035
0.643070788	0.149333333	1	0.052941176	17.55880282
0.83643617	0.160390516	0.085539715	0.052941176	5.529906697
1	0.173553719	0.085539715	0.128342246	42.81292825
0.83643617	0.374670185	0.30952381	0.052941176	13.27473408
0.643070788	0.453074434	1	0.067073171	0
0.643070788	0.152284264	0.085539715	0.27826087	4.444109893
0.570291777	0.311440678	0.30952381	0.05952381	24.05265274
1	0.374670185	0.085539715	0.401960784	78.36249844
0.570291777	0.151260504	1	0.079365079	14.49254361
0.570291777	0.150943396	0.30952381	0.052941176	11.75749506
1	0.453074434	0.30952381	0.113207547	41.48980841
1	0.141527002	1	0.067073171	1.442502721
0.643070788	0.151260504	0.085539715	0.079365079	9.910073167
1	0.141527002	0.30952381	0.401960784	68.67316565
0.83643617	0.142857143	1	0.285714286	2.481415648
0.570291777	0.150943396	1	0.401960784	74.51133845
0.83643617	0.159574468	0.30952381	1	48.23965662
0.643070788	0.152284264	0.085539715	1	12.05269157
0.83643617	0.142857143	1	0.079365079	4.820162197
0.643070788	0.167346939	1	0.067073171	5.688672061
0.83643617	1	0.085539715	0.05952381	13.24692026
0.570291777	0.149333333	0.30952381	0.052941176	3.046255894
0.643070788	0.167346939	0.30952381	0.281818182	53.91867484
1	0.152173913	1	0.401960784	45.53588257
0.643070788	0.149333333	1	0.079365079	7.387205125
0.643070788	0.175	0.085539715	0.07106599	27.00233561
0.570291777	1	0.085539715	0.285714286	68.47251074
1	0.435897436	0.085539715	0.052941176	50.90618574
0.570291777	1	1	0.285714286	28.30443344
0.570291777	0.160390516	1	0.128342246	40.24019595
0.83643617	0.167346939	0.30952381	0.27826087	22.49487977
1	0.152173913	0.30952381	0.052941176	6.77799041
1	0.152173913	1	0.27826087	14.03184959
0.83643617	0.158008658	0.085539715	0.079365079	25.79234273
1	0.152284264	1	1	51.15306518
0.570291777	0.149333333	0.30952381	0.269565217	6.703331473
0.570291777	0.141527002	0.30952381	0.052941176	23.50114845
0.643070788	0.142857143	0.085539715	0.07106599	28.35051675
0.643070788	0.149105368	0.085539715	0.05952381	60.55316321
1	0.163316583	0.085539715	0.269565217	8.008432112
0.643070788	0.311440678	1	0.126582278	73.95398123
0.83643617	0.173553719	0.30952381	0.059171598	0.43718104
0.643070788	0.152284264	0.085539715	0.113207547	6.286120839
0.643070788	0.175	0.085539715	0.126582278	64.23525691
1	0.435897436	1	1	95.38648822
0.643070788	0.374670185	0.085539715	0.05952381	64.56169067
"""  # Replace ... with the rest of your data

# Convert to NumPy array
data = np.array([list(map(float, line.split())) for line in raw_data.strip().split('\n')])

# Split into X and Y
X = data[:, :4]  # First 4 columns
Y = data[:, 4]   # Last column

# Prepare your data
X_df = pd.DataFrame(X, columns=['x1', 'x2', 'x3', 'x4'])

# Fit a model (Random Forest works well for PDP)
rf_model = RandomForestRegressor()
rf_model.fit(X_df, Y)

#RANDOM FOREST FITTING EVALUATION START

# Predict on training or test set
Y_pred = rf_model.predict(X_df)

# Evaluate
RF_EVALUATION="<h1>Model fitting</h1><br>Data are fitted with a <strong>Random Forest</strong> Algorithm. <br>Values of fitting are displayed below:<br>"
RF_EVALUATION+="R²:"+str(r2_score(Y, Y_pred))+"<br>"
RF_EVALUATION+="MAE :"+str(mean_absolute_error(Y, Y_pred))+"<br>"
RF_EVALUATION+="RMSE :"+str(np.sqrt(mean_squared_error(Y, Y_pred)))+"<br>"
##print("R²:", r2_score(Y, Y_pred))
##print("MAE:", mean_absolute_error(Y, Y_pred))
##print("RMSE:", np.sqrt(mean_squared_error(Y, Y_pred)))


scores = cross_val_score(rf_model, X_df, Y, cv=5, scoring='r2')  # or 'neg_mean_squared_error'
RF_EVALUATION+="Cross-validated R² scores:<br>"+str(scores)+"<br>"
RF_EVALUATION+="Mean R² :"+str(scores.mean())+"<br>"
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
features_to_plot = ['x1', 'x2', 'x3', 'x4']  # You can include single features or tuples for interactions

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
