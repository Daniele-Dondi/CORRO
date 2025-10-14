from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import VarianceThreshold
from xgboost import XGBRegressor
import warnings
import numpy as np
from sklearn.exceptions import ConvergenceWarning
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from numpy.polynomial.legendre import legval
from sklearn.base import BaseEstimator, TransformerMixin
import scipy.special as sp


class LegendreFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, degree=3):
        self.degree = degree

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        #from scipy.special import eval_legendre
        X = np.asarray(X)
        X_scaled = 2 * (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0)) - 1  # scale to [-1, 1]
        features = [sp.eval_legendre(d, X_scaled) for d in range(self.degree + 1)]
        return np.concatenate(features, axis=1)

##class LegendreFeatures(BaseEstimator, TransformerMixin):
##    def __init__(self, degree=3):
##        self.degree = degree
##
##    def fit(self, X, y=None):
##        self.min_ = X.min(axis=0)
##        self.max_ = X.max(axis=0)
##        return self
##
##    def transform(self, X):
##        import numpy as np
##        from scipy.special import eval_legendre
##        X = np.asarray(X)
##        denom = (self.max_ - self.min_)
##        denom[denom == 0] = 1  # avoid division by zero
##        X_scaled = 2 * (X - self.min_) / denom - 1
##        features = [eval_legendre(d, X_scaled) for d in range(self.degree + 1)]
##        return np.concatenate(features, axis=1)


def interpret_r2_scores(r2_train, r2_test, r2_whole):
    delta_train_test = r2_train - r2_test
    delta_train_whole = r2_train - r2_whole

    if r2_train < 0.2 and r2_test < 0.2:
        return "Very poor fit — likely underfitting or missing key patterns."
    elif r2_train > 0.9 and r2_test < 0.5:
        return "Severe overfitting — perfect training fit but poor generalization."
    elif r2_train > 0.8 and r2_test > 0.75 and delta_train_test < 0.1:
        return "Strong fit and good generalization — model is performing reliably."
    elif r2_train > 0.8 and delta_train_test > 0.1:
        return "Good training fit but signs of overfitting — generalization could be improved."
    elif r2_train > 0.5 and r2_test > 0.5:
        return "Moderate fit — model captures some structure but may benefit from tuning."
    else:
        return "Unusual behavior — consider inspecting residuals or feature scaling."

def format_prediction_result(best_input, best_yield):
    formatted = ", ".join(
        f"{key} = {float(value):.3f}" for key, value in best_input.items()
    )
    return f"🥇 Best predicted yield: {best_yield:.3f}%\n📈 Optimal input: {formatted}"


def find_optimal_input(model, bounds, n_samples=1000):
    feature_names = list(bounds.keys())
    X_random = np.array([
        [np.random.uniform(bounds[feat][0], bounds[feat][1]) for feat in feature_names]
        for _ in range(n_samples)
    ])
    X_random = pd.DataFrame(X_random, columns=feature_names)
    y_pred = model.predict(X_random)  # Pipeline handles scaling internally
    best_idx = np.argmax(y_pred)
    best_input = X_random.iloc[best_idx].to_dict()
    best_yield = y_pred[best_idx]
    return best_input, best_yield

    
def get_feature_bounds(df):
    return {
        col: (df[col].min(), df[col].max())
        for col in df.columns[:-1]  # exclude target column
        if pd.api.types.is_numeric_dtype(df[col])
    }

def RemoveConstantColumns(X):
    # Initialize the transformer with threshold=0 to remove constant features
    selector = VarianceThreshold(threshold=0)

    # Fit the selector to the data
    selector.fit(X)

    # Get the mask of features that are not constant
    mask = selector.get_support()

    # Identify removed (constant) features
    removed_columns = X.columns[~mask].tolist()

    # Apply the transformation to remove constant features
    X_reduced = selector.transform(X)

    # Optionally convert back to DataFrame with remaining column names
    X_reduced = pd.DataFrame(X_reduced, columns=X.columns[mask])

    # Show message box if any columns were removed
    if removed_columns:
        messagebox.showinfo(
            "Removed Constant Features",
            "The following constant features were removed:\n\n" + ", ".join(removed_columns)
        )
        return X_reduced
    else:
        return X
    

