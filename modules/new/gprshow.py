import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import matplotlib.gridspec as gridspec

def on_closing():
    Exit()

def Exit():
    canvas.get_tk_widget().destroy()
    root.destroy()
    root.quit()

def update_plot(*args):
    grid_size = 50
    x_vals = np.linspace(-1, 1, grid_size)
    x1_grid, x2_grid = np.meshgrid(x_vals, x_vals)

    X_pred = np.zeros((grid_size**2, n_dims))
    X_pred[:, dim1] = x1_grid.ravel()
    X_pred[:, dim2] = x2_grid.ravel()

    for i in fixed_dims:
        X_pred[:, i] = slider_vars[i].get()

    Y_pred, _ = gpr.predict(X_pred, return_std=True)
    Z = Y_pred.reshape(x1_grid.shape)

    ax.clear()
    cbar_ax.clear()  # clear the fixed colorbar axis

    cp = ax.contourf(x1_grid, x2_grid, Z, levels=20, cmap='viridis')
    fig.colorbar(cp, cax=cbar_ax)  # use fixed axis

    fixed_text = ", ".join([f"x{i+1}={slider_vars[i].get():.1f}" for i in fixed_dims])
    ax.set_title(f"Response Surface ({fixed_text})")
    ax.set_xlabel(f"x{dim1+1}")
    ax.set_ylabel(f"x{dim2+1}")
    canvas.draw()


### === Sample DOE and GPR setup ===
##X = np.array([
##    [-1, -1, -1, -1],
##    [ 1, -1, -1, -1],
##    [-1,  1, -1, -1],
##    [ 1,  1, -1, -1],
##    [-1, -1,  1, -1],
##    [ 1, -1,  1, -1],
##    [-1,  1,  1, -1],
##    [ 1,  1,  1, -1],
##    [ 0,  0,  0,  0]
##])
##Y = np.array([70.7, 53.8, 68.2, 71.2, 61.7, 79.1, 50.8, 58.6, 59.3])

import numpy as np

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

### Min-Max normalization to range [-1, 1]
##X_min = X.min(axis=0)
##X_max = X.max(axis=0)
##
### Avoid division by zero
##denominator = X_max - X_min
##denominator[denominator == 0] = 1
##
##X = 2 * (X - X_min) / denominator - 1

# === Train GPR with ARD kernel ===
kernel = C(1.0) * RBF(length_scale=[1.0]*X.shape[1])
gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
gpr.fit(X, Y)

# === GPR Predictions at Training Points ===
Y_fit, Y_fit_std = gpr.predict(X, return_std=True)
print("\nGPR Predictions at Training Points:")
for i, (x, y_true, y_pred, y_std) in enumerate(zip(X, Y, Y_fit, Y_fit_std)):
    print(f"Point {i+1}: X = {x}, True Y = {y_true:.2f}, Predicted Y = {y_pred:.2f} ± {y_std:.2f}")

# === ARD-based feature selection ===
length_scales = gpr.kernel_.k2.length_scale
feature_ranking = sorted(enumerate(length_scales), key=lambda x: x[1])
top_dims_ard = [i for i, _ in feature_ranking[:2]]
print("\nARD-based top dimensions selected for visualization:")
for i in top_dims_ard:
    print(f"x{i+1} (length scale = {length_scales[i]:.4f})")

# === GUI Setup ===
root = tk.Tk()
root.title("Dynamic Response Surface")
root.protocol("WM_DELETE_WINDOW", on_closing)

# === Matplotlib Figure ===
fig = plt.figure(figsize=(6, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1])  # 20:1 ratio for plot vs colorbar
ax = fig.add_subplot(gs[0])
cbar_ax = fig.add_subplot(gs[1])  # fixed colorbar axis
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# === Identify dimensions ===
n_dims = X.shape[1]
dim1, dim2 = top_dims_ard #choose the two top dimensions to start with
fixed_dims = [i for i in range(n_dims) if i not in [dim1, dim2]] #all other dimensions are fixed

# === Create sliders dynamically ===
slider_vars = {}
slider_frame = tk.Frame(root)
slider_frame.pack()

for i in fixed_dims:
    var = tk.DoubleVar(value=0.0)
    slider = tk.Scale(slider_frame, from_=-1, to=1, resolution=0.1,
                      orient=tk.HORIZONTAL, label=f"x{i+1}", variable=var, command=update_plot)
    slider.pack()
    slider_vars[i] = var

# Add a quit button
quit_button = tk.Button(master=root, text="Quit", command=Exit)
quit_button.pack(side=tk.BOTTOM)

# Initial plot
update_plot()

root.mainloop()
