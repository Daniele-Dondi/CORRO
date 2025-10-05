import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import matplotlib.gridspec as gridspec


# === Sample DOE and GPR setup ===
X = np.array([
    [-1, -1, -1, -1],
    [ 1, -1, -1, -1],
    [-1,  1, -1, -1],
    [ 1,  1, -1, -1],
    [-1, -1,  1, -1],
    [ 1, -1,  1, -1],
    [-1,  1,  1, -1],
    [ 1,  1,  1, -1],
    [ 0,  0,  0,  0]
])
Y = np.array([70.7, 53.8, 68.2, 71.2, 61.7, 79.1, 50.8, 58.6, 59.3])

# === Train GPR with ARD kernel ===
kernel = C(1.0) * RBF(length_scale=[1.0]*X.shape[1])
gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
gpr.fit(X, Y)

# === STEP 3: ARD-based feature selection ===
length_scales = gpr.kernel_.k2.length_scale
feature_ranking = sorted(enumerate(length_scales), key=lambda x: x[1])
top_dims_ard = [i for i, _ in feature_ranking[:2]]
print("\nARD-based top dimensions selected for visualization:")
for i in top_dims_ard:
    print(f"x{i+1} (length scale = {length_scales[i]:.4f})")

# === GUI Setup ===
root = tk.Tk()
root.title("Dynamic Response Surface")

# === Matplotlib Figure ===
fig = plt.figure(figsize=(6, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1])  # 20:1 ratio for plot vs colorbar
ax = fig.add_subplot(gs[0])
cbar_ax = fig.add_subplot(gs[1])  # fixed colorbar axis
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()


# === Identify dimensions ===
n_dims = X.shape[1]
dim1, dim2 = top_dims_ard#0, 1  # visualize these two
fixed_dims = [i for i in range(n_dims) if i not in [dim1, dim2]]

# === Create sliders dynamically ===
slider_vars = {}
slider_frame = tk.Frame(root)
slider_frame.pack()

for i in fixed_dims:
    var = tk.DoubleVar(value=0.0)
    slider = tk.Scale(slider_frame, from_=-1, to=1, resolution=0.1,
                      orient=tk.HORIZONTAL, label=f"x{i+1}", variable=var)
    slider.pack()
    slider_vars[i] = var

def update_plot():
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


# === Update button ===
update_btn = tk.Button(root, text="Update Plot", command=update_plot)
update_btn.pack()

# Initial plot
update_plot()

root.mainloop()
