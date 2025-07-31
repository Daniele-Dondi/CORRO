import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_main_effects(df, response_column):
    """
    Plots main effects for each factor in df on the response_column.
    
    Parameters:
    df : DataFrame with factor columns and one response column
    response_column : Name of the column holding the measured response
    """
    factors = [col for col in df.columns if col != response_column]
    num_factors = len(factors)
    
    fig, axes = plt.subplots(1, num_factors, figsize=(5 * num_factors, 4))
    if num_factors == 1:
        axes = [axes]  # make it iterable
    
    for ax, factor in zip(axes, factors):
        sns.pointplot(x=factor, y=response_column, data=df, errorbar=None, ax=ax)
        ax.set_title(f"Main Effect: {factor}")
        ax.set_ylabel(response_column)
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()

#EXAMPLE USAGE
df = pd.DataFrame({
    "Temperature (°C)": [50, 50, 70, 70],
    "pH": [6, 8, 6, 8],
    "Time (min)": [30, 30, 30, 30],
    "Yield (%)": [65, 70, 80, 85]
})

plot_main_effects(df, response_column="Yield (%)")
