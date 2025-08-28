##from sklearn.gaussian_process import GaussianProcessRegressor
##from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
##import numpy as np
##
##import numpy as np
##
### Input variables: x1, x2, x3
##X = np.array([
##    [-1, -1, -1],
##    [ 1, -1, -1],
##    [-1,  1, -1],
##    [ 1,  1, -1],
##    [-1, -1,  1],
##    [ 1, -1,  1],
##    [-1,  1,  1],
##    [ 1,  1,  1],
##    [ 0,  0,  0]
##])
##
### Output variable: s
##Y = np.array([
##    70.7,
##    53.8,
##    68.2,
##    71.2,
##    61.7,
##    79.1,
##    50.8,
##    58.6,
##    59.3
##])
##
##
### Define kernel: constant * radial basis function
##kernel = C(1.0, (2e-3, 2e3)) * RBF(length_scale=1.0)
##
### Create and fit the model
##gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
##gpr.fit(X, Y)
##
##
##
### New input points to predict
##X_pred = np.array([
##    [2.5, 4.0],
##    [3.5, 5.5]
##])
##
### Predict with uncertainty
##Y_pred, sigma = gpr.predict(X_pred, return_std=True)
##
##print("Predicted Y:", Y_pred)
##print("Uncertainty (std dev):", sigma)
##
##import matplotlib.pyplot as plt
##
##plt.errorbar(X_pred[:, 0], Y_pred, yerr=sigma, fmt='o', label='Predictions')
##plt.xlabel("X1")
##plt.ylabel("Predicted Y")
##plt.legend()
##plt.show()


import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.metrics import r2_score

# === Step 1: Your DoE data ===
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
Y = np.array([
    70.7,
    53.8,
    68.2,
    71.2,
    61.7,
    79.1,
    50.8,
    58.6,
    59.3
])

# === Step 2: Define the kernel and model ===
kernel = C(1.0, (1e-3, 1e3)) * RBF(length_scale=0.01, length_scale_bounds=(1e-5, 1e2))
gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)

# === Step 3: Fit the model ===
gpr.fit(X, Y)


# === Step 4: Create prediction grid (x1 vs x2, x3 fixed at 0) ===
x1_vals = np.linspace(-1, 1, 50)
x2_vals = np.linspace(-1, 1, 50)
x1_grid, x2_grid = np.meshgrid(x1_vals, x2_vals)
x3_fixed = np.zeros_like(x1_grid)

X_pred = np.column_stack([
    x1_grid.ravel(),
    x2_grid.ravel(),
    x3_fixed.ravel()
])

# === Step 5: Predict and reshape ===
Y_pred, sigma = gpr.predict(X_pred, return_std=True)
Z = Y_pred.reshape(x1_grid.shape)

# === Step 6: Plot the response surface ===
plt.figure(figsize=(8, 6))
cp = plt.contourf(x1_grid, x2_grid, Z, levels=20, cmap='viridis')
plt.colorbar(cp)
plt.xlabel('x1')
plt.ylabel('x2')
plt.title('Response Surface (x3 = 0)')
plt.show()

# === Step 7: Predict at training points ===
Y_fit, Y_fit_std = gpr.predict(X, return_std=True)

# === Step 8: Print fitted values ===
print("Fitted values at training points:")
for i, (x, y_true, y_pred, y_std) in enumerate(zip(X, Y, Y_fit, Y_fit_std)):
    print(f"Point {i+1}: X = {x}, True Y = {y_true:.2f}, Predicted Y = {y_pred:.2f} ± {y_std:.2f}")

###########################################

print("\n\nnow moving to polynomial grade 2")
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

### Example input data (X1, X2, ..., Xn)
##X = np.array([[1, 2], [2, 3], [3, 4]])  # Replace with your DoE matrix
##Y = np.array([5, 7, 9])                # Replace with your output data

# Create polynomial features (degree=2 includes interactions)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Fit the model
model = LinearRegression()
model.fit(X_poly, Y)

# Coefficients
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Predict
y_pred = model.predict(X_poly)

# R² score
r_squared = r2_score(Y, y_pred)
print(f"R² score: {r_squared:.4f}")
###########################################

print("\n\nnow moving to polynomial grade 3")
# Create polynomial features (degree=2 includes interactions)
poly = PolynomialFeatures(degree=3, include_bias=False)
X_poly = poly.fit_transform(X)

# Fit the model
model = LinearRegression()
model.fit(X_poly, Y)

# Coefficients
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Predict
y_pred = model.predict(X_poly)

# R² score
r_squared = r2_score(Y, y_pred)
print(f"R² score: {r_squared:.4f}")