def LoadAndGo(filename, output_widget, use_scaling, tune_svr, tune_gpr, use_kfold, make_prediction):
    df = pd.read_csv(filename)
    bounds = get_feature_bounds(df)    
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # 🔎 Pre-check for constant features
    X = RemoveConstantColumns(X)

    def maybe_scale(model):
        return make_pipeline(StandardScaler(), model) if use_scaling else model

    models = {
        "AdaBoost": maybe_scale(AdaBoostRegressor()),
        "XGBoost": maybe_scale(XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)),
        "Random Forest": maybe_scale(RandomForestRegressor()),
        "Legendre 3rd + Random Forest": maybe_scale(make_pipeline(LegendreFeatures(degree=3), RandomForestRegressor())),        
        "Polynomial Regression degree 1": maybe_scale(make_pipeline(PolynomialFeatures(degree=1), LinearRegression())),
        "Polynomial Regression degree 2": maybe_scale(make_pipeline(PolynomialFeatures(degree=2), LinearRegression())),
        "Polynomial Regression degree 3": maybe_scale(make_pipeline(PolynomialFeatures(degree=3), LinearRegression())),
        "Legendre Regression degree 2": maybe_scale(make_pipeline(LegendreFeatures(degree=2), LinearRegression())),
        "Legendre Regression degree 3": maybe_scale(make_pipeline(LegendreFeatures(degree=3), LinearRegression())),
        "Legendre Regression degree 4": maybe_scale(make_pipeline(LegendreFeatures(degree=4), LinearRegression())),
        "Legendre Regression degree 5": maybe_scale(make_pipeline(LegendreFeatures(degree=5), LinearRegression())),
        "Legendre 3rd + GPR": maybe_scale(make_pipeline(LegendreFeatures(degree=3), GaussianProcessRegressor())),
        "Legendre 3rd + SVR": maybe_scale(make_pipeline(LegendreFeatures(degree=3), SVR()))
    }

    if tune_svr:
        svr_pipeline = make_pipeline(StandardScaler(), SVR())
        param_grid = {
            'svr__C': [0.1, 1, 10],
            'svr__epsilon': [0.01, 0.1, 0.5],
            'svr__kernel': ['rbf', 'linear']
        }
        svr_model = GridSearchCV(svr_pipeline, param_grid, cv=5, n_jobs=-1)
        models["SVR (tuned)"] = svr_model
    else:
        models["SVR"] = maybe_scale(SVR(kernel='rbf', C=1.0, epsilon=0.1))

    # 🔧 Add Legendre + SVR (tuned)
    legendre_svr_pipeline = Pipeline([
        ('legendre', LegendreFeatures()),  # step name is 'legendre'
        ('svr', SVR())
    ])

    param_grid_svr = {
        'legendre__degree': [2, 3, 4],
        'svr__C': [0.1, 1, 10],
        'svr__epsilon': [0.01, 0.1],
        'svr__kernel': ['rbf', 'linear']
    }
    models["Legendre + SVR (tuned)"] = GridSearchCV(legendre_svr_pipeline, param_grid_svr, cv=5, n_jobs=-1)

    if tune_gpr:
        
        gpr_pipeline = Pipeline([('gpr', GaussianProcessRegressor())])
        gpr_param_grid = {
            'gpr__kernel': [
                C(1.0, (0.1, 10.0)) * RBF(length_scale=1.0, length_scale_bounds=(0.01, 10.0)),
                C(0.5, (0.1, 5.0)) * RBF(length_scale=0.5, length_scale_bounds=(0.01, 5.0))
            ],
            'gpr__alpha': [1e-2, 1e-1, 1.0]
        }
        gpr_model = GridSearchCV(gpr_pipeline, gpr_param_grid, cv=5, n_jobs=-1)
        models["GPR (tuned)"] = gpr_model
    else:
        models["GPR"] = maybe_scale(GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=1.0), alpha=1e-2))

    output_widget.delete("1.0", tk.END)

    for name, model in models.items():
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", category=ConvergenceWarning)

            try:
                comment=""
                if use_kfold and not isinstance(model, GridSearchCV):
                    scores = cross_val_score(model, X, y, cv=5, scoring='r2')
                    r2_mean = scores.mean()
                    r2_std = scores.std()
                    comment = f"Cross-validated R² = {r2_mean:.3f} ± {r2_std:.3f}\n"

                # Train/test split evaluation
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model.fit(X_train, y_train)
                r2_train = model.score(X_train, y_train)
                r2_test = model.score(X_test, y_test)
                r2_whole = model.score(X, y)
                comment += (
                    f"R² on training = {r2_train:.3f}\n"
                    f"R² on test     = {r2_test:.3f}\n"
                    f"R² on whole    = {r2_whole:.3f}\n"
                    f"→ {interpret_r2_scores(r2_train, r2_test, r2_whole)}"
                )

                tuning_str = ""
                if isinstance(model, GridSearchCV):
                    best_params = model.best_params_
                    best_score = model.best_score_
                    tuning_str = f"\n\n🔧 Best params: {best_params}\n🔍 CV score: {best_score:.3f}"                
                    best_model = model.best_estimator_
                    best_model.fit(X, y)  # Refit on full data
                    r2_whole = best_model.score(X, y)
                    comment += f"\nBest model refitted on full data\nR² on whole = {r2_whole:.3f}"
                    
                if make_prediction:
                    best_input, best_yield = find_optimal_input(model, bounds)
                    comment+="\n"+format_prediction_result(best_input, best_yield)                
                
                warning_str = f"\n⚠️ Warning: {str(w[-1].message)}" if w else ""
                result = f"{name}:\n  → {comment}{tuning_str}{warning_str}\n\n"

            except Exception as e:
                # Catch any crash and report it instead of stopping
                result = f"{name}:\n  ❌ Error during evaluation\n\n"
                print(str(e)+"\n")
            
            output_widget.insert(tk.END, result)
            output_widget.see(tk.END)
    
