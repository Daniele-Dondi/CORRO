import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def get_top_dimensions(X, Y, top_n=2):
    df = pd.DataFrame(X, columns=[f'x{i+1}' for i in range(X.shape[1])])
    df['Y'] = Y
    correlations = df.corr()['Y'].abs().drop('Y')
    top_dims = correlations.nlargest(top_n).index
    return [int(dim[1:]) - 1 for dim in top_dims]


# === STEP 1: Define DOE matrix (X) and response (Y) ===
# Example: 5-factor DOE with center point
##X = np.array([
##    [-1, -1, -1, -1, -1],
##    [ 1, -1, -1, -1, -1],
##    [-1,  1, -1, -1, -1],
##    [ 1,  1, -1, -1, -1],
##    [-1, -1,  1, -1, -1],
##    [ 1, -1,  1, -1, -1],
##    [-1,  1,  1, -1, -1],
##    [ 1,  1,  1, -1, -1],
##    [ 0,  0,  0,  0,  0]  # center point
##])

X = np.array([
    [-1, -1, -1],
    [ 1, -1, -1],
    [-1,  1, -1],
    [ 1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [-1,  1,  1],
    [ 1,  1,  1],
    [ 0,  0,  0]
])

Y = np.array([70.7, 53.8, 68.2, 71.2, 61.7, 79.1, 50.8, 58.6, 59.3])

# === STEP 2: Automatically choose top 2 influential dimensions ===
top_dims=get_top_dimensions(X, Y, top_n=2)
dim1, dim2 = int(top_dims[0]) - 1, int(top_dims[1]) - 1
print(f"\nTop dimensions selected for visualization: {top_dims[0]} and {top_dims[1]}")

# === STEP 3: Gaussian Process Regression ===
kernel = C(1.0, (1e-3, 1e3)) * RBF(length_scale=[0.1]*X.shape[1], length_scale_bounds=(1e-5, 1e2))
gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
#gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
gpr.fit(X, Y)

# === STEP 4: Response Surface Visualization (2D slice) ===
grid_size = 50
x_vals = np.linspace(-1, 1, grid_size)
x1_grid, x2_grid = np.meshgrid(x_vals, x_vals)

X_pred = np.zeros((grid_size**2, X.shape[1]))
X_pred[:, dim1] = x1_grid.ravel()
X_pred[:, dim2] = x2_grid.ravel()

Y_pred, sigma = gpr.predict(X_pred, return_std=True)
Z = Y_pred.reshape(x1_grid.shape)

plt.figure(figsize=(8, 6))
cp = plt.contourf(x1_grid, x2_grid, Z, levels=20, cmap='viridis')
plt.colorbar(cp)
plt.xlabel(top_dims[0])
plt.ylabel(top_dims[1])
fixed_dims = [f'x{i+1}' for i in range(X.shape[1]) if i not in [dim1, dim2]]
plt.title(f'Response Surface ({", ".join(fixed_dims)} fixed at 0)')
plt.show()

# === STEP 5: GPR Predictions at Training Points ===
Y_fit, Y_fit_std = gpr.predict(X, return_std=True)
print("\nGPR Predictions at Training Points:")
for i, (x, y_true, y_pred, y_std) in enumerate(zip(X, Y, Y_fit, Y_fit_std)):
    print(f"Point {i+1}: X = {x}, True Y = {y_true:.2f}, Predicted Y = {y_pred:.2f} ± {y_std:.2f}")

# === STEP 6: Polynomial Regression (Degree 1 - 3) ===
for degree in [1, 2, 3]:
    print(f"\nPolynomial Regression (Degree {degree})")
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, Y)

    # Coefficients
    print("Coefficients:", model.coef_)

    y_pred = model.predict(X_poly)
    r_squared = r2_score(Y, y_pred)

    print("Intercept:", model.intercept_)
    print("R² score:", r_squared)