def load_csv(output_widget, scaling_var, tune_svr_var, tune_gpr_var, use_kfold_var, predict_var):
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv")]
    )
    if file_path:
        LoadAndGo(
            file_path,
            output_widget,
            scaling_var.get() == 1,
            tune_svr_var.get() == 1,
            tune_gpr_var.get() == 1,
            use_kfold_var.get() == 1,
            predict_var.get() == 1
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Model Comparison Tool")
    root.geometry("750x650")

    scaling_var = tk.IntVar(value=1)
    tune_svr_var = tk.IntVar(value=1)
    tune_gpr_var = tk.IntVar(value=0)
    use_kfold_var = tk.IntVar(value=0)
    predict_var = tk.IntVar(value=0)

    # Scaling toggle
    scaling_frame = tk.Frame(root)
    scaling_frame.pack(pady=5)
    tk.Label(scaling_frame, text="Apply scaling to all models?").pack(side=tk.LEFT)
    tk.Radiobutton(scaling_frame, text="Yes", variable=scaling_var, value=1).pack(side=tk.LEFT)
    tk.Radiobutton(scaling_frame, text="No", variable=scaling_var, value=0).pack(side=tk.LEFT)

    # SVR tuning toggle
    svr_frame = tk.Frame(root)
    svr_frame.pack(pady=5)
    tk.Label(svr_frame, text="Enable automatic SVR tuning?").pack(side=tk.LEFT)
    tk.Radiobutton(svr_frame, text="Yes", variable=tune_svr_var, value=1).pack(side=tk.LEFT)
    tk.Radiobutton(svr_frame, text="No", variable=tune_svr_var, value=0).pack(side=tk.LEFT)

    # GPR tuning toggle
    gpr_frame = tk.Frame(root)
    gpr_frame.pack(pady=5)
    tk.Label(gpr_frame, text="Enable automatic GPR tuning?").pack(side=tk.LEFT)
    tk.Radiobutton(gpr_frame, text="Yes", variable=tune_gpr_var, value=1).pack(side=tk.LEFT)
    tk.Radiobutton(gpr_frame, text="No", variable=tune_gpr_var, value=0).pack(side=tk.LEFT)

    # K-fold toggle
    kfold_frame = tk.Frame(root)
    kfold_frame.pack(pady=5)
    tk.Label(kfold_frame, text="Use K-Fold cross-validation?").pack(side=tk.LEFT)
    tk.Radiobutton(kfold_frame, text="Yes", variable=use_kfold_var, value=1).pack(side=tk.LEFT)
    tk.Radiobutton(kfold_frame, text="No", variable=use_kfold_var, value=0).pack(side=tk.LEFT)

    # Predict toggle
    kpred_frame = tk.Frame(root)
    kpred_frame.pack(pady=5)
    tk.Label(kpred_frame, text="Make best point prediction?").pack(side=tk.LEFT)
    tk.Radiobutton(kpred_frame, text="Yes", variable=predict_var, value=1).pack(side=tk.LEFT)
    tk.Radiobutton(kpred_frame, text="No", variable=predict_var, value=0).pack(side=tk.LEFT)
    

    # Load button
    load_button = tk.Button(root, text="Load CSV File", command=lambda: load_csv(output_text, scaling_var, tune_svr_var, tune_gpr_var, use_kfold_var, predict_var))
    load_button.pack(pady=10)

    # Output display
    output_text = tk.Text(root, wrap="word", height=25, width=90)
    output_text.pack(padx=10, pady=10)

    root.mainloop()

                          
##from sklearn.model_selection import train_test_split, GridSearchCV
##from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
##from sklearn.pipeline import make_pipeline
##from sklearn.preprocessing import PolynomialFeatures, StandardScaler
##from sklearn.linear_model import LinearRegression
##from sklearn.svm import SVR
##from sklearn.gaussian_process import GaussianProcessRegressor
##from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
##import warnings
##from sklearn.exceptions import ConvergenceWarning
##import pandas as pd
##import tkinter as tk
##from tkinter import filedialog
##
##def interpret_r2_scores(r2_train, r2_test, r2_whole):
##    delta_train_test = r2_train - r2_test
##    delta_train_whole = r2_train - r2_whole
##
##    if r2_train < 0.2 and r2_test < 0.2:
##        return "Very poor fit — likely underfitting or missing key patterns."
##    elif r2_train > 0.9 and r2_test < 0.5:
##        return "Severe overfitting — perfect training fit but poor generalization."
##    elif r2_train > 0.8 and r2_test > 0.75 and delta_train_test < 0.1:
##        return "Strong fit and good generalization — model is performing reliably."
##    elif r2_train > 0.8 and delta_train_test > 0.1:
##        return "Good training fit but signs of overfitting — generalization could be improved."
##    elif r2_train > 0.5 and r2_test > 0.5:
##        return "Moderate fit — model captures some structure but may benefit from tuning."
##    else:
##        return "Unusual behavior — consider inspecting residuals or feature scaling."
##
##def LoadAndGo(filename, output_widget, use_scaling, tune_svr):
##    df = pd.read_csv(filename)
##    X = df.iloc[:, :-1]
##    y = df.iloc[:, -1]
##
##    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
##
##    def maybe_scale(model):
##        return make_pipeline(StandardScaler(), model) if use_scaling else model
##
##    models = {
##        "AdaBoost": maybe_scale(AdaBoostRegressor()),
##        "Random Forest": maybe_scale(RandomForestRegressor()),
##        "Polynomial Regression degree 1": maybe_scale(make_pipeline(PolynomialFeatures(degree=1), LinearRegression())),
##        "Polynomial Regression degree 2": maybe_scale(make_pipeline(PolynomialFeatures(degree=2), LinearRegression())),
##        "Polynomial Regression degree 3": maybe_scale(make_pipeline(PolynomialFeatures(degree=3), LinearRegression())),
##        "GPR": maybe_scale(GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=1.0, length_scale_bounds=(1e-8, 1e3)), alpha=1e-2))
##    }
##
##    # SVR with optional GridSearchCV
##    if tune_svr:
##        svr_pipeline = make_pipeline(StandardScaler(), SVR())
##        param_grid = {
##            'svr__C': [0.1, 1, 10],
##            'svr__epsilon': [0.01, 0.1, 0.5],
##            'svr__kernel': ['rbf', 'linear']
##        }
##        svr_model = GridSearchCV(svr_pipeline, param_grid, cv=5, n_jobs=-1)
##        models["SVR (tuned)"] = svr_model
##    else:
##        models["SVR"] = maybe_scale(SVR(kernel='rbf', C=1.0, epsilon=0.1))
##
##    output_widget.delete("1.0", tk.END)
##
##    for name, model in models.items():
##        with warnings.catch_warnings(record=True) as w:
##            warnings.simplefilter("always", category=ConvergenceWarning)
##            model.fit(X_train, y_train)
##
##            r2_train = model.score(X_train, y_train)
##            r2_test = model.score(X_test, y_test)
##            r2_whole = model.score(X, y)
##            comment = interpret_r2_scores(r2_train, r2_test, r2_whole)
##
##            warning_str = f"\n⚠️ Warning: {str(w[-1].message)}" if w else ""
##            tuning_str = ""
##            if "SVR" in name and tune_svr:
##                best_params = model.best_params_
##                best_score = model.best_score_
##                tuning_str = f"\n🔧 Best params: {best_params}\n🔍 CV score: {best_score:.3f}"
##
##            result = (
##                f"{name}:\n"
##                f"  R² on training = {r2_train:.3f}\n"
##                f"  R² on test     = {r2_test:.3f}\n"
##                f"  R² on whole    = {r2_whole:.3f}\n"
##                f"  → {comment}{tuning_str}{warning_str}\n\n"
##            )
##            output_widget.insert(tk.END, result)
##            output_widget.see(tk.END)
##
##def load_csv(output_widget, scaling_var, tune_svr_var):
##    file_path = filedialog.askopenfilename(
##        title="Select CSV File",
##        filetypes=[("CSV files", "*.csv")]
##    )
##    if file_path:
##        use_scaling = scaling_var.get() == 1
##        tune_svr = tune_svr_var.get() == 1
##        LoadAndGo(file_path, output_widget, use_scaling, tune_svr)
##
##if __name__ == "__main__":
##    root = tk.Tk()
##    root.title("Model Comparison Tool")
##    root.geometry("700x600")
##
##    scaling_var = tk.IntVar(value=1)
##    tune_svr_var = tk.IntVar(value=1)
##
##    # Scaling toggle
##    scaling_frame = tk.Frame(root)
##    scaling_frame.pack(pady=5)
##    tk.Label(scaling_frame, text="Apply scaling to all models?").pack(side=tk.LEFT)
##    tk.Radiobutton(scaling_frame, text="Yes", variable=scaling_var, value=1).pack(side=tk.LEFT)
##    tk.Radiobutton(scaling_frame, text="No", variable=scaling_var, value=0).pack(side=tk.LEFT)
##
##    # SVR tuning toggle
##    svr_frame = tk.Frame(root)
##    svr_frame.pack(pady=5)
##    tk.Label(svr_frame, text="Enable automatic SVR tuning?").pack(side=tk.LEFT)
##    tk.Radiobutton(svr_frame, text="Yes", variable=tune_svr_var, value=1).pack(side=tk.LEFT)
##    tk.Radiobutton(svr_frame, text="No", variable=tune_svr_var, value=0).pack(side=tk.LEFT)
##
##    # Load button
##    load_button = tk.Button(root, text="Load CSV File", command=lambda: load_csv(output_text, scaling_var, tune_svr_var))
##    load_button.pack(pady=10)
##
##    # Output display
##    output_text = tk.Text(root, wrap="word", height=25, width=90)
##    output_text.pack(padx=10, pady=10)
##
##    root.mainloop()
##
##
####from sklearn.model_selection import train_test_split
####from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
####from sklearn.pipeline import make_pipeline
####from sklearn.preprocessing import PolynomialFeatures, StandardScaler
####from sklearn.linear_model import LinearRegression
####from sklearn.svm import SVR
####from sklearn.gaussian_process import GaussianProcessRegressor
####from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
####import warnings
####from sklearn.exceptions import ConvergenceWarning
####import pandas as pd
####import tkinter as tk
####from tkinter import filedialog
####
####def interpret_r2_scores(r2_train, r2_test, r2_whole):
####    delta_train_test = r2_train - r2_test
####    delta_train_whole = r2_train - r2_whole
####
####    if r2_train < 0.2 and r2_test < 0.2:
####        return "Very poor fit — likely underfitting or missing key patterns."
####    elif r2_train > 0.9 and r2_test < 0.5:
####        return "Severe overfitting — perfect training fit but poor generalization."
####    elif r2_train > 0.8 and r2_test > 0.75 and delta_train_test < 0.1:
####        return "Strong fit and good generalization — model is performing reliably."
####    elif r2_train > 0.8 and delta_train_test > 0.1:
####        return "Good training fit but signs of overfitting — generalization could be improved."
####    elif r2_train > 0.5 and r2_test > 0.5:
####        return "Moderate fit — model captures some structure but may benefit from tuning."
####    else:
####        return "Unusual behavior — consider inspecting residuals or feature scaling."
####
####def LoadAndGo(filename, output_widget, use_scaling):
####    df = pd.read_csv(filename)
####    X = df.iloc[:, :-1]
####    y = df.iloc[:, -1]
####
####    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
####
####    def maybe_scale(model):
####        return make_pipeline(StandardScaler(), model) if use_scaling else model
####
####    models = {
####        "AdaBoost": maybe_scale(AdaBoostRegressor()),
####        "Random Forest": maybe_scale(RandomForestRegressor()),
####        "Polynomial Regression degree 1": maybe_scale(make_pipeline(PolynomialFeatures(degree=1), LinearRegression())),
####        "Polynomial Regression degree 2": maybe_scale(make_pipeline(PolynomialFeatures(degree=2), LinearRegression())),
####        "Polynomial Regression degree 3": maybe_scale(make_pipeline(PolynomialFeatures(degree=3), LinearRegression())),
####        "SVR": maybe_scale(SVR(kernel='rbf', C=1.0, epsilon=0.1)),
####        "GPR": maybe_scale(GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=1.0, length_scale_bounds=(1e-8, 1e3)), alpha=1e-2))
####    }
####
####    output_widget.delete("1.0", tk.END)
####
####    for name, model in models.items():
####        with warnings.catch_warnings(record=True) as w:
####            warnings.simplefilter("always", category=ConvergenceWarning)
####            model.fit(X_train, y_train)
####
####            r2_train = model.score(X_train, y_train)
####            r2_test = model.score(X_test, y_test)
####            r2_whole = model.score(X, y)
####            comment = interpret_r2_scores(r2_train, r2_test, r2_whole)
####
####            warning_str = f"\n⚠️ Warning: {str(w[-1].message)}" if w else ""
####            result = (
####                f"{name}:\n"
####                f"  R² on training = {r2_train:.3f}\n"
####                f"  R² on test     = {r2_test:.3f}\n"
####                f"  R² on whole    = {r2_whole:.3f}\n"
####                f"  → {comment}{warning_str}\n\n"
####            )
####            output_widget.insert(tk.END, result)
####            output_widget.see(tk.END)
####
####def load_csv(output_widget, scaling_var):
####    file_path = filedialog.askopenfilename(
####        title="Select CSV File",
####        filetypes=[("CSV files", "*.csv")]
####    )
####    if file_path:
####        use_scaling = scaling_var.get() == 1
####        LoadAndGo(file_path, output_widget, use_scaling)
####
####if __name__ == "__main__":
####    root = tk.Tk()
####    root.title("Model Comparison Tool")
####    root.geometry("650x550")
####
####    scaling_var = tk.IntVar(value=1)
####
####    scaling_frame = tk.Frame(root)
####    scaling_frame.pack(pady=5)
####    tk.Label(scaling_frame, text="Apply scaling to all models?").pack(side=tk.LEFT)
####    tk.Radiobutton(scaling_frame, text="Yes", variable=scaling_var, value=1).pack(side=tk.LEFT)
####    tk.Radiobutton(scaling_frame, text="No", variable=scaling_var, value=0).pack(side=tk.LEFT)
####
####    load_button = tk.Button(root, text="Load CSV File", command=lambda: load_csv(output_text, scaling_var))
####    load_button.pack(pady=10)
####
####    output_text = tk.Text(root, wrap="word", height=25, width=80)
####    output_text.pack(padx=10, pady=10)
####
####    root.mainloop()
####
####
######from sklearn.model_selection import train_test_split
######from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
######from sklearn.pipeline import make_pipeline
######from sklearn.preprocessing import PolynomialFeatures, StandardScaler
######from sklearn.linear_model import LinearRegression
######from sklearn.svm import SVR
######from sklearn.gaussian_process import GaussianProcessRegressor
######from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
######import warnings
######from sklearn.exceptions import ConvergenceWarning
######import pandas as pd
######import tkinter as tk
######from tkinter import filedialog
######
######def interpret_r2_scores(r2_train, r2_test, r2_whole):
######    delta_train_test = r2_train - r2_test
######    delta_train_whole = r2_train - r2_whole
######
######    if r2_train < 0.2 and r2_test < 0.2:
######        return "Very poor fit — likely underfitting or missing key patterns."
######    elif r2_train > 0.9 and r2_test < 0.5:
######        return "Severe overfitting — perfect training fit but poor generalization."
######    elif r2_train > 0.8 and r2_test > 0.75 and delta_train_test < 0.1:
######        return "Strong fit and good generalization — model is performing reliably."
######    elif r2_train > 0.8 and delta_train_test > 0.1:
######        return "Good training fit but signs of overfitting — generalization could be improved."
######    elif r2_train > 0.5 and r2_test > 0.5:
######        return "Moderate fit — model captures some structure but may benefit from tuning."
######    else:
######        return "Unusual behavior — consider inspecting residuals or feature scaling."
######
######def LoadAndGo(filename, output_widget):
######    df = pd.read_csv(filename)
######    X = df.iloc[:, :-1]
######    y = df.iloc[:, -1]
######
######    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
######
######    models = {
######        "AdaBoost": AdaBoostRegressor(),
######        "Random Forest": RandomForestRegressor(),
######        "Polynomial Regression degree 1": make_pipeline(PolynomialFeatures(degree=1), LinearRegression()),
######        "Polynomial Regression degree 2": make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),        
######        "Polynomial Regression degree 3": make_pipeline(PolynomialFeatures(degree=3), LinearRegression()),
######        "SVR": make_pipeline(StandardScaler(), SVR(kernel='rbf', C=1.0, epsilon=0.1)),
######        "GPR": GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=1.0, length_scale_bounds=(1e-8, 1e3)), alpha=1e-2)        
######    }
######
######    output_widget.delete("1.0", tk.END)
######
######    for name, model in models.items():
######        with warnings.catch_warnings(record=True) as w:
######            warnings.simplefilter("always", category=ConvergenceWarning)
######            model.fit(X_train, y_train)
######
######            r2_train = model.score(X_train, y_train)
######            r2_test = model.score(X_test, y_test)
######            r2_whole = model.score(X, y)
######            comment = interpret_r2_scores(r2_train, r2_test, r2_whole)
######
######            warning_str = f"\n⚠️ Warning: {str(w[-1].message)}" if w else ""
######            result = (
######                f"{name}:\n"
######                f"  R² on training = {r2_train:.3f}\n"
######                f"  R² on test     = {r2_test:.3f}\n"
######                f"  R² on whole    = {r2_whole:.3f}\n"
######                f"  → {comment}{warning_str}\n\n"
######            )
######            output_widget.insert(tk.END, result)
######            output_widget.see(tk.END)
######
######def load_csv(output_widget):
######    file_path = filedialog.askopenfilename(
######        title="Select CSV File",
######        filetypes=[("CSV files", "*.csv")]
######    )
######    if file_path:
######        LoadAndGo(file_path, output_widget)
######
######if __name__ == "__main__":
######    root = tk.Tk()
######    root.title("Model Comparison Tool")
######    root.geometry("600x500")
######
######    load_button = tk.Button(root, text="Load CSV File", command=lambda: load_csv(output_text))
######    load_button.pack(pady=10)
######
######    output_text = tk.Text(root, wrap="word", height=25, width=80)
######    output_text.pack(padx=10, pady=10)
######
######    root.mainloop()
######
######
########from sklearn.model_selection import train_test_split
########from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
########from sklearn.pipeline import make_pipeline
########from sklearn.preprocessing import PolynomialFeatures
########from sklearn.linear_model import LinearRegression
########from sklearn.svm import SVR
########from sklearn.gaussian_process import GaussianProcessRegressor
########from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
########import warnings
########from sklearn.exceptions import ConvergenceWarning
########import pandas as pd
########import tkinter as tk
########from tkinter import filedialog
########
########
########def LoadAndGo(filename):
########    # Load data
########    df = pd.read_csv(filename)
########    
########    # === Separate features and target ===
########    X = df.iloc[:, :-1]
########    y = df.iloc[:, -1]
########
########    # Split once
########    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
########
########    # Fit models
########    models = {
########        "AdaBoost": AdaBoostRegressor(),
########        "Random Forest": RandomForestRegressor(),
########        "Polynomial Regression degree 1": make_pipeline(PolynomialFeatures(degree=1), LinearRegression()),
########        "Polynomial Regression degree 2": make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),        
########        "Polynomial Regression degree 3": make_pipeline(PolynomialFeatures(degree=3), LinearRegression()),
########        "SVR": SVR(kernel='rbf', C=1.0, epsilon=0.1),
########        "GPR": GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=1.0,length_scale_bounds=(1e-8, 1e3)), alpha=1e-2)        
########    }
########
########    # Evaluate
########    for name, model in models.items():
########        with warnings.catch_warnings(record=True) as w:
########            warnings.simplefilter("always", category=ConvergenceWarning)
########            
########            # Fit your model here
########            model.fit(X_train, y_train)
########            
########            # Check for warnings
########            if w:
########                warning_msg = str(w[-1].message)
########                warning_str=f"⚠️ Warning: {warning_msg}"
########            else:
########                warning_str=""
########        
########    ##        model.fit(X_train, y_train)
########            r2_train = model.score(X_train, y_train)
########            r2_whole = model.score(X, y)
########            print(f"{name}: R² on training = {r2_train:.3f}, R² on whole = {r2_whole:.3f}"+interpret_r2_scores(r2_train, r2_whole)+warning_str)
########
########def interpret_r2_scores(r2_train, r2_whole):
########    comments = []
########    delta = r2_train - r2_whole
########
########    if r2_train < 0.2 and r2_whole < 0.2:
########        comment = " Very poor fit — likely underfitting or missing key patterns."
########    elif r2_train > 0.9 and r2_whole < 0.5:
########        comment = " Severe overfitting — perfect training fit but poor generalization."
########    elif r2_train > 0.8 and r2_whole > 0.75 and delta < 0.1:
########        comment = " Strong fit and good generalization — model is performing reliably."
########    elif r2_train > 0.8 and delta > 0.1:
########        comment = " Good training fit but signs of overfitting — generalization could be improved."
########    elif r2_train > 0.5 and r2_whole > 0.5:
########        comment = " Moderate fit — model captures some structure but may benefit from tuning."
########    else:
########        comment = " Unusual behavior — consider inspecting residuals or feature scaling."
########    return comment
########
########def load_csv():
########    # Open file dialog to select CSV
########    file_path = filedialog.askopenfilename(
########        title="Select CSV File",
########        filetypes=[("CSV files", "*.csv")]
########    )
########    
########    if file_path:
########        LoadAndGo(file_path)
########
########
########if __name__ == "__main__":
########    root = tk.Tk()
########    root.title("ALL")
########    root.geometry("300x150")
########
########    # Add button to trigger CSV loading
########    load_button = tk.Button(root, text="Load CSV File", command=load_csv)
########    load_button.pack(pady=50)
########
########    # Run the GUI loop
########    root.mainloop()
